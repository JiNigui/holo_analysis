from flask import Blueprint, request, jsonify, current_app, send_file, Response
import os
import subprocess
import sys
import glob
import datetime
import io
import json
from app.config.config import Config
from app.utils.jwt_utils import jwt_required
from app.api.logs import create_system_log

hole_analysis_bp = Blueprint('hole_analysis', __name__)

@hole_analysis_bp.route('/binary', methods=['POST'])
@jwt_required
def execute_binary_conversion():
    """执行图像二值化处理"""
    try:
        # 从请求上下文获取用户信息
        user_info = request.user

        # 获取请求参数
        data = request.get_json()
        if not data:
            # 记录参数验证失败日志
            try:
                create_system_log(
                    operation_type='BINARY_CONVERSION',
                    user_id=user_info['user_id'],
                    status='failed'
                )
            except Exception as log_error:
                print(f"记录参数验证失败日志失败: {str(log_error)}")
            return jsonify({
                'code': 400,
                'message': '请求参数不能为空'
            }), 400

        project_id = data.get('project_id')
        if not project_id:
            # 记录项目ID缺失失败日志
            try:
                create_system_log(
                    operation_type='BINARY_CONVERSION',
                    user_id=user_info['user_id'],
                    status='failed'
                )
            except Exception as log_error:
                print(f"记录项目ID缺失失败日志失败: {str(log_error)}")
            return jsonify({
                'code': 400,
                'message': '项目ID不能为空'
            }), 400

        # 获取项目信息以获取项目名
        from app.models.project import Project
        project = Project.query.get(project_id)
        if not project:
            # 记录项目不存在失败日志
            try:
                create_system_log(
                    operation_type='BINARY_CONVERSION',
                    user_id=user_info['user_id'],
                    project_id=int(project_id),
                    status='failed'
                )
            except Exception as log_error:
                print(f"记录项目不存在失败日志失败: {str(log_error)}")
            return jsonify({
                'code': 404,
                'message': '项目不存在'
            }), 404

        # 动态生成用户项目临时路径
        username = user_info['username']
        project_name = project.project_name
        
        # 输入目录：用户项目临时目录的first/input
        input_dir = os.path.join(
            Config.INTERMEDIATE_DATA_DIR,
            f"{username}_{project_name}",
            "first",
            "input"
        )

        # 输出目录：用户项目临时目录的first/output
        output_dir = os.path.join(
            Config.INTERMEDIATE_DATA_DIR,
            f"{username}_{project_name}",
            "first",
            "output"
        )

        # 确保输入目录存在且有文件
        if not os.path.exists(input_dir):
            # 记录输入目录不存在失败日志
            try:
                create_system_log(
                    operation_type='BINARY_CONVERSION',
                    user_id=user_info['user_id'],
                    project_id=int(project_id),
                    status='failed'
                )
            except Exception as log_error:
                print(f"记录输入目录不存在失败日志失败: {str(log_error)}")
            return jsonify({
                'code': 404,
                'message': f'输入目录不存在: {input_dir}'
            }), 404

        # 检查输入目录是否有.tif文件
        tif_files = [f for f in os.listdir(input_dir) if f.endswith('.tif') or f.endswith('.tiff')]
        if not tif_files:
            # 记录无TIF文件失败日志
            try:
                create_system_log(
                    operation_type='BINARY_CONVERSION',
                    user_id=user_info['user_id'],
                    project_id=int(project_id),
                    status='failed'
                )
            except Exception as log_error:
                print(f"记录无TIF文件失败日志失败: {str(log_error)}")
            return jsonify({
                'code': 400,
                'message': f'输入目录中没有找到.tif文件，请先上传图像文件'
            }), 400

        # 构建Python脚本路径
        script_path = os.path.join(
            Config.BASE_DIR,
            'hole-analysis',
            '第1步 原始图像的二值化',
            '加形态学.py'
        )

        # 检查脚本文件是否存在
        if not os.path.exists(script_path):
            # 记录脚本文件不存在失败日志
            try:
                create_system_log(
                    operation_type='BINARY_CONVERSION',
                    user_id=user_info['user_id'],
                    project_id=int(project_id),
                    status='failed'
                )
            except Exception as log_error:
                print(f"记录脚本文件不存在失败日志失败: {str(log_error)}")
            return jsonify({
                'code': 404,
                'message': f'二值化脚本文件不存在: {script_path}'
            }), 404

        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)

        # 设置工作目录为脚本所在目录
        script_dir = os.path.dirname(script_path)

        print(f"开始执行图像二值化处理...")
        print(f"输入目录: {input_dir}")
        print(f"输出目录: {output_dir}")
        print(f"脚本路径: {script_path}")
        print(f"找到 {len(tif_files)} 个.tif文件")

        # 执行Python脚本，传递输入和输出路径参数
        result = subprocess.run(
            [sys.executable, script_path, input_dir, output_dir],
            cwd=script_dir,
            capture_output=True,
            text=True,
            timeout=600  # 10分钟超时
        )

        # 检查执行结果
        if result.returncode == 0:
            # 记录成功日志
            try:
                create_system_log(
                    operation_type='BINARY_CONVERSION',
                    user_id=user_info['user_id'],
                    project_id=int(project_id),
                    status='success'
                )
                print(f"成功处理 {len(tif_files)} 个图像文件")
            except Exception as log_error:
                print(f"记录日志失败: {str(log_error)}")

            return jsonify({
                'code': 200,
                'message': f'图像二值化处理完成，共处理 {len(tif_files)} 个文件',
                'data': {
                    'input_dir': input_dir,
                    'output_dir': output_dir,
                    'processed_files': len(tif_files),
                    'output': result.stdout
                }
            }), 200
        else:
            # 记录失败日志
            try:
                create_system_log(
                    operation_type='BINARY_CONVERSION',
                    user_id=user_info['user_id'],
                    project_id=int(project_id),
                    status='failed'
                )
                print(f"处理失败: {result.stderr[:200]}")
            except Exception as log_error:
                print(f"记录日志失败: {str(log_error)}")

            return jsonify({
                'code': 500,
                'message': '图像二值化处理失败',
                'data': {
                    'error': result.stderr,
                    'output': result.stdout
                }
            }), 500

    except subprocess.TimeoutExpired:
        return jsonify({
            'code': 408,
            'message': '图像二值化处理超时（超过10分钟），请减少文件数量或联系管理员'
        }), 408

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"执行图像二值化时发生错误: {str(e)}")
        print(f"错误堆栈: {error_trace}")

        return jsonify({
            'code': 500,
            'message': f'执行图像二值化时发生错误: {str(e)}'
        }), 500


