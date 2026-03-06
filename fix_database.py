#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复数据库表结构 - 添加缺失的字段
"""

import sys
import os

# 添加后端路径到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'back-end'))

from app import create_app
from app.models import db

def fix_database():
    """修复数据库表结构"""
    app = create_app()
    
    with app.app_context():
        try:
            # 使用SQLAlchemy的ALTER TABLE语句添加缺失的字段
            from sqlalchemy import text
            
            # 检查是否已存在operation_name字段
            inspector = db.inspect(db.engine)
            columns = inspector.get_columns('operation_logs')
            column_names = [col['name'] for col in columns]
            
            if 'operation_name' not in column_names:
                # 添加operation_name字段
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE operation_logs ADD COLUMN operation_name VARCHAR(100) NOT NULL DEFAULT '未知操作'"))
                    conn.commit()
                print("✅ 已添加operation_name字段到operation_logs表")
            else:
                print("✅ operation_name字段已存在")
            
            # 再次检查表结构
            columns = inspector.get_columns('operation_logs')
            print("=== 修复后的operation_logs表结构 ===")
            for column in columns:
                print(f"字段名: {column['name']}, 类型: {column['type']}")
                
        except Exception as e:
            print(f"❌ 数据库修复失败: {e}")

if __name__ == "__main__":
    fix_database()