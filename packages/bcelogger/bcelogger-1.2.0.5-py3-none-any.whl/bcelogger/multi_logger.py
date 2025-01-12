#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import logging
import logging.handlers
import os
import sys

from logit import base_logger
from logit.conf import logit_multi_conf

_logger_initialized = []


def setup_multiprocess_logger(logger_name=None, output=None):
    """
    除了主进程外，每个进程在开始前都需要重新设置logger
    :param logger_name: logger name
    :param output: output path
    :return: logger
    """
    if logger_name is None:
        logger_name = sys._getframe().f_code.co_filename

    logger = logging.getLogger(logger_name)
    if logger_name in _logger_initialized:
        print("old logger_name is {}", logger_name)
        return logger

    file_name = logit_multi_conf.FileName
    if output is not None:
        if output.endswith(".txt") or output.endswith(".log"):
            file_name = output
        else:
            file_name = os.path.join(output, "log.txt")
    file_name = "{}.pid{}".format(file_name, os.getpid())

    multi_config = dict({
        "logger_name": logger_name,
        "file_name": file_name,
        "debug_file_suffix": logit_multi_conf.DEBUG_FILE_SUFFIX,
        "info_file_suffix": logit_multi_conf.INFO_FILE_SUFFIX,
        "wf_file_suffix": logit_multi_conf.WF_FILE_SUFFIX,
        "prefix": logit_multi_conf.Prefix,
        "max_file_num": logit_multi_conf.MaxFileNum,
    })

    multi_logger = base_logger.Logger(multi_config)
    _logger_initialized.append(logger_name)
    return multi_logger.logger