@hole_analysis_bp.route('/voi/confirm', methods=['POST'])
@jwt_required
def confirm_voi_selection():
    """确认VOI区域选择，保存框选部分的切片数据"""
    try:
        # 从请求上下文获取用户信息
        user_info = request.user

        # 获取请求参数
        data = request.get_json()
        if not data:
            # 记录参数验证失败日志
            try:
                create_system_log(
                    operation_type='VOI_REGION_CONFIRMATION',
                    user_id=user_info['user_id'],
                    status='failed'
                )
            except Exception as log_error:
                print(f"记录参数验证失败日志失败: {str(log_error)}")
            return jsonify({
                'code': 400,
                'message': '请求参数不能为空'
            }), 400

        project_id = data.get('project_id')
        selection_bounds = data.get('selection_bounds')
        
        if not project_id:
            # 记录项目ID缺失失败日志
            try:
                create_system_log(
                    operation_type='VOI_REGION_CONFIRMATION',
                    user_id=user_info['user_id'],
                    status='failed'
                )
            except Exception as log_error:
                print(f"记录项目ID缺失失败日志失败: {str(log_error)}")
            return jsonify({
                'code': 400,
                'message': '项目ID不能为空'
            }), 400
            
        if not selection_bounds:
            # 记录选择区域边界缺失失败日志
            try:
                create_system_log(
                    operation_type='VOI_REGION_CONFIRMATION',
                    user_id=user_info['user_id'],
                    status='failed'
                )
            except Exception as log_error:
                print(f"记录选择区域边界缺失失败日志失败: {str(log_error)}")
            return jsonify({
                'code': 400,
                'message': '选择区域边界不能为空'
            }), 400

        # 获取项目信息以获取项目名
        from app.models.project import Project
        project = Project.query.get(project_id)
        if not project:
            # 记录项目不存在失败日志
            try:
                create_system_log(
                    operation_type='VOI_REGION_CONFIRMATION',
                    user_id=user_info['user_id'],
                    project_id=int(project_id),
                    status='failed'
                )
            except Exception as log_error:
                print(f"记录项目不存在失败日志失败: {str(log_error)}")
            return jsonify({
                'code': 404,
                'message': '项目不存在'
            }), 404

        # 动态生成用户项目临时路径
        username = user_info['username']
        project_name = project.project_name

        # 输入目录：用户项目临时目录的first/output（二值化输出）
        input_dir = os.path.join(
            Config.INTERMEDIATE_DATA_DIR,
            f"{username}_{project_name}",
            "first",
            "output"
        )

        # 输出目录：用户项目临时目录的third/selected_tiff_slices（选择的切片）
        output_dir = os.path.join(
            Config.INTERMEDIATE_DATA_DIR,
            f"{username}_{project_name}",
            "third",
            "selected_tiff_slices"
        )

        # 创建输出目录（如果不存在）
        os.makedirs(output_dir, exist_ok=True)
        
        # 清理目标文件夹下的旧文件数据
        if os.path.exists(output_dir):
            for filename in os.listdir(output_dir):
                file_path = os.path.join(output_dir, filename)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(f"⚠️ 清理文件失败 {filename}: {str(e)}")

        # 检查输入目录是否存在
        if not os.path.exists(input_dir):
            # 记录输入目录不存在失败日志
            try:
                create_system_log(
                    operation_type='VOI_REGION_CONFIRMATION',
                    user_id=user_info['user_id'],
                    project_id=int(project_id),
                    status='failed'
                )
            except Exception as log_error:
                print(f"记录输入目录不存在失败日志失败: {str(log_error)}")
            return jsonify({
                'code': 404,
                'message': f'输入目录不存在，请先执行图像二值化: {input_dir}'
            }), 404

        # 检查是否有tiff文件
        # 使用自然数排序：按数字大小排序，而不是字符串排序
        def natural_sort_key(filename):
            import re
            # 提取文件名中的数字部分
            numbers = re.findall(r'\d+', filename)
            if numbers:
                # 返回数字作为排序键
                return int(numbers[-1])
            return filename
        
        tiff_files = [f for f in os.listdir(input_dir) if f.endswith('.tiff') or f.endswith('.tif')]
        tiff_files = sorted(tiff_files, key=natural_sort_key)
        
        if not tiff_files:
            # 记录无二值化图像文件失败日志
            try:
                create_system_log(
                    operation_type='VOI_REGION_CONFIRMATION',
                    user_id=user_info['user_id'],
                    project_id=int(project_id),
                    status='failed'
                )
            except Exception as log_error:
                print(f"记录无二值化图像文件失败日志失败: {str(log_error)}")
            return jsonify({
                'code': 400,
                'message': '输入目录中没有找到二值化图像文件'
            }), 400

        print(f"正在处理区域选择确认...")
        print(f"输入目录: {input_dir}")
        print(f"输出目录: {output_dir}")
        print(f"选择区域边界: {selection_bounds}")

        try:
            import numpy as np
            from PIL import Image
            import cv2
            import shutil
            
            # 解析选择区域边界（前端已转换的像素坐标）
            x_min = selection_bounds.get('x_min', 0)
            x_max = selection_bounds.get('x_max', 500)
            y_min = selection_bounds.get('y_min', 0)
            y_max = selection_bounds.get('y_max', 500)
            z_min = selection_bounds.get('z_min', 0)
            z_max = selection_bounds.get('z_max', len(tiff_files))
            
            # 确保边界在合理范围内（使用实际图像尺寸进行验证）
            # 先获取第一张图像的尺寸作为参考
            first_image_path = os.path.join(input_dir, tiff_files[0])
            first_image = np.array(Image.open(first_image_path))
            image_height, image_width = first_image.shape[:2]
            total_slices = len(tiff_files)
            
            print(f"📏 图像尺寸参考: {image_width}x{image_height}, 切片总数: {total_slices}")
            
            # 验证坐标范围，确保在合理范围内
            x_min, x_max = max(0, int(x_min)), min(image_width, int(x_max))
            y_min, y_max = max(0, int(y_min)), min(image_height, int(y_max))
            z_min, z_max = max(0, int(z_min)), min(total_slices, int(z_max))
            
            print(f"✅ 验证后的坐标范围: X[{x_min}-{x_max}], Y[{y_min}-{y_max}], Z[{z_min}-{z_max}]")
            
            # 确保裁剪区域有效
            if x_min >= x_max or y_min >= y_max or z_min >= z_max:
                return jsonify({
                    'code': 400,
                    'message': f'无效的裁剪区域: X[{x_min}-{x_max}], Y[{y_min}-{y_max}], Z[{z_min}-{z_max}]'
                }), 400
            
            # 处理选择的切片，按照自然数排序重新命名
            saved_files = []
            file_counter = 1  # 从1开始计数
            
            for z_index in range(int(z_min), int(z_max) + 1):
                if z_index < len(tiff_files):
                    tiff_file = tiff_files[z_index]
                    input_path = os.path.join(input_dir, tiff_file)
                    
                    # 按照自然数排序重新命名：slice_xxxx.tiff
                    output_filename = f"slice_{file_counter:04d}.tiff"
                    output_path = os.path.join(output_dir, output_filename)

                    try:
                        # 使用PIL读取（避免OpenCV中文路径问题）
                        image = np.array(Image.open(input_path))

                        # 确保图像是灰度图
                        if len(image.shape) > 2:
                            image = image[:, :, 0]  # 取第一个通道

                        # 获取原始图像尺寸
                        height, width = image.shape[:2]

                        # 前端已完成所有坐标转换，直接使用
                        crop_x_min = max(0, int(x_min))
                        crop_x_max = min(width, int(x_max))
                        crop_y_min = max(0, int(y_min))
                        crop_y_max = min(height, int(y_max))

                        # 确保裁剪区域有效
                        if crop_x_min < crop_x_max and crop_y_min < crop_y_max:
                            # 裁剪选择区域
                            cropped_image = image[crop_y_min:crop_y_max, crop_x_min:crop_x_max]

                            # 使用PIL保存裁剪后的图像
                            Image.fromarray(cropped_image).save(output_path)
                            saved_files.append({
                                'original_file': tiff_file,
                                'saved_file': output_filename,
                                'file_path': output_path,
                                'slice_number': file_counter,
                                'z_index': z_index
                            })
                            file_counter += 1
                            
                            print(f"✅ 已保存切片 {file_counter-1}: {output_filename} (原始: {tiff_file})")
                        else:
                            print(f"⚠️ 跳过无效裁剪区域: {tiff_file} (x:{crop_x_min}-{crop_x_max}, y:{crop_y_min}-{crop_y_max})")
                    except Exception as e:
                        print(f"❌ 处理切片 {tiff_file} 失败: {str(e)}")
                        continue
            
            # 构建返回数据
            saved_files_list = [file_info['saved_file'] for file_info in saved_files]
            
            # 记录VOI区域确认日志
            create_system_log(
                operation_type='VOI_REGION_CONFIRMATION',
                user_id=user_info['user_id'],
                project_id=int(project_id),
                status='success'
            )
            
            return jsonify({
                'code': 200,
                'message': f'VOI区域保存成功，已保存 {len(saved_files)} 个切片文件',
                'data': {
                    'saved_files_count': len(saved_files),
                    'output_dir': output_dir,
                    'selection_bounds': selection_bounds,
                    'saved_files': saved_files_list,
                    'file_details': saved_files,
                    'naming_convention': 'slice_xxxx.tiff',
                    'processing_summary': {
                        'total_slices_processed': len(saved_files),
                        'naming_start_index': 1,
                        'naming_end_index': len(saved_files),
                        'original_z_range': f'{z_min}-{z_max}',
                        'processed_z_range': f'{saved_files[0]["z_index"] if saved_files else 0}-{saved_files[-1]["z_index"] if saved_files else 0}'
                    }
                }
            }), 200
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"处理区域选择确认时发生错误: {str(e)}")
            print(f"错误堆栈: {error_trace}")
            
            return jsonify({
                'code': 500,
                'message': f'处理区域选择确认时发生错误: {str(e)}'
            }), 500

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"确认VOI区域选择时发生错误: {str(e)}")
        print(f"错误堆栈: {error_trace}")

        return jsonify({
            'code': 500,
            'message': f'确认VOI区域选择时发生错误: {str(e)}'
        }), 500

@hole_analysis_bp.route('/projects/<int:project_id>/3d_data', methods=['GET'])
@jwt_required
def get_3d_vtk_data(project_id):
    """获取3D模型的VTK数据"""
    try:
        print(f"=== 开始处理3D VTK数据请求 ===")
        print(f"项目ID: {project_id}")
        
        user_info = request.user
        print(f"用户信息: {user_info}")
        
        # 权限检查
        from app.models.project import Project
        project = Project.query.get(project_id)
        if not project:
            print(f"项目不存在: {project_id}")
            return jsonify({'code': 404, 'message': '项目不存在'}), 404
        if project.user_id != user_info['user_id']:
            print(f"权限不足: 用户{user_info['user_id']} 无权访问项目{project_id}")
            return jsonify({'code': 403, 'message': '没有权限访问此项目'}), 403

        # 动态生成用户项目临时路径
        username = user_info['username']
        project_name = project.project_name
        print(f"用户名: {username}, 项目名: {project_name}")

        # 数据目录：用户项目临时目录的first/output（二值化输出）
        binary_data_path = os.path.join(
            Config.INTERMEDIATE_DATA_DIR,
            f"{username}_{project_name}",
            "first",
            "output"
        )
        print(f"二值化数据目录: {binary_data_path}")
        
        if not os.path.exists(binary_data_path):
            print(f"二值化输出目录不存在: {binary_data_path}")
            return jsonify({
                'code': 404,
                'message': f'二值化输出目录不存在: {binary_data_path}'
            }), 404
        
        # 检查目录中是否有二值化文件
        tiff_files = [f for f in os.listdir(binary_data_path) 
                      if f.startswith('binary_slice_') and f.endswith('.tiff')]
        print(f"找到 {len(tiff_files)} 个二值化切片文件")
        
        if not tiff_files:
            print("二值化数据目录中没有找到切片文件")
            return jsonify({
                'code': 400,
                'message': '二值化数据目录中没有找到切片文件'
            }), 400

        # 导入VTK处理器
        import sys
        import importlib.util
        
        # 添加hole-analysis目录到Python路径
        hole_analysis_path = os.path.join(os.path.dirname(__file__), '..', '..', 'hole-analysis')
        print(f"hole-analysis路径: {hole_analysis_path}")
        sys.path.insert(0, hole_analysis_path)
        
        print("开始动态导入PyVista处理器模块...")
        
        # 导入PyVista处理器
        module_path_pyvista = os.path.join(hole_analysis_path, '第2步 选择自己感兴趣的区域', 'vtk_surface_processor_pyvista.py')
        print(f"PyVista处理器模块路径: {module_path_pyvista}")
        
        if not os.path.exists(module_path_pyvista):
            print(f"PyVista处理器模块文件不存在: {module_path_pyvista}")
            return jsonify({
                'code': 500,
                'message': f'PyVista处理器模块文件不存在: {module_path_pyvista}'
            }), 500
        
        spec_pyvista = importlib.util.spec_from_file_location("vtk_surface_processor_pyvista", module_path_pyvista)
        vtk_module_pyvista = importlib.util.module_from_spec(spec_pyvista)
        spec_pyvista.loader.exec_module(vtk_module_pyvista)
        VTKSurfaceProcessorPyVista = vtk_module_pyvista.VTKSurfaceProcessorPyVista
        print("PyVista处理器模块导入成功")
        
        # 创建处理器并生成VTK表面数据
        print("创建PyVista处理器实例...")
        processor = VTKSurfaceProcessorPyVista(binary_data_path)
        
        # 设置VTK文件输出目录为second/tmp
        vtk_output_dir = os.path.join(
            Config.INTERMEDIATE_DATA_DIR,
            f"{username}_{project_name}",
            "second",
            "tmp"
        )
        print(f"VTK文件输出目录: {vtk_output_dir}")
        
        # 确保输出目录存在
        os.makedirs(vtk_output_dir, exist_ok=True)
        print("输出目录创建/确认完成")
        
        # 清理旧的VTP文件，确保传输最新文件
        print("清理旧的VTP文件...")
        for filename in os.listdir(vtk_output_dir):
            if filename.endswith('.vtp') and filename.startswith('surface_'):
                old_file_path = os.path.join(vtk_output_dir, filename)
                try:
                    os.remove(old_file_path)
                    print(f"已删除旧文件: {filename}")
                except Exception as e:
                    print(f"删除旧文件失败 {filename}: {e}")
        
        # 生成VTK表面数据
        print("开始生成VTK表面数据...")
        vtk_file_path = processor.generate_surface(vtk_output_dir)
        print(f"VTK文件生成成功，路径: {vtk_file_path}")
        
        # 验证文件是否确实生成在当前目录
        if not os.path.exists(vtk_file_path):
            raise RuntimeError(f"VTK文件生成失败，文件不存在: {vtk_file_path}")
        
        # 获取文件信息
        file_size = os.path.getsize(vtk_file_path)
        print(f"VTK文件大小: {file_size / (1024*1024):.2f} MB")
        
        # 验证文件确实在指定目录中
        file_dir = os.path.dirname(vtk_file_path)
        if file_dir != vtk_output_dir:
            print(f"警告: 生成的文件不在预期目录中")
            print(f"预期目录: {vtk_output_dir}")
            print(f"实际目录: {file_dir}")
        
        # 列出当前目录中的所有VTP文件
        current_vtp_files = [f for f in os.listdir(vtk_output_dir) if f.endswith('.vtp')]
        print(f"当前目录中的VTP文件: {current_vtp_files}")
        
        # 记录3D模型构建成功日志
        create_system_log(
            operation_type='3D_MODEL_CONSTRUCTION',
            user_id=user_info['user_id'],
            project_id=project_id,
            status='success'
        )
        
        # 直接返回VTK文件，优化大文件传输
        print("开始返回VTK文件给前端...")
        return send_file(
            vtk_file_path,
            as_attachment=True,
            download_name=os.path.basename(vtk_file_path),
            mimetype='application/octet-stream',
            # 大文件传输优化
            conditional=True,  # 支持条件请求（断点续传）
            etag=False,        # 禁用ETag计算，减少CPU开销
            max_age=0          # 不缓存，确保获取最新文件
        )
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"生成3D模型VTK数据时发生错误: {str(e)}")
        print(f"错误堆栈: {error_trace}")
        
        # 记录3D模型构建失败日志
        try:
            create_system_log(
                operation_type='3D_MODEL_CONSTRUCTION',
                user_id=user_info['user_id'],
                project_id=project_id,
                status='failed'
            )
        except Exception as log_error:
            print(f"记录3D模型构建失败日志失败: {str(log_error)}")
        
        return jsonify({
            'code': 500,
            'message': f'生成3D模型VTK数据时发生错误: {str(e)}'
        }), 500


