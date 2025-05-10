#!/usr/bin/env python
"""
新浪新闻提取器实现
"""

import re
from datetime import datetime
from typing import Optional

from bs4 import BeautifulSoup

from ..extractors.base_extractor import BaseExtractor


class SinaExtractor(BaseExtractor):
    """新浪新闻内容提取器"""
    
    def __init__(self):
        """初始化新浪提取器"""
        super().__init__(name="sina_extractor")
        
    def extract_title(self, soup: BeautifulSoup) -> str:
        """
        提取文章标题
        
        Args:
            soup: BeautifulSoup对象
            
        Returns:
            str: 文章标题
        """
        # 尝试多种可能的标题选择器
        selectors = [
            "h1.main-title",
            "h1.title",
            ".main-title",
            "h1.entry-title",
            "h1#artibodyTitle",
            ".article-header h1",
            ".title_wrapper h1",
            ".content h1",
            "h1.data-title",
            "#artibody h1",
            ".article h1",
            ".article-box h1",
            "h1"
        ]
        
        for selector in selectors:
            title_elems = soup.select(selector)
            if title_elems:
                for title_elem in title_elems:
                    title_text = title_elem.get_text().strip()
                    if title_text and len(title_text) > 5:  # 避免空或太短的标题
                        return title_text
                    
        # 回退到页面标题
        title = soup.title.get_text().strip() if soup.title else ""
        # 去掉网站名称后缀
        title = re.sub(r'[-_].*?(新浪|sina|网易|网|中国|栏目|专题).*?$', '', title, flags=re.IGNORECASE)
        return title
        
    def extract_content(self, soup: BeautifulSoup) -> str:
        """
        提取文章内容
        
        Args:
            soup: BeautifulSoup对象
            
        Returns:
            str: 文章内容
        """
        # 尝试多种可能的内容选择器
        selectors = [
            "#artibody",
            ".article-content",
            ".article-body",
            ".article",
            "#article_content",
            ".artical-content",
            ".content",
            ".main-content",
            ".article-box", 
            "#art_content",
            ".art_content",
            ".article_content",
            ".moduleParagraph",
            ".article-body-content"
        ]
        
        for selector in selectors:
            content_elems = soup.select(selector)
            for content_elem in content_elems:
                # 尝试查找段落
                paragraphs = content_elem.select("p")
                if paragraphs:
                    # 过滤掉太短的段落和可能是广告的段落
                    filtered_paragraphs = []
                    for p in paragraphs:
                        text = p.get_text().strip()
                        if text and len(text) > 3 and not re.search(r'(责编|编辑|记者|原标题|来源|标签|关键词|点此查看|var|function|document|if\s*\(|for\s*\()', text):
                            filtered_paragraphs.append(text)
                    
                    if filtered_paragraphs:
                        content = "\n\n".join(filtered_paragraphs)
                        return content
                
                # 如果没有段落标签或过滤后没有段落，尝试直接获取文本
                text = content_elem.get_text().strip()
                if text and len(text) > 100:  # 确保有足够长度
                    # 过滤掉网页中可能的噪音
                    text = re.sub(r'责任编辑.*?$', '', text)
                    text = re.sub(r'(\n\s*){3,}', '\n\n', text)  # 多个空行替换为两个换行
                    return text
                    
        # 最后尝试，直接获取页面主要文本
        main_text = ""
        for tag in soup.find_all(['p', 'div']):
            text = tag.get_text().strip()
            if len(text) > 100 and not re.search(r'(责编|编辑|记者|原标题|来源|标签|关键词|点此查看|var|function|document|if\s*\(|for\s*\()', text):
                main_text = text
                break
        
        return main_text
        
    def extract_publish_time(self, soup: BeautifulSoup) -> Optional[datetime]:
        """
        提取发布时间
        
        Args:
            soup: BeautifulSoup对象
            
        Returns:
            Optional[datetime]: 发布时间，如果无法提取则返回None
        """
        # 尝试多种可能的时间选择器
        selectors = [
            ".date",
            ".time-source",
            ".article-info .time",
            ".publish-time",
            ".entry-date",
            ".time",
            ".article-date",
            ".source-time",
            ".article-meta span",
            ".article_info .time",
            "time"
        ]
        
        # 首先尝试从meta标签提取
        meta_selectors = [
            'meta[property="article:published_time"]',
            'meta[name="publishdate"]',
            'meta[name="publish_date"]',
            'meta[name="date"]',
            'meta[itemprop="datePublished"]'
        ]
        
        for selector in meta_selectors:
            meta_time = soup.select_one(selector)
            if meta_time and meta_time.get('content'):
                try:
                    time_str = meta_time['content']
                    # 处理不同格式的时间字符串
                    if 'T' in time_str:
                        time_str = time_str.replace('Z', '+00:00')
                        return datetime.fromisoformat(time_str)
                    else:
                        # 尝试解析YYYY-MM-DD格式
                        return datetime.strptime(time_str, '%Y-%m-%d')
                except:
                    pass
        
        # 然后尝试从HTML元素提取
        for selector in selectors:
            time_elems = soup.select(selector)
            for time_elem in time_elems:
                time_text = time_elem.get_text().strip()
                # 尝试多种正则提取时间
                date_patterns = [
                    r'(\d{4})[-年](\d{1,2})[-月](\d{1,2})[日号\s]*?(\d{1,2}):(\d{1,2})',  # 2023年05月21日 12:34
                    r'(\d{4})[-年](\d{1,2})[-月](\d{1,2})[日号\s]*',  # 2023年05月21日
                    r'(\d{2})-(\d{2})\s+(\d{2}):(\d{2})',  # 05-21 12:34
                    r'(\d{4})/(\d{1,2})/(\d{1,2})\s*(\d{1,2}):(\d{1,2})'  # 2023/05/21 12:34
                ]
                
                for pattern in date_patterns:
                    date_match = re.search(pattern, time_text)
                    if date_match:
                        groups = date_match.groups()
                        try:
                            if len(groups) == 5:  # 完整日期时间
                                year, month, day, hour, minute = map(int, groups)
                                return datetime(year, month, day, hour, minute)
                            elif len(groups) == 3:  # 只有日期
                                year, month, day = map(int, groups)
                                return datetime(year, month, day)
                            elif len(groups) == 4 and len(groups[0]) == 2:  # MM-DD HH:MM
                                curr_year = datetime.now().year
                                month, day, hour, minute = map(int, groups)
                                return datetime(curr_year, month, day, hour, minute)
                        except ValueError:
                            continue
                
        # 如果无法提取时间，返回None
        return None
        
    def extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        """
        提取作者
        
        Args:
            soup: BeautifulSoup对象
            
        Returns:
            Optional[str]: 作者，如果无法提取则返回None
        """
        # 尝试多种可能的作者选择器
        selectors = [
            ".author",
            ".article-author",
            ".show_author",
            ".source",
            ".article-source",
            ".article_source",
            ".article-meta .source",
            ".name",
            ".editor"
        ]
        
        # 特殊的文本模式
        patterns = [
            r'来源[：:]\s*([^\s]+)',
            r'作者[：:]\s*([^\s]+)',
            r'编辑[：:]\s*([^\s]+)',
            r'记者[：:]\s*([^\s]+)',
            r'出品[：:]\s*([^\s]+)'
        ]
        
        # 尝试从元素中提取
        for selector in selectors:
            author_elems = soup.select(selector)
            for author_elem in author_elems:
                author_text = author_elem.get_text().strip()
                if author_text:
                    # 查找特定模式
                    for pattern in patterns:
                        match = re.search(pattern, author_text)
                        if match:
                            return match.group(1).strip()
                    # 如果元素内容很短，可能就是作者名
                    if len(author_text) < 20:
                        return author_text
        
        # 尝试从整篇文章的开始部分查找
        content_elems = soup.select("p")
        for p in content_elems[:3]:  # 只检查前3个段落
            text = p.get_text().strip()
            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    return match.group(1).strip()
                    
        return None 