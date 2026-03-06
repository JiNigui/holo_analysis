#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新数据库表结构
"""

import sys
import os

# 添加后端路径到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'back-end'))

from app import create_app
from app.models import db

def update_database():
    """更新数据库表结构"""
    app = create_app()
    
    with app.app_context():
        try:
            # 创建所有表（如果不存在）
            db.create_all()
            print("✅ 数据库表结构已更新")
            
            # 检查OperationLog表是否存在
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'operation_logs' in tables:
                print("✅ operation_logs表存在")
                
                # 检查表结构
                columns = inspector.get_columns('operation_logs')
                print("=== operation_logs表结构 ===")
                for column in columns:
                    print(f"字段名: {column['name']}, 类型: {column['type']}")
            else:
                print("❌ operation_logs表不存在")
                
        except Exception as e:
            print(f"❌ 数据库更新失败: {e}")

if __name__ == "__main__":
    update_database()