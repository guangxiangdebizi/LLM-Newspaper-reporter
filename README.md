# 新闻爬取与分析工具

这个项目是一个架构化的新闻爬取与分析工具，可以从新浪新闻网站爬取文章，并使用DeepSeek模型生成分析报告。本工具可以帮助你快速获取新闻内容并生成专业的分析报告。

## 功能特点

- 支持爬取新浪新闻不同分类的文章（国际、国内、科技、财经、体育、娱乐、教育、健康）
- 智能提取文章标题、内容、发布时间和作者信息
- 使用DeepSeek大模型对文章进行深度分析和洞察
- 生成结构化的Markdown格式分析报告
- 模块化设计，易于扩展和维护
- 完善的错误处理和日志记录
- 支持自定义配置和参数调整
- **Web界面**：提供直观易用的网页界面

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
├── web/                       # Web应用目录
│   ├── api/                   # API定义
│   │   ├── news_api.py        # 新闻相关API
│   │   └── report_api.py      # 报告相关API
│   ├── static/                # 静态资源
│   │   ├── css/               # 样式文件
│   │   ├── js/                # JavaScript文件
│   │   └── img/               # 图片资源
│   ├── templates/             # HTML模板
│   │   ├── base.html          # 基础模板
│   │   ├── index.html         # 首页
│   │   ├── scraper.html       # 爬虫页面
│   │   └── reports.html       # 报告页面
│   ├── __init__.py            # Web应用初始化
│   └── routes.py              # 路由定义
├── logs/                      # 日志目录
├── news_reports/              # 分析报告输出目录
├── main.py                    # 命令行主入口文件
├── web_main.py                # Web服务入口文件
├── requirements.txt           # 核心依赖
├── web_requirements.txt       # Web应用依赖
└── README.md                  # 项目说明
```

## 安装与使用

### 环境要求

- Python 3.8 或更高版本
- 操作系统：Windows/Linux/macOS
- 网络连接：需要能够访问新浪新闻网站和DeepSeek API
- 依赖包：
  - 核心依赖：requests, beautifulsoup4, html5lib, lxml, openai
  - Web界面依赖：flask, flask-cors, waitress, python-dotenv

### 详细安装步骤

1. **克隆或下载项目**

   ```bash
   # 使用git克隆
   git clone https://github.com/yourusername/newspaper-mcp.git
   cd newspaper-mcp
   
   # 或者直接下载ZIP文件并解压
   ```

2. **创建并激活虚拟环境（推荐）**

   Windows:
   ```bash
   # 创建虚拟环境
   python -m venv venv
   
   # 激活虚拟环境
   .\venv\Scripts\activate
   ```

   Linux/macOS:
   ```bash
   # 创建虚拟环境
   python3 -m venv venv
   
   # 激活虚拟环境
   source venv/bin/activate
   ```

3. **安装依赖包**

   ```bash
   # 安装核心依赖
   pip install -r requirements.txt
   
   # 安装Web界面依赖（如需使用Web界面）
   pip install -r web_requirements.txt
   ```

4. **配置DeepSeek API密钥**

   方法1：设置环境变量

   Windows:
   ```bash
   # 临时设置（当前会话有效）
   set DEEPSEEK_API_KEY=your_key_here
   
   # 永久设置（需要管理员权限）
   setx DEEPSEEK_API_KEY "your_key_here"
   ```

   Linux/macOS:
   ```bash
   # 临时设置（当前会话有效）
   export DEEPSEEK_API_KEY=your_key_here
   
   # 永久设置（添加到~/.bashrc或~/.zshrc）
   echo 'export DEEPSEEK_API_KEY=your_key_here' >> ~/.bashrc
   source ~/.bashrc
   ```

   方法2：创建.env文件
   ```bash
   # 在项目根目录创建.env文件
   echo "DEEPSEEK_API_KEY=your_key_here" > .env
   ```

### 配置说明

1. **API配置**
   - 在`app/config/settings.py`中可以修改以下配置：
     ```python
     DEEPSEEK_API_KEY = "your_key_here"  # DeepSeek API密钥
     DEEPSEEK_MODEL = "deepseek-chat"    # 使用的模型名称
     DEEPSEEK_MAX_TOKENS = 8000          # 最大token数
     DEEPSEEK_TEMPERATURE = 0.7          # 温度参数
     ```

2. **爬虫配置**
   - 在`app/config/settings.py`中可以修改以下配置：
     ```python
     REQUEST_TIMEOUT = 30        # 请求超时时间(秒)
     MAX_RETRIES = 3            # 最大重试次数
     REQUEST_DELAY = (2, 5)     # 请求延迟时间范围(秒)
     RETRY_DELAY = (5, 10)      # 重试延迟时间范围(秒)
     ```

3. **输出配置**
   - 分析报告默认保存在`news_reports`目录
   - 日志文件默认保存在`logs`目录
   - 可以在`app/config/settings.py`中修改输出目录：
     ```python
     OUTPUT_DIR = Path("./news_reports")  # 修改为你的目标目录
     ```

## 使用方法

### 命令行模式

1. **基本使用**

   ```bash
   # 爬取财经新闻并生成分析报告
   python main.py --category 财经 --limit 5
   ```

2. **带预览的使用**

   ```bash
   # 爬取科技新闻，生成报告并预览内容
   python main.py --category 科技 --limit 3 --preview
   ```

3. **调试模式**

   ```bash
   # 启用调试模式，显示详细日志
   python main.py --category 国际 --limit 2 --debug
   ```

4. **参数说明**

   - `--category`: 新闻分类
     - 可选值：国际、国内、科技、财经、体育、娱乐、教育、健康
     - 默认值：财经
   
   - `--limit`: 爬取文章数量
     - 范围：1-20
     - 默认值：5
   
   - `--preview`: 预览报告
     - 不指定：仅保存报告
     - 指定：在控制台显示报告预览
   
   - `--debug`: 调试模式
     - 不指定：仅显示重要信息
     - 指定：显示详细日志

### Web界面模式

1. **启动Web服务**

   ```bash
   # 开发模式
   python web_main.py --debug
   
   # 生产模式
   python web_main.py
   ```

2. **访问Web界面**
   
   在浏览器中打开: http://127.0.0.1:5000

3. **使用Web界面**

   - **首页**: 概述和快速入口
   - **爬虫页面**: 爬取文章和生成分析报告
   - **报告页面**: 查看和搜索已生成的报告

4. **参数说明**

   - `--host`: 监听地址
     - 默认值：127.0.0.1
     - 使用 0.0.0.0 可以从外部访问
   
   - `--port`: 监听端口
     - 默认值：5000
   
   - `--debug`: 调试模式
     - 不指定：生产模式
     - 指定：开发模式，自动重载

### 输出示例

1. **分析报告格式**
   ```markdown
   # 财经新闻分析报告
   
   ## 今日速览
   - 要点1
   - 要点2
   
   ## 深度分析
   详细分析内容...
   
   ## 趋势洞察
   趋势分析内容...
   ```

2. **日志输出**
   ```
   2024-03-10 10:30:15 - INFO - 开始爬取财经新闻
   2024-03-10 10:30:20 - INFO - 成功爬取5篇文章
   2024-03-10 10:30:25 - INFO - 开始分析文章
   2024-03-10 10:30:35 - INFO - 分析完成
   2024-03-10 10:30:36 - INFO - 报告已保存到: news_reports/财经_分析报告_20240310_103036.md
   ```

## 常见问题

1. **API密钥问题**
   - 确保正确设置了DEEPSEEK_API_KEY环境变量
   - 检查API密钥是否有效
   - 确认网络连接是否正常

2. **爬取失败**
   - 检查网络连接
   - 确认目标网站是否可访问
   - 查看日志文件了解详细错误信息

3. **分析失败**
   - 检查API密钥和配置
   - 确认文章内容是否完整
   - 查看日志了解具体错误

4. **Web界面问题**
   - 确保已安装所有Web依赖 (`pip install -r web_requirements.txt`)
   - 检查端口是否被占用，如被占用请使用 `--port` 参数更改端口
   - 查看控制台输出的错误信息

## Web界面配置

1. **外部访问**
   
   默认情况下，Web服务只能从本机访问。要允许从其他设备访问：
   
   ```bash
   python web_main.py --host 0.0.0.0
   ```

2. **更改端口**
   
   如果默认端口5000被占用：
   
   ```bash
   python web_main.py --port 8080
   ```

3. **前端样式定制**
   
   如需自定义样式，编辑 `web/static/css/style.css` 文件。

4. **网页模板修改**
   
   页面模板位于 `web/templates/` 目录，可以根据需要修改。

## 扩展指南

### 添加新的新闻源

1. 在`app/extractors`目录下创建新的提取器类：
   ```python
   from .base_extractor import BaseExtractor
   
   class NewSourceExtractor(BaseExtractor):
       def extract_title(self, soup):
           # 实现标题提取逻辑
           pass
       
       def extract_content(self, soup):
           # 实现内容提取逻辑
           pass
   ```

2. 在`app/scrapers`目录下创建新的爬虫类：
   ```python
   from .base_scraper import BaseScraper
   
   class NewSourceScraper(BaseScraper):
       def get_categories(self):
           # 实现分类获取逻辑
           pass
       
       def get_article_urls(self, category_url, limit):
           # 实现文章URL获取逻辑
           pass
   ```

3. 在`app/config/settings.py`中添加配置：
   ```python
   NEW_SOURCE_CATEGORIES = {
       "分类1": "URL1",
       "分类2": "URL2"
   }
   ```

4. 在Web界面中集成新的新闻源（如需要）：
   - 修改 `web/api/news_api.py` 添加对新新闻源的支持
   - 更新前端界面以显示新的选项

### 添加新的分析模型

1. 在`app/analyzers`目录下创建新的分析器类：
   ```python
   from .base_analyzer import BaseAnalyzer
   
   class NewModelAnalyzer(BaseAnalyzer):
       def prepare_content(self, articles):
           # 实现内容准备逻辑
           pass
       
       def analyze(self, articles):
           # 实现分析逻辑
           pass
   ```

2. 在`app/config/settings.py`中添加模型配置：
   ```python
   NEW_MODEL_API_KEY = "your_key_here"
   NEW_MODEL_CONFIG = {
       "model": "model_name",
       "max_tokens": 8000,
       "temperature": 0.7
   }
   ```

3. 在Web界面中集成新的分析模型（如需要）：
   - 修改 `web/api/news_api.py` 添加对新分析模型的支持
   - 更新前端界面以允许选择分析模型

## 许可证

MIT

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 联系方式

- 项目维护者：[Your Name]
- 邮箱：[your.email@example.com]
- 项目地址：[https://github.com/yourusername/newspaper-mcp]

欢迎提交问题和贡献代码！ 