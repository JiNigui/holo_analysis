"""
目录管理器
负责项目临时目录的创建、管理和清理
"""

import os
import shutil
from app.config.config import Config


class DirectoryManager:
    """目录管理器 - 负责项目临时目录的创建和清理"""
    
    @staticmethod
    def create_project_directory(username, project_name):
        """
        为项目创建完整的临时目录结构
        
        Args:
            username: 用户名
            project_name: 项目名
            
        Returns:
            str: 项目根目录路径
        """
        # 生成项目目录名：用户名_项目名
        project_dir_name = f"{username}_{project_name}"
        base_dir = os.path.join(Config.INTERMEDIATE_DATA_DIR, project_dir_name)
        
        # 定义完整的目录结构
        directories = [
            'first/input', 'first/output',
            'second/tmp',
            'third/selected_tiff_slices', 
            'fourth/masks', 'fourth/output',
            'fifth/output',
            'sixth/output'
        ]
        
        # 创建所有目录
        for directory in directories:
            full_path = os.path.join(base_dir, directory)
            os.makedirs(full_path, exist_ok=True)
            print(f"创建目录: {full_path}")
        
        return base_dir  # 返回项目根目录路径
    
    @staticmethod
    def delete_project_directory(username, project_name):
        """
        删除项目的临时目录
        
        Args:
            username: 用户名
            project_name: 项目名
            
        Returns:
            bool: 删除成功返回True，目录不存在返回False
        """
        project_dir_name = f"{username}_{project_name}"
        project_dir = os.path.join(Config.INTERMEDIATE_DATA_DIR, project_dir_name)
        
        if os.path.exists(project_dir):
            try:
                shutil.rmtree(project_dir)
                print(f"删除项目目录: {project_dir}")
                return True
            except Exception as e:
                print(f"删除项目目录失败 {project_dir}: {str(e)}")
                return False
        else:
            print(f"项目目录不存在: {project_dir}")
            return False
    
    @staticmethod
    def get_project_directory(username, project_name):
        """
        获取项目的临时目录路径
        
        Args:
            username: 用户名
            project_name: 项目名
            
        Returns:
            str: 项目目录路径
        """
        project_dir_name = f"{username}_{project_name}"
        return os.path.join(Config.INTERMEDIATE_DATA_DIR, project_dir_name)
    
    @staticmethod
    def project_directory_exists(username, project_name):
        """
        检查项目的临时目录是否存在
        
        Args:
            username: 用户名
            project_name: 项目名
            
        Returns:
            bool: 目录存在返回True，否则返回False
        """
        project_dir = DirectoryManager.get_project_directory(username, project_name)
        return os.path.exists(project_dir)
    
    @staticmethod
    def get_project_paths(username, project_name):
        """
        获取项目所有子目录的完整路径
        
        Args:
            username: 用户名
            project_name: 项目名
            
        Returns:
            dict: 包含所有子目录路径的字典
        """
        base_dir = DirectoryManager.get_project_directory(username, project_name)
        
        return {
            'base_dir': base_dir,
            'first_input': os.path.join(base_dir, 'first', 'input'),
            'first_output': os.path.join(base_dir, 'first', 'output'),
            'third_output': os.path.join(base_dir, 'third', 'selected_tiff_slices'),
            'fourth_masks': os.path.join(base_dir, 'fourth', 'masks'),
            'fourth_output': os.path.join(base_dir, 'fourth', 'output'),
            'fifth_output': os.path.join(base_dir, 'fifth', 'output'),
            'sixth_output': os.path.join(base_dir, 'sixth', 'output')
        }