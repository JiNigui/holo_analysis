import os
import vtk
import numpy as np
import pandas as pd
from matplotlib import rcParams

# 设置中文字体支持
rcParams['font.family'] = 'SimHei'  # 'Microsoft YaHei' 也可以
rcParams['axes.unicode_minus'] = False

# 输出目录
output_dir = "selected_regions"
os.makedirs(output_dir, exist_ok=True)

# 输出 CSV 文件路径
csv_file = os.path.join(output_dir, "duanlu1.csv")

# 1. 加载 VTK 文件
print("加载 VTK 文件...")
reader = vtk.vtkPolyDataReader()
reader.SetFileName("duanlu1_output_with_regions.vtk")
reader.Update()
polydata = reader.GetOutput()
print(f"文件加载完成，点云包含 {polydata.GetNumberOfPoints()} 个点。")

# 2. 提取连通域
print("提取连通域...")
connectivity_filter = vtk.vtkConnectivityFilter()
connectivity_filter.SetInputData(polydata)
connectivity_filter.SetExtractionModeToAllRegions()
connectivity_filter.Update()

region_count = connectivity_filter.GetNumberOfExtractedRegions()
print(f"共检测到 {region_count} 个连通域。")

# 3. 收集形态学参数（含球形度 + 三维长宽高比）
region_params = []

for i in range(region_count):
    # 提取当前连通域
    region_extractor = vtk.vtkThreshold()
    region_extractor.SetInputConnection(connectivity_filter.GetOutputPort())
    region_extractor.SetInputArrayToProcess(0, 0, 0, vtk.vtkDataObject.FIELD_ASSOCIATION_CELLS, "RegionId")
    region_extractor.SetLowerThreshold(i)
    region_extractor.SetUpperThreshold(i)
    region_extractor.Update()

    # 获取当前连通域几何数据
    geometry_filter = vtk.vtkGeometryFilter()
    geometry_filter.SetInputConnection(region_extractor.GetOutputPort())
    geometry_filter.Update()

    poly_data = geometry_filter.GetOutput()

    # 获取连通域的所有点
    points = np.array([poly_data.GetPoint(j) for j in range(poly_data.GetNumberOfPoints())])

    # 计算最小包围盒
    min_point = np.min(points, axis=0)
    max_point = np.max(points, axis=0)

    # ✅ 计算三维长宽高比
    bounding_box_lengths = max_point - min_point
    max_length = np.max(bounding_box_lengths)
    min_length = np.min(bounding_box_lengths)

    # 避免除以0
    if min_length > 0:
        aspect_ratio = max_length / min_length
    else:
        aspect_ratio = 0

    # 使用 MassProperties 计算体积和表面积
    mass_properties = vtk.vtkMassProperties()
    mass_properties.SetInputData(poly_data)
    mass_properties.Update()

    volume = mass_properties.GetVolume()
    surface_area = mass_properties.GetSurfaceArea()

    # ✅ 计算球形度
    if surface_area > 0:
        sphericity = (np.pi ** (1 / 3) * (6 * volume) ** (2 / 3)) / surface_area
        # 确保球形度在 [0, 1] 范围内
        sphericity = min(max(sphericity, 0), 1)
    else:
        sphericity = 0

    # 将参数保存到列表
    region_params.append({
        'RegionId': i,
        'Volume': volume,
        'Surface Area': surface_area,
        'Aspect Ratio': aspect_ratio,
        'Sphericity': sphericity,
        'Min Point': min_point.tolist(),
        'Max Point': max_point.tolist()
    })

# 4. 导出形态学参数到 CSV 文件
print("导出形态学参数到 CSV 文件...")
df = pd.DataFrame(region_params)
df.to_csv(csv_file, index=False)
print(f"形态学参数已保存到 {csv_file}")

# 5. 计算标准化方差（含球形度 + 三维长宽高比）
print("计算标准化方差...")

