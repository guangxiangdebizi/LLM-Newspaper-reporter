#!/usr/bin/env python
"""
新闻文章数据模型
"""

import hashlib
from datetime import datetime
from typing import Optional


class Article:
    """新闻文章数据模型"""
    
    def __init__(
        self, 
        title: str, 
        url: str, 
        content: str, 
        source: str,
        category: str,
        published_time: Optional[datetime] = None,
        author: Optional[str] = None,
        raw_html: Optional[str] = None
    ):
        self.title = title
        self.url = url
        self.content = content
        self.source = source
        self.category = category
        self.published_time = published_time or datetime.now()
        self.author = author
        self.raw_html = raw_html  # 存储原始HTML，方便未来调试和改进提取算法
        
    def get_id(self) -> str:
        """生成文章的唯一ID"""
        content_hash = hashlib.md5(self.content.encode()).hexdigest()
        return f"{self.source}_{content_hash[:10]}"
        
    def to_dict(self) -> dict:
        """将文章转换为字典"""
        return {
            "id": self.get_id(),
            "title": self.title,
            "url": self.url,
            "content": self.content,
            "source": self.source,
            "category": self.category,
            "published_time": self.published_time.isoformat() if self.published_time else None,
            "author": self.author
        } 