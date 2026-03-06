#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建测试用户
"""

import sys
import os

# 添加后端路径到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'back-end'))

from app import create_app
from app.models import db, User

def create_test_user():
    """创建测试用户"""
    app = create_app()
    
    with app.app_context():
        # 检查是否已存在测试用户
        existing_user = User.query.filter_by(username='admin').first()
        if existing_user:
            print("测试用户已存在")
            print(f"用户名: {existing_user.username}")
            print(f"密码: 123456 (已加密)")
            return
        
        # 创建测试用户
        test_user = User(
            username='admin',
            password='123456',  # 密码会在保存时自动加密
            email='admin@example.com',
            role='admin'
        )
        
        db.session.add(test_user)
        db.session.commit()
        
        print("✅ 测试用户创建成功")
        print(f"用户名: admin")
        print(f"密码: 123456")
        print(f"邮箱: admin@example.com")
        print(f"角色: admin")

if __name__ == "__main__":
    create_test_user()