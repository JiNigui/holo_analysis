import os
import sys
import subprocess
import json
import time
from pathlib import Path

def get_conda_env_path(env_name="holo_detectron2"):
    """获取指定conda环境的完整路径"""
    try:
        # 使用conda info获取环境路径
        result = subprocess.run(
            ["conda", "info", "--envs"],
            capture_output=True,
            text=True,
            check=True
        )
        
        # 解析环境列表，找到指定环境
        for line in result.stdout.split('\n'):
            if env_name in line and line.strip().startswith('*' if env_name == 'base' else ''):
                parts = line.split()
                if len(parts) >= 2:
                    env_path = parts[-1]
                    return env_path
        
        return None
        
    except Exception as e:
        print(f"获取conda环境路径失败: {e}")
        return None

def activate_conda_env(env_name="holo_detectron2"):
    """激活conda环境并返回环境变量"""
    try:
        env_path = get_conda_env_path(env_name)
        if not env_path:
            raise Exception(f"未找到conda环境: {env_name}")
        
        print(f"激活虚拟环境: {env_name}")
        print(f"虚拟环境路径: {env_path}")
        
        # 获取当前环境变量
        current_env = os.environ.copy()
        
        # 设置虚拟环境的Python路径
        python_path = os.path.join(env_path, "python.exe")
        if not os.path.exists(python_path):
            raise Exception(f"虚拟环境中未找到Python解释器: {python_path}")
        
        print(f"使用虚拟环境Python: {python_path}")
        
        # 设置PATH环境变量，将虚拟环境的路径放在最前面
        env_bin_path = os.path.join(env_path, "Scripts")
        env_lib_path = os.path.join(env_path, "Library", "bin")
        
        new_path = f"{env_bin_path};{env_lib_path};{current_env.get('PATH', '')}"
        
        # 创建新的环境变量字典
        env = current_env.copy()
        env['PATH'] = new_path
        env['CONDA_DEFAULT_ENV'] = env_name
        env['CONDA_PREFIX'] = env_path
        
        # 添加项目目录到PYTHONPATH
        project_root = Path(__file__).parent.parent.parent.parent
        detectron2_path = project_root / "detectron2"
        
        pythonpath = str(detectron2_path)
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = f"{pythonpath};{env['PYTHONPATH']}"
        else:
            env['PYTHONPATH'] = pythonpath
        
        print(f"已设置PYTHONPATH: {env['PYTHONPATH']}")
        
        return env, python_path
        
    except Exception as e:
        print(f"激活虚拟环境失败: {e}")
        return None, None

