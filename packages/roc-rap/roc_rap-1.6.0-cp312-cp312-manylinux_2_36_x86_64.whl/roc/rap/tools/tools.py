#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os.path as osp

from poppy.core.generic.paths import Paths
from poppy.core.logger import logger as poppy_logger

__all__ = ["paths", "to_logger"]

# root directory of the module
_ROOT_DIRECTORY = osp.abspath(
    osp.join(
        osp.dirname(__file__),
        osp.pardir,
    )
)

# create a path object that can be used to get some common path in the module
paths = Paths(_ROOT_DIRECTORY)


def to_logger(message, level="info", logger=poppy_logger):
    """
    Send a message to the logger.
    (Can be used in Cython modules)

    :param message: message
    :param level: logging level
    :param logger: logger to use
    :return: None
    """
    logging_function_dict = {
        "debug": logger.debug,
        "info": logger.info,
        "warn": logger.warning,
        "warning": logger.warning,
        "error": logger.error,
        "critical": logger.critical,
        "exception": logger.exception,
    }
    logging_function = logging_function_dict.get(level.lower(), logger.info)
    logging_function(message)
