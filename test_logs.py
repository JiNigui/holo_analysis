#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试系统日志功能
"""

import requests
import json

# 后端API基础URL
BASE_URL = "http://127.0.0.1:5000"

def test_get_logs():
    """测试获取日志列表"""
    print("=== 测试获取日志列表 ===")
    try:
        response = requests.get(f"{BASE_URL}/api/logs/logs")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
            print("✅ 获取日志列表成功")
        else:
            print(f"❌ 获取日志列表失败: {response.text}")
    except Exception as e:
        print(f"❌ 请求异常: {e}")

def test_create_log():
    """测试创建日志记录"""
    print("\n=== 测试创建日志记录 ===")
    try:
        log_data = {
            "user_id": 1,
            "username": "test_user",
            "operation_type": "USER_LOGIN",
            "operation_name": "用户登录",
            "ip_address": "127.0.0.1",
            "status": "success",
            "details": "测试日志记录"
        }
        response = requests.post(f"{BASE_URL}/api/logs/logs", json=log_data)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
            print("✅ 创建日志记录成功")
        else:
            print(f"❌ 创建日志记录失败: {response.text}")
    except Exception as e:
        print(f"❌ 请求异常: {e}")

def test_user_login():
    """测试用户登录（会触发登录日志）"""
    print("\n=== 测试用户登录 ===")
    try:
        login_data = {
            "username": "testuser",
            "password": "123456"
        }
        response = requests.post(f"{BASE_URL}/api/user/login", json=login_data)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"登录成功: {json.dumps(data, ensure_ascii=False, indent=2)}")
            print("✅ 用户登录成功")
            return data.get('token')
        else:
            print(f"❌ 用户登录失败: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return None

def test_get_logs_with_token(token):
    """使用token测试获取日志列表"""
    print("=== 测试获取日志列表（使用token） ===")
    try:
        headers = {
            'Authorization': f'Bearer {token}'
        }
        response = requests.get(f"{BASE_URL}/api/logs/logs", headers=headers)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
            print("✅ 获取日志列表成功")
        else:
            print(f"❌ 获取日志列表失败: {response.text}")
    except Exception as e:
        print(f"❌ 请求异常: {e}")

def test_create_log_with_token(token):
    """测试创建日志记录（使用token）"""
    print("=== 测试创建日志记录（使用token） ===")
    
    # 准备日志数据
    log_data = {
        "operation_type": "用户登录",  # 操作类型即操作名称
        "status": "success",
        "project_id": None  # 登录操作不需要项目
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/logs/logs",
        json=log_data,
        headers=headers
    )
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ 创建日志记录成功")
        print(f"响应: {response.json()}")
        return True
    else:
        print(f"❌ 创建日志记录失败: {response.text}")
        return False

def main():
    """主测试函数"""
    print("开始测试系统日志功能...\n")
    
    # 测试用户登录（会触发登录日志）
    token = test_user_login()
    
    if token:
        # 使用token测试获取日志列表
        test_get_logs_with_token(token)
        
        # 使用token测试创建日志记录
        test_create_log_with_token(token)
        
        # 再次获取日志列表，查看是否有新日志
        print("\n=== 再次获取日志列表，查看新日志 ===")
        test_get_logs_with_token(token)
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    main()