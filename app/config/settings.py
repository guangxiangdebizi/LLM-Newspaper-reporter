#!/usr/bin/env python
"""
全局配置设置模块
"""

import os
from pathlib import Path
from typing import Dict, List

# API密钥配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "your api here")

# 输出目录配置
BASE_DIR = Path(__file__).parent.parent.parent
OUTPUT_DIR = BASE_DIR / "news_reports"
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

# 请求配置
REQUEST_TIMEOUT = 30  # 请求超时时间(秒)
MAX_RETRIES = 3  # 最大重试次数
REQUEST_DELAY = (2, 5)  # 请求延迟时间范围(秒)
RETRY_DELAY = (5, 10)  # 重试延迟时间范围(秒)

# User-Agent列表
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
]

# 新浪新闻分类URL配置
SINA_CATEGORIES: Dict[str, str] = {
    "国际": "https://news.sina.com.cn/world/",
    "国内": "https://news.sina.com.cn/china/",
    "科技": "https://tech.sina.com.cn/",
    "财经": "https://finance.sina.com.cn/",
    "体育": "https://sports.sina.com.cn/", 
    "娱乐": "https://ent.sina.com.cn/",
    "教育": "https://edu.sina.com.cn/",
    "健康": "https://health.sina.com.cn/"
}

# DeepSeek API配置
DEEPSEEK_MODEL = "deepseek-chat"
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
DEEPSEEK_MAX_TOKENS = 8000
DEEPSEEK_TEMPERATURE = 0.7

# DeepSeek系统提示词
DEEPSEEK_SYSTEM_PROMPT = """你是一位资深的新闻分析师，擅长对各类新闻进行深度解读和分析。你的任务是分析多篇新闻文章，提炼出关键信息，发现潜在趋势和规律，生成一份有价值的新闻分析报告。

你的分析报告需要具备以下特点：

1. **结构化与筛选性**：不是简单罗列事件，而是用专业眼光帮助读者理解"发生了什么、意味着什么、下一步可能会怎样"。

2. **战略视角与操作指引**：既要帮读者看清形势，也要提供思路和启发。对于新兴技术或事件，阐释其在产业链中的潜力、挑战和破局点。

3. **清晰呈现**：使用Markdown格式，保持结构清晰，分区引导阅读。可以包含：今日速览、深度精选、趋势洞察等板块。

4. **多维度分析**：从宏观经济、科技前沿、国际局势、产业动向、资本市场等多个维度进行分析。

5. **高信息密度**：确保读者能在5分钟内掌握关键信息，15分钟内获得可转化为认知价值的内容。

请以Markdown格式输出，注意段落组织，适当使用标题、列表、引用等格式元素增强可读性。不要简单复述原文内容，而是进行深度分析和洞察。
然后请你使用正确的引用格式，引用格式需要遵循apa引用格式"""
