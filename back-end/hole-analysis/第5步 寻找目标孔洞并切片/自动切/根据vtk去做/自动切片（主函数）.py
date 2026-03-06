import os
import vtk
import numpy as np
import json
import datetime
import argparse

def main():
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='自动切片主函数')
    parser.add_argument('--input-file', type=str, required=True,
                       help='输入VTK文件路径')
    parser.add_argument('--output-dir', type=str, required=True,
                       help='输出目录路径')
    
    args = parser.parse_args()
    
    print("====== 自动切片流程开始 ======")
    print(f"输入文件: {args.input_file}")
    print(f"输出目录: {args.output_dir}")
    
    # 检查输入文件是否存在
    if not os.path.exists(args.input_file):
        print(f"错误: 输入文件不存在: {args.input_file}")
        exit(1)
    
    # 确保输出目录存在
    os.makedirs(args.output_dir, exist_ok=True)
    
    # 进度文件路径（使用动态输出目录）
    progress_file_path = os.path.join(args.output_dir, 'progress_status.json')

    def update_progress(progress, status, message):
        """更新进度信息到进度文件"""
        progress_data = {
            "progress": progress,
            "status": status,
            "message": message,
            "timestamp": datetime.datetime.now().isoformat()
        }
        with open(progress_file_path, 'w', encoding='utf-8') as f:
            json.dump(progress_data, f, ensure_ascii=False)
        print(f"进度更新: {progress}% - {status}: {message}")

    # 1. 加载 VTK 文件
    print("加载 VTK 文件...")
    reader = vtk.vtkPolyDataReader()
    reader.SetFileName(args.input_file)  # 使用动态输入文件路径
    reader.Update()
    polydata = reader.GetOutput()
    print(f"文件加载完成，点云包含 {polydata.GetNumberOfPoints()} 个点。")

    # 步骤2 (30%)：VTK文件加载完成后
    update_progress(30, "VTK文件加载完成", f"VTK文件加载完成，共包含{polydata.GetNumberOfPoints()}个点")

    # 2. 提取连通域
    print("提取连通域...")
    connectivity_filter = vtk.vtkConnectivityFilter()
    connectivity_filter.SetInputData(polydata)
    connectivity_filter.SetExtractionModeToAllRegions()  # 提取所有连通域
    connectivity_filter.ColorRegionsOn()  # 为每个区域着色
    connectivity_filter.Update()

    region_count = connectivity_filter.GetNumberOfExtractedRegions()
    print(f"共检测到 {region_count} 个连通域。")

    # 步骤3 (50%)：连通域提取完成后
    update_progress(50, "连通域提取完成", f"共检测到{region_count}个连通域")

    # 3. 找到最大连通域（修复：使用替代方法获取区域大小）
    largest_region_id = None  # 最大连通域的 ID
    largest_region_cells = 0  # 最大连通域的单元格数量

    # 修复：创建一个更高效的方法来查找最大连通域
    # 先获取区域ID数组
    region_ids = connectivity_filter.GetOutput().GetCellData().GetArray("RegionId")

    # 计算每个区域的单元格数量（比原代码更高效）
    region_sizes = np.zeros(region_count, dtype=int)
    for i in range(region_ids.GetNumberOfTuples()):
        region_id = int(region_ids.GetTuple1(i))
        region_sizes[region_id] += 1

    # 找到最大连通域
    largest_region_id = np.argmax(region_sizes)
    largest_region_points = region_sizes[largest_region_id]

    # 只提取最大连通域进行后续处理（优化点：避免处理所有连通域）
    region_extractor = vtk.vtkThreshold()
    region_extractor.SetInputConnection(connectivity_filter.GetOutputPort())
    region_extractor.SetInputArrayToProcess(
        0, 0, 0, vtk.vtkDataObject.FIELD_ASSOCIATION_CELLS, "RegionId"
    )
    region_extractor.SetLowerThreshold(largest_region_id)
    region_extractor.SetUpperThreshold(largest_region_id)
    region_extractor.Update()

    # 获取最大连通域的几何数据
    geometry_filter = vtk.vtkGeometryFilter()
    geometry_filter.SetInputConnection(region_extractor.GetOutputPort())
    geometry_filter.Update()

    largest_poly_data = geometry_filter.GetOutput()

    # 计算几何中心（优化点：使用vtkCenterOfMass直接计算）
    center_filter = vtk.vtkCenterOfMass()
    center_filter.SetInputData(largest_poly_data)
    center_filter.SetUseScalarsAsWeights(False)
    center_filter.Update()
    largest_region_centroid = center_filter.GetCenter()

    print(f"最大连通域 ID: {largest_region_id}, 单元格数量: {largest_region_points}")
    print(f"最大连通域的几何中心坐标: {largest_region_centroid}")

    # 步骤4 (70%)：最大连通域找到后
    update_progress(70, "最大连通域已找到", f"最大连通域ID: {largest_region_id}, 包含{largest_region_points}个单元格")

    # 4. 在最大连通域的几何中心设置切割平面
    normal = (0, 0, 1)  # 法向量
    origin = largest_region_centroid  # 平面原点为最大连通域的几何中心

    # 5. 计算最大截面（优化点：减少平面数量、重用过滤器实例）
    print("计算最大截面...")
    max_area = 0
    best_plane = None

    # 创建可重用的过滤器实例（优化点：避免重复创建过滤器）
    clipper = vtk.vtkClipPolyData()
    clipper.SetInputData(largest_poly_data)  # 只对最大连通域操作
    clipper.SetClipFunction(vtk.vtkPlane())

    mass_properties = vtk.vtkMassProperties()

    # 减少测试平面的数量，使用更智能的采样（优化点：减少循环次数）
    for angle in np.linspace(0, np.pi, 90):  # 减少到90个角度
        # 使用vtkTransform旋转法向量
        transform = vtk.vtkTransform()
        transform.RotateWXYZ(np.degrees(angle), normal[0], normal[1], normal[2])
        
        # 旋转后的法向量
        rotated_normal = np.array(transform.GetMatrix().MultiplyPoint(np.array([normal[0], normal[1], normal[2], 0]))[:3])
        
        # 进行切割
        clipper.GetClipFunction().SetNormal(rotated_normal)
        clipper.GetClipFunction().SetOrigin(origin)
        clipper.Update()
        
        clipped_polydata = clipper.GetOutput()
        
        # 使用vtkMassProperties计算截面面积
        mass_properties.SetInputData(clipped_polydata)
        mass_properties.Update()
        
        # 获取截面面积
        area = mass_properties.GetSurfaceArea()
        
        # 更新最大截面
        if area > max_area:
            max_area = area
            best_plane = rotated_normal

    # 输出最大截面信息
    print(f"最大截面面积: {max_area}, 最佳平面法向量: {best_plane}")

    # 可选：如果需要更精确的结果，可以在找到的最佳角度附近进行细粒度搜索
    if best_plane is not None:
        print("进行细粒度搜索以提高精度...")
        # 找到最佳角度的索引
        best_angle_index = np.where(np.linspace(0, np.pi, 90) == np.arccos(np.dot(best_plane, normal)/np.linalg.norm(best_plane)))[0][0]
        
        # 在最佳角度附近创建更细的角度范围
        start_angle = max(0, best_angle_index - 2)
        end_angle = min(89, best_angle_index + 2)
        
        # 使用更细的角度步长
        for angle in np.linspace(np.linspace(0, np.pi, 90)[start_angle], np.linspace(0, np.pi, 90)[end_angle], 10):
            transform = vtk.vtkTransform()
            transform.RotateWXYZ(np.degrees(angle), normal[0], normal[1], normal[2])
            
            rotated_normal = np.array(transform.GetMatrix().MultiplyPoint(np.array([normal[0], normal[1], normal[2], 0]))[:3])
            
            clipper.GetClipFunction().SetNormal(rotated_normal)
            clipper.GetClipFunction().SetOrigin(origin)
            clipper.Update()
            
            clipped_polydata = clipper.GetOutput()
            mass_properties.SetInputData(clipped_polydata)
            mass_properties.Update()
            
            area = mass_properties.GetSurfaceArea()
            
            if area > max_area:
                max_area = area
                best_plane = rotated_normal

    print(f"优化后最大截面面积: {max_area}, 最佳平面法向量: {best_plane}")

    # 6. 生成 combined_selected_regions.vtk 文件（包含筛选后的目标孔洞）
    print("生成 combined_selected_regions.vtk 文件...")

    # 方法1：直接保存最大连通域（使用动态输出目录）
    combined_vtk_path = os.path.join(args.output_dir, 'combined_selected_regions.vtk')
    writer = vtk.vtkPolyDataWriter()
    writer.SetFileName(combined_vtk_path)
    writer.SetInputData(largest_poly_data)
    writer.Write()

    print("combined_selected_regions.vtk 文件生成完成！")
    print(f"文件保存路径: {combined_vtk_path}")

    # 步骤5 (90%)：切片数据生成后
    update_progress(90, "切片数据生成完成", "combined_selected_regions.vtk文件已生成")

    # 输出结构化参数供其他脚本使用
    result_data = {
        'max_area': float(max_area),
        'best_plane': best_plane.tolist() if best_plane is not None else None,
        'centroid': [float(x) for x in largest_region_centroid],
        'largest_region_id': int(largest_region_id),
        'largest_region_points': int(largest_region_points),
        'combined_file_path': combined_vtk_path
    }

    # 可选：保存参数到JSON文件供其他脚本使用（使用动态输出目录）
    analysis_params_path = os.path.join(args.output_dir, 'analysis_parameters.json')
    with open(analysis_params_path, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, indent=2, ensure_ascii=False)

    print("分析参数已保存到 analysis_parameters.json")
    print("\n=== 分析完成 ===")
    print(f"最大连通域ID: {largest_region_id}")
    print(f"几何中心: {largest_region_centroid}")
    print(f"最大截面面积: {max_area}")
    print(f"最佳平面法向量: {best_plane}")
    print(f"筛选文件: {combined_vtk_path}")
    
    # 第五步主函数完成，保持90%进度，等待后端API调用可视化脚本
    print("第五步主函数已完成，等待后端API调用可视化脚本生成PNG图像...")

if __name__ == "__main__":
    main()