@hole_analysis_bp.route('/projects/<int:project_id>/batch/<int:batch_index>', methods=['GET'])
@jwt_required
def get_voi_preview_batch(project_id, batch_index):
    """获取VOI预览数据批次（支持增量加载）"""
    try:
        user_info = request.user
        
        # 权限检查
        from app.models.project import Project
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'code': 404, 'message': '项目不存在'}), 404
        if project.user_id != user_info['user_id']:
            return jsonify({'code': 403, 'message': '没有权限访问此项目'}), 403
        
        # 获取项目信息以获取项目名
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'code': 404, 'message': '项目不存在'}), 404

        # 动态生成用户项目临时路径
        username = user_info['username']
        project_name = project.project_name

        # 数据目录：用户项目临时目录的first/output（二值化输出）
        input_dir = os.path.join(
            Config.INTERMEDIATE_DATA_DIR,
            f"{username}_{project_name}",
            "first",
            "output"
        )
        
        if not os.path.exists(input_dir):
            return jsonify({
                'code': 404,
                'message': f'二值化输出目录不存在: {input_dir}'
            }), 404
        
        # 获取查询参数
        batch_size = request.args.get('batch_size', 200, type=int)
        sample_rate = request.args.get('sample_rate', 5, type=int)
        
        # 创建处理器并生成批次数据
        processor = VOIDataProcessor(input_dir)
        
        # 使用正确的批次处理方法
        zip_data = processor.create_batch_tiff_zip_package(
            batch_index=batch_index,
            batch_size=batch_size,
            sample_rate=sample_rate
        )
        
        if not zip_data:
            return jsonify({
                'code': 500,
                'message': '生成批次数据包失败'
            }), 500
        
        # 返回ZIP二进制数据
        response = Response(
            zip_data,
            mimetype='application/zip',
            headers={
                'Content-Disposition': f'attachment; filename=voi_batch_{batch_index}.zip'
            }
        )
        return response
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"获取VOI预览批次数据时发生错误: {str(e)}")
        print(f"错误堆栈: {error_trace}")
        
        # 记录获取VOI预览批次数据失败日志
        try:
            create_system_log(
                operation_type='3D_MODEL_CONSTRUCTION',
                user_id=user_info['user_id'],
                project_id=project_id,
                status='failed'
            )
        except Exception as log_error:
            print(f"记录获取VOI预览批次数据失败日志失败: {str(log_error)}")
        
        return jsonify({
            'code': 500,
            'message': f'获取VOI预览批次数据时发生错误: {str(e)}'
        }), 500


@hole_analysis_bp.route('/hole-detection', methods=['POST'])
@jwt_required
def execute_hole_detection():
    """执行孔洞识别（第三步）"""
    try:
        # 从请求上下文获取用户信息
        user_info = request.user

        # 获取请求参数
        data = request.get_json()
        if not data:
            # 记录参数验证失败日志
            try:
                create_system_log(
                    operation_type='MASK_RCNN_DETECTION',
                    user_id=user_info['user_id'],
                    status='failed'
                )
            except Exception as log_error:
                print(f"记录参数验证失败日志失败: {str(log_error)}")
            return jsonify({
                'code': 400,
                'message': '请求参数不能为空'
            }), 400

        project_id = data.get('project_id')
        if not project_id:
            # 记录项目ID缺失失败日志
            try:
                create_system_log(
                    operation_type='MASK_RCNN_DETECTION',
                    user_id=user_info['user_id'],
                    status='failed'
                )
            except Exception as log_error:
                print(f"记录项目ID缺失失败日志失败: {str(log_error)}")
            return jsonify({
                'code': 400,
                'message': '项目ID不能为空'
            }), 400

        # 检查项目权限
        from app.models.project import Project
        project = Project.query.get(int(project_id))
        if not project:
            # 记录项目不存在失败日志
            try:
                create_system_log(
                    operation_type='MASK_RCNN_DETECTION',
                    user_id=user_info['user_id'],
                    project_id=int(project_id),
                    status='failed'
                )
            except Exception as log_error:
                print(f"记录项目不存在失败日志失败: {str(log_error)}")
            return jsonify({
                'code': 404,
                'message': '项目不存在'
            }), 404

        if project.user_id != user_info['user_id']:
            # 记录权限不足失败日志
            try:
                create_system_log(
                    operation_type='MASK_RCNN_DETECTION',
                    user_id=user_info['user_id'],
                    project_id=int(project_id),
                    status='failed'
                )
            except Exception as log_error:
                print(f"记录权限不足失败日志失败: {str(log_error)}")
            return jsonify({
                'code': 403,
                'message': '没有权限访问此项目'
            }), 403

        # 动态生成用户项目临时路径
        username = user_info['username']
        project_name = project.project_name

        # 输入目录：用户项目临时目录的third/selected_tiff_slices
        selected_slices_dir = os.path.join(
            Config.INTERMEDIATE_DATA_DIR,
            f"{username}_{project_name}",
            "third",
            "selected_tiff_slices"
        )

        if not os.path.exists(selected_slices_dir):
            # 记录VOI区域选择未完成失败日志
            try:
                create_system_log(
                    operation_type='MASK_RCNN_DETECTION',
                    user_id=user_info['user_id'],
                    project_id=int(project_id),
                    status='failed'
                )
            except Exception as log_error:
                print(f"记录VOI区域选择未完成失败日志失败: {str(log_error)}")
            return jsonify({
                'code': 400,
                'message': '请先完成VOI区域选择（第二步）'
            }), 400

        # 检查是否有切片文件
        slice_files = [f for f in os.listdir(selected_slices_dir) if f.endswith('.tiff')]
        if not slice_files:
            # 记录无切片文件失败日志
            try:
                create_system_log(
                    operation_type='MASK_RCNN_DETECTION',
                    user_id=user_info['user_id'],
                    project_id=int(project_id),
                    status='failed'
                )
            except Exception as log_error:
                print(f"记录无切片文件失败日志失败: {str(log_error)}")
            return jsonify({
                'code': 400,
                'message': '没有找到选择的切片文件，请先完成VOI区域选择'
            }), 400

        # 输出目录：用户项目临时目录的fourth/masks
        masks_output_dir = os.path.join(
            Config.INTERMEDIATE_DATA_DIR,
            f"{username}_{project_name}",
            "fourth",
            "masks"
        )

        # 确保输出目录存在
        os.makedirs(masks_output_dir, exist_ok=True)

        print(f"开始执行孔洞识别...")
        print(f"项目ID: {project_id}")
        print(f"找到 {len(slice_files)} 个切片文件")
        print(f"输入目录: {selected_slices_dir}")
        print(f"输出目录: {masks_output_dir}")

        # 构建operate.py脚本路径
        operate_script_path = os.path.join(
            Config.BASE_DIR,
            'hole-analysis',
            '第3步 Mask R-CNN孔洞识别',
            'operate.py'
        )

        # 检查脚本文件是否存在
        if not os.path.exists(operate_script_path):
            return jsonify({
                'code': 404,
                'message': f'孔洞识别操作脚本不存在: {operate_script_path}'
            }), 404

        # 设置工作目录
        script_dir = os.path.dirname(operate_script_path)

        # 执行孔洞识别脚本，传递动态路径参数
        result = subprocess.run(
            [sys.executable, operate_script_path, 
             f"--input-dir={selected_slices_dir}",
             f"--output-dir={masks_output_dir}"],
            cwd=script_dir,
            # 移除capture_output，让输出实时显示
            text=True,
            timeout=3600  # 1小时超时
        )

        # 检查执行结果
        if result.returncode == 0:
            # 检查masks目录中是否有生成的掩码文件（使用动态路径）
            mask_files = []
            if os.path.exists(masks_output_dir):
                mask_files = [f for f in os.listdir(masks_output_dir) if f.endswith('.tiff')]
            
            operation_result = {
                "status": "success", 
                "message": f"孔洞识别完成，生成 {len(mask_files)} 个掩码文件",
                "input_files": len(slice_files),
                "output_files": len(mask_files)
            }

            # 记录成功日志
            try:
                create_system_log(
                    operation_type='MASK_RCNN_DETECTION',
                    user_id=user_info['user_id'],
                    project_id=int(project_id),
                    status='success'
                )
            except Exception as log_error:
                print(f"记录日志失败: {str(log_error)}")

            return jsonify({
                'code': 200,
                'message': '孔洞识别完成',
                'data': {
                    'project_id': project_id,
                    'operation_result': operation_result,
                    'input_files_count': len(slice_files),
                    'output_files_count': len(mask_files),
                    'output_path': masks_output_dir,
                    'timestamp': datetime.datetime.now().isoformat()
                }
            }), 200
        else:
            # 记录失败日志
            try:
                create_system_log(
                    operation_type='MASK_RCNN_DETECTION',
                    user_id=user_info['user_id'],
                    project_id=int(project_id),
                    status='failed'
                )
            except Exception as log_error:
                print(f"记录日志失败: {str(log_error)}")

            return jsonify({
                'code': 500,
                'message': f'孔洞识别执行失败，返回码: {result.returncode}'
            }), 500

    except subprocess.TimeoutExpired:
        return jsonify({
            'code': 408,
            'message': '孔洞识别执行超时（超过1小时），请检查文件大小或联系管理员'
        }), 408

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"执行孔洞识别时发生错误: {str(e)}")
        print(f"错误堆栈: {error_trace}")

        return jsonify({
            'code': 500,
            'message': f'执行孔洞识别时发生错误: {str(e)}'
        }), 500


