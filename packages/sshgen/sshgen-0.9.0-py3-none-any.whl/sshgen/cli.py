#!/usr/bin/env python
from typing import Annotated

from cyclopts import App, Group
from cyclopts import Parameter

from sshgen import __app_name__, __version__
from sshgen.logger import init_logger
from sshgen.models.loglevel import LogLevel
from sshgen.utils.app import AppUtils
from sshgen.utils.file import FileUtils

app = App(version=f"{__app_name__} v{__version__}", version_flags=["--version"], help_flags=["--help"])
app.meta.group_parameters = Group("Debug Output")


@app.command(name="generate")
def generate_hosts_file(
    hosts_file: Annotated[str, Parameter(name=["--hosts-file", "-h"], allow_leading_hyphen=True)] = "./hosts.yml",
    output: Annotated[str, Parameter(["--output", "-o"])] = "./config",
) -> None:
    """
    Command to generate SSH configuration file.

    By default, it uses file hosts.yml placed in your working directory and outputs to the file named "config".

    Example usage: sshgen generate -o my_ssh_config
    """

    hosts_file = FileUtils.get_hosts_path(file_path=hosts_file)
    output_file = FileUtils.get_output_path(file_path=output)

    sshgen = AppUtils(hosts_file, output_file)
    sshgen.generate_ssh_config()


@app.meta.default()
def main(
    *tokens: Annotated[str, Parameter(show=False, allow_leading_hyphen=True)],
    verbose: Annotated[
        bool, Parameter(name="--verbose", show_default=False, negative="", env_var=["SSHGEN_VERBOSE", "SSHGEN_DEBUG"])
    ] = False,
) -> None:
    """
    sshgen generates SSH configuration file based on an Ansible hosts file.
    """

    if verbose:
        init_logger(level=LogLevel.DEBUG)
    else:
        init_logger(level=LogLevel.INFO)

    app(tokens)


if __name__ == "__main__":
    app.meta()
