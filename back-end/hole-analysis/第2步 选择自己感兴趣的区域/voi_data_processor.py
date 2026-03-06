"""
VOI数据处理器模块
负责生成统一批次数据
"""

import os
import zipfile
import numpy as np
from PIL import Image
import io
import json
from typing import List, Tuple, Dict
import logging

logger = logging.getLogger(__name__)


class VOIDataProcessor:
    """VOI数据处理类"""
    
    def __init__(self, binary_data_path: str):
        """
        初始化处理器
        
        Args:
            binary_data_path: 二值化数据目录路径
        """
        self.binary_data_path = binary_data_path
        # 动态计算总切片数
        self.total_slices = self._calculate_total_slices()
    
    def _calculate_total_slices(self) -> int:
        """动态计算目录中的TIFF文件总数"""
        import glob
        pattern = os.path.join(self.binary_data_path, "binary_slice_*.tiff")
        files = glob.glob(pattern)
        return len(files)
        
    def get_slice_files(self) -> List[str]:
        """获取所有切片文件路径"""
        import glob
        pattern = os.path.join(self.binary_data_path, "binary_slice_*.tiff")
        files = glob.glob(pattern)
        
        # 按自然数排序（处理binary_slice_1.tiff, binary_slice_2.tiff, ..., binary_slice_10.tiff等）
        files.sort(key=lambda x: int(''.join(filter(str.isdigit, os.path.basename(x)))))
        
        return files
    
    def load_slice_data(self, file_path: str) -> np.ndarray:
        """加载单个切片数据"""
        try:
            with Image.open(file_path) as img:
                # 转换为二值化数组 (0/1)
                img_array = np.array(img)
                # 二值化处理，大于0的值设为1
                binary_array = (img_array > 0).astype(np.uint8)
                return binary_array
        except Exception as e:
            logger.error(f"加载切片文件失败: {file_path}, 错误: {e}")
            raise
    
    def generate_enhancement_data(self, start_slice: int, end_slice: int) -> Dict:
        """
        生成增强数据块
        
        Args:
            start_slice: 起始切片编号
            end_slice: 结束切片编号
            
        Returns:
            包含压缩数据和元数据的字典
        """
        try:
            slice_files = self.get_slice_files()
            
            # 获取指定范围的切片
            selected_files = slice_files[start_slice-1:end_slice]
            
            if not selected_files:
                raise ValueError(f"切片范围无效: {start_slice}-{end_slice}")
            
            # 加载数据
            voxel_data = []
            for file_path in selected_files:
                slice_data = self.load_slice_data(file_path)
                voxel_data.append(slice_data)
            
            # 转换为三维数组
            voxel_array = np.stack(voxel_data, axis=0)
            
            # 行程编码压缩
            compressed_data = self.rle_compress(voxel_array)
            
            # 元数据
            metadata = {
                "start_slice": start_slice,
                "end_slice": end_slice,
                "block_size": len(selected_files),
                "dimensions": voxel_array.shape,
                "data_format": "rle_compressed"
            }
            
            return {
                "metadata": metadata,
                "compressed_data": compressed_data
            }
            
        except Exception as e:
            logger.error(f"生成增强数据失败: {e}")
            raise
    
    def rle_compress(self, voxel_array: np.ndarray) -> bytes:
        """
        行程编码压缩
        
        Args:
            voxel_array: 三维体素数组
            
        Returns:
            压缩后的字节数据
        """
        # 展平数组
        flat_array = voxel_array.flatten()
        
        # 行程编码
        compressed = []
        current_value = flat_array[0]
        count = 1
        
        for value in flat_array[1:]:
            if value == current_value and count < 255:
                count += 1
            else:
                compressed.extend([current_value, count])
                current_value = value
                count = 1
        
        compressed.extend([current_value, count])
        
        return bytes(compressed)
    
    def create_batch_tiff_zip_package(self, batch_index: int = 1, batch_size: int = 200, sample_rate: int = 1) -> bytes:
        """
        创建批次TIFF文件的ZIP压缩包（支持增量加载）
        
        Args:
            batch_index: 批次索引（从1开始）
            batch_size: 每批次文件数量
            sample_rate: 采样率，默认1（不采样，统一高质量模式）
            
        Returns:
            ZIP压缩包的字节数据
        """
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # 获取所有切片文件并按自然数排序
            slice_files = self.get_slice_files()
            slice_files.sort(key=lambda x: int(''.join(filter(str.isdigit, os.path.basename(x)))))
            
            # 统一批次处理：按批次索引和大小选择文件（批次索引从1开始）
            start_idx = (batch_index - 1) * batch_size
            end_idx = min(batch_index * batch_size, len(slice_files))
            
            # 安全检查：确保批次索引在有效范围内
            if start_idx >= len(slice_files):
                raise ValueError(f"批次 {batch_index} 超出文件范围，总文件数: {len(slice_files)}")
            
            # 应用采样率（默认1，即不采样）
            sampled_files = slice_files[start_idx:end_idx:max(1, sample_rate)]
            
            if not sampled_files:
                raise ValueError(f"批次 {batch_index} 无可用文件，总文件数: {len(slice_files)}")
            
            # 提取原始文件名列表
            original_filenames = [os.path.basename(file_path) for file_path in sampled_files]
            
            # 添加元数据
            metadata = {
                "batch_index": batch_index,
                "batch_type": "unified",  # 统一批次模式
                "batch_size": len(sampled_files),
                "total_slices": self.total_slices,
                "file_format": "tiff",
                "original_filenames": original_filenames,
                "file_order": "natural",
                "sample_rate": sample_rate,
                "start_slice": start_idx + 1,  # 起始切片编号（1-based）
                "end_slice": end_idx,  # 结束切片编号
                "total_batches": (len(slice_files) + batch_size - 1) // batch_size  # 总批次数
            }
            metadata_json = json.dumps(metadata, indent=2)
            zip_file.writestr("metadata.json", metadata_json)
            
            # 添加TIFF文件到ZIP包，保留原始文件名
            for file_path in sampled_files:
                original_filename = os.path.basename(file_path)
                zip_file.write(file_path, original_filename)
        
        zip_buffer.seek(0)
        return zip_buffer.getvalue()
    
    def create_unified_batch_package(self, batch_index: int = 1, batch_size: int = 200) -> bytes:
        """
        创建统一批次数据包（高质量模式，不采样）
        
        Args:
            batch_index: 批次索引（从1开始）
            batch_size: 每批次文件数量
            
        Returns:
            ZIP压缩包的字节数据
        """
        # 直接调用批次TIFF ZIP包创建方法，使用高质量模式（sample_rate=1）
        return self.create_batch_tiff_zip_package(batch_index, batch_size, sample_rate=1)
    
    def calculate_remaining_files(self, sample_rate: int = 5) -> List[str]:
        """
        计算剩余文件（统一批次模式，此方法已弃用）
        
        Args:
            sample_rate: 采样率
            
        Returns:
            剩余文件列表
        """
        # 统一批次模式下，此方法不再使用
        return []
    
    def calculate_total_batches(self, batch_size: int = 200, sample_rate: int = 1) -> Dict:
        """
        计算总批次信息（统一批次模式）
        
        Args:
            batch_size: 每批次文件数量
            sample_rate: 采样率，默认1（不采样）
            
        Returns:
            批次信息字典
        """
        slice_files = self.get_slice_files()
        total_files = len(slice_files)
        
        # 统一批次模式：直接计算总批次数
        total_batches = (total_files + batch_size - 1) // batch_size  # 向上取整
        
        # 获取TIFF图像尺寸（从第一个文件）
        image_width, image_height = 0, 0
        if slice_files:
            try:
                with Image.open(slice_files[0]) as img:
                    image_width, image_height = img.size
            except Exception as e:
                print(f"获取TIFF尺寸时发生错误: {str(e)}")
                # 使用默认尺寸
                image_width, image_height = 512, 512
        
        return {
            "total_files": total_files,
            "batch_size": batch_size,
            "total_batches": total_batches,
            "sample_rate": sample_rate,
            "image_width": image_width,
            "image_height": image_height,
            "dimensions": [image_width, image_height, total_files]
        }
    
    def get_unified_batch_info(self, batch_size: int = 200) -> Dict:
        """
        获取统一批次信息（用于前端批次规划）
        
        Args:
            batch_size: 每批次文件数量
            
        Returns:
            统一批次信息字典
        """
        # 使用统一批次模式计算批次信息
        batch_info = self.calculate_total_batches(batch_size, sample_rate=1)
        
        # 获取所有文件并按自然数排序
        slice_files = self.get_slice_files()
        slice_files.sort(key=lambda x: int(''.join(filter(str.isdigit, os.path.basename(x)))))
        
        # 添加文件详细信息
        batch_info["file_names"] = [os.path.basename(f) for f in slice_files]
        batch_info["first_file"] = os.path.basename(slice_files[0]) if slice_files else ""
        batch_info["last_file"] = os.path.basename(slice_files[-1]) if slice_files else ""
        
        # 确保包含TIFF尺寸信息
        if "image_width" not in batch_info:
            batch_info["image_width"] = batch_info.get("total_files", 0)
        if "image_height" not in batch_info:
            batch_info["image_height"] = batch_info.get("total_files", 0)
        if "dimensions" not in batch_info:
            batch_info["dimensions"] = [batch_info.get("image_width", 0), batch_info.get("image_height", 0), batch_info.get("total_files", 0)]
        
        return batch_info
    
    def get_batch_info(self, batch_index: int, batch_size: int = 200, sample_rate: int = 1) -> Dict:
        """
        获取批次详细信息（统一批次模式）
        
        Args:
            batch_index: 批次索引（从1开始）
            batch_size: 每批次文件数量
            sample_rate: 采样率，默认1（不采样）
            
        Returns:
            批次详细信息字典
        """
        batch_info = self.calculate_total_batches(batch_size, sample_rate)
        
        # 统一批次模式：按批次索引和大小选择文件（批次索引从1开始）
        slice_files = self.get_slice_files()
        slice_files.sort(key=lambda x: int(''.join(filter(str.isdigit, os.path.basename(x)))))
        
        start_idx = (batch_index - 1) * batch_size
        end_idx = min(batch_index * batch_size, len(slice_files))
        
        # 安全检查：确保批次索引在有效范围内
        if start_idx >= len(slice_files):
            raise ValueError(f"批次 {batch_index} 超出文件范围，总文件数: {len(slice_files)}")
        
        # 应用采样率
        batch_files = slice_files[start_idx:end_idx:max(1, sample_rate)]
        
        return {
            "batch_index": batch_index,
            "batch_type": "unified",
            "file_count": len(batch_files),
            "file_names": [os.path.basename(f) for f in batch_files],
            "start_index": start_idx,
            "end_index": end_idx,
            "is_last_batch": batch_index == batch_info["total_batches"],
            "start_slice": start_idx + 1,  # 起始切片编号（1-based）
            "end_slice": end_idx,  # 结束切片编号
            **batch_info
        }

    def create_tiff_zip_package(self, sample_rate: int = 5) -> bytes:
        """
        创建包含TIFF文件的ZIP压缩包
        
        Args:
            sample_rate: 采样率，默认5抽1
            
        Returns:
            ZIP压缩包的字节数据
        """
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # 获取切片文件
            slice_files = self.get_slice_files()
            
            # 5抽1采样
            sampled_files = slice_files[::sample_rate]
            
            # 添加元数据
            # 提取原始文件名列表（按自然排序）
            original_filenames = [os.path.basename(file_path) for file_path in sampled_files]
            
            metadata = {
                "total_slices": self.total_slices,
                "sampled_slices": len(sampled_files),
                "sample_rate": sample_rate,
                "file_format": "tiff",
                "original_filenames": original_filenames,  # 添加原始文件名列表
                "file_order": "natural"  # 标识按自然数排序
            }
            metadata_json = json.dumps(metadata, indent=2)
            zip_file.writestr("metadata.json", metadata_json)
            
            # 添加TIFF文件到ZIP包，保留原始文件名
            for file_path in sampled_files:
                # 提取原始文件名（如：binary_slice_5.tiff）
                original_filename = os.path.basename(file_path)
                zip_file.write(file_path, original_filename)
        
        zip_buffer.seek(0)
        return zip_buffer.getvalue()


