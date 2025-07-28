"""
中央日志配置模块。

该模块提供了一个统一的函数 `setup_logging`，用于在应用程序启动时配置全局日志记录器。
它遵循最佳实践，结合了控制台输出和文件输出，并提供了清晰的日志格式，便于调试和追踪。
"""

import logging
import logging.handlers
from pathlib import Path

# 定义日志格式，确保日志来源清晰可追溯
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - [%(module)s.%(funcName)s:%(lineno)d] - %(message)s"


def setup_logging(log_level: str = "INFO") -> None:
    """
    配置全局日志记录器。

    此函数应在应用程序启动时调用一次。
    它会设置一个根记录器，将日志同时输出到控制台和可轮换的日志文件中。

    Args:
        log_level (str): 要设置的最低日志级别 (例如 "DEBUG", "INFO", "WARNING")。
                         默认为 "INFO"。
    """
    # 创建 logs 目录 (如果不存在)
    log_dir = Path(__file__).resolve().parent.parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)

    # 获取根 logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # 清除任何可能已经存在的 handlers，以避免重复记录
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # 1. 创建控制台 handler (StreamHandler)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))

    # 将 handlers 添加到根 logger
    root_logger.addHandler(console_handler)

    # 提供一条初始日志，确认配置成功
    logging.info("日志系统初始化完成，将记录到控制台和")
