#!/usr/bin/env python
import logging

from sshgen.models.loglevel import LogLevel


def init_logger(level: LogLevel) -> None:
    logging.basicConfig(
        level=level.value, format="[%(asctime)s] [%(levelname)s] - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
