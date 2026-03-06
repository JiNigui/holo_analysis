import os
import json
import argparse
import pyvista as pv
import numpy as np
from matplotlib import pyplot as plt

def main():
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='输出平面方程并显示在画布上')
    parser.add_argument('--params-file', type=str, default='analysis_parameters.json',
                       help='分析参数文件路径（默认: analysis_parameters.json）')
    parser.add_argument('--vtk-file', type=str, default='combined_selected_regions.vtk',
                       help='VTK文件路径（默认: combined_selected_regions.vtk）')
    parser.add_argument('--output-dir', type=str, default='.',
                       help='输出目录路径（默认: 当前目录）')
    
    args = parser.parse_args()
    
    # 使用动态路径
    params_file_path = args.params_file
    vtk_file_path = args.vtk_file
    output_dir = args.output_dir
    
    print(f"参数文件路径: {params_file_path}")
    print(f"VTK文件路径: {vtk_file_path}")
    print(f"输出目录: {output_dir}")
    
    # 检查参数文件是否存在
    if not os.path.exists(params_file_path):
        print(f"错误：分析参数文件不存在: {params_file_path}")
        exit(1)

    # 读取分析参数
    with open(params_file_path, 'r', encoding='utf-8') as f:
        analysis_params = json.load(f)

    # 从参数文件中获取法向量和原点
    normal = analysis_params.get('best_plane', [0, 0, 1.])  # 目标平面的法向量
    origin = analysis_params.get('centroid', [0, 0, 0])  # 目标平面上的某个点

    print(f"从参数文件加载: normal={normal}, origin={origin}")

    # 检查VTK文件是否存在
    if not os.path.exists(vtk_file_path):
        print(f"错误：VTK文件不存在: {vtk_file_path}")
        exit(1)

    # 加载 .vtk 文件
    mesh = pv.read(vtk_file_path)

    print(f"Mesh loaded: {mesh}")

    # 创建 PyVista 数据对象
    grid = pv.wrap(mesh)

    # 创建一个平面切片
    plane_slice = grid.slice(normal=normal, origin=origin)

    # 获取切片的点坐标和法向量
    points = plane_slice.points  # 切片上的所有点
    normal = np.array(normal)  # 目标平面的法向量
    origin = np.array(origin)  # 目标平面上的某个点

    # 计算每个点到平面的投影
    def project_to_plane(points, normal, origin):
        # 向量化计算投影
        normal = normal / np.linalg.norm(normal)  # 归一化法向量
        vectors_to_points = points - origin  # 每个点到平面的向量
        projection_lengths = np.dot(vectors_to_points, normal)  # 投影长度
        projection_points = points - np.outer(projection_lengths, normal)  # 计算投影后的点
        return projection_points

    # 对切片的点进行投影
    projected_points = project_to_plane(points, normal, origin)

    # 投影后我们可以得到二维点，假设我们想将其投影到平面并进行可视化
    # 如果要获取投影到平面上的二维坐标，只需选择投影后的前两列
    projected_2d = projected_points[:, :2]  # 选择 X-Y 平面

    # 可视化投影后的二维图像
    fig, ax = plt.subplots()
    ax.scatter(projected_2d[:, 0], projected_2d[:, 1], s=1, c='black')  # 绘制投影点
    ax.set_title("Projected 2D Image onto the Plane")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.axis('equal')

    # 在图像中标出切面在三维体中的位置
    # 切面原点位置
    ax.scatter(origin[0], origin[1], color='red', label=f"Cut Plane Origin (X={origin[0]}, Y={origin[1]})", s=50)

    # 绘制法向量，表示切面的方向
    ax.quiver(origin[0], origin[1], normal[0], normal[1], angles='xy', scale_units='xy', scale=1, color='blue', label="Normal Vector")

    # 添加图例
    ax.legend()

    # 保存图像到动态输出目录
    output_image_path = os.path.join(output_dir, 'projected_2d_image_with_cut_plane_position.png')
    plt.savefig(output_image_path)

    # 关闭图形，避免阻塞脚本执行
    plt.close()

    print(f"图像已成功生成: {output_image_path}")

if __name__ == "__main__":
    main()
