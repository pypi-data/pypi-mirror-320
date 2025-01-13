#!/usr/bin/env python
import logging

from sshgen.logger import init_logger
from sshgen.models.loglevel import LogLevel
from sshgen.utils.app import AppUtils
from sshgen.utils.file import FileUtils

log = logging.getLogger(__name__)


def run() -> None:
    init_logger(level=LogLevel.DEBUG)
    hosts_file = "./examples/hosts.yml"
    config_file = "./config"

    log.info("Starting sshgen with pre-defined settings")
    log.debug("Debug mode is ON")
    log.debug("Reading hosts from %s", hosts_file)
    log.debug("Saving generated config to %s", config_file)

    hosts_file = FileUtils.get_hosts_path(file_path=hosts_file)
    output_file = FileUtils.get_output_path(file_path=config_file)

    sshgen = AppUtils(hosts_file, output_file)
    sshgen.generate_ssh_config()


if __name__ == "__main__":
    run()
