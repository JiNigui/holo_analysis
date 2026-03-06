#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试单点登录功能
验证账号同一时间只能在一个设备在线
"""

import requests
import json
import time

# 后端API基础URL
BASE_URL = "http://localhost:5000"

def test_single_sign_on():
    """测试单点登录功能"""
    print("=== 测试单点登录功能 ===")
    
    # 测试用户凭据
    username = "admin"
    password = "123456"
    
    # 第一次登录（设备1）
    print("\n1. 设备1登录...")
    token1 = login(username, password)
    if not token1:
        print("❌ 设备1登录失败")
        return
    
    print("✅ 设备1登录成功")
    
    # 检查设备1的会话状态
    print("\n2. 检查设备1会话状态...")
    session_valid1 = check_session(token1)
    if session_valid1:
        print("✅ 设备1会话有效")
    else:
        print("❌ 设备1会话无效")
    
    # 第二次登录（设备2）- 应该使设备1下线
    print("\n3. 设备2登录（应该使设备1下线）...")
    token2 = login(username, password)
    if not token2:
        print("❌ 设备2登录失败")
        return
    
    print("✅ 设备2登录成功")
    
    # 检查设备2的会话状态
    print("\n4. 检查设备2会话状态...")
    session_valid2 = check_session(token2)
    if session_valid2:
        print("✅ 设备2会话有效")
    else:
        print("❌ 设备2会话无效")
    
    # 检查设备1的会话状态（应该已失效）
    print("\n5. 检查设备1会话状态（应该已失效）...")
    session_valid1 = check_session(token1)
    if not session_valid1:
        print("✅ 设备1会话已失效（符合预期）")
    else:
        print("❌ 设备1会话仍然有效（不符合单点登录要求）")
    
    # 测试强制下线功能
    print("\n6. 测试强制下线功能...")
    force_logout_success = force_logout(token2)
    if force_logout_success:
        print("✅ 强制下线成功")
    else:
        print("❌ 强制下线失败")
    
    # 检查设备2的会话状态（应该已失效）
    print("\n7. 检查设备2会话状态（应该已失效）...")
    session_valid2 = check_session(token2)
    if not session_valid2:
        print("✅ 设备2会话已失效（符合预期）")
    else:
        print("❌ 设备2会话仍然有效（不符合强制下线要求）")
    
    print("\n=== 单点登录测试完成 ===")

def login(username, password):
    """用户登录"""
    try:
        response = requests.post(f"{BASE_URL}/api/user/login", json={
            "username": username,
            "password": password
        })
        
        if response.status_code == 200:
            data = response.json()
            return data.get('token')
        else:
            print(f"登录失败: {response.text}")
            return None
    except Exception as e:
        print(f"登录请求异常: {e}")
        return None

def check_session(token):
    """检查会话有效性"""
    try:
        headers = {
            'Authorization': f'Bearer {token}'
        }
        response = requests.get(f"{BASE_URL}/api/user/check-session", headers=headers)
        
        if response.status_code == 200:
            return True
        else:
            return False
    except Exception as e:
        print(f"检查会话异常: {e}")
        return False

def force_logout(token):
    """强制下线"""
    try:
        headers = {
            'Authorization': f'Bearer {token}'
        }
        response = requests.post(f"{BASE_URL}/api/user/force-logout", headers=headers)
        
        if response.status_code == 200:
            return True
        else:
            print(f"强制下线失败: {response.text}")
            return False
    except Exception as e:
        print(f"强制下线请求异常: {e}")
        return False

if __name__ == "__main__":
    test_single_sign_on()