# 计算数值列的方差
numerical_columns = ['Volume', 'Surface Area', 'Aspect Ratio', 'Sphericity']
variance = df[numerical_columns].var()

# 计算每个特征的总和（用于标准化）
total_values = df[numerical_columns].sum()

# 计算标准化方差
standardized_variance = variance / total_values

# 6. 输出并追加标准化方差到 CSV
print("标准化方差计算结果（每个特征归一化到自身总和）：")
print(standardized_variance)

# 创建标准化方差数据框
std_var_df = pd.DataFrame(standardized_variance).T
std_var_df.insert(0, 'RegionId', 'Standardized Variance')

# 追加到 CSV 文件
std_var_df.to_csv(csv_file, mode='a', header=True, index=False)
print(f"标准化方差已追加到 {csv_file}")

# 7. 计算额外统计信息（含球形度 + 三维长宽高比）
print("计算额外的统计信息...")

# 体积统计
max_volume = df['Volume'].max()
min_volume = df['Volume'].min()
mean_volume = df['Volume'].mean()
median_volume = df['Volume'].median()
q25_volume = df['Volume'].quantile(0.25)
q75_volume = df['Volume'].quantile(0.75)

# 表面积统计
max_surface_area = df['Surface Area'].max()
min_surface_area = df['Surface Area'].min()
mean_surface_area = df['Surface Area'].mean()
median_surface_area = df['Surface Area'].median()
q25_surface_area = df['Surface Area'].quantile(0.25)
q75_surface_area = df['Surface Area'].quantile(0.75)

# 球形度统计
max_sphericity = df['Sphericity'].max()
min_sphericity = df['Sphericity'].min()
mean_sphericity = df['Sphericity'].mean()
median_sphericity = df['Sphericity'].median()
q25_sphericity = df['Sphericity'].quantile(0.25)
q75_sphericity = df['Sphericity'].quantile(0.75)

# 长宽高比统计
max_aspect_ratio = df['Aspect Ratio'].max()
min_aspect_ratio = df['Aspect Ratio'].min()
mean_aspect_ratio = df['Aspect Ratio'].mean()
median_aspect_ratio = df['Aspect Ratio'].median()
q25_aspect_ratio = df['Aspect Ratio'].quantile(0.25)
q75_aspect_ratio = df['Aspect Ratio'].quantile(0.75)

# 创建统计信息 DataFrame
stats_df = pd.DataFrame({
    'RegionId': ['Statistics'],  # 标识
    'Max Volume': [max_volume],
    'Min Volume': [min_volume],
    'Mean Volume': [mean_volume],
    'Median Volume': [median_volume],
    'Q25 Volume': [q25_volume],
    'Q75 Volume': [q75_volume],
    'Max Surface Area': [max_surface_area],
    'Min Surface Area': [min_surface_area],
    'Mean Surface Area': [mean_surface_area],
    'Median Surface Area': [median_surface_area],
    'Q25 Surface Area': [q25_surface_area],
    'Q75 Surface Area': [q75_surface_area],
    'Max Sphericity': [max_sphericity],
    'Min Sphericity': [min_sphericity],
    'Mean Sphericity': [mean_sphericity],
    'Median Sphericity': [median_sphericity],
    'Q25 Sphericity': [q25_sphericity],
    'Q75 Sphericity': [q75_sphericity],
    'Max Aspect Ratio': [max_aspect_ratio],
    'Min Aspect Ratio': [min_aspect_ratio],
    'Mean Aspect Ratio': [mean_aspect_ratio],
    'Median Aspect Ratio': [median_aspect_ratio],
    'Q25 Aspect Ratio': [q25_aspect_ratio],
    'Q75 Aspect Ratio': [q75_aspect_ratio]
})

# 追加统计信息到 CSV
stats_df.to_csv(csv_file, mode='a', header=True, index=False)

print(f"额外统计信息已追加到 {csv_file}")
