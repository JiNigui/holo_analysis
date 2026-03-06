from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from app.config.config import Config
from app.utils.jwt_utils import jwt_required
from app.api.logs import create_system_log, LOG_TYPES

upload_bp = Blueprint('upload', __name__)

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@upload_bp.route('/upload/image', methods=['POST'])
@jwt_required
def upload_image():
    """
    上传图像文件API
    需要JWT认证
    """
    try:
        # 从请求上下文获取用户信息
        user_info = request.user
        
        # 检查是否有文件被上传
        if 'file' not in request.files:
            return jsonify({
                'code': 400,
                'message': '没有选择文件'
            }), 400
            
        file = request.files['file']
        
        # 检查文件是否为空
        if file.filename == '':
            return jsonify({
                'code': 400,
                'message': '没有选择文件'
            }), 400
            
        # 检查文件扩展名
        if file and allowed_file(file.filename):
            # 安全地处理文件名
            filename = secure_filename(file.filename)
            
            # 获取项目ID（必须提供）
            project_id = request.form.get('project_id')
            if not project_id:
                return jsonify({
                    'code': 400,
                    'message': '项目ID不能为空，无法确定上传目录'
                }), 400
                
            step = request.form.get('step', 'step1')  # 默认第一步
            
            # 获取项目信息以确定项目名
            from app.models.project import Project
            project = Project.query.get(project_id)
            if not project:
                return jsonify({
                    'code': 404,
                    'message': '项目不存在'
                }), 404

            # 动态生成用户项目临时路径
            username = user_info['username']
            project_name = project.project_name
            
            # 根据步骤确定上传目录
            step_lower = str(step).lower().strip()
            if step_lower in ['step1', 'step_1', '1', '第一步', 'step 1']:
                # 第一步：上传到用户项目临时目录的first/input
                upload_dir = os.path.join(
                    Config.INTERMEDIATE_DATA_DIR,
                    f"{username}_{project_name}",
                    "first",
                    "input"
                )
            else:
                # 其他步骤：使用原有的项目目录结构
                upload_dir = os.path.join(
                    Config.UPLOAD_FOLDER,
                    'projects',
                    str(project_id),
                    step
                )
            
            # 确保目录存在
            os.makedirs(upload_dir, exist_ok=True)
            
            # 生成唯一文件名（避免覆盖）
            base_name, ext = os.path.splitext(filename)
            counter = 1
            unique_filename = filename
            
            while os.path.exists(os.path.join(upload_dir, unique_filename)):
                unique_filename = f"{base_name}_{counter}{ext}"
                counter += 1
            
            # 保存文件
            file_path = os.path.join(upload_dir, unique_filename)
            file.save(file_path)
            
            # 记录文件上传日志
            if project_id:
                create_system_log(
                    operation_type='FILE_UPLOAD',
                    user_id=user_info['user_id'],
                    project_id=int(project_id),
                    status='success',
                    details=f'上传图像文件: {unique_filename} (步骤: {step})'
                )
            
            return jsonify({
                'code': 200,
                'message': '文件上传成功',
                'data': {
                    'filename': unique_filename,
                    'file_path': file_path,
                    'relative_path': os.path.relpath(file_path, Config.UPLOAD_FOLDER),
                    'project_id': project_id,
                    'step': step
                }
            }), 200
        else:
            return jsonify({
                'code': 400,
                'message': f'不支持的文件类型。支持的类型: {Config.ALLOWED_EXTENSIONS}'
            }), 400
            
    except Exception as e:
        # 记录文件上传失败日志
        try:
            if project_id:
                create_system_log(
                    operation_type='FILE_UPLOAD',
                    user_id=user_info['user_id'],
                    project_id=int(project_id),
                    status='failed',
                    details=f'文件上传失败: {str(e)}'
                )
        except Exception as log_error:
            print(f"记录文件上传失败日志失败: {str(log_error)}")
        
        return jsonify({
            'code': 500,
            'message': f'文件上传失败：{str(e)}'
        }), 500