@hole_analysis_bp.route('/preprocess', methods=['POST'])
@jwt_required
def execute_data_preprocessing():
    """执行数据预处理（第四步）"""
    try:
        # 从请求上下文获取用户信息
        user_info = request.user

        # 获取请求参数
        data = request.get_json()
        if not data:
            # 记录参数验证失败日志
            try:
                create_system_log(
                    operation_type='DATA_PREPROCESSING',
                    user_id=user_info['user_id'],
                    status='failed'
                )
            except Exception as log_error:
                print(f"记录参数验证失败日志失败: {str(log_error)}")
            return jsonify({
                'code': 400,
                'message': '请求参数不能为空'
            }), 400

        project_id = data.get('project_id')
        if not project_id:
            # 记录项目ID缺失失败日志
            try:
                create_system_log(
                    operation_type='DATA_PREPROCESSING',
                    user_id=user_info['user_id'],
                    status='failed'
                )
            except Exception as log_error:
                print(f"记录项目ID缺失失败日志失败: {str(log_error)}")
            return jsonify({
                'code': 400,
                'message': '项目ID不能为空'
            }), 400

        # 检查项目权限
        from app.models.project import Project
        project = Project.query.get(int(project_id))
        if not project:
            # 记录项目不存在失败日志
            try:
                create_system_log(
                    operation_type='DATA_PREPROCESSING',
                    user_id=user_info['user_id'],
                    project_id=int(project_id),
                    status='failed'
                )
            except Exception as log_error:
                print(f"记录项目不存在失败日志失败: {str(log_error)}")
            return jsonify({
                'code': 404,
                'message': '项目不存在'
            }), 404

        if project.user_id != user_info['user_id']:
            # 记录权限不足失败日志
            try:
                create_system_log(
                    operation_type='DATA_PREPROCESSING',
                    user_id=user_info['user_id'],
                    project_id=int(project_id),
                    status='failed'
                )
            except Exception as log_error:
                print(f"记录权限不足失败日志失败: {str(log_error)}")
            return jsonify({
                'code': 403,
                'message': '没有权限访问此项目'
            }), 403

        # 动态生成用户项目临时路径
        username = user_info['username']
        project_name = project.project_name

        # 输入目录：用户项目临时目录的fourth/masks（第三步输出）
        masks_dir = os.path.join(
            Config.INTERMEDIATE_DATA_DIR,
            f"{username}_{project_name}",
            "fourth",
            "masks"
        )

        if not os.path.exists(masks_dir):
            # 记录孔洞识别未完成失败日志
            try:
                create_system_log(
                    operation_type='DATA_PREPROCESSING',
                    user_id=user_info['user_id'],
                    project_id=int(project_id),
                    status='failed'
                )
            except Exception as log_error:
                print(f"记录孔洞识别未完成失败日志失败: {str(log_error)}")
            return jsonify({
                'code': 400,
                'message': '请先完成孔洞识别（第三步）'
            }), 400

        # 检查是否有掩码文件
        mask_files = [f for f in os.listdir(masks_dir) if f.endswith('.tiff') or f.endswith('.tif')]
        if not mask_files:
            # 记录无掩码文件失败日志
            try:
                create_system_log(
                    operation_type='DATA_PREPROCESSING',
                    user_id=user_info['user_id'],
                    project_id=int(project_id),
                    status='failed'
                )
            except Exception as log_error:
                print(f"记录无掩码文件失败日志失败: {str(log_error)}")
            return jsonify({
                'code': 400,
                'message': '没有找到掩码文件，请先完成孔洞识别'
            }), 400

        # 输出目录：用户项目临时目录的fourth/output（第四步输出）
        output_dir = os.path.join(
            Config.INTERMEDIATE_DATA_DIR,
            f"{username}_{project_name}",
            "fourth",
            "output"
        )

        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)

        print(f"开始执行数据预处理...")
        print(f"项目ID: {project_id}")
        print(f"找到 {len(mask_files)} 个掩码文件")
        print(f"输入目录: {masks_dir}")
        print(f"输出目录: {output_dir}")

        # 构建数据预处理脚本路径
        script_path = os.path.join(
            Config.BASE_DIR,
            'hole-analysis',
            '第4步 数据预处理',
            '数据预处理（主函数）.py'
        )

        # 检查脚本文件是否存在
        if not os.path.exists(script_path):
            # 记录脚本文件不存在失败日志
            try:
                create_system_log(
                    operation_type='DATA_PREPROCESSING',
                    user_id=user_info['user_id'],
                    project_id=int(project_id),
                    status='failed'
                )
            except Exception as log_error:
                print(f"记录脚本文件不存在失败日志失败: {str(log_error)}")
            return jsonify({
                'code': 404,
                'message': f'数据预处理脚本文件不存在: {script_path}'
            }), 404

        # 设置工作目录为脚本所在目录
        script_dir = os.path.dirname(script_path)

        print(f"脚本路径: {script_path}")
        print(f"工作目录: {script_dir}")

        # 执行数据预处理脚本，传递动态路径参数
        result = subprocess.run(
            [sys.executable, script_path,
             f"--input-dir={masks_dir}",
             f"--output-dir={output_dir}"],
            cwd=script_dir,
            text=True,
            timeout=1800  # 30分钟超时
        )

        # 检查执行结果
        if result.returncode == 0:
            # 检查主函数输出的vtk文件是否存在
            main_output_vtk = os.path.join(output_dir, 'output_with_regions.vtk')
            if not os.path.exists(main_output_vtk):
                return jsonify({
                    'code': 500,
                    'message': '数据预处理完成但未生成 output_with_regions.vtk 文件'
                }), 500

            # 执行 another_filter.py 进行形态学清洗
            another_filter_path = os.path.join(
                Config.BASE_DIR,
                'hole-analysis',
                '第4步 数据预处理',
                'another_filter.py'
            )
            if not os.path.exists(another_filter_path):
                return jsonify({
                    'code': 404,
                    'message': f'形态学清洗脚本不存在: {another_filter_path}'
                }), 404

            print(f"开始执行形态学清洗 (another_filter.py)...")
            print(f"工作目录: {output_dir}")
            try:
                filter_result = subprocess.run(
                    [sys.executable, another_filter_path],
                    cwd=output_dir,
                    text=True,
                    timeout=600  # 10分钟超时
                )
            except subprocess.TimeoutExpired:
                return jsonify({
                    'code': 408,
                    'message': '形态学清洗执行超时（超过10分钟）'
                }), 408

            if filter_result.returncode != 0:
                return jsonify({
                    'code': 500,
                    'message': '形态学清洗执行失败，请检查后端日志'
                }), 500

            cleaned_vtk = os.path.join(output_dir, 'output_with_regions_cleaned_v3.vtk')
            if not os.path.exists(cleaned_vtk):
                return jsonify({
                    'code': 500,
                    'message': '形态学清洗完成但未生成 output_with_regions_cleaned_v3.vtk 文件'
                }), 500

            # 将 vtk 转换为 vtp，供前端 Three.js 渲染
            print("正在将 vtk 转换为 vtp 格式...")
            try:
                import pyvista as pv
                mesh_cleaned = pv.read(cleaned_vtk)
                if isinstance(mesh_cleaned, pv.UnstructuredGrid):
                    mesh_cleaned = mesh_cleaned.extract_surface()
                cleaned_vtp = os.path.join(output_dir, 'output_with_regions_cleaned_v3.vtp')
                mesh_cleaned.save(cleaned_vtp, binary=True)
                print(f"VTP 文件已保存: {cleaned_vtp}, 大小: {os.path.getsize(cleaned_vtp) / 1024 / 1024:.2f} MB")
            except Exception as conv_err:
                return jsonify({
                    'code': 500,
                    'message': f'VTP 转换失败: {str(conv_err)}'
                }), 500

            # 记录成功日志
            try:
                create_system_log(
                    operation_type='DATA_PREPROCESSING',
                    user_id=user_info['user_id'],
                    project_id=int(project_id),
                    status='success'
                )
            except Exception as log_error:
                print(f"记录日志失败: {str(log_error)}")

            print("数据预处理全流程完成，返回 VTP 文件给前端")
            return send_file(
                cleaned_vtp,
                as_attachment=True,
                download_name='output_with_regions_cleaned_v3.vtp',
                mimetype='application/octet-stream',
                conditional=True,
                etag=False,
                max_age=0
            )
        else:
            # 记录失败日志
            try:
                create_system_log(
                    operation_type='DATA_PREPROCESSING',
                    user_id=user_info['user_id'],
                    project_id=int(project_id),
                    status='failed'
                )
            except Exception as log_error:
                print(f"记录日志失败: {str(log_error)}")

            return jsonify({
                'code': 500,
                'message': f'数据预处理执行失败，返回码: {result.returncode}',
                'data': {
                    'operation_result': {
                        'status': 'error',
                        'message': result.stderr
                    }
                }
            }), 500

    except subprocess.TimeoutExpired:
        # 记录数据预处理超时失败日志
        try:
            create_system_log(
                operation_type='DATA_PREPROCESSING',
                user_id=user_info['user_id'],
                project_id=int(project_id),
                status='failed'
            )
        except Exception as log_error:
            print(f"记录数据预处理超时失败日志失败: {str(log_error)}")
        return jsonify({
            'code': 408,
            'message': '数据预处理执行超时（超过30分钟），请检查文件大小或联系管理员',
            'data': {
                'operation_result': {
                    'status': 'error',
                    'message': '数据预处理执行超时'
                }
            }
        }), 408

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"执行数据预处理时发生错误: {str(e)}")
        print(f"错误堆栈: {error_trace}")

        # 记录数据预处理异常失败日志
        try:
            create_system_log(
                operation_type='DATA_PREPROCESSING',
                user_id=user_info['user_id'],
                project_id=int(project_id),
                status='failed'
            )
        except Exception as log_error:
            print(f"记录数据预处理异常失败日志失败: {str(log_error)}")

        return jsonify({
            'code': 500,
            'message': f'执行数据预处理时发生错误: {str(e)}'
        }), 500


