#!/usr/bin/env python
"""
新闻爬取与分析工具Web服务入口
"""

import os
import argparse
from dotenv import load_dotenv
from waitress import serve

# 加载环境变量
load_dotenv()

from web import create_app

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="新闻爬取与分析工具Web服务")
    parser.add_argument("--host", default="127.0.0.1", help="监听地址")
    parser.add_argument("--port", type=int, default=5000, help="监听端口")
    parser.add_argument("--debug", action="store_true", help="启用调试模式")
    
    return parser.parse_args()

def main():
    """主函数"""
    args = parse_args()
    app = create_app()
    
    if args.debug:
        # 开发模式
        app.run(host=args.host, port=args.port, debug=True)
    else:
        # 生产模式
        print(f"服务已启动在 http://{args.host}:{args.port}")
        serve(app, host=args.host, port=args.port)

if __name__ == "__main__":
    main() 