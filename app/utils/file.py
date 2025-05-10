#!/usr/bin/env python
"""
文件操作工具模块
"""

from datetime import datetime
from pathlib import Path
from typing import Optional

from ..config.settings import OUTPUT_DIR
from ..utils.logger import logger


def save_report(content: str, category: str, custom_dir: Optional[Path] = None) -> Path:
    """
    保存分析报告到文件
    
    Args:
        content: 报告内容
        category: 报告分类
        custom_dir: 自定义保存目录，如果为None则使用默认目录
        
    Returns:
        Path: 保存的文件路径
    """
    # 使用自定义目录或默认目录
    output_dir = custom_dir or OUTPUT_DIR
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{category}_分析报告_{timestamp}.md"
    filepath = output_dir / filename
    
    # 写入文件
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"报告已保存到: {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"保存报告出错: {e}")
        # 创建备用文件路径
        backup_path = output_dir / f"backup_{filename}"
        try:
            with open(backup_path, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"报告已保存到备用路径: {backup_path}")
            return backup_path
        except Exception as e2:
            logger.error(f"保存报告到备用路径出错: {e2}")
            raise 