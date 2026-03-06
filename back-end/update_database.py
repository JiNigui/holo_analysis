#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新数据库表结构
"""

import sys
import os

# 添加当前路径到Python路径
sys.path.append(os.path.dirname(__file__))

from app import create_app
from app.models import db

def update_database():
    """更新数据库表结构"""
    app = create_app()
    
    with app.app_context():
        try:
            # 创建所有表（如果不存在）
            db.create_all()
            print("✅ 数据库表结构已成功更新")
            print("✅ 新增字段：current_session_id, session_created_at")
        except Exception as e:
            print(f"❌ 更新数据库表结构失败：{e}")
            return False
    
    return True

if __name__ == "__main__":
    update_database()