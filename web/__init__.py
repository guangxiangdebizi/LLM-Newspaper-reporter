"""
Web应用初始化
"""

from flask import Flask
from flask_cors import CORS

def create_app():
    """创建Flask应用实例"""
    app = Flask(__name__, 
                static_folder="static",
                template_folder="templates")
    
    # 启用CORS
    CORS(app)
    
    # 配置密钥
    app.config["SECRET_KEY"] = "your_secret_key_here"
    
    # 注册蓝图
    from web.api.news_api import news_api
    from web.api.report_api import report_api
    from web.routes import main_routes
    
    app.register_blueprint(news_api, url_prefix="/api/news")
    app.register_blueprint(report_api, url_prefix="/api/reports")
    app.register_blueprint(main_routes)
    
    return app 