@hole_analysis_bp.route('/target-hole-analysis', methods=['POST'])
@jwt_required
def execute_target_hole_analysis():
    """执行目标孔洞分析（第五步）"""
    try:
        # 从请求上下文获取用户信息
        user_info = request.user

        # 获取请求参数
        data = request.get_json()
        if not data:
            # 记录参数验证失败日志
            try:
                create_system_log(
                    operation_type='TARGET_SLICING',
                    user_id=user_info['user_id'],
                    status='failed'
                )
            except Exception as log_error:
                print(f"记录参数验证失败日志失败: {str(log_error)}")
            return jsonify({
                'code': 400,
                'message': '请求参数不能为空'
            }), 400

        project_id = data.get('project_id')
        if not project_id:
            # 记录项目ID缺失失败日志
            try:
                create_system_log(
                    operation_type='TARGET_SLICING',
                    user_id=user_info['user_id'],
                    status='failed'
                )
            except Exception as log_error:
                print(f"记录项目ID缺失失败日志失败: {str(log_error)}")
            return jsonify({
                'code': 400,
                'message': '项目ID不能为空'
            }), 400

        # 检查项目权限
        from app.models.project import Project
        project = Project.query.get(int(project_id))
        if not project:
            # 记录项目不存在失败日志
            try:
                create_system_log(
                    operation_type='TARGET_SLICING',
                    user_id=user_info['user_id'],
                    project_id=int(project_id),
                    status='failed'
                )
            except Exception as log_error:
                print(f"记录项目不存在失败日志失败: {str(log_error)}")
            return jsonify({
                'code': 404,
                'message': '项目不存在'
            }), 404

        if project.user_id != user_info['user_id']:
            # 记录权限不足失败日志
            try:
                create_system_log(
                    operation_type='TARGET_SLICING',
                    user_id=user_info['user_id'],
                    project_id=int(project_id),
                    status='failed'
                )
            except Exception as log_error:
                print(f"记录权限不足失败日志失败: {str(log_error)}")
            return jsonify({
                'code': 403,
                'message': '没有权限访问此项目'
            }), 403

        # 动态生成用户项目临时路径
        username = user_info['username']
        project_name = project.project_name

        # 输入文件：用户项目临时目录的fourth/output/output_with_regions.vtk
        step4_output_file = os.path.join(
            Config.INTERMEDIATE_DATA_DIR,
            f"{username}_{project_name}",
            "fourth",
            "output",
            "output_with_regions.vtk"
        )

        if not os.path.exists(step4_output_file):
            # 记录数据预处理未完成失败日志
            try:
                create_system_log(
                    operation_type='TARGET_SLICING',
                    user_id=user_info['user_id'],
                    project_id=int(project_id),
                    status='failed'
                )
            except Exception as log_error:
                print(f"记录数据预处理未完成失败日志失败: {str(log_error)}")
            return jsonify({
                'code': 400,
                'message': '请先完成数据预处理（第四步）'
            }), 400

        # 输出目录：用户项目临时目录的fifth/output
        output_dir = os.path.join(
            Config.INTERMEDIATE_DATA_DIR,
            f"{username}_{project_name}",
            "fifth",
            "output"
        )

        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)

        print(f"开始执行目标孔洞分析...")
        print(f"项目ID: {project_id}")
        print(f"输入文件: {step4_output_file}")
        print(f"输出目录: {output_dir}")

        # 构建第五步主函数脚本路径
        step5_main_script_path = os.path.join(
            Config.BASE_DIR,
            'hole-analysis',
            '第5步 寻找目标孔洞并切片',
            '自动切',
            '根据vtk去做',
            '自动切片（主函数）.py'
        )

        # 检查脚本文件是否存在
        if not os.path.exists(step5_main_script_path):
            # 记录脚本文件不存在失败日志
            try:
                create_system_log(
                    operation_type='TARGET_SLICING',
                    user_id=user_info['user_id'],
                    project_id=int(project_id),
                    status='failed'
                )
            except Exception as log_error:
                print(f"记录脚本文件不存在失败日志失败: {str(log_error)}")
            return jsonify({
                'code': 404,
                'message': f'目标孔洞分析主函数脚本不存在: {step5_main_script_path}'
            }), 404

        # 设置工作目录为脚本所在目录
        script_dir = os.path.dirname(step5_main_script_path)

        print(f"脚本路径: {step5_main_script_path}")
        print(f"工作目录: {script_dir}")

        # 创建进度文件，初始化为10%（请求验证通过）
        progress_file_path = os.path.join(output_dir, 'progress_status.json')
        initial_progress = {
            "progress": 10,
            "status": "请求验证通过",
            "message": "API请求参数验证完成",
            "timestamp": datetime.datetime.now().isoformat()
        }
        with open(progress_file_path, 'w', encoding='utf-8') as f:
            json.dump(initial_progress, f, ensure_ascii=False)
        
        # 使用异步方式执行分析脚本
        import threading
        
        def run_analysis_script():
            try:
                # 执行第五步主函数脚本，传递动态路径参数
                result = subprocess.run(
                    [sys.executable, step5_main_script_path,
                     f"--input-file={step4_output_file}",
                     f"--output-dir={output_dir}"],
                    cwd=script_dir,
                    text=True,
                    timeout=1800  # 30分钟超时
                )

                # 检查执行结果
                if result.returncode == 0:
                    print("第五步主函数执行成功，开始检查输出文件...")
                    
                    # 检查输出文件是否存在（使用动态输出目录）
                    analysis_params_file = os.path.join(output_dir, 'analysis_parameters.json')
                    combined_vtk_file = os.path.join(output_dir, 'combined_selected_regions.vtk')
                    
                    if os.path.exists(analysis_params_file) and os.path.exists(combined_vtk_file):
                        print("检测到输出文件存在，开始执行可视化脚本...")
                        
                        # 构建可视化脚本路径
                        visualization_script_path = os.path.join(
                            script_dir,
                            '输出平面方程并显示在画布上.py'
                        )
                        
                        if not os.path.exists(visualization_script_path):
                            # 记录数据库失败日志
                            try:
                                create_system_log(
                                    operation_type='TARGET_SLICING',
                                    user_id=user_info['user_id'],
                                    project_id=int(project_id),
                                    status='failed'
                                )
                            except Exception as db_log_error:
                                print(f"记录数据库失败日志失败: {str(db_log_error)}")
                            
                            # 更新进度为错误状态
                            error_progress = {
                                "progress": 0,
                                "status": "脚本不存在",
                                "message": f"可视化脚本不存在: {visualization_script_path}",
                                "timestamp": datetime.datetime.now().isoformat()
                            }
                            with open(progress_file_path, 'w', encoding='utf-8') as f:
                                json.dump(error_progress, f, ensure_ascii=False)
                            return
                        
                        # 执行可视化脚本，传递动态路径参数
                        # 构建正确的参数：params-file 和 vtk-file
                        params_file = os.path.join(output_dir, 'analysis_parameters.json')
                        vtk_file = os.path.join(output_dir, 'combined_selected_regions.vtk')
                        
                        vis_result = subprocess.run(
                            [sys.executable, visualization_script_path,
                             f"--params-file={params_file}",
                             f"--vtk-file={vtk_file}",
                             f"--output-dir={output_dir}"],
                            cwd=script_dir,
                            text=True,
                            timeout=600  # 10分钟超时
                        )
                        
                        if vis_result.returncode == 0:
                            # 检查生成的图像文件（使用动态输出目录）
                            output_image_file = os.path.join(output_dir, 'projected_2d_image_with_cut_plane_position.png')
                            
                            if os.path.exists(output_image_file):
                                # 同时保存到第五步脚本目录，方便查阅
                                try:
                                    import shutil
                                    step5_dir = os.path.join(Config.BASE_DIR, 'hole-analysis', '第5步 寻找目标孔洞并切片')
                                    os.makedirs(step5_dir, exist_ok=True)
                                    dest_image = os.path.join(step5_dir, 'projected_2d_image_with_cut_plane_position.png')
                                    shutil.copy2(output_image_file, dest_image)
                                    print(f"切面图已复制到: {dest_image}")
                                except Exception as copy_err:
                                    print(f"复制切面图到第五步目录失败: {str(copy_err)}")

                                # 记录成功日志（使用动态输出目录）
                                try:
                                    log_file_path = os.path.join(output_dir, 'analysis_log.txt')
                                    with open(log_file_path, 'a', encoding='utf-8') as log_file:
                                        log_file.write(f"[{datetime.datetime.now().isoformat()}] 目标孔洞分析成功 - 用户ID: {user_info['user_id']}, 项目ID: {project_id}\n")
                                except Exception as log_error:
                                    print(f"记录日志失败: {str(log_error)}")
                                
                                # 记录数据库成功日志
                                try:
                                    create_system_log(
                                        operation_type='TARGET_SLICING',
                                        user_id=user_info['user_id'],
                                        project_id=int(project_id),
                                        status='success'
                                    )
                                except Exception as db_log_error:
                                    print(f"记录数据库成功日志失败: {str(db_log_error)}")
                                
                                # 更新进度为100%（结果图像生成后）
                                final_progress = {
                                    "progress": 100,
                                    "status": "结果图像生成完成",
                                    "message": "目标孔洞分析流程已完成，PNG图像已生成",
                                    "timestamp": datetime.datetime.now().isoformat()
                                }
                                with open(progress_file_path, 'w', encoding='utf-8') as f:
                                    json.dump(final_progress, f, ensure_ascii=False)
                                
                                # 等待进度监控函数读取更新（给文件写入和监控检测留出时间）
                                import time
                                time.sleep(2)
                                print("进度已更新到100%（结果图像生成完成）")
                            else:
                                # 更新进度为错误状态
                                error_progress = {
                                    "progress": 0,
                                    "status": "图像文件缺失",
                                    "message": "可视化脚本执行成功但未生成图像文件",
                                    "timestamp": datetime.datetime.now().isoformat()
                                }
                                with open(progress_file_path, 'w', encoding='utf-8') as f:
                                    json.dump(error_progress, f, ensure_ascii=False)
                        else:
                            # 记录数据库失败日志
                            try:
                                create_system_log(
                                    operation_type='TARGET_SLICING',
                                    user_id=user_info['user_id'],
                                    project_id=int(project_id),
                                    status='failed'
                                )
                            except Exception as db_log_error:
                                print(f"记录数据库失败日志失败: {str(db_log_error)}")
                            
                            # 更新进度为错误状态
                            error_progress = {
                                "progress": 0,
                                "status": "可视化失败",
                                "message": f"可视化脚本执行失败，返回码: {vis_result.returncode}",
                                "timestamp": datetime.datetime.now().isoformat()
                            }
                            with open(progress_file_path, 'w', encoding='utf-8') as f:
                                json.dump(error_progress, f, ensure_ascii=False)
                    else:
                        # 记录失败日志（使用动态输出目录）
                        try:
                            log_file_path = os.path.join(output_dir, 'analysis_log.txt')
                            with open(log_file_path, 'a', encoding='utf-8') as log_file:
                                log_file.write(f"[{datetime.datetime.now().isoformat()}] 目标孔洞分析失败 - 输出文件不存在 - 用户ID: {user_info['user_id']}, 项目ID: {project_id}\n")
                        except Exception as log_error:
                            print(f"记录日志失败: {str(log_error)}")
                        
                        # 记录数据库失败日志
                        try:
                            create_system_log(
                                operation_type='TARGET_SLICING',
                                user_id=user_info['user_id'],
                                project_id=int(project_id),
                                status='failed'
                            )
                        except Exception as db_log_error:
                            print(f"记录数据库失败日志失败: {str(db_log_error)}")
                        
                        # 更新进度为错误状态
                        error_progress = {
                            "progress": 0,
                            "status": "输出文件缺失",
                            "message": "寻找目标孔洞失败：输出文件不存在",
                            "timestamp": datetime.datetime.now().isoformat()
                        }
                        with open(progress_file_path, 'w', encoding='utf-8') as f:
                            json.dump(error_progress, f, ensure_ascii=False)
                else:
                    # 记录失败日志（使用动态输出目录）
                    try:
                        log_file_path = os.path.join(output_dir, 'analysis_log.txt')
                        with open(log_file_path, 'a', encoding='utf-8') as log_file:
                            log_file.write(f"[{datetime.datetime.now().isoformat()}] 目标孔洞分析失败 - 脚本执行失败 - 用户ID: {user_info['user_id']}, 项目ID: {project_id}\n")
                    except Exception as log_error:
                        print(f"记录日志失败: {str(log_error)}")

                    # 记录数据库失败日志
                    try:
                        create_system_log(
                            operation_type='TARGET_SLICING',
                            user_id=user_info['user_id'],
                            project_id=int(project_id),
                            status='failed'
                        )
                    except Exception as db_log_error:
                        print(f"记录数据库失败日志失败: {str(db_log_error)}")

                    # 更新进度为错误状态
                    error_progress = {
                        "progress": 0,
                        "status": "执行失败",
                        "message": f"目标孔洞分析执行失败，返回码: {result.returncode}",
                        "timestamp": datetime.datetime.now().isoformat()
                    }
                    with open(progress_file_path, 'w', encoding='utf-8') as f:
                        json.dump(error_progress, f, ensure_ascii=False)
                        
            except subprocess.TimeoutExpired:
                # 记录数据库失败日志
                try:
                    create_system_log(
                        operation_type='TARGET_SLICING',
                        user_id=user_info['user_id'],
                        project_id=int(project_id),
                        status='failed'
                    )
                except Exception as db_log_error:
                    print(f"记录数据库失败日志失败: {str(db_log_error)}")
                
                # 更新进度为超时状态
                timeout_progress = {
                    "progress": 0,
                    "status": "执行超时",
                    "message": "目标孔洞分析执行超时（超过30分钟）",
                    "timestamp": datetime.datetime.now().isoformat()
                }
                with open(progress_file_path, 'w', encoding='utf-8') as f:
                    json.dump(timeout_progress, f, ensure_ascii=False)
            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()
                print(f"执行目标孔洞分析时发生错误: {str(e)}")
                print(f"错误堆栈: {error_trace}")

                # 记录数据库失败日志
                try:
                    create_system_log(
                        operation_type='TARGET_SLICING',
                        user_id=user_info['user_id'],
                        project_id=int(project_id),
                        status='failed'
                    )
                except Exception as db_log_error:
                    print(f"记录数据库失败日志失败: {str(db_log_error)}")

                # 更新进度为错误状态
                error_progress = {
                    "progress": 0,
                    "status": "执行异常",
                    "message": f"执行目标孔洞分析时发生错误: {str(e)}",
                    "timestamp": datetime.datetime.now().isoformat()
                }
                with open(progress_file_path, 'w', encoding='utf-8') as f:
                    json.dump(error_progress, f, ensure_ascii=False)
        
        # 启动异步执行线程
        analysis_thread = threading.Thread(target=run_analysis_script)
        analysis_thread.daemon = True
        analysis_thread.start()
        
        print("脚本已开始异步执行，返回成功响应")
        
        # 立即返回成功响应，让前端通过SSE监控进度
        return jsonify({
            'code': 200,
            'message': '目标孔洞分析已开始执行，请通过SSE连接监控进度',
            'progress_url': f'/api/hole-analysis/target-hole-analysis-progress?project_id={project_id}'
        })

    except subprocess.TimeoutExpired:
        # 记录目标孔洞分析超时失败日志
        try:
            create_system_log(
                operation_type='TARGET_SLICING',
                user_id=user_info['user_id'],
                project_id=int(project_id),
                status='failed'
            )
        except Exception as log_error:
            print(f"记录目标孔洞分析超时失败日志失败: {str(log_error)}")
        return jsonify({
            'code': 408,
            'message': '目标孔洞分析执行超时（超过30分钟），请检查文件大小或联系管理员'
        }), 408

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"执行目标孔洞分析时发生错误: {str(e)}")
        print(f"错误堆栈: {error_trace}")

        # 记录目标孔洞分析异常失败日志
        try:
            create_system_log(
                operation_type='TARGET_SLICING',
                user_id=user_info['user_id'],
                project_id=int(project_id),
                status='failed'
            )
        except Exception as log_error:
            print(f"记录目标孔洞分析异常失败日志失败: {str(log_error)}")

        return jsonify({
            'code': 500,
            'message': f'执行目标孔洞分析时发生错误: {str(e)}'
        }), 500


