import os
import pyvista as pv
import numpy as np
import json
import argparse
from matplotlib import pyplot as plt
from skimage import measure

def get_slice_data(vtk_file_path, normal, origin):
    """
    从VTK文件中提取指定平面的切片数据
    
    Args:
        vtk_file_path: VTK文件路径
        normal: 平面法向量 [x, y, z]
        origin: 平面上的点 [x, y, z]
    
    Returns:
        dict: 包含切片点坐标和线段信息的字典
    """
    print(f"加载VTK文件: {vtk_file_path}")
    
    # 加载 .vtk 文件
    mesh = pv.read(vtk_file_path)
    print(f"网格加载完成: {mesh}")

    # 创建 PyVista 数据对象
    grid = pv.wrap(mesh)

    # 提取切片
    plane_slice = grid.slice(normal=normal, origin=origin)
    
    print(f"切片提取完成: {plane_slice}")
    
    # 获取切片的点数据
    points = plane_slice.points
    lines = plane_slice.lines if hasattr(plane_slice, 'lines') else None
    
    # 将数据转换为JSON可序列化的格式
    result = {
        'points': points.tolist() if points is not None else [],
        'lines': lines.tolist() if lines is not None else [],
        'n_points': len(points) if points is not None else 0,
        'n_lines': len(lines) if lines is not None else 0,
        'normal': normal,
        'origin': origin
    }
    
    print(f"切片数据准备完成，点数: {result['n_points']}, 线数: {result['n_lines']}")
    
    return result

def get_slice_data_from_params(vtk_file_path, params):
    """
    从参数字典中提取normal和origin，并获取切片数据
    
    Args:
        vtk_file_path: VTK文件路径
        params: 包含normal和origin的参数字典
    
    Returns:
        dict: 包含切片点坐标和线段信息的字典
    """
    normal = params.get('normal', [-0.78026193, 0.37575434, -0.5])
    origin = params.get('origin', [26.21065698, 14.67418985, 11.66648875])
    
    return get_slice_data(vtk_file_path, normal, origin)

def main():
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='获取3D切片数据')
    parser.add_argument('--vtk-file', type=str, required=True,
                       help='输入VTK文件路径')
    parser.add_argument('--params-file', type=str, required=True,
                       help='分析参数JSON文件路径')
    parser.add_argument('--output-dir', type=str, required=True,
                       help='输出目录路径')
    
    args = parser.parse_args()
    
    print("====== 获取3D切片数据开始 ======")
    print(f"VTK文件: {args.vtk_file}")
    print(f"参数文件: {args.params_file}")
    print(f"输出目录: {args.output_dir}")
    
    # 检查输入文件是否存在
    if not os.path.exists(args.vtk_file):
        print(f"错误: VTK文件不存在: {args.vtk_file}")
        exit(1)
    
    if not os.path.exists(args.params_file):
        print(f"错误: 参数文件不存在: {args.params_file}")
        exit(1)
    
    # 确保输出目录存在
    os.makedirs(args.output_dir, exist_ok=True)
    
    # 加载分析参数
    with open(args.params_file, 'r', encoding='utf-8') as f:
        params = json.load(f)
    
    print(f"加载分析参数成功: {params.keys()}")
    
    # 获取切片数据
    slice_data = get_slice_data_from_params(args.vtk_file, params)
    
    # 输出为JSON格式
    print("切片数据获取完成，输出JSON格式:")
    print(json.dumps(slice_data, indent=2))
    
    # 保存切片数据到输出目录
    output_file = os.path.join(args.output_dir, 'slice_data.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(slice_data, f, indent=2, ensure_ascii=False)
    
    print(f"切片数据已保存到: {output_file}")
    print("====== 获取3D切片数据完成 ======")

if __name__ == "__main__":
    main()