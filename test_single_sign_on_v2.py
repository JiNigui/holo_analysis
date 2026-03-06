#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试改进后的单点登录功能
验证账号同一时间只能在一个设备在线，新登录会被阻止
"""

import requests
import json
import time

# 后端API基础URL
BASE_URL = "http://localhost:5000"

def test_single_sign_on_v2():
    """测试改进后的单点登录功能"""
    print("=== 测试改进后的单点登录功能 ===")
    
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
    
    # 第二次登录（设备2）- 应该被阻止
    print("\n3. 设备2尝试登录（应该被阻止）...")
    token2 = login(username, password)
    if token2:
        print("❌ 设备2登录成功（不符合预期，应该被阻止）")
    else:
        print("✅ 设备2登录被阻止（符合预期）")
    
    # 检查设备1的会话状态（应该仍然有效）
    print("\n4. 检查设备1会话状态（应该仍然有效）...")
    session_valid1 = check_session(token1)
    if session_valid1:
        print("✅ 设备1会话仍然有效（符合预期）")
    else:
        print("❌ 设备1会话已失效（不符合预期）")
    
    # 设备1正常登出
    print("\n5. 设备1正常登出...")
    logout_success = logout(token1)
    if logout_success:
        print("✅ 设备1登出成功")
    else:
        print("❌ 设备1登出失败")
    
    # 设备2再次尝试登录（应该成功）
    print("\n6. 设备2再次尝试登录（应该成功）...")
    token2 = login(username, password)
    if token2:
        print("✅ 设备2登录成功（符合预期）")
    else:
        print("❌ 设备2登录失败（不符合预期）")
    
    # 检查设备2的会话状态
    print("\n7. 检查设备2会话状态...")
    session_valid2 = check_session(token2)
    if session_valid2:
        print("✅ 设备2会话有效")
    else:
        print("❌ 设备2会话无效")
    
    print("\n=== 改进后的单点登录测试完成 ===")

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
        elif response.status_code == 409:
            # 单点登录冲突
            data = response.json()
            print(f"登录被阻止: {data.get('message')}")
            return None
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

def logout(token):
    """用户登出"""
    try:
        headers = {
            'Authorization': f'Bearer {token}'
        }
        response = requests.post(f"{BASE_URL}/api/user/logout", headers=headers)
        
        if response.status_code == 200:
            return True
        else:
            print(f"登出失败: {response.text}")
            return False
    except Exception as e:
        print(f"登出请求异常: {e}")
        return False

if __name__ == "__main__":
    test_single_sign_on_v2()