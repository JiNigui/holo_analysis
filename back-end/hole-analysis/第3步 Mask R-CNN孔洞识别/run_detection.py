#!/usr/bin/env python3
"""
孔洞检测综合脚本 (基于 U-Net 与 DeepLabV3+ 的双模型融合架构)

整合 U-Net 和 DeepLabV3+ 的检测流程，一次性完成批量推理：
1. U-Net 推理 - 高分辨率局部特征提取，保留极微小气孔
2. DeepLabV3+ 推理 - 多尺度全局语境感知，提供宏观高置信度底座
3. 条件补充融合 - 通过“双向物理尺度过滤”截断误检，并融合两者优势
4. 形态学后处理 - 先闭后开，平滑边界并还原物理形貌
"""

import os
import sys
import warnings
import torch
import concurrent.futures
import numpy as np
import tifffile
import cv2
from tqdm import tqdm
import re
import segmentation_models_pytorch as smp

warnings.filterwarnings("ignore", category=FutureWarning)
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# 将当前脚本目录加入路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class DualModelDetector:
    def __init__(self, unet_path, deeplab_path, device, img_size=(512, 512), threshold=0.3):
        self.device = device
        self.img_size = img_size
        self.threshold = threshold

        # 物理尺度过滤参数 (与 fusion_new 保持一致)
        self.min_area_tau = 3
        self.max_area_tau = 50

        print("正在加载 U-Net 模型...")
        self.unet = self._load_model(unet_path)
        print("正在加载 DeepLabV3+ 模型...")
        self.deeplab = self._load_model(deeplab_path)

    def _load_model(self, model_path):
        model = smp.Unet(
            encoder_name="resnet34",
            encoder_weights=None,
            in_channels=3,
            classes=1
        ).to(self.device) if 'unet' in model_path.lower() else \
            smp.DeepLabV3Plus(
                encoder_name="resnet34",
                encoder_weights=None,
                in_channels=3,
                classes=1
            ).to(self.device)

        model.load_state_dict(torch.load(model_path, map_location=self.device, weights_only=False))
        model.eval()
        return model

    def preprocess(self, img):
        """输入预处理：调整尺寸、通道扩展、标准化"""
        img_resized = cv2.resize(img, self.img_size)
        img_stack = np.stack([img_resized] * 3, axis=-1)
        img_norm = img_stack / 255.0
        mean = np.array([0.485, 0.456, 0.406])
        std = np.array([0.229, 0.224, 0.225])
        img_norm = (img_norm - mean) / std
        img_tensor = img_norm.transpose(2, 0, 1)
        return torch.tensor(img_tensor, dtype=torch.float32).unsqueeze(0).to(self.device)

    def detect_and_fuse(self, img_gray):
        """单张图像的推理与融合核心逻辑"""
        orig_size = (img_gray.shape[1], img_gray.shape[0])
        input_tensor = self.preprocess(img_gray)

        # 1. 双模型推理
        with torch.no_grad():
            logits_unet = self.unet(input_tensor)
            pred_unet = torch.sigmoid(logits_unet).cpu().squeeze().numpy()

            logits_deeplab = self.deeplab(input_tensor)
            pred_deeplab = torch.sigmoid(logits_deeplab).cpu().squeeze().numpy()

        # 2. 尺寸还原与二值化基础掩膜
        pred_unet_resized = cv2.resize(pred_unet, orig_size)
        pred_deeplab_resized = cv2.resize(pred_deeplab, orig_size)

        hole_unet = (pred_unet_resized > self.threshold)
        hole_deeplab = (pred_deeplab_resized > self.threshold)

        # 3. 差异区域提取 (U-Net独有区域)
        diff_mask = hole_unet & (~hole_deeplab)

        # 4. 双向物理尺度过滤
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(diff_mask.astype(np.uint8),
                                                                                connectivity=8)
        supp_mask = np.zeros_like(diff_mask, dtype=bool)

        for i in range(1, num_labels):
            area = stats[i, cv2.CC_STAT_AREA]
            if self.min_area_tau <= area <= self.max_area_tau:
                supp_mask[labels == i] = True

        # 5. 条件补充融合
        fused_mask = hole_deeplab | supp_mask

        # 6. 形态学后处理 (先闭后开)
        fused_img_255 = (fused_mask.astype(np.uint8) * 255)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        closed_mask = cv2.morphologyEx(fused_img_255, cv2.MORPH_CLOSE, kernel)
        final_morph_mask = cv2.morphologyEx(closed_mask, cv2.MORPH_OPEN, kernel)

        # 7. 格式对齐 (根据 fusion_new.py 逻辑，孔洞=0，背景=255)
        final_output = np.where(final_morph_mask == 255, 0, 255).astype(np.uint8)
        return final_output


