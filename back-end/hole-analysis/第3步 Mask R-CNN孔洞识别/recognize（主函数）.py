import os
import torch
import concurrent.futures
import numpy as np
import tifffile
from tqdm import tqdm
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2 import model_zoo
import cv2

# 临时解决 OpenMP 冲突问题
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# 设置中文字体支持
import matplotlib.pyplot as plt
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]

class MaskRCNNProcessor:
    def __init__(self, model_path, input_folder, output_folder, confidence_threshold=0.9, num_classes=1):
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.predictor = self._initialize_predictor(model_path, confidence_threshold, num_classes)
        
        # 创建输出文件夹
        os.makedirs(output_folder, exist_ok=True)
        
        # 获取并排序图像文件
        self.image_files = [f for f in os.listdir(input_folder) if f.endswith('.tiff')]
        self.image_files = sorted(self.image_files, key=lambda x: int(x.split('.')[0].split('_')[-1]))
        
        # 统计信息
        self.success_count = 0
        self.fail_count = 0
    
    def _initialize_predictor(self, model_path, confidence_threshold, num_classes):
        """初始化Mask R-CNN预测器"""
        cfg = get_cfg()
        cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
        cfg.MODEL.WEIGHTS = model_path
        cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = confidence_threshold
        cfg.MODEL.ROI_HEADS.NUM_CLASSES = num_classes
        
        # 性能优化设置
        cfg.MODEL.DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
        
        # 性能优化：启用更快的推理设置
        cfg.MODEL.BACKBONE.FREEZE_AT = 0  # 不冻结骨干网络
        cfg.SOLVER.IMS_PER_BATCH = 1  # 推理时使用较小的批次
        
        # 如果使用GPU，启用更多优化
        if torch.cuda.is_available():
            cfg.MODEL.PIXEL_MEAN = [103.530, 116.280, 123.675]  # 使用更快的预处理
            # 启用半精度训练（有助于推理速度）
            cfg.MODEL.FP16_ENABLED = True
            # 优化内存使用
            cfg.MODEL.ROI_HEADS.BATCH_SIZE_PER_IMAGE = 64  # 减少内存占用
            # 启用CUDA优化
            torch.backends.cudnn.benchmark = True
        
        # 显示设备信息
        print(f"使用设备: {cfg.MODEL.DEVICE}")
        if torch.cuda.is_available():
            print(f"GPU型号: {torch.cuda.get_device_name()}")
            print(f"GPU内存: {torch.cuda.get_device_properties(0).total_memory/1024**3:.1f}GB")
            print("已启用GPU优化：半精度推理、CUDA加速")
        
        return DefaultPredictor(cfg)
    
    def process_single_image(self, image_file):
        """处理单张图像的函数，供多线程调用"""
        try:
            image_path = os.path.join(self.input_folder, image_file)
            
            # 使用tifffile高效读取TIFF图像
            img = tifffile.imread(image_path)
            
            # 性能优化：图像分辨率缩放（降低到75%分辨率）
            original_height, original_width = img.shape[:2]
            scale_factor = 0.75  # 降低到75%分辨率
            new_width = int(original_width * scale_factor)
            new_height = int(original_height * scale_factor)
            
            if len(img.shape) == 2:
                # 灰度图像
                img_resized = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
                img_resized = np.expand_dims(img_resized, axis=-1)
            else:
                # 彩色图像
                img_resized = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
            
            # 确保图像格式正确
            if len(img_resized.shape) == 2:
                img_resized = np.expand_dims(img_resized, axis=-1)
            
            # 性能优化：启用半精度推理（如果使用GPU）
            if torch.cuda.is_available():
                with torch.cuda.amp.autocast():
                    predictions = self.predictor(img_resized)
            else:
                predictions = self.predictor(img_resized)
            
            # 提取掩码
            masks = predictions["instances"].pred_masks.cpu().numpy()
            
            # 将掩码缩放回原始尺寸
            if masks.size > 0:
                resized_masks = []
                for mask in masks:
                    mask_resized = cv2.resize(mask.astype(np.float32), 
                                            (original_width, original_height), 
                                            interpolation=cv2.INTER_LINEAR)
                    resized_masks.append(mask_resized > 0.5)  # 二值化
                masks = np.array(resized_masks)
            
            # 创建掩码图像
            mask_only_img = np.zeros((original_height, original_width), dtype=np.uint8)
            for mask in masks:
                mask = mask.astype(np.uint8) * 255
                mask_only_img[mask == 255] = 255
            
            # 保存掩码图像
            output_mask_path = os.path.join(self.output_folder, f"{os.path.splitext(image_file)[0]}_mask.tiff")
            tifffile.imwrite(output_mask_path, mask_only_img)
            
            return True, image_file
        except Exception as e:
            print(f"处理图像 {image_file} 时出错: {str(e)}")
            return False, image_file
    
    def process_batch(self, max_workers=None, batch_size=50):
        """批量处理所有图像，智能选择多线程或多进程处理"""
        # 智能判断使用多线程还是多进程
        use_multiprocessing = self._should_use_multiprocessing()
        
        # 性能优化：调整工作进程/线程数
        if max_workers is None:
            if use_multiprocessing:
                # 多进程：使用更多进程数（但不超过CPU核心数）
                max_workers = min(6, os.cpu_count() or 6)  # 减少到6个进程，避免内存竞争
            else:
                # 多线程：根据GPU内存调整线程数
                if torch.cuda.is_available():
                    # GPU环境：使用更多线程（但避免内存溢出）
                    max_workers = min(8, os.cpu_count() or 8)  # 增加到8个线程
                else:
                    # CPU环境：保守设置线程数
                    max_workers = min(4, os.cpu_count() or 4)
        
        # 智能调整Windows环境下的处理方式
        if use_multiprocessing and os.name == 'nt':  # Windows系统且原本选择多进程
            print("Windows环境下使用多线程替代多进程（避免序列化问题）")
            use_multiprocessing = False  # 强制使用多线程
            max_workers = min(8, os.cpu_count() or 8)  # 调整为线程数
        
        # 根据最终选择显示处理方式
        executor_type = "多进程" if use_multiprocessing else "多线程"
        total_files = len(self.image_files)
        total_batches = (total_files + batch_size - 1) // batch_size
        
        print(f"开始处理 {total_files} 张图像，使用 {max_workers} 个{executor_type}，每批 {batch_size} 个文件，共 {total_batches} 批...")
        
        all_results = []
        
        # 分批处理
        for i in range(0, total_files, batch_size):
            batch_files = self.image_files[i:i + batch_size]
            batch_num = i//batch_size + 1
            print(f"处理第 {batch_num} 批，共 {len(batch_files)} 个文件...")
            
            if use_multiprocessing:
                # 使用进程池并行处理当前批次（避免GIL限制）
                with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
                    batch_results = list(tqdm(executor.map(self.process_single_image, batch_files), total=len(batch_files)))
            else:
                # 使用线程池并行处理当前批次（GPU环境适用）
                with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                    batch_results = list(tqdm(executor.map(self.process_single_image, batch_files), total=len(batch_files)))
            
            all_results.extend(batch_results)
            
            # 输出进度信息
            processed_files = len(all_results)
            progress_percent = (processed_files / total_files) * 100
            print(f"进度: {processed_files}/{total_files} ({progress_percent:.1f}%) - 第 {batch_num}/{total_batches} 批完成")
            
            # 每批处理后清理GPU内存（仅在GPU环境下）
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                print(f"第 {batch_num} 批处理完成，清理GPU内存")
        
        # 返回处理结果列表
        return all_results
    
    def _should_use_multiprocessing(self):
        """智能判断是否应该使用多进程处理"""
        # 判断逻辑：
        # 1. Windows系统：优先使用多线程（避免序列化问题）
        # 2. Linux系统：根据设备类型选择
        
        if os.name == 'nt':  # Windows系统
            # Windows环境下优先使用多线程
            print("Windows环境下使用多线程优化（避免序列化问题）")
            return False
        else:
            # Linux系统：根据设备类型选择
            if torch.cuda.is_available():
                # 有CUDA支持，使用GPU，适合多线程
                print("检测到GPU环境，使用多线程优化")
                return False
            else:
                # 无CUDA支持，使用CPU，适合多进程
                print("检测到CPU环境，使用多进程优化（避免GIL限制）")
                return True

