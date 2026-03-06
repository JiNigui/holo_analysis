import os
import sys
import imageio.v2 as imageio
import numpy as np
from skimage.filters import threshold_otsu
from skimage.color import rgb2gray
from skimage.morphology import closing, disk  # 使用闭操作去除小白点

def natural_sort_key(file_name):
    """Sort files by numeric parts of their names."""
    base_name = os.path.splitext(os.path.basename(file_name))[0]
    num_part = ''.join(filter(str.isdigit, base_name))
    return int(num_part) if num_part.isdigit() else 0

def process_images(input_folder='input', output_folder='output'):
    """处理图像二值化"""
    # 检查输入文件夹是否存在
    if not os.path.exists(input_folder):
        print(f"错误: 输入文件夹不存在: {input_folder}")
        return False
    
    # 获取所有 .tif 文件路径，并排序
    tiff_files = sorted(
        [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith('.tif')],
        key=natural_sort_key
    )
    
    if not tiff_files:
        print(f"错误: 在文件夹 {input_folder} 中未找到.tif文件")
        return False
    
    # 创建输出文件夹并清除已有文件
    if os.path.exists(output_folder):
        # 删除输出文件夹中的所有文件
        for file in os.listdir(output_folder):
            file_path = os.path.join(output_folder, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
    else:
        os.makedirs(output_folder)
    
    # 读取所有切片
    tiff_data = [imageio.imread(file) for file in tiff_files]
    
    processed_count = 0
    
    # 处理每个切片
    for idx, slice_data in enumerate(tiff_data):
        print(f"正在处理第 {idx + 1} 张切片，尺寸：{slice_data.shape}")

        # 如果是RGB图像，先转为灰度图像
        if len(slice_data.shape) == 3:
            slice_data = rgb2gray(slice_data) * 255
            slice_data = slice_data.astype(np.uint8)
            print(f"转换为灰度后尺寸：{slice_data.shape}")

        # Otsu二值化
        threshold = threshold_otsu(slice_data)
        print(f"阈值: {threshold}")
        binary_slice = slice_data >= threshold  # 白色背景为True，黑色孔洞为False

        # ---- 形态学闭操作：去除小白点噪声 ----
        selem = disk(2)  # 可调：disk(3) 或 disk(4)
        cleaned_slice = closing(binary_slice, selem)

        # 反转图像（前景变白，背景变黑）并保存
        binary_image_path = os.path.join(output_folder, f'binary_slice_{idx + 1}.tiff')
        imageio.imwrite(binary_image_path, (~cleaned_slice * 255).astype(np.uint8))

        print(f"第 {idx + 1} 张切片处理完成，保存至 {binary_image_path}\n")
        processed_count += 1
    
    print(f"处理完成，共处理 {processed_count} 张切片")
    return True

def main():
    """主函数，支持命令行参数"""
    # 默认参数
    input_folder = 'input'
    output_folder = 'output'
    
    # 解析命令行参数
    if len(sys.argv) > 1:
        input_folder = sys.argv[1]
    if len(sys.argv) > 2:
        output_folder = sys.argv[2]
    
    print(f"开始图像二值化处理...")
    print(f"输入文件夹: {input_folder}")
    print(f"输出文件夹: {output_folder}")
    
    success = process_images(input_folder, output_folder)
    
    if success:
        print("图像二值化处理成功完成")
        sys.exit(0)
    else:
        print("图像二值化处理失败")
        sys.exit(1)

if __name__ == "__main__":
    main()
