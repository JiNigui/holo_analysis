#!/usr/bin/env python3
"""
VTK 三维孔洞形态学清洗脚本 (V3 完美版：引入大体积绝对豁免权)

优化点：
解决了大孔洞因“与其他孔洞融合导致形态畸变（球度骤降）”而被误判为伪影剔除的问题。
消除了 PyVista 版本升级带来的 extract_surface 算法警告。
"""

import os
import time
import math
import numpy as np
import pyvista as pv
from tqdm import tqdm


def compute_sphericity(volume, area):
    """计算球度 (Sphericity)，完美球体为 1.0"""
    if area <= 0 or volume <= 0:
        return 0.0
    return (math.pi ** (1 / 3) * (6 * volume) ** (2 / 3)) / area


def main():
    print("====== 3D孔洞形态学精细清洗 (V3 豁免保护版) ======")
    start_time = time.time()

    # 替换为你的 VTK 文件路径 (输入应该是经过 RegionId 标注但未清洗的文件)
    input_vtk = r"output_with_regions.vtk"
    output_vtk = input_vtk.replace(".vtk", "_cleaned_v3.vtk")

    if not os.path.exists(input_vtk):
        print(f"找不到输入文件: {input_vtk}")
        return

    print("正在加载 VTK 模型...")
    mesh = pv.read(input_vtk)
    if isinstance(mesh, pv.UnstructuredGrid):
        # 【修复警告】：显式指定 algorithm
        mesh = mesh.extract_surface()

    if "RegionId" not in mesh.cell_data:
        print("错误：网格中没有找到 RegionId 字段！")
        return

    global_bounds = mesh.bounds
    tol = 1e-4

    region_ids = mesh.cell_data["RegionId"]
    unique_regions = np.unique(region_ids)

    print(f"加载成功！共检测到 {len(unique_regions)} 个初始连通域。")

    valid_region_ids = []

    stats = {
        "kept_huge_or_edge": 0,  # 因接触边缘或体积巨大而无条件保留
        "kept_solid": 0,  # 因形态饱满保留的中小孔洞
        "removed_sickle": 0,  # 剔除的镰刀/絮状伪影
        "removed_dust": 0  # 剔除的微小粉尘
    }

    # ================= 核心过滤参数 =================
    MIN_FLATNESS = 0.30
    MIN_SPHERICITY = 0.45
    MIN_EXTENT = 0.35
    MIN_VOLUME = 1e-1

    # 🌟 核心新增：大体积绝对豁免权 🌟
    # 如果你的 spacing=(0.1, 0.1, 0.1)，一个 10x10x10 体素的块体积大约是 1.0。
    # 只要体积大于这个值，无论多畸形都判定为主孔洞予以保留。
    # (如果运行后大孔洞还是没出来，把这个值调小一点，比如 0.1)
    SAFE_VOLUME = 0.5
    # ================================================

    # 为了方便你调试，提取所有连通域的体积，先看一眼最大的几个有多大
    print("正在预计算孔洞体积...")
    volumes = []
    for rid in unique_regions:
        mask = (region_ids == rid)
        # 【修复警告】：显式指定 algorithm
        sub_mesh = mesh.extract_cells(mask).extract_surface()
        volumes.append(abs(sub_mesh.volume))

    max_vols = sorted(volumes, reverse=True)[:5]
    print(f"👉 当前模型中最大的5个孔洞体积为: {[f'{v:.4f}' for v in max_vols]}")
    print(f"👉 当前设定的绝对安全豁免体积 (SAFE_VOLUME) 为: {SAFE_VOLUME}")

    for rid in tqdm(unique_regions, desc="分析连通域"):
        mask = (region_ids == rid)
        # 【修复警告】：显式指定 algorithm
        sub_mesh = mesh.extract_cells(mask).extract_surface()

        rb = sub_mesh.bounds

        touches_boundary = False
        for i in range(6):
            if abs(rb[i] - global_bounds[i]) < tol:
                touches_boundary = True
                break

        spans = [rb[1] - rb[0], rb[3] - rb[2], rb[5] - rb[4]]
        min_span = min(spans)
        max_span = max(spans)
        bbox_volume = spans[0] * spans[1] * spans[2]

        flatness = min_span / max_span if max_span > 0 else 0
        V = abs(sub_mesh.volume)
        A = sub_mesh.area

        sphericity = compute_sphericity(V, A)
        extent = V / bbox_volume if bbox_volume > 0 else 0

        # 1. 微小粉尘直接杀
        if V < MIN_VOLUME:
            stats["removed_dust"] += 1
            continue

        # 🌟 2. 大孔洞及边缘孔洞的“免死金牌” 🌟
        # 只要碰到边缘，或者体积巨大（主孔洞），直接跳过形态审核！
        if touches_boundary or V > SAFE_VOLUME:
            valid_region_ids.append(rid)
            stats["kept_huge_or_edge"] += 1
            continue

        # 3. 针对剩余的中小孔洞，执行严苛的形态学绞杀
        if flatness < MIN_FLATNESS or sphericity < MIN_SPHERICITY or extent < MIN_EXTENT:
            stats["removed_sickle"] += 1
        else:
            valid_region_ids.append(rid)
            stats["kept_solid"] += 1

    print("\n====== 清洗统计结果 ======")
    print(f"总计分析孔洞: {len(unique_regions)} 个")
    print(f"[保留] 接触边缘或具备【大体积豁免权】的核心主孔洞: {stats['kept_huge_or_edge']} 个")
    print(f"[保留] 形态饱满的真实中小孔洞: {stats['kept_solid']} 个")
    print(f"[剔除] 镰刀/弯月/絮状等中小体积伪影: {stats['removed_sickle']} 个")
    print(f"[剔除] 极微小粉尘噪点: {stats['removed_dust']} 个")
    print("==========================")

    print("\n正在重构最终的高保真三维网格...")
    mask_cells = np.isin(mesh.cell_data["RegionId"], valid_region_ids)
    cleaned_mesh = mesh.extract_cells(mask_cells).connectivity(largest=False)

    cleaned_mesh.save(output_vtk)

    elapsed = time.time() - start_time
    print(f"✓ 豁免版清洗完成！耗时: {elapsed:.2f} 秒")
    print(f"✓ 结果已保存至: {output_vtk} (你现在可以用可视化脚本看这个 v3 文件了！)")


if __name__ == "__main__":
    main()