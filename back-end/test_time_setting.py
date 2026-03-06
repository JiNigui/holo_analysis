#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试时间设置：验证项目创建时间是否使用本地时间
"""

import requests
import json
import datetime

BASE_URL = "http://127.0.0.1:5000"

def test_time_setting():
    """测试时间设置"""
    print("=== 测试时间设置 ===")
    
    # 1. 登录获取token
    print("1. 用户登录...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/user/login",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code != 200:
        print(f"❌ 登录失败: {response.text}")
        return
    
    # 获取token
    response_data = response.json()
    token = None
    
    # 检查不同的响应格式
    if 'token' in response_data:
        token = response_data['token']
    elif 'data' in response_data and 'token' in response_data['data']:
        token = response_data['data']['token']
    
    if not token:
        print("❌ 未获取到token")
        print(f"完整响应: {response_data}")
        return
    
    print("✅ 登录成功")
    
    # 2. 创建测试项目
    print("\n2. 创建测试项目...")
    project_data = {
        "project_name": "时间测试项目_" + str(datetime.datetime.now().timestamp()),
        "description": "用于测试时间设置的测试项目"
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/project/projects",
        json=project_data,
        headers=headers
    )
    
    if response.status_code not in [200, 201]:
        print(f"❌ 创建项目失败: {response.text}")
        return
    
    project_response = response.json()
    project_id = project_response.get('data', {}).get('id')
    
    if not project_id:
        print("❌ 未获取到项目ID")
        print(f"完整响应: {project_response}")
        return
    
    print("✅ 项目创建成功")
    print(f"项目ID: {project_id}")
    
    # 3. 获取项目详情
    print("\n3. 获取项目详情...")
    response = requests.get(
        f"{BASE_URL}/api/project/projects/{project_id}",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ 获取项目详情失败: {response.text}")
        return
    
    project_details = response.json()
    created_time_str = project_details.get('data', {}).get('created_time')
    
    if not created_time_str:
        print("❌ 未获取到创建时间")
        return
    
    # 4. 解析时间并比较
    print("\n4. 时间分析...")
    
    # 解析项目创建时间
    project_created_time = datetime.datetime.fromisoformat(created_time_str.replace('Z', '+00:00'))
    
    # 获取当前时间
    current_utc_time = datetime.datetime.utcnow()
    current_local_time = datetime.datetime.now()
    
    print(f"项目创建时间: {project_created_time}")
    print(f"当前UTC时间: {current_utc_time}")
    print(f"当前本地时间: {current_local_time}")
    
    # 计算时间差
    utc_time_diff = abs((project_created_time - current_utc_time).total_seconds())
    local_time_diff = abs((project_created_time - current_local_time).total_seconds())
    
    print(f"与UTC时间差: {utc_time_diff:.0f} 秒")
    print(f"与本地时间差: {local_time_diff:.0f} 秒")
    
    # 判断时间设置
    if local_time_diff < 60:  # 允许1分钟误差
        print("\n✅ 时间设置正确：项目创建时间使用本地时间")
    elif utc_time_diff < 60:
        print("\n❌ 时间设置错误：项目创建时间仍使用UTC时间")
    else:
        print("\n⚠️ 时间设置异常：时间差过大")
    
    # 5. 清理测试项目
    print("\n5. 清理测试项目...")
    response = requests.delete(
        f"{BASE_URL}/api/project/projects/{project_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        print("✅ 测试项目已清理")
    else:
        print(f"⚠️ 清理项目失败: {response.text}")

if __name__ == "__main__":
    test_time_setting()