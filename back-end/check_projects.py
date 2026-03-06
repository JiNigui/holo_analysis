#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据库中的项目和用户信息
"""

from app import create_app
from app.models import db, Project, User
import os

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

with app.app_context():
    # 查询所有项目
    projects = Project.query.all()
    print('=== 数据库中的所有项目 ===')
    for project in projects:
        user = User.query.get(project.user_id)
        print(f'项目ID: {project.id}')
        print(f'项目名称: {project.project_name}')
        print(f'创建用户: {user.username if user else "未知用户"} (ID: {project.user_id})')
        print(f'创建时间: {project.created_time}')
        print(f'描述: {project.description}')
        print('---')
    
    # 查询所有用户
    print('\n=== 数据库中的所有用户 ===')
    users = User.query.all()
    for user in users:
        print(f'用户ID: {user.id}, 用户名: {user.username}, 角色: {user.role}')