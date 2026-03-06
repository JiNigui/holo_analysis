#!/usr/bin/env python3
"""
测试前端认证和项目数据加载问题
"""

import requests
import json
import jwt
import datetime

def test_authentication():
    """测试认证功能"""
    print("=== 测试认证功能 ===")
    
    # 生成一个有效的JWT token
    payload = {
        'user_id': 2,
        'username': 'user',
        'role': 'user',
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    
    token = jwt.encode(payload, 'hard-to-guess-string', algorithm='HS256')
    print(f"生成的JWT token: {token}")
    
    # 测试项目详情API
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # 假设项目ID为1
    project_id = 1
    url = f"http://127.0.0.1:5000/api/project/projects/{project_id}"
    
    try:
        response = requests.get(url, headers=headers)
        print(f"项目详情API响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"项目数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            # 检查数据结构
            if 'data' in data:
                project_data = data['data']
                print(f"项目名称字段: {project_data.get('project_name', '未找到project_name字段')}")
                print(f"创建时间字段: {project_data.get('created_time', '未找到created_time字段')}")
                print(f"其他字段: {list(project_data.keys())}")
        else:
            print(f"错误响应: {response.text}")
            
    except Exception as e:
        print(f"请求失败: {e}")

def test_upload_api():
    """测试上传API"""
    print("\n=== 测试上传API ===")
    
    # 生成一个有效的JWT token
    payload = {
        'user_id': 2,
        'username': 'user',
        'role': 'user',
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    
    token = jwt.encode(payload, 'hard-to-guess-string', algorithm='HS256')
    
    # 测试上传API
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    url = "http://127.0.0.1:5000/api/upload/upload/image"
    
    # 准备测试文件
    import os
    test_file_path = os.path.join(os.path.dirname(__file__), '..', 'data_test', 'xz158.tif')
    
    if os.path.exists(test_file_path):
        print(f"找到测试文件: {test_file_path}")
        
        files = {'file': open(test_file_path, 'rb')}
        data = {'project_id': '1', 'step': 'step1'}
        
        try:
            response = requests.post(url, headers=headers, files=files, data=data)
            print(f"上传API响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"上传成功: {json.dumps(data, indent=2, ensure_ascii=False)}")
            else:
                print(f"上传失败: {response.text}")
                
        except Exception as e:
            print(f"上传请求失败: {e}")
        finally:
            files['file'].close()
    else:
        print(f"测试文件不存在: {test_file_path}")

def check_backend_logs():
    """检查后端日志中的认证错误"""
    print("\n=== 检查后端认证配置 ===")
    
    # 检查config.py中的SECRET_KEY
    config_path = os.path.join(os.path.dirname(__file__), 'app', 'config', 'config.py')
    
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'SECRET_KEY' in content:
                print("找到SECRET_KEY配置")
            else:
                print("未找到SECRET_KEY配置")
    
    print("请检查后端服务日志中的认证错误信息")

if __name__ == "__main__":
    import os
    os.chdir(os.path.dirname(__file__))
    
    test_authentication()
    test_upload_api()
    check_backend_logs()