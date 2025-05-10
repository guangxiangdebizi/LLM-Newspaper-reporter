#!/usr/bin/env python
"""
爬虫基类模块
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional

from ..models.article import Article
from ..utils.logger import logger


class BaseScraper(ABC):
    """
    爬虫基类，定义爬虫接口
    所有具体爬虫实现必须继承此类
    """
    
    def __init__(self, name: str = "base_scraper"):
        """
        初始化爬虫
        
        Args:
            name: 爬虫名称
        """
        self.name = name
        self.logger = logger
        
    @abstractmethod
    def get_categories(self) -> Dict[str, str]:
        """
        获取支持的新闻分类及其URL
        
        Returns:
            Dict[str, str]: 分类名称到分类URL的映射
        """
        pass
        
    @abstractmethod
    def get_article_urls(self, category_url: str, limit: int = 10) -> List[str]:
        """
        获取分类页面中的文章URL列表
        
        Args:
            category_url: 分类页面URL
            limit: 最多获取多少篇文章
            
        Returns:
            List[str]: 文章URL列表
        """
        pass
        
    @abstractmethod
    def scrape_article(self, url: str, category: str) -> Optional[Article]:
        """
        爬取单篇文章内容
        
        Args:
            url: 文章URL
            category: 文章分类
            
        Returns:
            Optional[Article]: 文章对象，失败则返回None
        """
        pass
        
    def scrape_category(self, category: str, limit: int = 10) -> List[Article]:
        """
        爬取某个分类下的所有文章
        
        Args:
            category: 分类名称
            limit: 最多爬取多少篇文章
            
        Returns:
            List[Article]: 文章对象列表
        """
        self.logger.info(f"爬取分类 '{category}'")
        articles = []
        
        try:
            # 获取分类URL
            categories = self.get_categories()
            if category not in categories:
                self.logger.error(f"不支持的分类: {category}")
                self.logger.info(f"支持的分类: {', '.join(categories.keys())}")
                return []
                
            category_url = categories[category]
            
            # 获取文章URL列表
            article_urls = self.get_article_urls(category_url, limit=limit)
            self.logger.info(f"在分类 '{category}' 中找到 {len(article_urls)} 篇文章")
            
            if not article_urls:
                self.logger.warning(f"未找到任何文章URL")
                return []
                
            # 爬取每篇文章
            for article_url in article_urls:
                try:
                    article = self.scrape_article(article_url, category)
                    if article:
                        articles.append(article)
                        self.logger.info(f"成功爬取文章: {article.title[:20]}...")
                except Exception as e:
                    self.logger.error(f"爬取文章出错 {article_url}: {e}")
                    
        except Exception as e:
            self.logger.error(f"爬取分类出错 '{category}': {e}")
            
        return articles 