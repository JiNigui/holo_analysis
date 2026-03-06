#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移脚本 - 更新operation_logs表结构以匹配SQL建表语句
"""

import sys
import os

# 添加后端路径到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'back-end'))

from app import create_app
from app.models import db

def migrate_database():
    """迁移数据库表结构"""
    app = create_app()
    
    with app.app_context():
        try:
            from sqlalchemy import text
            
            # 检查当前表结构
            inspector = db.inspect(db.engine)
            columns = inspector.get_columns('operation_logs')
            column_names = [col['name'] for col in columns]
            
            print("=== 当前表结构 ===")
            for column in columns:
                print(f"字段名: {column['name']}, 类型: {column['type']}")
            
            # 根据SQL建表语句更新表结构
            with db.engine.connect() as conn:
                # 如果存在operation_name字段，删除它（因为operation_type就是操作名称）
                if 'operation_name' in column_names:
                    conn.execute(text("ALTER TABLE operation_logs DROP COLUMN operation_name"))
                    print("✅ 已删除operation_name字段")
                
                # 如果存在operation_details字段，删除它
                if 'operation_details' in column_names:
                    conn.execute(text("ALTER TABLE operation_logs DROP COLUMN operation_details"))
                    print("✅ 已删除operation_details字段")
                
                # 如果存在ip_address字段，删除它
                if 'ip_address' in column_names:
                    conn.execute(text("ALTER TABLE operation_logs DROP COLUMN ip_address"))
                    print("✅ 已删除ip_address字段")
                
                # 如果存在created_at字段，重命名为operation_time
                if 'created_at' in column_names:
                    conn.execute(text("ALTER TABLE operation_logs CHANGE created_at operation_time DATETIME NOT NULL"))
                    print("✅ 已将created_at字段重命名为operation_time")
                
                # 如果operation_time字段不存在，创建它
                if 'operation_time' not in column_names:
                    conn.execute(text("ALTER TABLE operation_logs ADD COLUMN operation_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP"))
                    print("✅ 已添加operation_time字段")
                
                # 修改project_id字段为可为NULL
                conn.execute(text("ALTER TABLE operation_logs MODIFY project_id INT NULL"))
                print("✅ 已将project_id字段改为可为NULL")
                
                conn.commit()
            
            # 再次检查表结构
            columns = inspector.get_columns('operation_logs')
            print("\n=== 迁移后的表结构 ===")
            for column in columns:
                print(f"字段名: {column['name']}, 类型: {column['type']}, 可为空: {column.get('nullable', True)}")
            
            print("\n✅ 数据库迁移完成")
            
        except Exception as e:
            print(f"❌ 数据库迁移失败: {e}")

if __name__ == "__main__":
    migrate_database()