"""
新闻相关API
"""

import os
from flask import Blueprint, request, jsonify

from app.scrapers.sina_scraper import SinaScraper
from app.analyzers.deepseek_analyzer import DeepSeekAnalyzer
from app.utils.file import save_report
from app.config.settings import SINA_CATEGORIES

news_api = Blueprint("news_api", __name__)

@news_api.route("/categories", methods=["GET"])
def get_categories():
    """获取所有支持的新闻分类"""
    return jsonify({
        "success": True,
        "data": list(SINA_CATEGORIES.keys())
    })

@news_api.route("/scrape", methods=["POST"])
def scrape_news():
    """爬取新闻并分析"""
    data = request.json
    category = data.get("category", "财经")
    limit = data.get("limit", 5)
    
    # 参数验证
    if category not in SINA_CATEGORIES:
        return jsonify({
            "success": False,
            "message": f"不支持的分类: {category}"
        }), 400
    
    if not isinstance(limit, int) or limit < 1 or limit > 20:
        return jsonify({
            "success": False,
            "message": "limit参数必须是1-20之间的整数"
        }), 400
    
    try:
        # 创建爬虫
        scraper = SinaScraper()
        
        # 爬取文章
        articles = scraper.scrape_category(category, limit=limit)
        
        if not articles:
            return jsonify({
                "success": False,
                "message": "未爬取到任何文章"
            }), 404
        
        # 准备响应数据
        article_data = []
        for article in articles:
            article_data.append({
                "id": article.get_id(),
                "title": article.title,
                "url": article.url,
                "source": article.source,
                "category": article.category,
                "published_time": article.published_time.isoformat() if article.published_time else None,
                "author": article.author,
                "content_preview": article.content[:200] + "..." if len(article.content) > 200 else article.content
            })
        
        return jsonify({
            "success": True,
            "data": {
                "articles": article_data,
                "count": len(article_data)
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"爬取过程出错: {str(e)}"
        }), 500

@news_api.route("/analyze", methods=["POST"])
def analyze_news():
    """分析新闻"""
    data = request.json
    category = data.get("category", "财经")
    limit = data.get("limit", 5)
    
    try:
        # 创建爬虫
        scraper = SinaScraper()
        
        # 爬取文章
        articles = scraper.scrape_category(category, limit=limit)
        
        if not articles:
            return jsonify({
                "success": False,
                "message": "未爬取到任何文章"
            }), 404
        
        # 创建分析器
        analyzer = DeepSeekAnalyzer()
        
        # 分析文章
        result = analyzer.analyze(articles)
        
        if not result:
            return jsonify({
                "success": False,
                "message": "分析失败"
            }), 500
        
        # 保存报告
        report_path = save_report(result, category)
        
        return jsonify({
            "success": True,
            "data": {
                "report_content": result,
                "report_path": str(report_path),
                "article_count": len(articles)
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"分析过程出错: {str(e)}"
        }), 500 