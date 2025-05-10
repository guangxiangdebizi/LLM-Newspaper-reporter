#!/usr/bin/env python
"""
日志配置模块
"""

import logging
import os
from pathlib import Path


def setup_logger(name: str = "news_analyzer", log_level: str = "INFO") -> logging.Logger:
    """
    配置并返回一个日志记录器
    
    Args:
        name: 日志记录器名称
        log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        配置好的日志记录器
    """
    # 转换日志级别字符串为对应的常量
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"无效的日志级别: {log_level}")
    
    # 获取环境变量中的日志级别，如果存在的话覆盖默认设置
    env_log_level = os.getenv("LOG_LEVEL")
    if env_log_level:
        numeric_level = getattr(logging, env_log_level.upper(), numeric_level)
    
    # 创建日志目录
    log_dir = Path("./logs")
    log_dir.mkdir(exist_ok=True, parents=True)
    
    # 配置日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # 文件处理器
    file_handler = logging.FileHandler(
        log_dir / f"{name}.log", 
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    
    # 获取或创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(numeric_level)
    
    # 清除现有处理器，避免重复添加
    if logger.handlers:
        logger.handlers.clear()
        
    # 添加处理器
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger


# 创建默认的日志记录器
logger = setup_logger()


if __name__ == "__main__":
    # 测试日志记录
    logger.debug("这是一条调试消息")
    logger.info("这是一条信息消息")
    logger.warning("这是一条警告消息")
    logger.error("这是一条错误消息")
    logger.critical("这是一条严重错误消息") 