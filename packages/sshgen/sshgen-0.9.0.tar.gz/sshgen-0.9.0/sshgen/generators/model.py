#!/usr/bin/env python
import logging

from ruamel.yaml import CommentedMap

from sshgen.models.host import HostModel
from sshgen.models.metafields import MetaFieldsModel

log = logging.getLogger(__name__)


class MapToHost:
    # Improve the method to reduce complexity. See: https://www.flake8rules.com/rules/C901.html
    @staticmethod
    def convert(parsed_hosts: CommentedMap) -> list[HostModel]:
        host_models = []

        for host_group, hosts in parsed_hosts.items():
            for host, host_details in hosts["hosts"].items():
                ansible_host = host_details.get("ansible_host")
                ansible_user = host_details.get("ansible_user", "root")  # Fallback to `root` user if field not found

                if ansible_host is None:
                    log.warning(
                        "Host %s in group %s must contain ansible_host. Skip host processing.", host, host_group
                    )
                    log.debug("Host %s in group %s will not be counted in the total skipped hosts.", host, host_group)
                    continue

                model = HostModel(
                    host=host,
                    host_group=host_group,
                    ansible_host=ansible_host.strip(),
                    ansible_user=ansible_user.strip(),
                )

                if host_details.get("ansible_port"):
                    model.ansible_port = host_details.get("ansible_port")

                meta = host_details.get("_meta", {})
                auth_type = meta.get("_auth_type")
                auth_path = meta.get("_auth_path")
                aliases = meta.get("_aliases")
                skip = meta.get("_skip", False)  # Fallback to False if no 'skip' field found

                if any(isinstance(field, str | list) for field in (auth_type, auth_path, aliases)):
                    model.meta_fields = MetaFieldsModel(auth_type, auth_path, aliases)

                model.meta_fields.skip = skip

                if model.meta_fields.aliases:
                    alias_count_map: dict[str, int] = {}

                    for alias in model.meta_fields.aliases:
                        if alias == host:
                            log.warning(
                                "Host %s and alias %s are equal to each other. Skip alias processing.", host, alias
                            )
                            continue

                        alias_stripped = alias.strip()
                        alias_count_map[alias_stripped] = alias_count_map.get(alias, 0) + 1

                    log.debug("Aliases found for host %s in group %s: %s", host, host_group, alias_count_map)

                    duplicates = [alias for alias, count in alias_count_map.items() if count > 1]

                    if duplicates:
                        log.warning("Duplicated aliases %s found for host: %s", duplicates, model.host)

                    model.meta_fields.aliases = list(alias_count_map.keys())

                host_models.append(model)

        log.debug("Total hosts found (include skipped): %s", len(host_models))

        return host_models
