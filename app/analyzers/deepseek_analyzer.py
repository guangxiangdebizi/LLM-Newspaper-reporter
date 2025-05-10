#!/usr/bin/env python
"""
DeepSeek分析器实现
"""

from typing import List, Optional

import openai

from ..analyzers.base_analyzer import BaseAnalyzer
from ..config.settings import (
    DEEPSEEK_API_KEY, 
    DEEPSEEK_BASE_URL, 
    DEEPSEEK_MODEL, 
    DEEPSEEK_MAX_TOKENS, 
    DEEPSEEK_TEMPERATURE, 
    DEEPSEEK_SYSTEM_PROMPT
)
from ..models.article import Article


class DeepSeekAnalyzer(BaseAnalyzer):
    """DeepSeek新闻分析器"""
    
    def __init__(self):
        """初始化DeepSeek分析器"""
        super().__init__(name="deepseek_analyzer")
        self.client = None
        
        if DEEPSEEK_API_KEY:
            self.client = openai.OpenAI(
                api_key=DEEPSEEK_API_KEY,
                base_url=DEEPSEEK_BASE_URL
            )
        else:
            self.logger.error("DEEPSEEK_API_KEY未设置，请设置环境变量")
            
    def prepare_content(self, articles: List[Article]) -> str:
        """
        准备文章内容，用于输入到分析模型
        
        Args:
            articles: 文章对象列表
            
        Returns:
            str: 准备好的内容
        """
        contents = []
        
        for i, article in enumerate(articles, 1):
            content = f"## 文章{i}: {article.title}\n\n"
            
            if article.published_time:
                content += f"发布时间: {article.published_time.strftime('%Y-%m-%d %H:%M')}\n"
                
            if article.source:
                content += f"来源: {article.source}"
                if article.author:
                    content += f" - {article.author}"
                content += "\n"
                
            if article.category:
                content += f"分类: {article.category}\n"
                
            content += f"\n{article.content}\n\n"
            content += f"原文链接: {article.url}\n\n"
            content += "---\n\n"
            
            contents.append(content)
            
        return "".join(contents)
        
    def analyze(self, articles: List[Article]) -> Optional[str]:
        """
        使用DeepSeek API分析新闻文章
        
        Args:
            articles: 文章对象列表
            
        Returns:
            Optional[str]: 分析结果，失败则返回None
        """
        if not articles:
            self.logger.warning("没有文章可以分析")
            return None
            
        if not self.client:
            self.logger.error("DeepSeek客户端未初始化")
            return None
        
        # 准备文章内容
        article_text = self.prepare_content(articles)
        
        # 准备用户提示词
        user_prompt = f"以下是多篇新闻文章，请对它们进行综合分析，生成一份详细的分析报告：\n\n{article_text}"
        
        # 调用DeepSeek API
        try:
            self.logger.info("调用DeepSeek API进行分析")
            
            response = self.client.chat.completions.create(
                model=DEEPSEEK_MODEL,
                messages=[
                    {"role": "system", "content": DEEPSEEK_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=DEEPSEEK_MAX_TOKENS,
                temperature=DEEPSEEK_TEMPERATURE
            )
            
            analysis_content = response.choices[0].message.content
            
            if not analysis_content:
                self.logger.error("DeepSeek API返回空内容")
                return None
                
            self.logger.info("分析完成")
            return analysis_content
            
        except Exception as e:
            self.logger.error(f"调用DeepSeek API出错: {e}")
            return None 