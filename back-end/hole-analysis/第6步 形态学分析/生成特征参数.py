import os
import vtk
import numpy as np
import pandas as pd
from matplotlib import rcParams

# 设置支持中文的字体
rcParams['font.family'] = 'SimHei'  # 或者 'Microsoft YaHei'
rcParams['axes.unicode_minus'] = False  # 处理负号显示问题

# 输出目录
output_dir = "selected_regions"
os.makedirs(output_dir, exist_ok=True)  # 确保输出目录存在

# 输出 CSV 文件路径
csv_file = os.path.join(output_dir, "1.csv")

# 1. 加载 VTK 文件
print("加载 VTK 文件...")
reader = vtk.vtkPolyDataReader()
reader.SetFileName("output_with_regions.vtk")  # 输入文件
reader.Update()
polydata = reader.GetOutput()
print(f"文件加载完成，点云包含 {polydata.GetNumberOfPoints()} 个点。")

# 2. 提取连通域
print("提取连通域...")
connectivity_filter = vtk.vtkConnectivityFilter()
connectivity_filter.SetInputData(polydata)
connectivity_filter.SetExtractionModeToAllRegions()  # 提取所有连通域
connectivity_filter.Update()

region_count = connectivity_filter.GetNumberOfExtractedRegions()
print(f"共检测到 {region_count} 个连通域。")

# 3. 收集每个连通域的形态学参数
region_params = []

for i in range(region_count):
    # 提取当前连通域
    region_extractor = vtk.vtkThreshold()
    region_extractor.SetInputConnection(connectivity_filter.GetOutputPort())
    region_extractor.SetInputArrayToProcess(
        0, 0, 0, vtk.vtkDataObject.FIELD_ASSOCIATION_CELLS, "RegionId"
    )
    region_extractor.SetLowerThreshold(i)
    region_extractor.SetUpperThreshold(i)
    region_extractor.Update()

    # 获取当前连通域的几何数据
    geometry_filter = vtk.vtkGeometryFilter()
    geometry_filter.SetInputConnection(region_extractor.GetOutputPort())
    geometry_filter.Update()

    poly_data = geometry_filter.GetOutput()

    # 获取连通域的所有点
    points = np.array([poly_data.GetPoint(j) for j in range(poly_data.GetNumberOfPoints())])

    # 计算最小包围盒
    min_point = np.min(points, axis=0)
    max_point = np.max(points, axis=0)

    # 计算长宽比
    aspect_ratio = (max_point[0] - min_point[0]) / (max_point[1] - min_point[1])

    # 使用 MassProperties 计算体积和表面积
    mass_properties = vtk.vtkMassProperties()
    mass_properties.SetInputData(poly_data)
    mass_properties.Update()

    volume = mass_properties.GetVolume()
    surface_area = mass_properties.GetSurfaceArea()

    # 将计算出的参数保存到列表中
    region_params.append({
        'RegionId': i,
        'Volume': volume,
        'Surface Area': surface_area,
        'Aspect Ratio': aspect_ratio,
        'Min Point': min_point,
        'Max Point': max_point
    })

# 4. 导出为 CSV 文件
print("导出形态学参数到 CSV 文件...")
df = pd.DataFrame(region_params)
df.to_csv(csv_file, index=False)
print(f"形态学参数已保存到 {csv_file}")

# 5. 计算各个值的方差
print("计算方差...")
variances = df[['Volume', 'Surface Area', 'Aspect Ratio']].var()
print("方差计算完成：")
print(variances)
