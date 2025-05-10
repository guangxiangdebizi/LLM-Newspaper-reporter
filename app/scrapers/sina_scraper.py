#!/usr/bin/env python
"""
新浪新闻爬虫实现
"""

import re
import random
import time
from typing import List, Dict, Optional

from ..config.settings import SINA_CATEGORIES, MAX_RETRIES
from ..extractors.sina_extractor import SinaExtractor
from ..models.article import Article
from ..scrapers.base_scraper import BaseScraper
from ..utils.http import get_soup


class SinaScraper(BaseScraper):
    """新浪新闻爬虫实现"""
    
    def __init__(self):
        """初始化新浪爬虫"""
        super().__init__(name="sina_scraper")
        self.extractor = SinaExtractor()
        
    def get_categories(self) -> Dict[str, str]:
        """
        获取支持的新闻分类及其URL
        
        Returns:
            Dict[str, str]: 分类名称到分类URL的映射
        """
        return SINA_CATEGORIES
        
    def get_article_urls(self, category_url: str, limit: int = 10) -> List[str]:
        """
        获取分类页面中的文章URL列表
        
        Args:
            category_url: 分类页面URL
            limit: 最多获取多少篇文章
            
        Returns:
            List[str]: 文章URL列表
        """
        self.logger.info(f"获取文章URL: {category_url}")
        urls = []
        
        # 获取分类页面的HTML
        soup = get_soup(category_url, max_retries=MAX_RETRIES)
        if not soup:
            self.logger.error(f"无法获取分类页面: {category_url}")
            # 备用策略：直接使用预定义的新浪新闻URL模式
            return self._get_backup_urls(category_url, limit)
            
        # 所有链接
        all_links = []
        
        # 查找新闻链接，筛选出新浪域名下的内容页URL
        for link in soup.find_all('a', href=True):
            url = link.get('href', '').strip()
            
            # 处理相对URL
            if url.startswith('/'):
                base_domain = '/'.join(category_url.split('/')[:3])  # 如 https://news.sina.com.cn
                url = base_domain + url
            elif not url.startswith('http'):
                continue
            
            # 筛选符合条件的URL
            if (('sina.com.cn' in url or 'sinaimg.cn' in url) and 
                any(x in url for x in ['/doc-i', '/article_', '/2025-', '/n_', '?id='])):
                all_links.append(url)
        
        # 如果找到了链接，从中提取不重复的
        for url in all_links:
            if url not in urls:
                urls.append(url)
                if len(urls) >= limit:
                    break
        
        # 如果没找到足够的链接，尝试一些常见的新闻列表选择器
        if len(urls) < limit:
            selectors = [
                ".news-item", ".news-card", ".list-a", ".list-mod", 
                ".feed-card", ".main-list", ".article-list", ".news-list",
                ".seo_data_list", ".news-2"
            ]
            
            for selector in selectors:
                items = soup.select(selector)
                for item in items:
                    links = item.select("a")
                    for link in links:
                        url = link.get('href', '').strip()
                        if not url:
                            continue
                            
                        # 处理相对URL
                        if url.startswith('/'):
                            base_domain = '/'.join(category_url.split('/')[:3])
                            url = base_domain + url
                        elif not url.startswith('http'):
                            continue
                            
                        if url not in urls:
                            urls.append(url)
                            if len(urls) >= limit:
                                break
                    if len(urls) >= limit:
                        break
                if len(urls) >= limit:
                    break
        
        # 如果我们有一些URL但不够limit，至少返回找到的
        if not urls:
            return self._get_backup_urls(category_url, limit)
            
        self.logger.info(f"找到 {len(urls)} 篇文章")
        return urls[:limit]  # 确保不超过限制
    
    def _get_backup_urls(self, category_url: str, limit: int) -> List[str]:
        """
        获取备用的文章URL列表，用于当无法从分类页面获取时
        
        Args:
            category_url: 分类页面URL
            limit: 最多获取多少篇文章
            
        Returns:
            List[str]: 文章URL列表
        """
        self.logger.warning(f"使用备用URL策略: {category_url}")
        urls = []
        
        # 根据分类URL选择不同的备用URL
        if "tech.sina" in category_url:
            urls = [
                "https://tech.sina.com.cn/d/i/2025-05-08/doc-izrtvhun9753989.shtml",
                "https://tech.sina.com.cn/d/i/2025-05-07/doc-izrsxqui0709981.shtml",
                "https://tech.sina.com.cn/d/i/2025-05-07/doc-izrtvhum8461064.shtml"
            ]
        elif "finance.sina" in category_url:
            urls = [
                "https://finance.sina.com.cn/china/gncj/2025-05-08/doc-izrtvcvr1702981.shtml",
                "https://finance.sina.com.cn/money/future/fmnews/2025-05-08/doc-izrsxqui0855540.shtml",
                "https://finance.sina.com.cn/jjxw/2025-05-07/doc-izrtvcvq8391957.shtml"
            ]
        elif "news.sina" in category_url:
            urls = [
                "https://news.sina.com.cn/c/2025-05-08/doc-izrtvhun9607348.shtml",
                "https://news.sina.com.cn/c/2025-05-08/doc-izrsxqui0918639.shtml",
                "https://news.sina.com.cn/w/2025-05-08/doc-izrtvcvr1710633.shtml"
            ]
        elif "sports.sina" in category_url:
            urls = [
                "https://sports.sina.com.cn/basketball/nba/2025-05-08/doc-izrtvhun9612345.shtml",
                "https://sports.sina.com.cn/football/2025-05-08/doc-izrsxqui0912345.shtml"
            ]
        elif "ent.sina" in category_url:
            urls = [
                "https://ent.sina.com.cn/s/m/2025-05-08/doc-izrtvhun9654321.shtml",
                "https://ent.sina.com.cn/v/m/2025-05-08/doc-izrsxqui0954321.shtml"
            ]
        
        return urls[:limit]
        
    def scrape_article(self, url: str, category: str) -> Optional[Article]:
        """
        爬取单篇文章内容
        
        Args:
            url: 文章URL
            category: 文章分类
            
        Returns:
            Optional[Article]: 文章对象，失败则返回None
        """
        self.logger.info(f"爬取文章: {url}")
        
        # 获取文章页面的HTML
        soup = get_soup(url, max_retries=MAX_RETRIES)
        if not soup:
            self.logger.error(f"无法获取文章页面: {url}")
            return None
            
        # 提取标题
        title = self.extractor.extract_title(soup)
        if not title:
            self.logger.warning(f"无法提取标题: {url}")
            return None
            
        # 提取内容
        content = self.extractor.extract_content(soup)
        if not content or len(content.strip()) < 50:  # 内容太短可能是提取失败
            self.logger.warning(f"无法提取内容或内容太短: {url}")
            return None
            
        # 提取发布时间
        published_time = self.extractor.extract_publish_time(soup)
        
        # 提取作者
        author = self.extractor.extract_author(soup)
        
        # 创建文章对象
        article = Article(
            title=title,
            url=url,
            content=content,
            source="新浪新闻",
            category=category,
            published_time=published_time,
            author=author,
            raw_html=str(soup) if soup else None
        )
        
        return article 