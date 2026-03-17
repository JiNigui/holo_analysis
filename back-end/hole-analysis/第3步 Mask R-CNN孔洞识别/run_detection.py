#!/usr/bin/env python3
"""
孔洞检测综合脚本

整合UNet和Mask R-CNN的检测流程，一次性完成：
1. UNet检测 - 对边缘部分和小孔洞的检测效果更好
2. Mask R-CNN检测 - 对大空洞的检测比较好
3. 模型融合 - 结合两者的优势
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
import os
import torch
import concurrent.futures
import numpy as np
import tifffile
import cv2
from tqdm import tqdm
import re
import segmentation_models_pytorch as smp
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2 import model_zoo

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"


class UNetDetector:
    def __init__(self, model_path, img_size=(512, 512), threshold=0.3):
        self.img_size = img_size
        self.threshold = threshold
        self.model = self._initialize_model(model_path)

    def _initialize_model(self, model_path):
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = smp.Unet(
            encoder_name="resnet34",
            encoder_weights=None,
            in_channels=3,
            classes=1
        ).to(device)
        model.load_state_dict(torch.load(model_path, map_location=device, weights_only=False))
        model.eval()
        return model

    def preprocess(self, img):
        img = np.array(img, dtype=np.float32)
        img = cv2.resize(img, self.img_size)
        img = np.stack([img] * 3, axis=-1)
        img = img / 255.0
        mean = np.array([0.485, 0.456, 0.406])
        std = np.array([0.229, 0.224, 0.225])
        img = (img - mean) / std
        img = img.transpose(2, 0, 1)
        return torch.tensor(img, dtype=torch.float32).unsqueeze(0)

    def detect(self, img):
        if len(img.shape) == 3:
            img = img[:, :, 0]
        orig_size = (img.shape[1], img.shape[0])

        input_tensor = self.preprocess(img).to(next(self.model.parameters()).device)

        with torch.no_grad():
            logits = self.model(input_tensor)
            pred = torch.sigmoid(logits).cpu().squeeze().numpy()

        pred_bin = (pred > self.threshold).astype(np.uint8) * 255
        pred_bin = cv2.resize(pred_bin, orig_size)
        return pred_bin


class MaskRCNNDetector:
    def __init__(self, model_path, confidence_threshold=0.9, num_classes=1):
        self.predictor = self._initialize_predictor(model_path, confidence_threshold, num_classes)

    def _initialize_predictor(self, model_path, confidence_threshold, num_classes):
        cfg = get_cfg()
        cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
        cfg.MODEL.WEIGHTS = model_path
        cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = confidence_threshold
        cfg.MODEL.ROI_HEADS.NUM_CLASSES = num_classes
        cfg.MODEL.DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
        if torch.cuda.is_available():
            cfg.MODEL.PIXEL_MEAN = [103.530, 116.280, 123.675]
        return DefaultPredictor(cfg)

    def detect(self, img):
        if len(img.shape) == 2:
            img = np.expand_dims(img, axis=-1)

        predictions = self.predictor(img)
        masks = predictions["instances"].pred_masks.cpu().numpy()

        mask_only_img = np.zeros(img.shape[:2], dtype=np.uint8)
        for mask in masks:
            mask = mask.astype(np.uint8) * 255
            mask_only_img[mask == 255] = 255

        return mask_only_img


class HoleDetectionProcessor:
    def __init__(self, unet_model_path, maskrcnn_model_path, input_folder, output_folder,
                 unet_threshold=0.3, maskrcnn_confidence=0.9, img_size=(512, 512)):
        self.input_folder = input_folder
        self.output_folder = output_folder

        os.makedirs(output_folder, exist_ok=True)

        self.unet_detector = UNetDetector(unet_model_path, img_size, unet_threshold)
        self.maskrcnn_detector = MaskRCNNDetector(maskrcnn_model_path, maskrcnn_confidence)

        self.image_files = [f for f in os.listdir(input_folder) if f.endswith('.tiff')]
        self.image_files = sorted(self.image_files, key=lambda x: int(re.findall(r'\d+', x)[-1]))

        self.success_count = 0
        self.fail_count = 0

    def fuse_masks(self, unet_mask, maskrcnn_mask):
        unet_mask = unet_mask.astype(np.uint8)
        maskrcnn_mask = maskrcnn_mask.astype(np.uint8)

        unet_binary = (unet_mask > 127).astype(np.uint8)
        maskrcnn_binary = (maskrcnn_mask > 127).astype(np.uint8)

        fused_mask = unet_binary | maskrcnn_binary

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        fused_mask = cv2.morphologyEx(fused_mask, cv2.MORPH_CLOSE, kernel)
        fused_mask = cv2.morphologyEx(fused_mask, cv2.MORPH_OPEN, kernel)

        return fused_mask * 255

    def process_single_image(self, image_file):
        try:
            image_path = os.path.join(self.input_folder, image_file)
            img = tifffile.imread(image_path)

            if len(img.shape) == 3:
                img = img[:, :, 0]

            base_name = os.path.splitext(image_file)[0]

            unet_mask = self.unet_detector.detect(img)

            if len(img.shape) == 2:
                img_3d = np.expand_dims(img, axis=-1)
            else:
                img_3d = img

            maskrcnn_mask = self.maskrcnn_detector.detect(img_3d)

            if unet_mask.shape != maskrcnn_mask.shape:
                maskrcnn_mask = cv2.resize(maskrcnn_mask, (unet_mask.shape[1], unet_mask.shape[0]))

            fused_mask = self.fuse_masks(unet_mask, maskrcnn_mask)
            fused_output_path = os.path.join(self.output_folder, f"{base_name}_fused_mask.tiff")
            tifffile.imwrite(fused_output_path, fused_mask)
            self.success_count += 1

            return True, image_file

        except Exception as e:
            print(f"处理图像 {image_file} 时出错: {str(e)}")
            self.fail_count += 1
            return False, image_file

    def process_batch(self, max_workers=None):
        if max_workers is None:
            max_workers = min(4, os.cpu_count() or 4)

        print(f"开始处理 {len(self.image_files)} 张图像，使用 {max_workers} 个线程...")

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(tqdm(executor.map(self.process_single_image, self.image_files), total=len(self.image_files)))

        print(f"\n=== 检测完成 ===")
        print(f"成功: {self.success_count}, 失败: {self.fail_count}")


def main():
    import argparse
    
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='孔洞检测综合脚本')
    parser.add_argument('--input-dir', required=True, help='输入目录路径（包含TIFF文件）')
    parser.add_argument('--output-dir', required=True, help='输出目录路径（保存掩码文件）')
    parser.add_argument('--unet-model', default='unet.pth', help='UNet模型文件路径')
    parser.add_argument('--maskrcnn-model', default='model_final.pth', help='Mask R-CNN模型文件路径')
    parser.add_argument('--unet-threshold', type=float, default=0.3, help='UNet检测阈值')
    parser.add_argument('--maskrcnn-confidence', type=float, default=0.9, help='Mask R-CNN置信度阈值')
    
    args = parser.parse_args()
    
    # 使用绝对路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    unet_model_path = os.path.abspath(args.unet_model)
    maskrcnn_model_path = os.path.abspath(args.maskrcnn_model)
    input_folder = os.path.abspath(args.input_dir)
    output_folder = os.path.abspath(args.output_dir)
    
    print("=== 孔洞检测综合配置 ===")
    print(f"UNet模型: {unet_model_path}")
    print(f"Mask R-CNN模型: {maskrcnn_model_path}")
    print(f"输入目录: {input_folder}")
    print(f"输出目录: {output_folder}")
    print(f"UNet阈值: {args.unet_threshold}")
    print(f"Mask R-CNN置信度: {args.maskrcnn_confidence}")
    print("========================\n")

    # 检查文件存在性
    if not os.path.exists(unet_model_path):
        print(f"错误：UNet模型不存在: {unet_model_path}")
        return

    if not os.path.exists(maskrcnn_model_path):
        print(f"错误：Mask R-CNN模型不存在: {maskrcnn_model_path}")
        return

    if not os.path.exists(input_folder):
        print(f"错误：输入目录不存在: {input_folder}")
        return

    # 创建处理器并执行
    processor = HoleDetectionProcessor(
        unet_model_path=unet_model_path,
        maskrcnn_model_path=maskrcnn_model_path,
        input_folder=input_folder,
        output_folder=output_folder,
        unet_threshold=args.unet_threshold,
        maskrcnn_confidence=args.maskrcnn_confidence,
        img_size=(512, 512)
    )
    
    processor.process_batch()


if __name__ == "__main__":
    main()
