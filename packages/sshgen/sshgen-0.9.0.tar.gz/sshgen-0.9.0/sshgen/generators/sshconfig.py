#!/usr/bin/env python
import copy
import logging
from pathlib import Path

from sshgen.models.host import HostModel
from sshgen.utils.common import CommonUtils
from sshgen.utils.file import FileUtils

log = logging.getLogger(__name__)


class SSHConfig:
    def __init__(self, models: list[HostModel], output_file: Path | None = None):
        self.raw_models = models
        self.template_path = FileUtils.as_package_file("templates/ssh_config.template")
        self.ssh_template = self._open_template()
        self.output_file = output_file
        self._skipped: list[HostModel] = []

    def generate(self) -> None:
        filtered_models: list[HostModel] = self._filter_models()
        configs: list[str] = [self._process(m) for m in filtered_models]
        self._save_config(configs)

    def _filter_models(self) -> list[HostModel]:
        models = copy.deepcopy(self.raw_models)
        log.debug("Filtering hosts where _skip metafield was defined")

        filtered_models: list[HostModel] = []

        for model in models:
            is_skipped = model.meta_fields.skip
            log.debug("Host %s should be skipped: %s", model.host, is_skipped)

            if is_skipped:
                self._skipped.append(model)
                continue

            filtered_models.append(model)

        return filtered_models

    def _process(self, model: HostModel) -> str:
        log.debug("Processing %s from group %s", model.host, model.host_group)
        temp = (
            self.ssh_template.replace("{{ host }}", model.host)
            .replace("{{ hostname }}", model.ansible_host)
            .replace("{{ host_comment }}", model.host_group)
            .replace("{{ ssh_user }}", model.ansible_user)
            .replace("{{ port }}", f"Port {model.ansible_port!s}")
        )

        log.debug("Adding SSH port %s for host %s", model.ansible_port, model.host)

        if model.meta_fields.aliases:
            log.debug("Adding aliases %s for host %s ", model.meta_fields.aliases, model.host)
            temp = temp.replace("{{ host_alias }}", " ".join(model.meta_fields.aliases))
        else:
            temp = temp.replace("{{ host_alias }} #", "#")

        if model.meta_fields.auth_type and model.meta_fields.auth_path:
            log.debug("Adding custom auth methods for host %s ", model.host)
            temp = temp.replace("{{ identification }}", f"{model.meta_fields.auth_type} {model.meta_fields.auth_path}")

        fallback_auth = "\n".join(self._get_fallback_auth())
        temp = temp.replace("{{ identification }}", fallback_auth).replace("{{ host_alias }}", "")

        return temp

    def _open_template(self) -> str:
        log.debug("Using template file %s to generate ssh config", self.template_path)
        return self.template_path.read_text()

    def _save_config(self, templates: list[str]) -> None:
        CommonUtils.check_and_exit(
            condition=len(templates) > 0, message="No templates found to generate. Exiting...", exit_code=0
        )

        FileUtils.create_file(self.output_file)
        FileUtils.write_text(file_path=self.output_file, data="\n".join(templates))

        log.info("Generated SSH config file was saved to %s", self.output_file)
        log.debug("Skipped hosts list: %s", self._parse_skipped())
        log.info("Total processed hosts: %d, total skipped hosts: %d", len(templates), len(self._skipped))

    def _parse_skipped(self) -> str:
        if len(self._skipped) > 0:
            return ", ".join([model.ansible_host for model in self._skipped])

        return "no hosts found"

    @staticmethod
    def _get_fallback_auth() -> list[str]:
        parameter = "IdentitiesOnly yes"
        width = len(parameter) + 4
        return ["IdentityFile ~/.ssh/ssh_key", f"{parameter: >{width}}"]
