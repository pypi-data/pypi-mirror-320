#!/usr/bin/env python
import logging
import sys
from pathlib import Path

from sshgen.utils.common import CommonUtils

log = logging.getLogger(__name__)


class FileUtils:
    @staticmethod
    def get_hosts_path(file_path: str) -> Path:
        resolved_path = FileUtils.resolve_path(file_path)

        CommonUtils.check_and_exit(
            resolved_path.exists(), f"Ansible hosts file does not exists at {resolved_path}. Exiting..."
        )
        CommonUtils.check_and_exit(
            FileUtils.is_yaml_file(resolved_path),
            "Ansible hosts file is not a yaml file. Valid extensions are: yaml or yml. Exiting...",
        )
        CommonUtils.check_and_exit(
            not FileUtils.is_empty(resolved_path), f"Ansible hosts file {resolved_path} is empty. Exiting..."
        )

        return resolved_path

    @staticmethod
    def get_output_path(file_path: str) -> Path:
        return FileUtils.resolve_path(file_path)

    @staticmethod
    def as_package_file(file_path: str) -> Path:
        return Path(__file__).resolve().parent.parent / Path(file_path)

    @staticmethod
    def resolve_path(file_path: str) -> Path:
        return FileUtils.get_base_path() / Path(file_path)

    @staticmethod
    def get_base_path() -> Path:
        return Path(__file__).cwd().resolve()

    @staticmethod
    def is_yaml_file(file_path: Path) -> bool:
        return file_path.suffix in {".yml", ".yaml"}

    @staticmethod
    def is_empty(file_path: Path) -> bool:
        return file_path.is_file() and file_path.stat().st_size == 0

    @staticmethod
    def create_file(file_path: Path) -> None:
        if not file_path.exists():
            log.debug("Path %s is not exists, trying to create required folders and file", file_path)

        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.touch(exist_ok=True)
        except OSError as e:
            log.exception("Failed to create file or directory: %s, reason: %s", file_path, e.strerror)
            sys.exit(1)

    @staticmethod
    def write_text(file_path: Path, data: str) -> None:
        try:
            file_path.write_text(data)
        except OSError as e:
            log.exception("Failed to create file or directory: %s, reason: %s", file_path, e.strerror)
            sys.exit(1)
