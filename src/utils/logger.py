"""日志工具"""

from __future__ import annotations
import logging
import sys


def setup_logger(name: str = "tdf", level: str = "INFO") -> logging.Logger:
    """配置统一日志"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        # 不向上级传播，避免重复
        logger.propagate = False

    return logger


# 全局 logger 实例
logger = setup_logger()
