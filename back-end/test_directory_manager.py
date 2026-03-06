"""
测试目录管理器功能
"""

import os
import sys

# 添加应用路径到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.directory_manager import DirectoryManager
from app.config.config import Config

def test_directory_creation():
    """测试目录创建功能"""
    print("=== 测试目录创建功能 ===")
    
    # 测试数据
    username = "testuser"
    project_name = "testproject"
    
    # 创建目录
    try:
        project_dir = DirectoryManager.create_project_directory(username, project_name)
        print(f"✅ 目录创建成功: {project_dir}")
        
        # 检查目录是否存在
        if os.path.exists(project_dir):
            print("✅ 项目根目录存在")
        
        # 检查所有子目录是否存在
        paths = DirectoryManager.get_project_paths(username, project_name)
        for key, path in paths.items():
            if os.path.exists(path):
                print(f"✅ {key}: {path} - 存在")
            else:
                print(f"❌ {key}: {path} - 不存在")
        
        return True
        
    except Exception as e:
        print(f"❌ 目录创建失败: {str(e)}")
        return False

def test_directory_deletion():
    """测试目录删除功能"""
    print("\n=== 测试目录删除功能 ===")
    
    # 测试数据
    username = "testuser"
    project_name = "testproject"
    
    # 删除目录
    try:
        result = DirectoryManager.delete_project_directory(username, project_name)
        
        if result:
            print("✅ 目录删除成功")
        else:
            print("❌ 目录删除失败")
        
        # 检查目录是否已删除
        project_dir = DirectoryManager.get_project_directory(username, project_name)
        if not os.path.exists(project_dir):
            print("✅ 项目目录已成功删除")
        else:
            print("❌ 项目目录仍然存在")
        
        return result
        
    except Exception as e:
        print(f"❌ 目录删除失败: {str(e)}")
        return False

def test_directory_exists():
    """测试目录存在性检查"""
    print("\n=== 测试目录存在性检查 ===")
    
    # 测试数据
    username = "testuser"
    project_name = "testproject"
    
    # 检查不存在的目录
    exists = DirectoryManager.project_directory_exists(username, project_name)
    print(f"不存在的目录检查结果: {exists}")
    
    # 创建目录后检查
    DirectoryManager.create_project_directory(username, project_name)
    exists = DirectoryManager.project_directory_exists(username, project_name)
    print(f"创建后的目录检查结果: {exists}")
    
    # 清理测试目录
    DirectoryManager.delete_project_directory(username, project_name)
    
    return True

def main():
    """主测试函数"""
    print("开始测试目录管理器功能...\n")
    
    # 测试配置
    print(f"配置的临时数据目录: {Config.INTERMEDIATE_DATA_DIR}")
    
    # 运行测试
    test1_result = test_directory_creation()
    test2_result = test_directory_deletion()
    test3_result = test_directory_exists()
    
    print("\n=== 测试结果汇总 ===")
    print(f"目录创建测试: {'✅ 通过' if test1_result else '❌ 失败'}")
    print(f"目录删除测试: {'✅ 通过' if test2_result else '❌ 失败'}")
    print(f"存在性检查测试: {'✅ 通过' if test3_result else '❌ 失败'}")
    
    if test1_result and test2_result and test3_result:
        print("\n🎉 所有测试通过！目录管理器功能正常。")
    else:
        print("\n⚠️ 部分测试失败，请检查代码。")

if __name__ == "__main__":
    main()