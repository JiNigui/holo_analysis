import os
import pyvista as pv
import numpy as np
from matplotlib import pyplot as plt
from skimage import measure

# 加载现有的 .vtk 文件
vtk_file_path = 'output_with_regions.vtk'  # 替换为你的 .vtk 文件路径

# 加载 .vtk 文件
mesh = pv.read(vtk_file_path)

print(f"Mesh loaded: {mesh}")

# 创建 PyVista 数据对象
grid = pv.wrap(mesh)

# 设定一个法向量 normal 和 一个过点 origin
normal = [-0.78026193,0.37575434,-0.5]  # 目标平面的法向量，例如沿 X 轴
origin = [26.21065698,14.67418985,11.66648875]  # 目标平面上的某个点，例如选择中间的切片

# 提取切片
plane_slice = grid.slice(normal=normal, origin=origin)

# 可视化
plane_slice.plot()
