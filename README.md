# 新闻爬取与分析工具

这个项目是一个架构化的新闻爬取与分析工具，可以从新浪新闻网站爬取文章，并使用DeepSeek模型生成分析报告。

## 功能特点

- 支持爬取新浪新闻不同分类的文章
- 智能提取文章标题、内容、发布时间和作者
- 使用DeepSeek大模型对文章进行深度分析
- 生成Markdown格式的分析报告
- 模块化设计，易于扩展和维护

## 目录结构

```
newspaper-mcp/
├── app/                       # 主应用包
│   ├── analyzers/             # 分析器模块
│   │   ├── base_analyzer.py   # 分析器基类
│   │   └── deepseek_analyzer.py # DeepSeek分析器实现
│   ├── config/                # 配置模块
│   │   └── settings.py        # 全局配置
│   ├── extractors/            # 提取器模块
│   │   ├── base_extractor.py  # 提取器基类
│   │   └── sina_extractor.py  # 新浪新闻提取器实现
│   ├── models/                # 数据模型
│   │   └── article.py         # 文章模型
│   ├── scrapers/              # 爬虫模块
│   │   ├── base_scraper.py    # 爬虫基类
│   │   └── sina_scraper.py    # 新浪新闻爬虫实现
│   └── utils/                 # 工具函数
│       ├── file.py            # 文件操作工具
│       ├── http.py            # HTTP请求工具
│       └── logger.py          # 日志工具
├── logs/                      # 日志目录
├── news_reports/              # 分析报告输出目录
├── main.py                    # 主入口文件
├── requirements.txt           # 依赖列表
└── README.md                  # 项目说明
```

## 安装与使用

### 环境要求

- Python 3.8+
- 依赖包: requests, beautifulsoup4, html5lib, lxml, openai

### 安装步骤

1. 克隆仓库或下载源码

```bash
git clone https://github.com/yourusername/newspaper-mcp.git
cd newspaper-mcp
```

2. 安装依赖

```bash
pip install -r requirements.txt
```

3. 设置DeepSeek API密钥

在Windows上:

```bash
set DEEPSEEK_API_KEY=your_key_here
```

在Linux或macOS上:

```bash
export DEEPSEEK_API_KEY=your_key_here
```

### 使用方法

运行主程序:

```bash
python main.py --category 财经 --limit 5 --preview
```

参数说明:

- `--category`: 要爬取的新闻分类，支持: 国际, 国内, 科技, 财经, 体育, 娱乐, 教育, 健康
- `--limit`: 爬取的文章数量
- `--preview`: 是否预览报告内容
- `--debug`: 启用调试模式

## 扩展指南

### 添加新的新闻源

1. 在`app/extractors`目录下创建新的提取器类
2. 在`app/scrapers`目录下创建新的爬虫类
3. 在`app/config/settings.py`中添加新闻源的配置

### 添加新的分析模型

1. 在`app/analyzers`目录下创建新的分析器类
2. 在`app/config/settings.py`中添加分析模型的配置

## 许可证

MIT

## 贡献

欢迎提交问题和贡献代码! 