from __future__ import annotations

import logging
import os
import sys

FORMATTER = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
LOG_FILE = os.path.join(os.getcwd(), "logfile.log")


class Logger:
    """Factory for console/file loggers used in pipeline scripts."""

    def __init__(self, show: bool) -> None:
        self.show = show

    def get_console_handler(self) -> logging.StreamHandler:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(FORMATTER)
        return handler

    def get_file_handler(self) -> logging.FileHandler:
        handler = logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8")
        handler.setFormatter(FORMATTER)
        return handler

    def get_logger(self, logger_name: str) -> logging.Logger:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)
        logger.handlers = []
        if self.show:
            logger.addHandler(self.get_console_handler())
        logger.addHandler(self.get_file_handler())
        logger.propagate = False
        return logger
