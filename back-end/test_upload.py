#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试文件上传功能
"""

import requests
import os
import json

def test_file_upload():
    """测试文件上传功能"""
    
    # 测试token（使用与后端相同的密钥生成）
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoyLCJ1c2VybmFtZSI6InVzZXIiLCJyb2xlIjoidXNlciIsImlhdCI6MTc2NDk0MjY3MiwiZXhwIjoxNzY0OTQ2MjcyfQ.l8grb868MgoN7nOeTEYZtVbvf3FgDSxetLc0196mMkg"
    
    # API端点
    url = "http://127.0.0.1:5000/api/upload/upload/image"
    
    # 准备测试文件（使用data_test目录中的测试文件）
    test_file_path = os.path.join(os.path.dirname(__file__), "..", "data_test", "xz158.tif")
    
    if not os.path.exists(test_file_path):
        print(f"❌ 测试文件不存在: {test_file_path}")
        return False
    
    print(f"✅ 找到测试文件: {test_file_path}")
    
    # 准备请求头
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # 准备表单数据
    files = {
        'file': ('xz158.tif', open(test_file_path, 'rb'), 'image/tiff')
    }
    
    data = {
        'project_id': '12',
        'step': 'step1'
    }
    
    try:
        print("📤 正在上传文件...")
        response = requests.post(url, headers=headers, files=files, data=data)
        
        print(f"📊 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 文件上传成功!")
            print(f"响应数据: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"❌ 文件上传失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        return False
    finally:
        # 确保文件被关闭
        if 'files' in locals():
            files['file'][1].close()

if __name__ == "__main__":
    print("=== 测试文件上传功能 ===")
    success = test_file_upload()
    
    if success:
        print("\n🎉 文件上传测试通过!")
    else:
        print("\n💥 文件上传测试失败!")
    
    print("=== 测试完成 ===")