def create_batch_package(binary_data_path: str, batch_index: int = 1, batch_size: int = 200) -> bytes:
    """
    创建批次数据包的便捷函数（统一批次模式）
    
    Args:
        binary_data_path: 二值化数据目录路径
        batch_index: 批次索引（从1开始）
        batch_size: 每批次文件数量
        
    Returns:
        ZIP压缩包的字节数据
    """
    processor = VOIDataProcessor(binary_data_path)
    return processor.create_batch_tiff_zip_package(batch_index, batch_size, sample_rate=1)  # 统一使用高质量模式，不采样


if __name__ == "__main__":
    # 测试代码
    binary_path = r"d:\孔洞项目\孔洞分析软件\back-end\hole-analysis\第1步 原始图像的二值化\output"
    
    try:
        # 创建处理器实例
        processor = VOIDataProcessor(binary_path)
        
        # 测试批次信息计算（统一批次模式）
        batch_info = processor.calculate_total_batches(batch_size=200, sample_rate=1)
        print(f"批次信息: {batch_info}")
        
        # 测试批次数据生成
        print("\n=== 批次数据包生成测试 ===")
        for i in range(1, batch_info['total_batches'] + 1):
            batch_zip = create_batch_package(binary_path, batch_index=i, batch_size=200)
            print(f"批次 {i} 数据包大小: {len(batch_zip)} 字节")
        
        print("\n=== 测试完成 ===")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()