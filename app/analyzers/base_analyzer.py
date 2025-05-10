#!/usr/bin/env python
"""
分析器基类模块
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..models.article import Article
from ..utils.logger import logger


class BaseAnalyzer(ABC):
    """
    分析器基类，定义分析器接口
    所有具体分析器实现必须继承此类
    """
    
    def __init__(self, name: str = "base_analyzer"):
        """
        初始化分析器
        
        Args:
            name: 分析器名称
        """
        self.name = name
        self.logger = logger
        
    @abstractmethod
    def prepare_content(self, articles: List[Article]) -> str:
        """
        准备文章内容，用于输入到分析模型
        
        Args:
            articles: 文章对象列表
            
        Returns:
            str: 准备好的内容
        """
        pass
        
    @abstractmethod
    def analyze(self, articles: List[Article]) -> Optional[str]:
        """
        分析文章
        
        Args:
            articles: 文章对象列表
            
        Returns:
            Optional[str]: 分析结果，失败则返回None
        """
        pass 