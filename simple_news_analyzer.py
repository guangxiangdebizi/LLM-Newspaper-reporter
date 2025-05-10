#!/usr/bin/env python
"""
简单的新闻爬取与分析工具
直接从新浪新闻爬取文章，然后使用DeepSeek模型生成分析报告
"""

import os
import re
import time
import random
import logging
import requests
import json
import hashlib
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import List, Dict, Optional
import argparse

# 尝试导入html5lib，如果不存在则给出提示
try:
    import html5lib
except ImportError:
    print("请安装html5lib: pip install html5lib")
    print("这个库能够更好地处理损坏的HTML")

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("news_analyzer")

# 全局配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "nonono")
OUTPUT_DIR = Path("./news_reports")
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

# 多个User-Agent轮换使用
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
]


class NewsArticle:
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
    ):
        self.title = title
        self.url = url
        self.content = content
        self.source = source
        self.category = category
        self.published_time = published_time or datetime.now()
        self.author = author
        
    def get_id(self) -> str:
        """生成文章的唯一ID"""
        content_hash = hashlib.md5(self.content.encode()).hexdigest()
        return f"{self.source}_{content_hash[:10]}"


def get_headers() -> Dict[str, str]:
    """获取随机的请求头"""
    user_agent = random.choice(USER_AGENTS)
    return {
        "User-Agent": user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Pragma": "no-cache",
        "DNT": "1"
    }


def get_sina_category_urls() -> Dict[str, str]:
    """获取新浪新闻各分类的URL"""
    categories = {
        "国际": "https://news.sina.com.cn/world/",
        "国内": "https://news.sina.com.cn/china/",
        "科技": "https://tech.sina.com.cn/",
        "财经": "https://finance.sina.com.cn/",
        "体育": "https://sports.sina.com.cn/", 
        "娱乐": "https://ent.sina.com.cn/",
        "教育": "https://edu.sina.com.cn/",
        "健康": "https://health.sina.com.cn/"
    }
    
    return categories


