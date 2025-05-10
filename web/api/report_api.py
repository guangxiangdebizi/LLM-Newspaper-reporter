"""
报告相关API
"""

import os
from pathlib import Path
from flask import Blueprint, jsonify, request

from app.config.settings import OUTPUT_DIR

report_api = Blueprint("report_api", __name__)

@report_api.route("/list", methods=["GET"])
def list_reports():
    """获取所有报告列表"""
    try:
        reports = []
        
        # 确保目录存在
        OUTPUT_DIR.mkdir(exist_ok=True, parents=True)
        
        # 查找所有MD文件
        for file in OUTPUT_DIR.glob("*.md"):
            if file.is_file():
                # 解析文件名获取元数据
                filename = file.name
                # 假设文件名格式为: 分类_分析报告_日期_时间.md
                parts = filename.split("_")
                
                if len(parts) >= 4:
                    category = parts[0]
                    date_str = parts[2]
                    time_str = parts[3].replace(".md", "")
                    
                    reports.append({
                        "id": filename,
                        "path": str(file),
                        "category": category,
                        "date": date_str,
                        "time": time_str,
                        "size": file.stat().st_size,
                        "created": file.stat().st_ctime
                    })
        
        # 按创建时间排序，最新的在前
        reports.sort(key=lambda x: x["created"], reverse=True)
        
        return jsonify({
            "success": True,
            "data": reports
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"获取报告列表出错: {str(e)}"
        }), 500

@report_api.route("/<report_id>", methods=["GET"])
def get_report(report_id):
    """获取特定报告内容"""
    try:
        report_path = OUTPUT_DIR / report_id
        
        if not report_path.exists() or not report_path.is_file():
            return jsonify({
                "success": False,
                "message": "报告不存在"
            }), 404
        
        # 读取报告内容
        with open(report_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        return jsonify({
            "success": True,
            "data": {
                "id": report_id,
                "content": content
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"获取报告内容出错: {str(e)}"
        }), 500 