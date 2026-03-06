#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据库中的用户信息
"""

import sys
import os

# 添加后端路径到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'back-end'))

from app import create_app
from app.models import db, User

def check_users():
    """检查数据库中的用户信息"""
    app = create_app()
    
    with app.app_context():
        # 获取所有用户
        users = User.query.all()
        
        print("=== 数据库中的用户信息 ===")
        for user in users:
            print(f"用户ID: {user.id}")
            print(f"用户名: {user.username}")
            print(f"密码哈希: {user.password}")
            print(f"角色: {user.role}")
            print(f"创建时间: {user.created_at}")
            
            # 测试密码验证
            test_password = "123456"
            is_valid = user.verify_password(test_password)
            print(f"密码'123456'验证结果: {is_valid}")
            
            print("-" * 50)

if __name__ == "__main__":
    check_users()