def get_article_urls(category_url: str, limit: int = 10, max_retries: int = 3) -> List[str]:
    """获取分类页面中的文章URL列表"""
    logger.info(f"获取文章URL: {category_url}")
    urls = []
    
    for attempt in range(max_retries):
        try:
            # 随机延迟，避免频繁请求
            time.sleep(random.uniform(2, 5))
            
            headers = get_headers()
            response = requests.get(category_url, headers=headers, timeout=30)
            
            # 请求状态检查
            if response.status_code == 403:
                logger.warning(f"请求被拒绝(403)，尝试重试 ({attempt+1}/{max_retries})")
                time.sleep(random.uniform(5, 10))  # 更长的等待时间
                continue
                
            response.raise_for_status()
            
            # 尝试使用html5lib解析器，对错误更宽容
            try:
                soup = BeautifulSoup(response.content, "html5lib")
            except:
                # 如果html5lib不可用，回退到lxml或html.parser
                try:
                    soup = BeautifulSoup(response.content, "lxml")
                except:
                    soup = BeautifulSoup(response.content, "html.parser")
            
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
            
            # 如果找到足够的链接就退出
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
            
            if urls:  # 如果找到了链接就退出重试循环
                break
                
        except Exception as e:
            logger.error(f"获取文章URL出错 (尝试 {attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(random.uniform(5, 10))  # 失败后等待更长时间
            else:
                logger.error(f"在{max_retries}次尝试后无法获取文章URL")
    
    # 如果我们有一些URL但不够limit，至少返回找到的
    logger.info(f"找到 {len(urls)} 篇文章")
    return urls[:limit]  # 确保不超过限制


def scrape_article(url: str, category: str, max_retries: int = 3) -> Optional[NewsArticle]:
    """爬取单篇文章内容"""
    logger.info(f"爬取文章: {url}")
    
    for attempt in range(max_retries):
        try:
            # 随机延迟，防止被封
            time.sleep(random.uniform(3, 6))
            
            headers = get_headers()
            response = requests.get(url, headers=headers, timeout=30)
            
            # 请求状态检查
            if response.status_code == 403:
                logger.warning(f"请求被拒绝(403)，尝试重试 ({attempt+1}/{max_retries})")
                time.sleep(random.uniform(5, 10))
                continue
                
            response.raise_for_status()
            
            # 尝试使用html5lib解析器，对错误更宽容
            try:
                soup = BeautifulSoup(response.content, "html5lib")
            except:
                # 如果html5lib不可用，回退到lxml或html.parser
                try:
                    soup = BeautifulSoup(response.content, "lxml")
                except:
                    soup = BeautifulSoup(response.content, "html.parser")
            
            # 提取标题
            title = extract_title(soup)
            if not title:
                logger.warning(f"无法提取标题: {url}")
                if attempt < max_retries - 1:
                    continue
                return None
                
            # 提取内容
            content = extract_content(soup)
            if not content or len(content.strip()) < 50:  # 内容太短可能是提取失败
                logger.warning(f"无法提取内容或内容太短: {url}")
                if attempt < max_retries - 1:
                    continue
                return None
                
            # 提取发布时间
            published_time = extract_publish_time(soup)
            
            # 提取作者
            author = extract_author(soup)
            
            article = NewsArticle(
                title=title,
                url=url,
                content=content,
                source="新浪新闻",
                category=category,
                published_time=published_time,
                author=author
            )
            
            return article
            
        except Exception as e:
            logger.error(f"爬取文章出错 (尝试 {attempt+1}/{max_retries}): {url} - {e}")
            if attempt < max_retries - 1:
                time.sleep(random.uniform(5, 10))
            else:
                logger.error(f"在{max_retries}次尝试后无法爬取文章")
                
    return None


def extract_title(soup: BeautifulSoup) -> str:
    """提取文章标题"""
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


def extract_content(soup: BeautifulSoup) -> str:
    """提取文章内容"""
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


def extract_publish_time(soup: BeautifulSoup) -> Optional[datetime]:
    """提取发布时间"""
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


def extract_author(soup: BeautifulSoup) -> Optional[str]:
    """提取作者"""
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


def scrape_category(category: str, url: str, limit: int = 10) -> List[NewsArticle]:
    """爬取某个分类下的所有文章"""
    articles = []
    logger.info(f"爬取分类 '{category}' - {url}")
    
    try:
        article_urls = get_article_urls(url, limit=limit)
        logger.info(f"在分类 '{category}' 中找到 {len(article_urls)} 篇文章")
        
        if not article_urls:
            logger.warning(f"未找到任何文章URL，尝试备用策略")
            # 备用策略：直接使用预定义的新浪新闻URL模式
            if "tech.sina" in url:
                article_urls = [
                    "https://tech.sina.com.cn/d/i/2025-05-08/doc-izrtvhun9753989.shtml",
                    "https://tech.sina.com.cn/d/i/2025-05-07/doc-izrsxqui0709981.shtml",
                    "https://tech.sina.com.cn/d/i/2025-05-07/doc-izrtvhum8461064.shtml"
                ][:limit]
            elif "finance.sina" in url:
                article_urls = [
                    "https://finance.sina.com.cn/china/gncj/2025-05-08/doc-izrtvcvr1702981.shtml",
                    "https://finance.sina.com.cn/money/future/fmnews/2025-05-08/doc-izrsxqui0855540.shtml",
                    "https://finance.sina.com.cn/jjxw/2025-05-07/doc-izrtvcvq8391957.shtml"
                ][:limit]
            elif "news.sina" in url:
                article_urls = [
                    "https://news.sina.com.cn/c/2025-05-08/doc-izrtvhun9607348.shtml",
                    "https://news.sina.com.cn/c/2025-05-08/doc-izrsxqui0918639.shtml",
                    "https://news.sina.com.cn/w/2025-05-08/doc-izrtvcvr1710633.shtml"
                ][:limit]
        
        for article_url in article_urls:
            try:
                article = scrape_article(article_url, category)
                if article:
                    articles.append(article)
                    logger.info(f"成功爬取文章: {article.title[:20]}...")
            except Exception as e:
                logger.error(f"爬取文章出错 {article_url}: {e}")
                
    except Exception as e:
        logger.error(f"爬取分类出错 '{category}': {e}")
        
    return articles


def analyze_with_deepseek(articles: List[NewsArticle]) -> Optional[str]:
    """使用DeepSeek API分析新闻文章"""
    if not articles:
        logger.warning("没有文章可以分析")
        return None
        
    if not DEEPSEEK_API_KEY:
        logger.error("DEEPSEEK_API_KEY未设置，请设置环境变量")
        return None
    
    # 准备文章内容
    article_text = prepare_article_content(articles)
    
    # 设置系统提示词
    system_prompt = """你是一位资深的新闻分析师，擅长对各类新闻进行深度解读和分析。你的任务是分析多篇新闻文章，提炼出关键信息，发现潜在趋势和规律，生成一份有价值的新闻分析报告。

你的分析报告需要具备以下特点：

1. **结构化与筛选性**：不是简单罗列事件，而是用专业眼光帮助读者理解"发生了什么、意味着什么、下一步可能会怎样"。

2. **战略视角与操作指引**：既要帮读者看清形势，也要提供思路和启发。对于新兴技术或事件，阐释其在产业链中的潜力、挑战和破局点。

3. **清晰呈现**：使用Markdown格式，保持结构清晰，分区引导阅读。可以包含：今日速览、深度精选、趋势洞察等板块。

4. **多维度分析**：从宏观经济、科技前沿、国际局势、产业动向、资本市场等多个维度进行分析。

5. **高信息密度**：确保读者能在5分钟内掌握关键信息，15分钟内获得可转化为认知价值的内容。

请以Markdown格式输出，注意段落组织，适当使用标题、列表、引用等格式元素增强可读性。不要简单复述原文内容，而是进行深度分析和洞察。"""

    # 准备用户提示词
    user_prompt = f"以下是多篇新闻文章，请对它们进行综合分析，生成一份详细的分析报告：\n\n{article_text}"
    
    # 调用DeepSeek API
    try:
        logger.info("调用DeepSeek API进行分析")
        import openai
        
        client = openai.OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com/v1"
        )
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=40960,
            temperature=0.7
        )
        
        analysis_content = response.choices[0].message.content
        
        if not analysis_content:
            logger.error("DeepSeek API返回空内容")
            return None
            
        logger.info("分析完成")
        return analysis_content
        
    except Exception as e:
        logger.error(f"调用DeepSeek API出错: {e}")
        return None


