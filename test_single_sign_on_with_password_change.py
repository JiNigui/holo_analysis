#!/usr/bin/env python3
"""
测试单点登录与密码修改的兼容性
验证：
1. 设备1登录后，设备2无法登录（单点登录生效）
2. 设备1修改密码后，设备1保持登录状态
3. 设备1修改密码后，设备2仍然无法登录（会话仍然有效）
4. 设备1登出后，设备2可以登录
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000/api"

def login(username, password):
    """登录函数"""
    url = f"{BASE_URL}/login"
    data = {
        "username": username,
        "password": password
    }
    
    response = requests.post(url, json=data)
    return response

def check_session(token):
    """检查会话状态"""
    url = f"{BASE_URL}/check-session"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(url, headers=headers)
    return response

def logout(token):
    """登出函数"""
    url = f"{BASE_URL}/logout"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.post(url, headers=headers)
    return response

def update_profile(token, old_password, new_password):
    """修改个人信息（包括密码）"""
    url = f"{BASE_URL}/profile"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "old_password": old_password,
        "new_password": new_password
    }
    
    response = requests.put(url, headers=headers, json=data)
    return response

def test_single_sign_on_with_password_change():
    """测试单点登录与密码修改的兼容性"""
    
    # 测试账号
    test_username = "testuser"
    original_password = "test123"
    new_password = "newtest456"
    
    print("=== 测试单点登录与密码修改兼容性 ===")
    
    # 1. 设备1登录
    print("\n1. 设备1登录...")
    device1_login = login(test_username, original_password)
    if device1_login.status_code == 200:
        device1_token = device1_login.json()['token']
        print(f"   设备1登录成功，token: {device1_token[:20]}...")
    else:
        print(f"   设备1登录失败: {device1_login.status_code} - {device1_login.text}")
        return
    
    # 2. 设备2尝试登录（应该被阻止）
    print("\n2. 设备2尝试登录...")
    device2_login = login(test_username, original_password)
    if device2_login.status_code == 409:
        print("   ✓ 设备2登录被阻止（单点登录生效）")
    else:
        print(f"   ✗ 设备2登录异常: {device2_login.status_code} - {device2_login.text}")
    
    # 3. 检查设备1会话状态
    print("\n3. 检查设备1会话状态...")
    device1_session = check_session(device1_token)
    if device1_session.status_code == 200:
        print("   ✓ 设备1会话有效")
    else:
        print(f"   ✗ 设备1会话异常: {device1_session.status_code} - {device1_session.text}")
    
    # 4. 设备1修改密码
    print("\n4. 设备1修改密码...")
    update_result = update_profile(device1_token, original_password, new_password)
    if update_result.status_code == 200:
        print("   ✓ 设备1密码修改成功")
    else:
        print(f"   ✗ 设备1密码修改失败: {update_result.status_code} - {update_result.text}")
    
    # 5. 检查设备1会话是否仍然有效
    print("\n5. 检查设备1会话是否仍然有效...")
    device1_session_after = check_session(device1_token)
    if device1_session_after.status_code == 200:
        print("   ✓ 设备1会话仍然有效（修改密码后保持登录）")
    else:
        print(f"   ✗ 设备1会话失效: {device1_session_after.status_code} - {device1_session_after.text}")
    
    # 6. 设备2再次尝试登录（应该仍然被阻止）
    print("\n6. 设备2再次尝试登录...")
    device2_login_again = login(test_username, new_password)  # 使用新密码
    if device2_login_again.status_code == 409:
        print("   ✓ 设备2登录仍然被阻止（会话仍然有效）")
    else:
        print(f"   ✗ 设备2登录异常: {device2_login_again.status_code} - {device2_login_again.text}")
    
    # 7. 设备1登出
    print("\n7. 设备1登出...")
    logout_result = logout(device1_token)
    if logout_result.status_code == 200:
        print("   ✓ 设备1登出成功")
    else:
        print(f"   ✗ 设备1登出失败: {logout_result.status_code} - {logout_result.text}")
    
    # 8. 设备2尝试登录（现在应该可以登录）
    print("\n8. 设备2尝试登录...")
    device2_final_login = login(test_username, new_password)
    if device2_final_login.status_code == 200:
        device2_token = device2_final_login.json()['token']
        print(f"   ✓ 设备2登录成功，token: {device2_token[:20]}...")
    else:
        print(f"   ✗ 设备2登录失败: {device2_final_login.status_code} - {device2_final_login.text}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_single_sign_on_with_password_change()