@hole_analysis_bp.route('/target-hole-progress/<int:project_id>', methods=['GET'])
@jwt_required
def get_target_hole_progress(project_id):
    """轮询目标孔洞分析进度"""
    try:
        user_info = request.user
        from app.models.project import Project
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'code': 404, 'message': '项目不存在'}), 404
        if project.user_id != user_info['user_id']:
            return jsonify({'code': 403, 'message': '没有权限访问此项目'}), 403

        username = user_info['username']
        project_name = project.project_name
        progress_file_path = os.path.join(
            Config.INTERMEDIATE_DATA_DIR,
            f"{username}_{project_name}",
            "fifth", "output", "progress_status.json"
        )

        if not os.path.exists(progress_file_path):
            return jsonify({'code': 200, 'data': {'progress': 0, 'status': '等待开始', 'message': '进度文件不存在'}}), 200

        with open(progress_file_path, 'r', encoding='utf-8') as f:
            progress_data = json.load(f)

        result = {
            'progress': progress_data.get('progress', 0),
            'status': progress_data.get('status', ''),
            'message': progress_data.get('message', ''),
            'timestamp': progress_data.get('timestamp', '')
        }

        return jsonify({'code': 200, 'data': result}), 200

    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)}), 500


@hole_analysis_bp.route('/projects/<int:project_id>/voi-3d-data', methods=['GET'])
@jwt_required
def get_voi_3d_data(project_id):
    """返回第四步形态清洗后的 VTP 文件（第五步 3D 切面展示使用）"""
    try:
        user_info = request.user
        from app.models.project import Project
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'code': 404, 'message': '项目不存在'}), 404
        if project.user_id != user_info['user_id']:
            return jsonify({'code': 403, 'message': '没有权限访问此项目'}), 403

        username = user_info['username']
        project_name = project.project_name

        vtp_path = os.path.join(
            Config.INTERMEDIATE_DATA_DIR,
            f"{username}_{project_name}",
            "fourth", "output", "output_with_regions_cleaned_v3.vtp"
        )
        if not os.path.exists(vtp_path):
            return jsonify({'code': 404, 'message': '清洗后的VTP文件不存在，请先完成第四步数据预处理'}), 404

        print(f"[voi-3d-data] 返回 cleaned VTP: {vtp_path}, 大小: {os.path.getsize(vtp_path)/1024/1024:.2f} MB")
        return send_file(
            vtp_path,
            as_attachment=True,
            download_name='output_with_regions_cleaned_v3.vtp',
            mimetype='application/octet-stream',
            conditional=True,
            etag=False,
            max_age=0
        )

    except Exception as e:
        import traceback
        print(f"[voi-3d-data] 错误: {traceback.format_exc()}")
        return jsonify({'code': 500, 'message': f'获取VTP文件失败: {str(e)}'}), 500


@hole_analysis_bp.route('/projects/<int:project_id>/cut-plane-params', methods=['GET'])
@jwt_required
def get_cut_plane_params(project_id):
    """读取analysis_parameters.json，返回切面法向量和原点"""
    try:
        user_info = request.user
        from app.models.project import Project
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'code': 404, 'message': '项目不存在'}), 404
        if project.user_id != user_info['user_id']:
            return jsonify({'code': 403, 'message': '没有权限访问此项目'}), 403

        username = user_info['username']
        project_name = project.project_name
        params_path = os.path.join(
            Config.INTERMEDIATE_DATA_DIR,
            f"{username}_{project_name}",
            "fifth", "output", "analysis_parameters.json"
        )
        if not os.path.exists(params_path):
            return jsonify({'code': 404, 'message': '分析参数文件不存在，请先完成目标孔洞分析'}), 404

        with open(params_path, 'r', encoding='utf-8') as f:
            params = json.load(f)

        return jsonify({
            'code': 200,
            'data': {
                'normal': params.get('best_plane'),
                'origin': params.get('centroid')
            }
        }), 200

    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)}), 500


@hole_analysis_bp.route('/target-hole-analysis-progress', methods=['GET'])
def target_hole_analysis_progress():
    """目标孔洞分析进度推送（SSE）- 监控真实处理进度（已废弃，保留兼容）"""
    try:
        # 获取项目ID参数
        project_id = request.args.get('project_id')
        if not project_id:
            return jsonify({
                'code': 400,
                'message': '项目ID不能为空'
            }), 400

        # 检查项目权限
        from app.models.project import Project
        from app.models.user import User
        project = Project.query.get(int(project_id))
        if not project:
            return jsonify({
                'code': 404,
                'message': '项目不存在'
            }), 404

        # 获取用户信息
        user = User.query.get(project.user_id)
        if not user:
            return jsonify({
                'code': 404,
                'message': '用户不存在'
            }), 404

        # 生成动态路径
        username = user.username
        project_name = project.project_name
        
        # 动态进度文件路径
        progress_file_path = os.path.join(
            Config.INTERMEDIATE_DATA_DIR,
            f"{username}_{project_name}",
            "fifth",
            "output",
            "progress_status.json"
        )

        # 动态PNG图像文件路径
        png_image_path = os.path.join(
            Config.INTERMEDIATE_DATA_DIR,
            f"{username}_{project_name}",
            "fifth",
            "output",
            "projected_2d_image_with_cut_plane_position.png"
        )

        print(f"进度监控路径配置:")
        print(f"- 进度文件: {progress_file_path}")
        print(f"- PNG图像: {png_image_path}")

        # 设置SSE响应头
        def generate():
            # 发送初始连接确认
            yield f"data: {json.dumps({'type': 'connected', 'message': 'SSE连接已建立'})}\n\n"

            # 步骤1 (10%)：请求验证通过后 - 立即发送
            progress_data_10 = {
                'type': 'progress',
                'progress': 10,
                'status': '请求验证通过',
                'message': 'API请求参数验证完成',
                'timestamp': datetime.datetime.now().isoformat()
            }
            yield f"data: {json.dumps(progress_data_10)}\n\n"

            # 监控进度文件，实时推送进度
            last_progress = 10
            processing_started = False
            progress_file_checked = False
            
            import time
            for i in range(1800):  # 最多等待30分钟
                # 检查进度文件是否存在
                if os.path.exists(progress_file_path):
                    try:
                        with open(progress_file_path, 'r', encoding='utf-8') as f:
                            progress_data = json.load(f)
                        
                        current_progress = progress_data.get('progress', last_progress)
                        
                        # 只有当进度有变化时才推送，防止重复推送
                        if current_progress > last_progress:
                            progress_data_current = {
                                'type': 'progress',
                                'progress': current_progress,
                                'status': progress_data.get('status', '处理中'),
                                'message': progress_data.get('message', '正在处理中'),
                                'timestamp': datetime.datetime.now().isoformat()
                            }
                            yield f"data: {json.dumps(progress_data_current)}\n\n"
                            last_progress = current_progress
                            progress_file_checked = True
                        
                        # 如果进度达到100%，检查PNG文件并发送结果（无论进度是否变化）
                        if current_progress >= 100:
                            # 检查PNG文件是否存在
                            if os.path.exists(png_image_path):
                                # 读取PNG图像文件并转换为base64
                                import base64
                                with open(png_image_path, 'rb') as image_file:
                                    image_data = base64.b64encode(image_file.read()).decode('utf-8')
                                
                                image_data_dict = {
                                    'type': 'image',
                                    'progress': 100,
                                    'status': '分析完成',
                                    'message': 'PNG图像已生成',
                                    'image_data': image_data,
                                    'timestamp': datetime.datetime.now().isoformat()
                                }
                                yield f"data: {json.dumps(image_data_dict)}\n\n"
                                
                                # 清理进度文件，避免下次使用时读取到旧数据
                                try:
                                    if os.path.exists(progress_file_path):
                                        os.remove(progress_file_path)
                                        print("进度文件已清理")
                                except Exception as e:
                                    print(f"清理进度文件失败: {str(e)}")
                                
                                break
                            else:
                                # 如果PNG文件不存在，等待一段时间后继续检查
                                if i % 5 == 0:  # 每5秒检查一次PNG文件
                                    print(f"等待PNG文件生成... ({i}秒)")
                                
                                # 如果等待超过60秒还没有PNG文件，发送完成消息
                                if i > 60:
                                    completed_data = {
                                        'type': 'completed',
                                        'progress': 100,
                                        'status': '分析完成',
                                        'message': '目标孔洞分析流程已完成，但PNG图像生成超时',
                                        'timestamp': datetime.datetime.now().isoformat()
                                    }
                                    yield f"data: {json.dumps(completed_data)}\n\n"
                                    
                                    # 清理进度文件
                                    try:
                                        if os.path.exists(progress_file_path):
                                            os.remove(progress_file_path)
                                            print("进度文件已清理（超时）")
                                    except Exception as e:
                                        print(f"清理进度文件失败: {str(e)}")
                                    
                                    break
                    except json.JSONDecodeError as e:
                        print(f"进度文件JSON格式错误: {str(e)}，等待文件写入完成")
                        time.sleep(0.5)  # 等待文件写入完成
                    except Exception as e:
                        print(f"读取进度文件失败: {str(e)}")
                else:
                    # 如果进度文件不存在，但已经检查过，说明处理可能已经结束
                    if progress_file_checked and i > 60:  # 超过1分钟没有进度文件
                        print("进度文件已消失，可能处理已完成")
                        if last_progress < 100:
                            # 发送处理中断消息
                            interrupted_data = {
                                'type': 'error',
                                'progress': last_progress,
                                'status': '处理中断',
                                'message': '处理过程中进度文件消失，可能处理被中断',
                                'timestamp': datetime.datetime.now().isoformat()
                            }
                            yield f"data: {json.dumps(interrupted_data)}\n\n"
                        break
                
                # 检查是否超时
                time.sleep(1)  # 每秒检查一次
            
            # 如果超时仍未完成
            if last_progress < 100:
                timeout_data = {
                    'type': 'error',
                    'progress': last_progress,
                    'status': '处理超时',
                    'message': '目标孔洞分析处理超时（30分钟）',
                    'timestamp': datetime.datetime.now().isoformat()
                }
                yield f"data: {json.dumps(timeout_data)}\n\n"

        return Response(generate(), mimetype='text/event-stream')

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"目标孔洞分析进度推送时发生错误: {str(e)}")
        print(f"错误堆栈: {error_trace}")

        return jsonify({
            'code': 500,
            'message': f'目标孔洞分析进度推送时发生错误: {str(e)}'
        }), 500


