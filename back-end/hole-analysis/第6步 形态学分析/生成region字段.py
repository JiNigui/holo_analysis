import vtk

# 1. 加载 VTK 文件
print("加载 VTK 文件中...")
reader = vtk.vtkPolyDataReader()
reader.SetFileName("duanlu1.vtk")
reader.Update()
input_data = reader.GetOutput()
print(f"加载完成，点云包含 {input_data.GetNumberOfPoints()} 个点。")

# 2. 提取连通域
print("提取连通域中...")
connectivity_filter = vtk.vtkConnectivityFilter()
connectivity_filter.SetInputData(input_data)
connectivity_filter.SetExtractionModeToAllRegions()  # 提取所有连通域
connectivity_filter.ColorRegionsOn()  # 为每个连通域分配不同的颜色
connectivity_filter.Update()

# 3. 确认生成 RegionId 字段
output_data = connectivity_filter.GetOutput()
if output_data.GetCellData().HasArray("RegionId"):
    print("成功生成 RegionId 字段。")
else:
    print("未生成 RegionId 字段，可能是提取连通域的步骤有问题。")

# 4. 查看连通域数目
region_count = connectivity_filter.GetNumberOfExtractedRegions()
print(f"共检测到 {region_count} 个连通域。")

# 5. 保存连通域结果（包括 RegionId）
print("保存筛选结果中...")
writer = vtk.vtkPolyDataWriter()
writer.SetFileName("duanlu1.vtk")
writer.SetInputData(output_data)
writer.Write()

print("处理完成，结果已保存到 'duanlu1.vtk'。")