def run_hole_detection(input_dir=None, output_dir=None):
    """执行孔洞识别的主函数
    
    Args:
        input_dir: 输入目录路径（包含selected_tiff_slices）
        output_dir: 输出目录路径（masks目录）
    """
    try:
        # 获取当前文件所在目录
        current_dir = Path(__file__).parent
        print(f"当前工作目录: {current_dir}")
        
        # 使用传入的路径或默认路径
        if input_dir is None:
            input_dir = current_dir / "selected_tiff_slices"
        else:
            input_dir = Path(input_dir)
            
        if output_dir is None:
            output_dir = current_dir.parent / "第4步 数据预处理" / "masks"
        else:
            output_dir = Path(output_dir)
        
        print(f"输入目录: {input_dir}")
        print(f"输出目录: {output_dir}")
        
        # 检查输入目录是否存在
        if not input_dir.exists():
            return {"status": "error", "message": f"输入目录不存在: {input_dir}"}
        
        # 检查输入目录中是否有文件
        input_files = [f for f in os.listdir(input_dir) if f.endswith('.tiff')]
        if not input_files:
            return {"status": "error", "message": f"输入目录中没有找到.tiff文件: {input_dir}"}
        
        print(f"找到 {len(input_files)} 个输入文件")
        
        # 预处理：清理输出目录中的旧文件
        if output_dir.exists():
            # 获取所有.tiff文件
            old_mask_files = [f for f in os.listdir(output_dir) if f.endswith('.tiff')]
            if old_mask_files:
                print(f"清理输出目录中的 {len(old_mask_files)} 个旧掩码文件...")
                for file in old_mask_files:
                    file_path = output_dir / file
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        print(f"删除文件 {file} 失败: {e}")
        else:
            # 如果输出目录不存在，创建它
            output_dir.mkdir(exist_ok=True)
            print("创建输出目录")
        
        # 激活conda环境
        env, env_python = activate_conda_env("holo_detectron2")
        if not env or not env_python:
            return {"status": "error", "message": "激活虚拟环境失败"}
        
        # 检查recognize.py文件是否存在
        script_path = current_dir / "run_detection.py"
        if not script_path.exists():
            return {"status": "error", "message": f"未找到识别脚本: {script_path}"}
        
        print(f"识别脚本路径: {script_path}")
        
        # 构建Python命令（在holo_detectron2环境中执行），传递路径参数
        unet_model_path = current_dir / "unet.pth"
        maskrcnn_model_path = current_dir / "model_final.pth"
    
        python_cmd = [env_python, str(script_path), 
                     f"--input-dir={input_dir}",
                     f"--output-dir={output_dir}",
                     f"--unet-model={unet_model_path}",
                     f"--maskrcnn-model={maskrcnn_model_path}"]
        
        # 执行孔洞识别脚本
        print("开始执行孔洞识别...")
        start_time = time.time()
        
        # 使用Popen实现实时输出和进度监控
        import threading
        
        # 创建进度监控变量
        progress_info = {
            "current_batch": 0,
            "total_batches": 0,
            "processed_files": 0,
            "total_files": 0,
            "status": "starting",
            "progress_percent": 0.0
        }
        
        # 启动子进程
        process = subprocess.Popen(
            python_cmd,
            cwd=str(current_dir),
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            universal_newlines=True
        )
        
        # 实时读取输出并解析进度
        stdout_lines = []
        
        def read_output():
            for line in iter(process.stdout.readline, ''):
                stdout_lines.append(line)
                
                # 实时输出到控制台（前端可以看到）
                print(line.strip())
                
                # 解析进度信息
                if "开始处理" in line:
                    # 例如: "开始处理 96 张图像，使用 4 个多线程，每批 50 个文件，共 2 批..."
                    import re
                    match = re.search(r'开始处理 (\d+) 张图像', line)
                    if match:
                        progress_info["total_files"] = int(match.group(1))
                        progress_info["status"] = "processing"
                        print(f"[进度] 开始处理 {progress_info['total_files']} 张图像")
                        
                elif "进度:" in line or "检测完成" in line:
                    # 例如: "进度: 50/96 (52.1%) - 第 1/2 批完成"
                    import re
                    match = re.search(r'进度: (\d+)/(\d+) \((\d+\.?\d*)%\) - 第 (\d+)/(\d+) 批完成', line)
                    if match:
                        progress_info["processed_files"] = int(match.group(1))
                        progress_info["total_files"] = int(match.group(2))
                        progress_info["progress_percent"] = float(match.group(3))
                        progress_info["current_batch"] = int(match.group(4))
                        progress_info["total_batches"] = int(match.group(5))
                        print(f"[进度] 已完成 {progress_info['processed_files']}/{progress_info['total_files']} ({progress_info['progress_percent']}%)")
                        
                elif "检测完成" in line:
                    progress_info["status"] = "completed"
                    print("[进度] 图像处理完成")
        
        # 启动输出读取线程
        output_thread = threading.Thread(target=read_output)
        output_thread.daemon = True
        output_thread.start()
        
        # 等待进程完成
        process.wait()
        
        # 收集所有输出
        result = subprocess.CompletedProcess(
            args=python_cmd,
            returncode=process.returncode,
            stdout=''.join(stdout_lines),
            stderr=''
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"孔洞识别执行完成，耗时: {execution_time:.2f}秒")
        
        # 检查执行结果
        if result.returncode == 0:
            # 获取输入文件数量（使用动态路径）
            input_files = [f for f in os.listdir(input_dir) if f.endswith('.tiff')]
            input_count = len(input_files)
            
            # 获取输出文件数量（使用动态路径）
            mask_files = []
            if output_dir.exists():
                mask_files = [f for f in os.listdir(output_dir) if f.endswith('.tiff')]
            output_count = len(mask_files)
            
            # 从脚本输出中解析成功处理数量
            success_count = 0
            
            # 打印完整的stdout用于调试
            print("脚本输出内容:")
            print("=" * 50)
            print(result.stdout)
            print("=" * 50)
            
            try:
                if result.stdout:
                    # 查找JSON格式的结果行
                    for line in result.stdout.split('\n'):
                        line = line.strip()
                        if line.startswith('{') and line.endswith('}'):
                            try:
                                # 尝试解析JSON
                                result_data = json.loads(line)
                                success_count = result_data.get('success_count', 0)
                                print(f"成功解析JSON数据: {result_data}")
                                print(f"从JSON中获取success_count: {success_count}")
                                break
                            except json.JSONDecodeError as e:
                                print(f"JSON解析错误: {e}")
                                print(f"解析失败的行: {line}")
                                continue
                    
                    # 如果JSON解析失败，尝试从文本中提取
                    if success_count == 0:
                        # 方法1：从"成功: X"这样的文本中提取
                        import re
                        match = re.search(r'成功:\s*(\d+)', result.stdout)
                        if match:
                            success_count = int(match.group(1))
                            print(f"从文本中提取success_count: {success_count}")
                        else:
                            # 方法2：如果还是没找到，使用输出文件数量
                            success_count = output_count
                            print(f"使用输出文件数量作为success_count: {success_count}")
            except Exception as e:
                print(f"解析success_count时发生错误: {e}")
                # 如果解析失败，使用输出文件数量作为成功数量
                success_count = output_count
            
            # 简单验证：三个数量相等
            is_success = (input_count == output_count == success_count)
            
            if is_success:
                return {
                    "status": "success",
                    "message": "孔洞识别成功完成",
                    "execution_time": execution_time
                }
            else:
                return {
                    "status": "error",
                    "message": f"孔洞识别部分失败：输入{input_count}个文件，输出{output_count}个文件，成功处理{success_count}个文件",
                    "execution_time": execution_time
                }
        else:
            return {
                "status": "error",
                "message": f"孔洞识别执行失败，返回码: {result.returncode}",
                "execution_time": execution_time
            }
            
    except subprocess.TimeoutExpired:
        return {"status": "error", "message": "孔洞识别执行超时（超过1小时）"}
    except Exception as e:
        return {"status": "error", "message": f"执行孔洞识别时发生错误: {str(e)}"}

def main():
    """主函数，支持命令行参数"""
    import argparse
    
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='孔洞识别操作脚本')
    parser.add_argument('--input-dir', type=str, help='输入目录路径（包含selected_tiff_slices）')
    parser.add_argument('--output-dir', type=str, help='输出目录路径（masks目录）')
    
    args = parser.parse_args()
    
    print("开始执行孔洞识别操作...")
    print(f"输入目录: {args.input_dir}")
    print(f"输出目录: {args.output_dir}")
    
    # 激活虚拟环境，执行孔洞识别
    result = run_hole_detection(input_dir=args.input_dir, output_dir=args.output_dir)
    
    # 输出结果
    print("\n执行结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    if result["status"] == "success":
        print("\n✅ 孔洞识别成功完成!")
    else:
        print("\n❌ 孔洞识别失败!")

if __name__ == "__main__":
    main()