#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手动添加会话字段到users表
"""

import sys
import os

# 添加当前路径到Python路径
sys.path.append(os.path.dirname(__file__))

from app import create_app
from app.models import db

def add_session_fields():
    """手动添加会话字段到users表"""
    app = create_app()
    
    with app.app_context():
        try:
            # 使用SQLAlchemy的DDL功能来执行ALTER TABLE语句
            from sqlalchemy import text
            
            # 检查字段是否已存在
            inspector = db.inspect(db.engine)
            columns = inspector.get_columns('users')
            existing_fields = {col['name'] for col in columns}
            
            # 需要添加的字段
            fields_to_add = ['current_session_id', 'session_created_at']
            
            # 执行ALTER TABLE语句添加缺失的字段
            for field in fields_to_add:
                if field not in existing_fields:
                    if field == 'current_session_id':
                        # 添加VARCHAR(100)字段，允许NULL
                        db.session.execute(text(f"ALTER TABLE users ADD COLUMN {field} VARCHAR(100) NULL"))
                        print(f"✅ 已添加字段: {field}")
                    elif field == 'session_created_at':
                        # 添加DATETIME字段，允许NULL
                        db.session.execute(text(f"ALTER TABLE users ADD COLUMN {field} DATETIME NULL"))
                        print(f"✅ 已添加字段: {field}")
                else:
                    print(f"ℹ️ 字段已存在: {field}")
            
            # 提交更改
            db.session.commit()
            print("✅ 所有字段已成功添加")
            
        except Exception as e:
            print(f"❌ 添加字段失败：{e}")
            db.session.rollback()
            return False
    
    return True

if __name__ == "__main__":
    add_session_fields()