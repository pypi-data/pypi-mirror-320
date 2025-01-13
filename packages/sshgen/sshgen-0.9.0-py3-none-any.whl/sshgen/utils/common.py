#!/usr/bin/env python
import logging
import sys

log = logging.getLogger(__name__)


class CommonUtils:
    @staticmethod
    def check_and_exit(condition: bool, message: str, exit_code: int = 1) -> None:
        if not condition:
            log.error(message)
            log.debug("Exiting with code: %s", exit_code)
            sys.exit(exit_code)
