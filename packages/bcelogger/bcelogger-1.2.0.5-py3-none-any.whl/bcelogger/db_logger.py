#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from logit import base_logger
from logit.conf import logit_db_conf

__db_config = dict({
    "logger_name": "db_logger",
    "file_name": logit_db_conf.DBFileName,
    "debug_file_suffix": logit_db_conf.DB_DEBUG_FILE_SUFFIX,
    "info_file_suffix": logit_db_conf.DB_INFO_FILE_SUFFIX,
    "wf_file_suffix": logit_db_conf.DB_WF_FILE_SUFFIX,
    "prefix": logit_db_conf.DBPrefix,
    "max_file_num": logit_db_conf.DBMaxFileNum,
})

_db_logger = base_logger.Logger(__db_config)


def debug(message, *args, **kwargs):
    """
   接口：调试级别的日志
   :param message: 日志内容
   :param args: 格式化参数
   :param kwargs: 日志tag参数
   :return:
   """
    fmt_message = base_logger.format_message(message, **kwargs)
    _db_logger.logger.debug(fmt_message, *args, stacklevel=2)


def info(message, *args, **kwargs):
    """
    接口：info级别的日志
    :param message: 日志内容
    :param args: 格式化参数
    :param kwargs: 日志tag参数
    :return:
    """
    fmt_message = base_logger.format_message(message, **kwargs)
    _db_logger.logger.info(fmt_message, *args, stacklevel=2)


def trace(message, *args, **kwargs):
    """
    接口：追踪调用链路级别的日志
    :param message: 日志内容
    :param args: 格式化参数
    :param kwargs: 日志tag参数
    :return:
    """
    fmt_message = base_logger.format_message(message, **kwargs)
    _db_logger.logger.log(base_logger.level_trace, fmt_message, *args, stacklevel=2)


def warning(message, *args, **kwargs):
    """
    接口：警告级别的日志
    :param message: 日志内容
    :param args: 格式化参数
    :param kwargs: 日志tag参数
    :return:
    """
    fmt_message = base_logger.format_message(message, **kwargs)
    _db_logger.logger.warning(fmt_message, *args, stacklevel=2)


def error(message, *args, **kwargs):
    """
    接口：错误级别的日志
    :param message: 日志内容
    :param args: 格式化参数
    :param kwargs: 日志tag参数
    :return:
    """
    fmt_message = base_logger.format_message(message, **kwargs)
    _db_logger.logger.error(fmt_message, *args, stacklevel=2)


def fatal(message, *args, **kwargs):
    """
    接口：严重错误级别的日志
    :param message: 日志内容
    :param args: 格式化参数
    :param kwargs: 日志tag参数
    :return:
    """
    fmt_message = base_logger.format_message(message, **kwargs)
    _db_logger.logger.fatal(fmt_message, *args, stacklevel=2)
