# -*- coding: utf-8 -*-
# 项目设置文件
import sys
import logging

from loguru import logger


class InterceptHandler(logging.Handler):

    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except AttributeError:
            level = record.levelno

        frame, depth = logging.currentframe(), 6
        # frame, depth = sys._getframe(6), 6
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(
            depth=depth,
            exception=record.exc_info
        ).log(level, record.getMessage())


def setup_logging(log_level):
    """设置日志"""
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(log_level)
    logging.basicConfig(handlers=[InterceptHandler()], level=0)
    for _log in ['uvicorn', 'httpx']:
        _logger = logging.getLogger(_log)
        _logger.handlers = [InterceptHandler()]

    logger.configure(handlers=[
        {
            "sink": sys.stdout,
            "serialize": False,  # 格式化
            "colorize": True  # 带颜色打印
        },
        {
            "sink": "logs/my.log",  # 日志文件
            "enqueue": True,  # 异步写入
            "colorize": False  # 文件不要颜色
        }
    ])