def prepare_article_content(articles: List[NewsArticle]) -> str:
    """准备文章内容，用于输入到模型"""
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


def save_report(content: str, category: str) -> Path:
    """保存分析报告"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{category}_分析报告_{timestamp}.md"
    filepath = OUTPUT_DIR / filename
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    return filepath


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="新闻爬取与分析工具")
    parser.add_argument("--category", default="财经", help="要爬取的新闻分类，例如：科技、财经、国际等")
    parser.add_argument("--limit", type=int, default=5, help="爬取的文章数量")
    args = parser.parse_args()
    
    # 检查API密钥
    if not DEEPSEEK_API_KEY:
        logger.error("请设置DEEPSEEK_API_KEY环境变量")
        logger.info("Windows: set DEEPSEEK_API_KEY=your_key_here")
        logger.info("Linux/Mac: export DEEPSEEK_API_KEY=your_key_here")
        return
    
    # 获取分类URL
    category_urls = get_sina_category_urls()
    if args.category not in category_urls:
        logger.error(f"不支持的分类: {args.category}")
        logger.info(f"支持的分类: {', '.join(category_urls.keys())}")
        return
    
    category_url = category_urls[args.category]
    
    # 爬取文章
    logger.info(f"开始爬取 {args.category} 分类的新闻，数量: {args.limit}")
    articles = scrape_category(args.category, category_url, limit=args.limit)
    
    if not articles:
        logger.error("未爬取到任何文章")
        return
    
    logger.info(f"成功爬取 {len(articles)} 篇文章")
    
    # 分析文章
    logger.info("开始分析文章...")
    analysis_result = analyze_with_deepseek(articles)
    
    if not analysis_result:
        logger.error("分析失败")
        return
    
    # 保存报告
    report_path = save_report(analysis_result, args.category)
    logger.info(f"分析报告已保存到: {report_path}")
    
    # 输出报告预览
    logger.info("\n=== 报告预览 ===\n")
    preview_lines = analysis_result.split("\n")[:10]
    print("\n".join(preview_lines))
    print("\n...(更多内容请查看完整报告)...\n")


if __name__ == "__main__":
    main() 
