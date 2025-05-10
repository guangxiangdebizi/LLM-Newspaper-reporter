#!/usr/bin/env python
"""
新闻爬取与分析工具主入口
"""

import argparse
import sys
import os
from typing import Optional, List

from app.models.article import Article
from app.scrapers.sina_scraper import SinaScraper
from app.analyzers.deepseek_analyzer import DeepSeekAnalyzer
from app.utils.logger import logger
from app.utils.file import save_report
from app.config.settings import DEEPSEEK_API_KEY, SINA_CATEGORIES


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="新闻爬取与分析工具")
    parser.add_argument(
        "--category", 
        default="财经", 
        help=f"要爬取的新闻分类，支持: {', '.join(SINA_CATEGORIES.keys())}"
    )
    parser.add_argument(
        "--limit", 
        type=int, 
        default=5, 
        help="爬取的文章数量"
    )
    parser.add_argument(
        "--preview", 
        action="store_true", 
        help="是否预览报告内容"
    )
    parser.add_argument(
        "--debug", 
        action="store_true", 
        help="启用调试模式"
    )
    
    return parser.parse_args()


def check_environment() -> bool:
    """
    检查运行环境是否满足要求
    
    Returns:
        bool: 环境是否满足要求
    """
    # 检查API密钥
    if not DEEPSEEK_API_KEY:
        logger.error("请设置DEEPSEEK_API_KEY环境变量")
        logger.info("Windows: set DEEPSEEK_API_KEY=your_key_here")
        logger.info("Linux/Mac: export DEEPSEEK_API_KEY=your_key_here")
        return False
        
    # 检查必要的Python包
    try:
        import openai
        import requests
        import bs4
    except ImportError as e:
        logger.error(f"缺少必要的Python包: {e}")
        logger.info("请安装必要的依赖: pip install -r requirements.txt")
        return False
        
    return True


def crawl_news(category: str, limit: int) -> List[Article]:
    """
    爬取指定分类的新闻
    
    Args:
        category: 新闻分类
        limit: 爬取数量
        
    Returns:
        List[Article]: 文章列表
    """
    logger.info(f"开始爬取 {category} 分类的新闻，数量: {limit}")
    
    # 创建爬虫
    scraper = SinaScraper()
    
    # 爬取文章
    articles = scraper.scrape_category(category, limit=limit)
    
    if not articles:
        logger.error("未爬取到任何文章")
        return []
    
    logger.info(f"成功爬取 {len(articles)} 篇文章")
    return articles


def analyze_news(articles: List[Article]) -> Optional[str]:
    """
    分析新闻文章
    
    Args:
        articles: 文章列表
        
    Returns:
        Optional[str]: 分析结果，失败则返回None
    """
    if not articles:
        logger.error("没有文章可以分析")
        return None
        
    logger.info("开始分析文章...")
    
    # 创建分析器
    analyzer = DeepSeekAnalyzer()
    
    # 分析文章
    result = analyzer.analyze(articles)
    
    if not result:
        logger.error("分析失败")
        return None
        
    logger.info("分析完成")
    return result


def preview_report(content: str, max_lines: int = 10):
    """
    预览报告内容
    
    Args:
        content: 报告内容
        max_lines: 最多显示的行数
    """
    logger.info("\n=== 报告预览 ===\n")
    preview_lines = content.split("\n")[:max_lines]
    print("\n".join(preview_lines))
    print("\n...(更多内容请查看完整报告)...\n")


def main():
    """主函数"""
    # 解析命令行参数
    args = parse_args()
    
    # 检查环境
    if not check_environment():
        return 1
    
    # 爬取新闻
    articles = crawl_news(args.category, args.limit)
    if not articles:
        return 1
    
    # 分析新闻
    analysis_result = analyze_news(articles)
    if not analysis_result:
        return 1
    
    # 保存报告
    report_path = save_report(analysis_result, args.category)
    logger.info(f"分析报告已保存到: {report_path}")
    
    # 预览报告
    if args.preview:
        preview_report(analysis_result)
        
    return 0


if __name__ == "__main__":
    sys.exit(main()) 