# 主函数
if __name__ == "__main__":
    import argparse
    
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='Mask R-CNN孔洞识别主函数')
    parser.add_argument('--input-dir', type=str, default='selected_tiff_slices', 
                       help='输入目录路径（默认: selected_tiff_slices）')
    parser.add_argument('--output-dir', type=str, default='../第4步 数据预处理/masks',
                       help='输出目录路径（默认: ../第4步 数据预处理/masks）')
    parser.add_argument('--model-path', type=str, default='model_final.pth',
                       help='模型文件路径（默认: model_final.pth）')
    parser.add_argument('--confidence', type=float, default=0.9,
                       help='置信度阈值（默认: 0.9）')
    
    args = parser.parse_args()
    
    # 配置参数
    MODEL_PATH = args.model_path
    INPUT_FOLDER = args.input_dir
    OUTPUT_FOLDER = args.output_dir
    CONFIDENCE_THRESHOLD = args.confidence
    
    print(f"模型路径: {MODEL_PATH}")
    print(f"输入目录: {INPUT_FOLDER}")
    print(f"输出目录: {OUTPUT_FOLDER}")
    print(f"置信度阈值: {CONFIDENCE_THRESHOLD}")
    
    # 检查输入目录是否存在
    import os
    if not os.path.exists(INPUT_FOLDER):
        print(f"错误: 输入目录不存在: {INPUT_FOLDER}")
        exit(1)
    
    # 检查输入目录中是否有文件
    input_files = [f for f in os.listdir(INPUT_FOLDER) if f.endswith('.tiff')]
    if not input_files:
        print(f"错误: 输入目录中没有找到.tiff文件: {INPUT_FOLDER}")
        exit(1)
    
    print(f"找到 {len(input_files)} 个输入文件")
    
    # 确保输出目录存在
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    
    # 创建处理器并开始处理
    processor = MaskRCNNProcessor(
        model_path=MODEL_PATH,
        input_folder=INPUT_FOLDER,
        output_folder=OUTPUT_FOLDER,
        confidence_threshold=CONFIDENCE_THRESHOLD
    )
    results = processor.process_batch()
    
    # 统计结果
    success_count = sum(1 for success, _ in results if success)
    fail_count = len(results) - success_count
    
    print(f"图像处理完成！成功: {success_count}, 失败: {fail_count}")
    
    # 输出JSON格式的结果，供operate.py使用
    import json
    result_data = {
        "total_images": len(results),
        "success_count": success_count,
        "fail_count": fail_count,
        "success_rate": success_count / len(results) if len(results) > 0 else 0
    }
    print(json.dumps(result_data, ensure_ascii=False))