@hole_analysis_bp.route('/max-hole-3d-view', methods=['POST'])
@jwt_required
def get_max_hole_3d_view():
    """
    获取最大孔洞的3D切割效果视图数据
    """
    print("=== 开始处理最大孔洞3D视图请求 ===")
    try:
        # 从请求上下文获取用户信息
        user_info = request.user
        print(f"1. 获取到用户信息: {user_info}")

        # 获取请求参数
        data = request.get_json()
        print(f"2. 获取到请求参数: {data}")
        if not data:
            print("3. 请求参数为空，返回错误")
            # 记录参数验证失败日志
            try:
                create_system_log(
                    operation_type='MAX_HOLE_3D_VIEW',
                    user_id=user_info['user_id'],
                    status='failed'
                )
            except Exception as log_error:
                print(f"记录参数验证失败日志失败: {str(log_error)}")
            return jsonify({
                'code': 400,
                'message': '请求参数不能为空'
            }), 400

        project_id = data.get('project_id')
        print(f"3. 提取到项目ID: {project_id}")
        if not project_id:
            print("4. 项目ID为空，返回错误")
            # 记录项目ID缺失失败日志
            try:
                create_system_log(
                    operation_type='MAX_HOLE_3D_VIEW',
                    user_id=user_info['user_id'],
                    status='failed'
                )
            except Exception as log_error:
                print(f"记录项目ID缺失失败日志失败: {str(log_error)}")
            return jsonify({
                'code': 400,
                'message': '项目ID不能为空'
            }), 400

        # 检查项目权限
        print(f"4. 开始检查项目权限")
        from app.models.project import Project
        project = Project.query.get(int(project_id))
        if not project:
            print(f"5. 项目不存在，ID: {project_id}")
            # 记录项目不存在失败日志
            try:
                create_system_log(
                    operation_type='MAX_HOLE_3D_VIEW',
                    user_id=user_info['user_id'],
                    project_id=int(project_id),
                    status='failed'
                )
            except Exception as log_error:
                print(f"记录项目不存在失败日志失败: {str(log_error)}")
            return jsonify({
                'code': 404,
                'message': '项目不存在'
            }), 404

        if project.user_id != user_info['user_id']:
            print(f"5. 用户权限不足，用户ID: {user_info['user_id']}，项目ID: {project_id}")
            # 记录权限不足失败日志
            try:
                create_system_log(
                    operation_type='MAX_HOLE_3D_VIEW',
                    user_id=user_info['user_id'],
                    project_id=int(project_id),
                    status='failed'
                )
            except Exception as log_error:
                print(f"记录权限不足失败日志失败: {str(log_error)}")
            return jsonify({
                'code': 403,
                'message': '没有权限访问此项目'
            }), 403

        print(f"5. 权限检查通过，开始生成最大孔洞3D视图数据")
        print(f"6. 项目ID: {project_id}")

        # 动态生成用户项目临时路径
        username = user_info['username']
        project_name = project.project_name

        # 构建文件路径（使用动态路径）
        vtk_file_path = os.path.join(
            Config.INTERMEDIATE_DATA_DIR,
            f"{username}_{project_name}",
            "fourth",
            "output",
            "output_with_regions.vtk"
        )
        
        analysis_params_path = os.path.join(
            Config.INTERMEDIATE_DATA_DIR,
            f"{username}_{project_name}",
            "fifth",
            "output",
            "analysis_parameters.json"
        )
        
        print(f"7. VTK文件路径: {vtk_file_path}")
        print(f"8. 分析参数文件路径: {analysis_params_path}")
        
        # 检查文件是否存在
        if not os.path.exists(vtk_file_path):
            print(f"9. VTK文件不存在: {vtk_file_path}")
            # 记录VTK文件不存在失败日志
            try:
                create_system_log(
                    operation_type='MAX_HOLE_3D_VIEW',
                    user_id=user_info['user_id'],
                    project_id=int(project_id),
                    status='failed'
                )
            except Exception as log_error:
                print(f"记录VTK文件不存在失败日志失败: {str(log_error)}")
            return jsonify({
                'code': 404,
                'message': f'VTK文件不存在: {vtk_file_path}'
            }), 404
        
        if not os.path.exists(analysis_params_path):
            print(f"9. 分析参数文件不存在: {analysis_params_path}")
            # 记录分析参数文件不存在失败日志
            try:
                create_system_log(
                    operation_type='MAX_HOLE_3D_VIEW',
                    user_id=user_info['user_id'],
                    project_id=int(project_id),
                    status='failed'
                )
            except Exception as log_error:
                print(f"记录分析参数文件不存在失败日志失败: {str(log_error)}")
            return jsonify({
                'code': 404,
                'message': f'分析参数文件不存在: {analysis_params_path}'
            }), 404
        
        print(f"9. 文件检查通过，开始导入切片数据模块")
        
        # 导入切片数据模块
        import sys
        slice_data_path = os.path.join(
            Config.BASE_DIR,
            'hole-analysis',
            '第5步 寻找目标孔洞并切片',
            '自动切',
            '根据vtk去做',
            'get_3d_slice_data.py'
        )
        
        # 确保模块路径在sys.path中
        sys.path.append(os.path.dirname(slice_data_path))
        print(f"10. 模块路径添加成功")
        
        # 动态导入模块
        from get_3d_slice_data import get_slice_data_from_params
        print(f"11. 成功导入切片数据模块")
        
        # 加载分析参数
        import json
        with open(analysis_params_path, 'r', encoding='utf-8') as f:
            analysis_params = json.load(f)
        print(f"12. 成功加载分析参数")
        
        # 获取切片数据
        print(f"13. 开始获取切片数据")
        slice_data = get_slice_data_from_params(vtk_file_path, analysis_params)
        print(f"14. 切片数据获取成功，点数: {slice_data['n_points']}, 线数: {slice_data['n_lines']}")
        
        # 将数据转换为JSON并压缩
        import gzip
        import json
        json_data = json.dumps(slice_data, ensure_ascii=False)
        compressed_data = gzip.compress(json_data.encode('utf-8'))
        print(f"15. 数据压缩成功，压缩后大小: {len(compressed_data) / 1024:.2f} KB")
        
        # 记录成功日志
        try:
            create_system_log(
                operation_type='MAX_HOLE_3D_VIEW',
                user_id=user_info['user_id'],
                project_id=int(project_id),
                status='success'
            )
            print(f"16. 成功记录系统日志")
        except Exception as log_error:
            print(f"16. 记录日志失败: {str(log_error)}")
        
        # 返回压缩后的JSON数据
        print(f"17. 开始返回压缩数据")
        return Response(
            compressed_data,
            content_type='application/json',
            headers={
                'Content-Encoding': 'gzip',
                'Content-Disposition': 'attachment; filename="vtk_3d_data.gz"'
            }
        )
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"生成最大孔洞3D视图数据时发生错误: {str(e)}")
        print(f"错误堆栈: {error_trace}")

        # 记录最大孔洞3D视图异常失败日志
        try:
            create_system_log(
                operation_type='MAX_HOLE_3D_VIEW',
                user_id=user_info['user_id'],
                project_id=int(project_id),
                status='failed'
            )
        except Exception as log_error:
            print(f"记录最大孔洞3D视图异常失败日志失败: {str(log_error)}")

        return jsonify({
            'code': 500,
            'message': f'生成最大孔洞3D视图数据时发生错误: {str(e)}'
        }), 500
    finally:
        print("=== 最大孔洞3D视图请求处理结束 ===")


