"""
Web路由定义
"""

from flask import Blueprint, render_template, redirect, url_for

main_routes = Blueprint("main", __name__)

@main_routes.route("/")
def index():
    """首页"""
    return render_template("index.html")

@main_routes.route("/scraper")
def scraper():
    """爬虫页面"""
    return render_template("scraper.html")

@main_routes.route("/reports")
def reports():
    """报告页面"""
    return render_template("reports.html") 