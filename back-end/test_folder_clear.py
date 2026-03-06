#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试文件夹清空功能
"""

import os
import shutil

def test_folder_clear_function():
    """测试文件夹清空功能"""
    
    # 目标文件夹路径
    target_dir = 'hole-analysis\\第1步 原始图像的二值化\\input'
    
    print("=== 测试文件夹清空功能 ===")
    print(f"目标文件夹: {os.path.abspath(target_dir)}")
    
    # 1. 确保文件夹存在
    os.makedirs(target_dir, exist_ok=True)
    print("✅ 确保文件夹存在")
    
    # 2. 创建一些测试文件
    test_files = ['test1.tif', 'test2.tif', 'test3.tif']
    for file_name in test_files:
        file_path = os.path.join(target_dir, file_name)
        with open(file_path, 'w') as f:
            f.write(f"这是测试文件 {file_name}")
    
    print(f"✅ 创建了 {len(test_files)} 个测试文件")
    print(f"当前文件夹内容: {os.listdir(target_dir)}")
    
    # 3. 模拟文件上传前的清空逻辑
    print("\n=== 模拟文件上传前的清空逻辑 ===")
    if os.path.exists(target_dir):
        for file_name in os.listdir(target_dir):
            file_path = os.path.join(target_dir, file_name)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"✅ 删除文件: {file_name}")
            except Exception as e:
                print(f"❌ 删除文件 {file_path} 失败: {e}")
    
    # 4. 检查清空结果
    remaining_files = os.listdir(target_dir)
    print(f"\n=== 清空结果检查 ===")
    print(f"剩余文件数量: {len(remaining_files)}")
    print(f"剩余文件列表: {remaining_files}")
    
    if len(remaining_files) == 0:
        print("🎉 文件夹清空功能测试通过！")
    else:
        print("💥 文件夹清空功能测试失败！")
    
    # 5. 模拟上传新文件
    print("\n=== 模拟上传新文件 ===")
    new_files = ['xz158.tif', 'xz159.tif', 'xz160.tif']
    for file_name in new_files:
        file_path = os.path.join(target_dir, file_name)
        with open(file_path, 'w') as f:
            f.write(f"这是新上传的文件 {file_name}")
    
    print(f"✅ 上传了 {len(new_files)} 个新文件")
    print(f"当前文件夹内容: {os.listdir(target_dir)}")
    
    # 6. 再次清空并上传不同文件
    print("\n=== 再次测试清空功能 ===")
    if os.path.exists(target_dir):
        for file_name in os.listdir(target_dir):
            file_path = os.path.join(target_dir, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
    
    different_files = ['image1.tif', 'image2.tif']
    for file_name in different_files:
        file_path = os.path.join(target_dir, file_name)
        with open(file_path, 'w') as f:
            f.write(f"这是不同批次上传的文件 {file_name}")
    
    print(f"✅ 上传了 {len(different_files)} 个不同文件")
    print(f"最终文件夹内容: {os.listdir(target_dir)}")
    
    # 清理测试文件
    for file_name in os.listdir(target_dir):
        file_path = os.path.join(target_dir, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)
    
    print("\n=== 测试完成 ===")
    print("✅ 所有测试文件已清理")

if __name__ == "__main__":
    test_folder_clear_function()