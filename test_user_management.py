#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试用户管理API功能
"""

import requests
import json

# 后端API基础URL
BASE_URL = "http://127.0.0.1:5000"

def login_admin():
    """管理员登录"""
    print("=== 管理员登录 ===")
    try:
        response = requests.post(f"{BASE_URL}/api/user/login", json={
            "username": "admin",
            "password": "admin111"
        })
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            print(f"✅ 管理员登录成功")
            print(f"Token: {token[:50]}...")
            return token
        else:
            print(f"❌ 管理员登录失败: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 登录请求异常: {e}")
        return None

def test_get_all_users(token):
    """测试获取所有用户列表"""
    print("\n=== 测试获取所有用户列表 ===")
    try:
        headers = {
            'Authorization': f'Bearer {token}'
        }
        response = requests.get(f"{BASE_URL}/api/user/users", headers=headers)
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 获取用户列表成功")
            print(f"用户数量: {len(data.get('data', []))}")
            print(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
            return True
        elif response.status_code == 403:
            print(f"❌ 权限不足: {response.text}")
            return False
        else:
            print(f"❌ 获取用户列表失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_get_user_profile(token):
    """测试获取当前用户信息"""
    print("\n=== 测试获取当前用户信息 ===")
    try:
        headers = {
            'Authorization': f'Bearer {token}'
        }
        response = requests.get(f"{BASE_URL}/api/user/profile", headers=headers)
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 获取用户信息成功")
            print(f"用户名: {data.get('data', {}).get('username')}")
            print(f"角色: {data.get('data', {}).get('role')}")
            return True
        else:
            print(f"❌ 获取用户信息失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("用户管理API功能测试")
    print("=" * 60)
    
    # 管理员登录
    token = login_admin()
    if not token:
        print("❌ 管理员登录失败，无法继续测试")
        return
    
    # 测试获取用户信息
    profile_success = test_get_user_profile(token)
    
    # 测试获取所有用户列表
    users_success = test_get_all_users(token)
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总:")
    print(f"   管理员登录: {'✅ 成功' if token else '❌ 失败'}")
    print(f"   获取用户信息: {'✅ 成功' if profile_success else '❌ 失败'}")
    print(f"   获取所有用户列表: {'✅ 成功' if users_success else '❌ 失败'}")
    
    if token and profile_success and users_success:
        print("🎉 所有用户管理API测试通过！")
    else:
        print("⚠️ 部分测试失败，请检查相关功能")

if __name__ == "__main__":
    main()