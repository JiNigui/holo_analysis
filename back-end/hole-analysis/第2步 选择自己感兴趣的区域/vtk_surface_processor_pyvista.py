"""
基于PyVista的VTK表面数据处理器
使用PyVista简化VTK操作，提高稳定性和可读性
"""

import os
import numpy as np
import tifffile
import pyvista as pv
from skimage import measure
import logging
import tempfile

# 配置日志
logger = logging.getLogger(__name__)

class VTKSurfaceProcessorPyVista:
    """基于PyVista的VTK表面数据处理器"""
    
    def __init__(self, binary_data_path: str):
        """
        初始化处理器
        
        Args:
            binary_data_path: 二值化TIFF文件目录路径
        """
        self.binary_data_path = binary_data_path
        
    def get_slice_files(self):
        """获取所有二值化切片文件，按数字顺序排序"""
        if not os.path.exists(self.binary_data_path):
            raise FileNotFoundError(f"二值化数据目录不存在: {self.binary_data_path}")
        
        # 获取所有二值化切片文件
        slice_files = []
        for filename in os.listdir(self.binary_data_path):
            if filename.startswith('binary_slice_') and filename.endswith('.tiff'):
                slice_files.append(os.path.join(self.binary_data_path, filename))
        
        # 按数字顺序排序
        slice_files.sort(key=lambda x: int(''.join(filter(str.isdigit, os.path.basename(x)))))
        
        return slice_files
    
    def load_slice_data(self, file_path: str) -> np.ndarray:
        """加载单个切片数据"""
        try:
            return tifffile.imread(file_path)
        except Exception as e:
            logger.error(f"加载切片文件失败 {file_path}: {e}")
            raise
    
    def create_volume_from_slices(self, slice_files):
        """从切片文件创建三维体积数据"""
        print("[PyVista处理器] 开始加载切片数据...")
        
        # 获取第一个切片的形状
        first_slice = self.load_slice_data(slice_files[0])
        height, width = first_slice.shape
        num_slices = len(slice_files)
        
        print(f"[PyVista处理器] 切片数量: {num_slices}, 切片尺寸: {height}x{width}")
        
        # 预分配内存
        volume = np.zeros((num_slices, height, width), dtype=np.uint8)
        
        # 加载所有切片
        for i, file_path in enumerate(slice_files):
            if i % 100 == 0:  # 每100个文件记录一次进度
                print(f"[PyVista处理器] 加载进度: {i+1}/{num_slices}")
            
            slice_data = self.load_slice_data(file_path)
            volume[i] = slice_data
        
        print(f"[PyVista处理器] 体积数据加载完成，维度: {volume.shape}")
        return volume
    
    def downsample_volume(self, volume, factor=2):
        """
        对体积数据进行下采样（采用原始代码的均值池化策略）
        
        Args:
            volume: 三维体积数据
            factor: 下采样因子
            
        Returns:
            下采样后的二值化体积数据
        """
        if factor <= 1:
            return volume
        
        print(f"[PyVista处理器] 开始下采样，因子: {factor}")
        
        # 获取原始体积尺寸
        z_size, y_size, x_size = volume.shape
        new_z = z_size // factor
        new_y = y_size // factor
        new_x = x_size // factor
        
        print(f"[PyVista处理器] 原始维度: {volume.shape}, 目标维度: ({new_z}, {new_y}, {new_x})")
        
        # 调整体积大小以适应整除（原始代码策略）
        cropped = volume[:new_z*factor, :new_y*factor, :new_x*factor]
        
        # 进行下采样 - 采用原始代码的均值池化方法
        # 重塑为块状结构: (new_z, factor, new_y, factor, new_x, factor)
        downsampled = cropped.reshape(new_z, factor, new_y, factor, new_x, factor)
        
        # 沿块维度求均值（原始代码策略）
        downsampled = downsampled.mean(axis=(1, 3, 5))
        
        # 转换回二值图像（原始代码策略）
        downsampled_binary = (downsampled > 0.5).astype(np.uint8)
        
        print(f"[PyVista处理器] 下采样完成，新维度: {downsampled_binary.shape}")
        
        # 检查下采样后的数据有效性
        unique_values = np.unique(downsampled_binary)
        print(f"[PyVista处理器] 下采样后唯一值: {unique_values}")
        
        return downsampled_binary
    
    def extract_surface_with_marching_cubes(self, volume, spacing=(1.0, 1.0, 1.0)):
        """使用Marching Cubes算法提取表面"""
        print("[PyVista处理器] 开始提取3D表面...")
        
        try:
            # 使用scikit-image的marching_cubes算法（更稳定）
            verts, faces, normals, values = measure.marching_cubes(
                volume, 
                level=0.5,  # 二值化阈值
                spacing=spacing,
                gradient_direction='ascent',
                step_size=2,  # 增加步长减少计算量
                allow_degenerate=False
            )
            
            print(f"[PyVista处理器] 表面提取成功")
            print(f"[PyVista处理器] 顶点数: {len(verts)}, 面数: {len(faces)}")
            
            # 转换为PyVista格式
            # 将面索引转换为PyVista格式（每个面前面加上顶点数）
            faces_pv = np.hstack([[3] + list(face) for face in faces])
            
            # 创建PyVista网格
            mesh = pv.PolyData(verts, faces_pv)
            
            return mesh
            
        except Exception as e:
            print(f"[PyVista处理器] Marching Cubes提取失败: {e}")
            # 如果提取失败，创建一个简单的立方体作为fallback
            print("[PyVista处理器] 使用fallback立方体")
            return self.create_fallback_mesh()
    
    def create_fallback_mesh(self):
        """创建fallback网格（简单的立方体）"""
        # 创建一个简单的立方体
        cube = pv.Cube()
        return cube
    
    def generate_surface(self, output_dir: str = None) -> str:
        """
        生成VTK表面数据
        
        Args:
            output_dir: VTK文件输出目录
            
        Returns:
            VTK文件路径
        """
        try:
            print("[PyVista处理器] 开始生成表面数据...")
            
            # 1. 获取切片文件
            slice_files = self.get_slice_files()
            if not slice_files:
                raise ValueError("没有找到二值化切片文件")
            
            print(f"[PyVista处理器] 找到 {len(slice_files)} 个切片文件")
            
            # 2. 创建体积数据
            volume = self.create_volume_from_slices(slice_files)
            
            # 3. 下采样处理
            downsample_factor = 2  # 降低下采样率，保留更多细节
            downsampled_volume = self.downsample_volume(volume, downsample_factor)
            
            # 4. 调整spacing参数（考虑下采样）
            adjusted_spacing = tuple(s * downsample_factor for s in (1.0, 1.0, 1.0))
            
            # 5. 提取表面
            mesh = self.extract_surface_with_marching_cubes(downsampled_volume, adjusted_spacing)
            
            # 6. 清理网格
            print("[PyVista处理器] 清理网格数据...")
            cleaned_mesh = mesh.clean()

            # 7. 去除孤立碎片（只保留最大连通体）
            print("[PyVista处理器] 去除孤立碎片...")
            conn = cleaned_mesh.connectivity(largest_region=True)
            cleaned_mesh = conn.extract_surface().clean()
            print(f"[PyVista处理器] 保留最大连通体，面数: {cleaned_mesh.n_cells}")

            # 8. 表面平滑（PolyData才支持smooth）
            print("[PyVista处理器] 平滑表面...")
            cleaned_mesh = cleaned_mesh.smooth(n_iter=50, relaxation_factor=0.1)
            print("[PyVista处理器] 平滑完成")

            # 10. 创建输出文件路径
            if output_dir is None:
                output_dir = tempfile.gettempdir()

            os.makedirs(output_dir, exist_ok=True)

            import uuid
            vtk_filename = f"surface_{uuid.uuid4().hex[:8]}.vtp"
            vtk_file_path = os.path.join(output_dir, vtk_filename)

            # 11. 保存为VTK文件（二进制格式，更高效）
            print(f"[PyVista处理器] 保存二进制VTP文件到: {vtk_file_path}")
            cleaned_mesh.save(vtk_file_path, binary=True)

            # 12. 检查文件是否成功生成
            if not os.path.exists(vtk_file_path):
                raise RuntimeError("VTK文件生成失败")

            file_size = os.path.getsize(vtk_file_path)
            print(f"[PyVista处理器] VTK文件生成成功，大小: {file_size / (1024*1024):.2f} MB")

            return vtk_file_path
            
        except Exception as e:
            logger.error(f"生成VTK表面数据失败: {str(e)}")
            raise