@hole_analysis_bp.route('/morphological-analysis', methods=['POST'])
@jwt_required
def execute_morphological_analysis():
    """执行形态学分析（第六步）"""
    try:
        # 从请求上下文获取用户信息
        user_info = request.user

        # 获取请求参数
        data = request.get_json()
        if not data:
            # 记录参数验证失败日志
            try:
                create_system_log(
                    operation_type='MORPHOLOGICAL_ANALYSIS',
                    user_id=user_info['user_id'],
                    status='failed'
                )
            except Exception as log_error:
                print(f"记录参数验证失败日志失败: {str(log_error)}")
            return jsonify({
                'code': 400,
                'message': '请求参数不能为空'
            }), 400

        project_id = data.get('project_id')
        if not project_id:
            # 记录项目ID缺失失败日志
            try:
                create_system_log(
                    operation_type='MORPHOLOGICAL_ANALYSIS',
                    user_id=user_info['user_id'],
                    status='failed'
                )
            except Exception as log_error:
                print(f"记录项目ID缺失失败日志失败: {str(log_error)}")
            return jsonify({
                'code': 400,
                'message': '项目ID不能为空'
            }), 400

        # 检查项目权限
        from app.models.project import Project
        project = Project.query.get(int(project_id))
        if not project:
            # 记录项目不存在失败日志
            try:
                create_system_log(
                    operation_type='MORPHOLOGICAL_ANALYSIS',
                    user_id=user_info['user_id'],
                    project_id=int(project_id),
                    status='failed'
                )
            except Exception as log_error:
                print(f"记录项目不存在失败日志失败: {str(log_error)}")
            return jsonify({
                'code': 404,
                'message': '项目不存在'
            }), 404

        if project.user_id != user_info['user_id']:
            # 记录权限不足失败日志
            try:
                create_system_log(
                    operation_type='MORPHOLOGICAL_ANALYSIS',
                    user_id=user_info['user_id'],
                    project_id=int(project_id),
                    status='failed'
                )
            except Exception as log_error:
                print(f"记录权限不足失败日志失败: {str(log_error)}")
            return jsonify({
                'code': 403,
                'message': '没有权限访问此项目'
            }), 403

        # 动态生成用户项目临时路径
        username = user_info['username']
        project_name = project.project_name

        # 输入文件：用户项目临时目录的fifth/output/combined_selected_regions.vtk
        input_vtk_file = os.path.join(
            Config.INTERMEDIATE_DATA_DIR,
            f"{username}_{project_name}",
            "fourth",
            "output",
            "output_with_regions_cleaned_v3.vtk"
        )

        # 检查输入文件是否存在
        if not os.path.exists(input_vtk_file):
            # 记录目标孔洞分析未完成失败日志
            try:
                create_system_log(
                    operation_type='MORPHOLOGICAL_ANALYSIS',
                    user_id=user_info['user_id'],
                    project_id=int(project_id),
                    status='failed'
                )
            except Exception as log_error:
                print(f"记录目标孔洞分析未完成失败日志失败: {str(log_error)}")
            return jsonify({
                'code': 400,
                'message': '请先完成第五步目标孔洞分析'
            }), 400

        # 输出目录：用户项目临时目录的sixth/output
        output_dir = os.path.join(
            Config.INTERMEDIATE_DATA_DIR,
            f"{username}_{project_name}",
            "sixth",
            "output"
        )

        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)

        # 构建Python脚本路径
        script_path = os.path.join(
            Config.BASE_DIR,
            'hole-analysis',
            '第6步 形态学分析',
            '参数输出加判别.py'
        )

        # 检查脚本文件是否存在
        if not os.path.exists(script_path):
            # 记录脚本文件不存在失败日志
            try:
                create_system_log(
                    operation_type='MORPHOLOGICAL_ANALYSIS',
                    user_id=user_info['user_id'],
                    project_id=int(project_id),
                    status='failed'
                )
            except Exception as log_error:
                print(f"记录脚本文件不存在失败日志失败: {str(log_error)}")
            return jsonify({
                'code': 404,
                'message': f'形态学分析脚本文件不存在: {script_path}'
            }), 404

        # 设置工作目录为脚本所在目录
        script_dir = os.path.dirname(script_path)

        print(f"开始执行形态学分析...")
        print(f"输入文件: {input_vtk_file}")
        print(f"输出目录: {output_dir}")
        print(f"脚本路径: {script_path}")

        # 执行Python脚本，传递输入和输出路径参数
        result = subprocess.run(
            [sys.executable, script_path, input_vtk_file, "--output-dir", output_dir],
            cwd=script_dir,
            capture_output=True,
            text=True,
            timeout=3600  # 1小时超时
        )

        # 检查执行结果
        if result.returncode == 0:
            # 检查输出文件是否生成
            excel_file = os.path.join(output_dir, "智能鉴定与三维全参数矩阵.xlsx")
            csv_file = os.path.join(output_dir, "单体孔洞参数明细.csv")
            
            if not (os.path.exists(excel_file) and os.path.exists(csv_file)):
                # 记录输出文件未生成失败日志
                try:
                    create_system_log(
                        operation_type='MORPHOLOGICAL_ANALYSIS',
                        user_id=user_info['user_id'],
                        project_id=int(project_id),
                        status='failed'
                    )
                except Exception as log_error:
                    print(f"记录输出文件未生成失败日志失败: {str(log_error)}")
                return jsonify({
                    'code': 500,
                    'message': '形态学分析执行成功，但未生成预期输出文件'
                }), 500

            # 读取文件内容
            try:
                with open(excel_file, 'rb') as f:
                    excel_content = f.read()
                with open(csv_file, 'rb') as f:
                    csv_content = f.read()

                # 将二进制内容转换为base64编码，便于JSON传输
                import base64
                excel_base64 = base64.b64encode(excel_content).decode('utf-8')
                csv_base64 = base64.b64encode(csv_content).decode('utf-8')

            except Exception as e:
                print(f"读取文件内容失败: {str(e)}")
                return jsonify({
                    'code': 500,
                    'message': f'读取分析结果文件失败: {str(e)}'
                }), 500

            # 将分析结果写入数据库
            try:
                import pandas as pd
                from app.models.hole_data import HoleData
                from app.models.features import Features
                from app.models import db

                # ---------- 解析 Excel 全局特征，写入 hole_data ----------
                import openpyxl
                wb_result = openpyxl.load_workbook(excel_file, data_only=True)
                ws_global = wb_result['智能鉴定与全局特征']

                # 将 Excel 内容读成 {参数名: 数值} 的字典（去掉大类标题行）
                param_map = {}
                for row in ws_global.iter_rows(min_row=2, values_only=True):
                    name, value, unit = row[0], row[1], row[2]
                    if name and not str(name).startswith('■') and value is not None:
                        param_map[str(name).strip()] = value

                # 中文参数名 → ORM字段名映射（只取到最大体积跳跃比）
                global_field_map = {
                    '孔洞总数量': 'total_number_of_voids',
                    '孔洞空间密度': 'void_space_density',
                    '孔洞总体积': 'total_void_volume',
                    '孔洞总表面积': 'total_void_surface_area',
                    '最大体积': 'maximum_volume',
                    '平均体积': 'mean_volume',
                    '最小体积': 'minimum_volume',
                    '最大表面积': 'maximum_surface_area',
                    '平均表面积': 'mean_surface_area',
                    '最小表面积': 'minimum_surface_area',
                    '最大等效直径': 'maximum_equivalent_diameter',
                    '平均等效直径': 'mean_equivalent_diameter',
                    '最小等效直径': 'minimum_equivalent_diameter',
                    '最大球度': 'maximum_sphericity',
                    '平均球度': 'mean_sphericity',
                    '最小球度': 'minimum_sphericity',
                    '最大矩度': 'maximum_rectangularity',
                    '平均矩度': 'mean_rectangularity',
                    '最小矩度': 'minimum_rectangularity',
                    '最大轴比': 'maximum_aspect_ratio',
                    '平均轴比': 'mean_aspect_ratio',
                    '最小轴比': 'minimum_aspect_ratio',
                    '最大长边': 'maximum_long_edge',
                    '平均长边': 'mean_long_edge',
                    '最小长边': 'minimum_long_edge',
                    '最大中心距': 'maximum_center_distance',
                    '平均中心距': 'mean_center_distance',
                    '最小中心距': 'minimum_center_distance',
                    '最大孔洞体积占比': 'maximum_void_volume_fraction',
                    '体积变异系数 (CV)': 'volume_coefficient_of_variation',
                    '体积基尼系数 (Gini)': 'volume_gini_coefficient',
                    '最大体积跳跃比': 'maximum_volume_jump_ratio',
                }

                hole_data_kwargs = {'project_id': int(project_id)}
                for zh_name, field in global_field_map.items():
                    hole_data_kwargs[field] = param_map.get(zh_name)

                # 删除旧记录再插入，保证每个项目只有一条
                HoleData.query.filter_by(project_id=int(project_id)).delete()
                hole_data_record = HoleData(**hole_data_kwargs)
                db.session.add(hole_data_record)

                # ---------- 解析 CSV 前20条单体孔洞，写入 features ----------
                df_csv = pd.read_csv(csv_file, encoding='utf-8-sig')
                df_top20 = df_csv.head(20)

                # 获取当前操作日志ID（最新一条 MORPHOLOGICAL_ANALYSIS success 记录）
                from app.models.operation_logs import OperationLog
                op_log = OperationLog.query.filter_by(
                    project_id=int(project_id),
                    operation_type='MORPHOLOGICAL_ANALYSIS'
                ).order_by(OperationLog.id.desc()).first()
                op_id = op_log.id if op_log else None

                # 删除该项目旧的 features 记录再插入
                Features.query.filter_by(project_id=int(project_id)).delete()
                now = datetime.datetime.now()
                for _, row in df_top20.iterrows():
                    feat = Features(
                        project_id=int(project_id),
                        hole_id=int(row['孔洞编号']),
                        volume=float(row['体积 (mm³)']),
                        surface_area=float(row['表面积 (mm²)']),
                        equivalent_diameter=float(row['等效直径 (mm)']),
                        sphericity=float(row['球度']),
                        rectangularity=float(row['矩度']),
                        aspect_ratio=float(row['主轴比']),
                        long_edge=float(row['长边 (mm)']),
                        center_distance=float(row['中心距 (mm)']),
                        operation_id=op_id,
                        analysis_time=now
                    )
                    db.session.add(feat)

                db.session.commit()
                print(f"数据库写入完成：hole_data 1条，features {len(df_top20)}条")

            except Exception as db_error:
                db.session.rollback()
                print(f"数据库写入失败（不影响文件返回）: {str(db_error)}")

            # 记录成功日志
            try:
                create_system_log(
                    operation_type='MORPHOLOGICAL_ANALYSIS',
                    user_id=user_info['user_id'],
                    project_id=int(project_id),
                    status='success'
                )
                print("形态学分析处理完成，文件内容已读取")
            except Exception as log_error:
                print(f"记录日志失败: {str(log_error)}")

            return jsonify({
                'code': 200,
                'message': '形态学分析处理完成',
                'data': {
                    'input_file': input_vtk_file,
                    'output_dir': output_dir,
                    'excel_content': excel_base64,  # 直接返回文件内容
                    'csv_content': csv_base64,       # 直接返回文件内容
                    'excel_filename': '智能鉴定与三维全参数矩阵.xlsx',
                    'csv_filename': '单体孔洞参数明细.csv',
                    'output': result.stdout
                }
            }), 200
        else:
            # 记录脚本执行失败日志
            try:
                create_system_log(
                    operation_type='MORPHOLOGICAL_ANALYSIS',
                    user_id=user_info['user_id'],
                    project_id=int(project_id),
                    status='failed'
                )
            except Exception as log_error:
                print(f"记录脚本执行失败日志失败: {str(log_error)}")
            
            error_message = f'形态学分析脚本执行失败: {result.stderr}'
            print(error_message)
            return jsonify({
                'code': 500,
                'message': error_message
            }), 500

    except subprocess.TimeoutExpired:
        # 记录超时失败日志
        try:
            create_system_log(
                operation_type='MORPHOLOGICAL_ANALYSIS',
                user_id=user_info['user_id'],
                project_id=int(project_id),
                status='failed'
            )
        except Exception as log_error:
            print(f"记录超时失败日志失败: {str(log_error)}")
        
        return jsonify({
            'code': 408,
            'message': '形态学分析执行超时（超过1小时）'
        }), 408
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"执行形态学分析时发生错误: {str(e)}")
        print(f"错误堆栈: {error_trace}")

        # 记录形态学分析异常失败日志
        try:
            create_system_log(
                operation_type='MORPHOLOGICAL_ANALYSIS',
                user_id=user_info['user_id'],
                project_id=int(project_id),
                status='failed'
            )
        except Exception as log_error:
            print(f"记录形态学分析异常失败日志失败: {str(log_error)}")

        return jsonify({
            'code': 500,
            'message': f'执行形态学分析时发生错误: {str(e)}'
        }), 500


@hole_analysis_bp.route('/download-morphological-file', methods=['GET'])
@jwt_required
def download_morphological_file():
    """下载形态学分析文件"""
    try:
        # 从请求上下文获取用户信息
        user_info = request.user

        # 获取请求参数
        file_type = request.args.get('type')  # 'excel' 或 'csv'
        project_id = request.args.get('project_id')

        if not file_type or not project_id:
            return jsonify({
                'code': 400,
                'message': '文件类型和项目ID不能为空'
            }), 400

        if file_type not in ['excel', 'csv']:
            return jsonify({
                'code': 400,
                'message': '文件类型必须是 excel 或 csv'
            }), 400

        # 检查项目权限
        from app.models.project import Project
        project = Project.query.get(int(project_id))
        if not project:
            return jsonify({
                'code': 404,
                'message': '项目不存在'
            }), 404

        if project.user_id != user_info['user_id']:
            return jsonify({
                'code': 403,
                'message': '没有权限访问此项目'
            }), 403

        # 动态生成文件路径
        username = user_info['username']
        project_name = project.project_name
        
        if file_type == 'excel':
            file_path = os.path.join(
                Config.INTERMEDIATE_DATA_DIR,
                f"{username}_{project_name}",
                "sixth",
                "output",
                "智能鉴定与三维全参数矩阵.xlsx"
            )
            filename = "智能鉴定与三维全参数矩阵.xlsx"
        else:
            file_path = os.path.join(
                Config.INTERMEDIATE_DATA_DIR,
                f"{username}_{project_name}",
                "sixth",
                "output",
                "单体孔洞参数明细.csv"
            )
            filename = "单体孔洞参数明细.csv"

        # 检查文件是否存在
        if not os.path.exists(file_path):
            return jsonify({
                'code': 404,
                'message': f'{file_type.upper()}文件不存在，请先执行形态学分析'
            }), 404

        # 返回文件下载
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"下载形态学分析文件时发生错误: {str(e)}")
        print(f"错误堆栈: {error_trace}")

        return jsonify({
            'code': 500,
            'message': f'下载文件时发生错误: {str(e)}'
        }), 500