class HoleDetectionProcessor:
    def __init__(self, unet_path, deeplab_path, input_folder, output_folder, img_size=(512, 512)):
        self.input_folder = input_folder
        self.output_folder = output_folder
        os.makedirs(output_folder, exist_ok=True)

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"使用计算设备: {self.device}")

        self.detector = DualModelDetector(unet_path, deeplab_path, self.device, img_size)

        # 读取并按切片序号排序
        self.image_files = [f for f in os.listdir(input_folder) if f.endswith(('.tiff', '.tif'))]
        self.image_files = sorted(self.image_files,
                                  key=lambda x: int(re.findall(r'\d+', x)[-1]) if re.findall(r'\d+', x) else 0)

        self.success_count = 0
        self.fail_count = 0

    def process_single_image(self, image_file):
        try:
            image_path = os.path.join(self.input_folder, image_file)
            img = tifffile.imread(image_path)

            # 统一转为灰度图
            if len(img.shape) == 3 and img.shape[2] == 3:
                img_gray = np.mean(img, axis=2).astype(img.dtype)
            elif len(img.shape) == 3:
                img_gray = img[0] if img.shape[0] < img.shape[-1] else img[:, :, 0]
            else:
                img_gray = img

            base_name = os.path.splitext(image_file)[0]

            # 核心融合检测
            fused_mask = self.detector.detect_and_fuse(img_gray)

            # 保存结果
            fused_output_path = os.path.join(self.output_folder, f"{base_name}_fused_mask.tiff")
            tifffile.imwrite(fused_output_path, fused_mask)

            return True, image_file

        except Exception as e:
            print(f"\n处理图像 {image_file} 时出错: {str(e)}")
            return False, image_file

    def process_batch(self, max_workers=None):
        if not self.image_files:
            print("输入目录中没有找到 TIFF 文件。")
            return

        # 如果使用 GPU，建议控制并发数以防显存 OOM
        if max_workers is None:
            max_workers = 2 if torch.cuda.is_available() else min(4, os.cpu_count() or 4)

        print(f"\n开始处理 {len(self.image_files)} 张图像，使用 {max_workers} 个线程...")

        # 进度条与多线程处理
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self.process_single_image, f) for f in self.image_files]
            for future in tqdm(concurrent.futures.as_completed(futures), total=len(self.image_files)):
                success, _ = future.result()
                if success:
                    self.success_count += 1
                else:
                    self.fail_count += 1

        print(f"\n=== 批量分割检测完成 ===")
        print(f"成功: {self.success_count}, 失败: {self.fail_count}")
        print(f"结果已保存至: {self.output_folder}")


def main():
    import argparse
    
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='孔洞检测综合脚本')
    parser.add_argument('--input-dir', required=True, help='输入目录路径')
    parser.add_argument('--output-dir', required=True, help='输出目录路径')
    parser.add_argument('--unet-model', required=True, help='UNet模型文件路径')
    parser.add_argument('--deeplab-model', required=True, help='DeepLabV3+模型文件路径')
    
    args = parser.parse_args()
    
    # 使用命令行参数
    unet_model_path = args.unet_model
    deeplab_model_path = args.deeplab_model
    input_folder = args.input_dir
    output_folder = args.output_dir

    print("=== 孔洞批量检测综合配置 (融合版) ===")
    print(f"U-Net 权重路径: {unet_model_path}")
    print(f"DeepLabV3+ 权重路径: {deeplab_model_path}")
    print(f"输入目录 (VOI): {input_folder}")
    print(f"输出目录 (检测): {output_folder}")
    print("=====================================\n")

    if not os.path.exists(unet_model_path):
        print(f"错误：U-Net 模型文件不存在: {unet_model_path}")
        return

    if not os.path.exists(deeplab_model_path):
        print(f"错误：DeepLabV3+ 模型文件不存在: {deeplab_model_path}")
        return

    if not os.path.exists(input_folder):
        print(f"错误：输入目录不存在: {input_folder}")
        print("请先运行 VOI 提取脚本 (run_voi.py)")
        return

    processor = HoleDetectionProcessor(
        unet_path=unet_model_path,
        deeplab_path=deeplab_model_path,
        input_folder=input_folder,
        output_folder=output_folder,
        img_size=(512, 512)
    )

    processor.process_batch()


if __name__ == "__main__":
    main()