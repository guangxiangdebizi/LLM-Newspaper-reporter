#!/usr/bin/env python
"""
HTTP请求工具模块
"""

import random
import time
from typing import Dict, Any, Optional, Tuple

import requests
from bs4 import BeautifulSoup

from ..config.settings import USER_AGENTS, REQUEST_TIMEOUT, REQUEST_DELAY, RETRY_DELAY
from ..utils.logger import logger


def get_random_headers() -> Dict[str, str]:
    """
    获取随机的请求头
    
    Returns:
        Dict[str, str]: 请求头字典
    """
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


def make_request(
    url: str, 
    method: str = "GET", 
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    cookies: Optional[Dict[str, str]] = None,
    timeout: int = REQUEST_TIMEOUT,
    max_retries: int = 3,
    delay_range: Tuple[float, float] = REQUEST_DELAY,
    retry_delay_range: Tuple[float, float] = RETRY_DELAY,
    verify: bool = True
) -> Optional[requests.Response]:
    """
    发送HTTP请求，支持重试机制和随机延迟
    
    Args:
        url: 请求URL
        method: 请求方法 (GET, POST, PUT等)
        params: URL参数
        data: 请求体数据
        headers: 请求头
        cookies: Cookie
        timeout: 请求超时时间(秒)
        max_retries: 最大重试次数
        delay_range: 请求前的随机延迟时间范围(秒)
        retry_delay_range: 重试前的随机延迟时间范围(秒) 
        verify: 是否验证SSL证书
        
    Returns:
        requests.Response: 响应对象，如果所有重试都失败则返回None
    """
    if headers is None:
        headers = get_random_headers()
        
    # 随机延迟，避免频繁请求
    time.sleep(random.uniform(*delay_range))
    
    for attempt in range(max_retries):
        try:
            logger.debug(f"发送{method}请求到: {url} (尝试 {attempt+1}/{max_retries})")
            
            response = requests.request(
                method=method,
                url=url,
                params=params,
                data=data,
                headers=headers,
                cookies=cookies,
                timeout=timeout,
                verify=verify
            )
            
            # 处理常见状态码
            if response.status_code == 200:
                return response
            elif response.status_code == 403:
                logger.warning(f"请求被拒绝(403): {url}")
                # 更换头部信息重试
                headers = get_random_headers()
            elif response.status_code in (429, 503):
                logger.warning(f"请求频率过高或服务不可用({response.status_code}): {url}")
            elif response.status_code in (404, 410):
                logger.warning(f"页面不存在({response.status_code}): {url}")
                return None  # 不需要重试，资源不存在
            else:
                logger.warning(f"请求失败({response.status_code}): {url}")
                
            # 如果不是最后一次尝试，等待后重试
            if attempt < max_retries - 1:
                retry_delay = random.uniform(*retry_delay_range)
                logger.debug(f"等待{retry_delay:.2f}秒后重试...")
                time.sleep(retry_delay)
            
        except (requests.RequestException, Exception) as e:
            logger.error(f"请求出错: {url} - {str(e)}")
            
            # 如果不是最后一次尝试，等待后重试
            if attempt < max_retries - 1:
                retry_delay = random.uniform(*retry_delay_range)
                logger.debug(f"等待{retry_delay:.2f}秒后重试...")
                time.sleep(retry_delay)
            else:
                logger.error(f"在{max_retries}次尝试后失败")
                return None
                
    return None


def get_soup(
    url: str, 
    parser: str = "html5lib",
    **request_kwargs
) -> Optional[BeautifulSoup]:
    """
    获取URL的BeautifulSoup对象
    
    Args:
        url: 请求URL
        parser: BeautifulSoup解析器 ('html5lib', 'lxml', 'html.parser')
        **request_kwargs: 传递给make_request的参数
        
    Returns:
        BeautifulSoup: 解析后的BeautifulSoup对象，失败则返回None
    """
    response = make_request(url, **request_kwargs)
    if not response:
        return None
        
    # 尝试使用指定的解析器
    try:
        soup = BeautifulSoup(response.content, parser)
        return soup
    except Exception as e:
        logger.error(f"BeautifulSoup解析失败: {str(e)}")
        
        # 尝试备用解析器
        backup_parsers = ["lxml", "html.parser", "html5lib"]
        backup_parsers.remove(parser) if parser in backup_parsers else None
        
        for backup_parser in backup_parsers:
            try:
                logger.debug(f"尝试使用备用解析器: {backup_parser}")
                soup = BeautifulSoup(response.content, backup_parser)
                return soup
            except Exception as e2:
                logger.debug(f"{backup_parser}解析器失败: {str(e2)}")
                
        logger.error("所有解析器都失败")
        return None 