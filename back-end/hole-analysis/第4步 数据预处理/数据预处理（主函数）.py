# 数据预处理整合流程
# 将多个预处理步骤整合为一个完整流程：
# 1. 加载孔洞识别后的tiff序列并堆叠成vtk
# 2. 填充vtk中的孔洞
# 3. 平滑vtk表面
# 4. 生成region字段标识连通域

import numpy as np
from skimage import measure
import imageio.v2 as imageio
import os
import pyvista as pv
import vtk
import time


def load_and_stack_tiff_slices(masks_folder='masks', output_vtk='hole.vtk', spacing=(0.1, 0.1, 0.1)):
    """
    加载tiff切片序列并堆叠成vtk文件
    :param masks_folder: 包含tiff切片的文件夹路径
    :param output_vtk: 输出的vtk文件名
    :param spacing: 体素间距
    :return: 生成的PyVista网格对象
    """
    print("==== 步骤1: 加载并堆叠tiff切片 ====")
    start_time = time.time()

    # 自定义排序函数，按数字排序
    def natural_sort_key(file_name):
        base_name = os.path.splitext(os.path.basename(file_name))[0]
        num_part = ''.join(filter(str.isdigit, base_name))
        return int(num_part) if num_part.isdigit() else 0

    # 获取并排序tiff文件
    tiff_files = sorted(
        [os.path.join(masks_folder, f) for f in os.listdir(masks_folder) if f.endswith('.tiff')],
        key=natural_sort_key
    )

    if not tiff_files:
        raise FileNotFoundError(f"在文件夹 '{masks_folder}' 中未找到tiff文件")

    print(f"找到 {len(tiff_files)} 个tiff文件")

    # 加载切片数据
    print("正在加载切片数据...")
    binary_slices = [imageio.imread(file) for file in tiff_files]

    # 堆叠切片以形成三维体数据
    volume = np.stack(binary_slices, axis=0)

    # 确保数据格式正确
    print(f"堆叠后体积形状: {volume.shape}, 唯一值: {np.unique(volume)}")

    # 提取3D表面
    print("正在提取3D表面...")
    verts, faces, _, _ = measure.marching_cubes(volume, level=0.5, spacing=spacing)

    # 转换 faces 为 PyVista 格式
    faces = np.hstack([[3] + list(face) for face in faces])

    # 创建 PyVista 的 PolyData
    mesh = pv.PolyData(verts, faces)

    # 保存为 .vtk 格式
    mesh.save(output_vtk)
    print(f"已保存为 '{output_vtk}'")

    elapsed_time = time.time() - start_time
    print(f"步骤1完成，耗时: {elapsed_time:.2f}秒\n")

    return mesh


def fill_holes_in_vtk(input_vtk, output_vtk='output.vtk', hole_size=1000.0):
    """
    填充vtk文件中的孔洞
    :param input_vtk: 输入的vtk文件名
    :param output_vtk: 输出的vtk文件名
    :param hole_size: 要填充的最大孔洞尺寸
    """
    print("==== 步骤2: 填充面片孔洞 ====")
    start_time = time.time()

    # 读取输入VTK文件
    reader = vtk.vtkPolyDataReader()
    reader.SetFileName(input_vtk)
    reader.Update()

    # 填充表面孔洞
    hole_filler = vtk.vtkFillHolesFilter()
    hole_filler.SetInputData(reader.GetOutput())
    hole_filler.SetHoleSize(hole_size)
    hole_filler.Update()

    # 保存结果
    writer = vtk.vtkPolyDataWriter()
    writer.SetFileName(output_vtk)
    writer.SetInputData(hole_filler.GetOutput())
    writer.Write()

    elapsed_time = time.time() - start_time
    print(f"已将填充后的VTK文件保存到: {output_vtk}")
    print(f"步骤2完成，耗时: {elapsed_time:.2f}秒\n")


def smooth_vtk_surface(input_vtk, output_vtk='output_smoothed.vtk', iterations=50, relaxation_factor=0.1):
    """
    平滑vtk文件的表面
    :param input_vtk: 输入的vtk文件名
    :param output_vtk: 输出的vtk文件名
    :param iterations: 平滑迭代次数
    :param relaxation_factor: 松弛因子
    """
    print("==== 步骤3: 表面平滑处理 ====")
    start_time = time.time()

    # 读取 .vtk 文件
    reader = vtk.vtkPolyDataReader()
    reader.SetFileName(input_vtk)
    reader.Update()

    # 平滑处理
    smooth_filter = vtk.vtkSmoothPolyDataFilter()
    smooth_filter.SetInputConnection(reader.GetOutputPort())
    smooth_filter.SetNumberOfIterations(iterations)  # 调整迭代次数以控制平滑程度
    smooth_filter.SetRelaxationFactor(relaxation_factor)   # 调整松弛因子
    smooth_filter.FeatureEdgeSmoothingOff() # 是否平滑特征边
    smooth_filter.Update()

    # 保存平滑后的 .vtk 文件
    writer = vtk.vtkPolyDataWriter()
    writer.SetFileName(output_vtk)
    writer.SetInputData(smooth_filter.GetOutput())
    writer.Write()

    elapsed_time = time.time() - start_time
    print(f"已将平滑后的VTK文件保存到: {output_vtk}")
    print(f"步骤3完成，耗时: {elapsed_time:.2f}秒\n")


