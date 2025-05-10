#!/usr/bin/env python
"""
提取器基类模块
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from bs4 import BeautifulSoup

from ..utils.logger import logger


class BaseExtractor(ABC):
    """
    提取器基类，定义提取器接口
    所有具体提取器实现必须继承此类
    """
    
    def __init__(self, name: str = "base_extractor"):
        """
        初始化提取器
        
        Args:
            name: 提取器名称
        """
        self.name = name
        self.logger = logger
        
    @abstractmethod
    def extract_title(self, soup: BeautifulSoup) -> str:
        """
        提取文章标题
        
        Args:
            soup: BeautifulSoup对象
            
        Returns:
            str: 文章标题
        """
        pass
        
    @abstractmethod
    def extract_content(self, soup: BeautifulSoup) -> str:
        """
        提取文章内容
        
        Args:
            soup: BeautifulSoup对象
            
        Returns:
            str: 文章内容
        """
        pass
        
    @abstractmethod
    def extract_publish_time(self, soup: BeautifulSoup) -> Optional[datetime]:
        """
        提取发布时间
        
        Args:
            soup: BeautifulSoup对象
            
        Returns:
            Optional[datetime]: 发布时间，如果无法提取则返回None
        """
        pass
        
    @abstractmethod
    def extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        """
        提取作者
        
        Args:
            soup: BeautifulSoup对象
            
        Returns:
            Optional[str]: 作者，如果无法提取则返回None
        """
        pass 