@upload_bp.route('/images/batch', methods=['POST'])
@jwt_required
def upload_images_batch():
    """
    批量上传图像文件API
    支持一次性上传多个文件，并清除旧文件
    需要JWT认证
    """
    try:
        # 从请求上下文获取用户信息
        user_info = request.user

        # 检查是否有文件被上传
        if 'files' not in request.files:
            return jsonify({
                'code': 400,
                'message': '没有选择文件'
            }), 400

        files = request.files.getlist('files')

        if not files or len(files) == 0:
            return jsonify({
                'code': 400,
                'message': '没有选择文件'
            }), 400

        # 获取项目ID和步骤
        project_id = request.form.get('project_id')
        step = request.form.get('step', 'step1')
        clear_old = request.form.get('clear_old', 'true').lower() == 'true'  # 是否清除旧文件

        # 必须提供项目ID才能确定上传目录
        if not project_id:
            return jsonify({
                'code': 400,
                'message': '项目ID不能为空，无法确定上传目录'
            }), 400

        # 获取项目信息以确定项目名
        from app.models.project import Project
        project = Project.query.get(project_id)
        if not project:
            return jsonify({
                'code': 404,
                'message': '项目不存在'
            }), 404

        # 动态生成用户项目临时路径
        username = user_info['username']
        project_name = project.project_name
        
        # 根据步骤确定上传目录
        step_lower = str(step).lower().strip()
        if step_lower in ['step1', 'step_1', '1', '第一步', 'step 1']:
            # 第一步：上传到用户项目临时目录的first/input
            upload_dir = os.path.join(
                Config.INTERMEDIATE_DATA_DIR,
                f"{username}_{project_name}",
                "first",
                "input"
            )
        else:
            # 其他步骤：使用原有的项目目录结构
            upload_dir = os.path.join(
                Config.UPLOAD_FOLDER,
                'projects',
                str(project_id),
                step
            )

        # 确保目录存在
        os.makedirs(upload_dir, exist_ok=True)

        # 清除旧文件（如果启用）
        if clear_old:
            try:
                # 删除目录中的所有文件，但保留目录
                for filename in os.listdir(upload_dir):
                    file_path = os.path.join(upload_dir, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
            except Exception as clear_error:
                print(f"清除旧文件失败: {str(clear_error)}")
                # 清除失败不影响上传，继续执行

        # 存储上传结果
        uploaded_files = []
        failed_files = []

        # 处理每个文件
        for file in files:
            if file.filename == '':
                continue

            # 检查文件扩展名
            if not allowed_file(file.filename):
                failed_files.append({
                    'filename': file.filename,
                    'reason': f'不支持的文件类型。支持的类型: {Config.ALLOWED_EXTENSIONS}'
                })
                continue

            # 安全地处理文件名
            filename = secure_filename(file.filename)

            if not filename or filename == '':
                failed_files.append({
                    'filename': file.filename,
                    'reason': '文件名无效'
                })
                continue

            # 保存文件（直接使用原文件名，因为已经清除了旧文件）
            file_path = os.path.join(upload_dir, filename)

            try:
                file.save(file_path)
                uploaded_files.append({
                    'filename': filename,
                    'file_path': file_path,
                    'relative_path': os.path.relpath(file_path, Config.UPLOAD_FOLDER) if upload_dir != Config.HOLE_ANALYSIS_UPLOAD_FOLDER else filename
                })
            except Exception as save_error:
                failed_files.append({
                    'filename': filename,
                    'reason': f'文件保存失败：{str(save_error)}'
                })

        # 记录上传日志
        if project_id and len(uploaded_files) > 0:
            try:
                create_system_log(
                    operation_type='FILE_UPLOAD_BATCH',
                    user_id=user_info['user_id'],
                    project_id=int(project_id),
                    status='success'
                )
            except Exception as log_error:
                print(f"记录上传日志失败: {str(log_error)}")

        # 返回结果
        return jsonify({
            'code': 200,
            'message': f'成功上传 {len(uploaded_files)} 个文件' + (f'，{len(failed_files)} 个文件失败' if failed_files else ''),
            'data': {
                'uploaded_count': len(uploaded_files),
                'failed_count': len(failed_files),
                'uploaded_files': uploaded_files,
                'failed_files': failed_files,
                'upload_dir': upload_dir,
                'project_id': project_id,
                'step': step
            }
        }), 200

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"批量文件上传异常: {str(e)}")
        print(f"错误堆栈: {error_trace}")
        
        # 记录批量文件上传失败日志
        try:
            if project_id:
                create_system_log(
                    operation_type='FILE_UPLOAD_BATCH',
                    user_id=user_info['user_id'],
                    project_id=int(project_id),
                    status='failed',
                    details=f'批量文件上传失败: {str(e)}'
                )
        except Exception as log_error:
            print(f"记录批量文件上传失败日志失败: {str(log_error)}")
        
        return jsonify({
            'code': 500,
            'message': f'批量文件上传失败：{str(e)}'
        }), 500

@upload_bp.route('/upload/delete', methods=['POST'])
@jwt_required
def delete_uploaded_file():
    """
    删除已上传的文件API
    需要JWT认证
    """
    try:
        # 从请求上下文获取用户信息
        user_info = request.user
        
        data = request.get_json()
        
        if not data or not data.get('file_path'):
            return jsonify({
                'code': 400,
                'message': '文件路径不能为空'
            }), 400
            
        file_path = data.get('file_path')
        
        # 安全检查：确保文件路径在UPLOAD_FOLDER内
        if not os.path.abspath(file_path).startswith(os.path.abspath(Config.UPLOAD_FOLDER)):
            return jsonify({
                'code': 403,
                'message': '无权删除此文件'
            }), 403
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return jsonify({
                'code': 404,
                'message': '文件不存在'
            }), 404
            
        # 删除文件
        os.remove(file_path)
        
        # 记录文件删除日志
        create_system_log(
            operation_type='FILE_DELETE',
            user_id=user_info['user_id'],
            status='success',
            details=f'删除文件: {os.path.basename(file_path)}'
        )
        
        return jsonify({
            'code': 200,
            'message': '文件删除成功'
        }), 200
        
    except Exception as e:
        # 记录文件删除失败日志
        try:
            create_system_log(
                operation_type='FILE_DELETE',
                user_id=user_info['user_id'],
                status='failed',
                details=f'文件删除失败: {str(e)}'
            )
        except Exception as log_error:
            print(f"记录文件删除失败日志失败: {str(log_error)}")
        
        return jsonify({
            'code': 500,
            'message': f'文件删除失败：{str(e)}'
        }), 500