def generate_region_ids(input_vtk, output_vtk='output_with_regions.vtk'):
    """
    生成region字段标识连通域
    :param input_vtk: 输入的vtk文件名
    :param output_vtk: 输出的vtk文件名
    """
    print("==== 步骤4: 生成连通域region字段 ====")
    start_time = time.time()

    # 加载 VTK 文件
    print("加载 VTK 文件中...")
    reader = vtk.vtkPolyDataReader()
    reader.SetFileName(input_vtk)
    reader.Update()
    input_data = reader.GetOutput()
    print(f"加载完成，点云包含 {input_data.GetNumberOfPoints()} 个点")

    # 提取连通域
    print("提取连通域中...")
    connectivity_filter = vtk.vtkConnectivityFilter()
    connectivity_filter.SetInputData(input_data)
    connectivity_filter.SetExtractionModeToAllRegions()  # 提取所有连通域
    connectivity_filter.ColorRegionsOn()  # 为每个连通域分配不同的颜色
    connectivity_filter.Update()

    # 确认生成 RegionId 字段
    output_data = connectivity_filter.GetOutput()
    if output_data.GetCellData().HasArray("RegionId"):
        print("成功生成 RegionId 字段")
    else:
        print("警告: 未生成 RegionId 字段，可能是提取连通域的步骤有问题")

    # 查看连通域数目
    region_count = connectivity_filter.GetNumberOfExtractedRegions()
    print(f"共检测到 {region_count} 个连通域")

    # 保存连通域结果（包括 RegionId）
    print("保存筛选结果中...")
    writer = vtk.vtkPolyDataWriter()
    writer.SetFileName(output_vtk)
    writer.SetInputData(output_data)
    writer.Write()

    elapsed_time = time.time() - start_time
    print(f"处理完成，结果已保存到 '{output_vtk}'")
    print(f"步骤4完成，耗时: {elapsed_time:.2f}秒\n")


def main():
    """
    主函数，按顺序执行所有数据预处理步骤
    """
    import argparse
    
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='数据预处理主函数')
    parser.add_argument('--input-dir', type=str, default='masks', 
                       help='输入目录路径（包含tiff切片，默认: masks）')
    parser.add_argument('--output-dir', type=str, default='.',
                       help='输出目录路径（默认: 当前目录）')
    
    args = parser.parse_args()
    
    print("====== 数据预处理整合流程开始 ======")
    print(f"输入目录: {args.input_dir}")
    print(f"输出目录: {args.output_dir}")
    total_start_time = time.time()

    # 检查输入目录是否存在
    if not os.path.exists(args.input_dir):
        print(f"错误: 输入目录不存在: {args.input_dir}")
        exit(1)
    
    # 检查输入目录中是否有文件
    input_files = [f for f in os.listdir(args.input_dir) if f.endswith('.tiff')]
    if not input_files:
        print(f"错误: 输入目录中没有找到.tiff文件: {args.input_dir}")
        exit(1)
    
    print(f"找到 {len(input_files)} 个输入文件")
    
    # 确保输出目录存在
    os.makedirs(args.output_dir, exist_ok=True)

    # 配置参数（使用动态路径）
    config = {
        'masks_folder': args.input_dir,  # tiff切片文件夹
        'temp_files': {
            'hole_vtk': os.path.join(args.output_dir, 'hole.vtk'),           # 堆叠后的vtk文件
            'filled_vtk': os.path.join(args.output_dir, 'output.vtk'),       # 填充后的vtk文件
            'smoothed_vtk': os.path.join(args.output_dir, 'output_smoothed.vtk')  # 平滑后的vtk文件
        },
        'final_output': os.path.join(args.output_dir, 'output_with_regions.vtk'),  # 最终输出文件
        'spacing': (0.1, 0.1, 0.1),  # 体素间距
        'hole_size': 1000.0,  # 填充孔洞的最大尺寸
        'smooth_iterations': 50,  # 平滑迭代次数
        'smooth_relaxation': 0.1  # 平滑松弛因子
    }

    try:
        # 步骤1: 加载并堆叠tiff切片
        load_and_stack_tiff_slices(
            masks_folder=config['masks_folder'],
            output_vtk=config['temp_files']['hole_vtk'],
            spacing=config['spacing']
        )

        # 步骤2: 填充面片孔洞
        fill_holes_in_vtk(
            input_vtk=config['temp_files']['hole_vtk'],
            output_vtk=config['temp_files']['filled_vtk'],
            hole_size=config['hole_size']
        )

        # 步骤3: 表面平滑处理
        smooth_vtk_surface(
            input_vtk=config['temp_files']['filled_vtk'],
            output_vtk=config['temp_files']['smoothed_vtk'],
            iterations=config['smooth_iterations'],
            relaxation_factor=config['smooth_relaxation']
        )

        # 步骤4: 生成连通域region字段
        generate_region_ids(
            input_vtk=config['temp_files']['smoothed_vtk'],
            output_vtk=config['final_output']
        )

        total_elapsed_time = time.time() - total_start_time
        print(f"====== 数据预处理整合流程完成 ======")
        print(f"总耗时: {total_elapsed_time:.2f}秒")
        print(f"最终结果已保存到: {config['final_output']}")

    except Exception as e:
        print(f"处理过程中发生错误: {str(e)}")


if __name__ == "__main__":
    main()
