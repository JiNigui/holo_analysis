from flask import Blueprint, request, jsonify
from app.models import db, Project
from app.utils.jwt_utils import jwt_required, admin_required
from app.api.logs import create_system_log, LOG_TYPES

project_bp = Blueprint('project', __name__)

@project_bp.route('/projects', methods=['POST'])
@jwt_required
def create_project():
    """
    创建项目API
    需要JWT认证
    """
    try:
        # 获取请求数据
        data = request.get_json()
        
        if not data or not data.get('project_name'):
            return jsonify({
                'code': 400,
                'message': '项目名称不能为空'
            }), 400
        
        # 从请求上下文获取用户信息
        user_info = request.user
        
        # 检查项目名是否已存在
        existing_project = Project.query.filter_by(
            project_name=data.get('project_name'),
            user_id=user_info['user_id']
        ).first()
        
        if existing_project:
            return jsonify({
                'code': 400,
                'message': '项目名称已存在'
            }), 400
        
        # 新增：创建项目临时目录
        from app.utils.directory_manager import DirectoryManager
        
        # 获取用户名和项目名
        username = user_info['username']
        project_name = data.get('project_name')
        
        # 创建项目临时目录
        try:
            project_temp_dir = DirectoryManager.create_project_directory(username, project_name)
            print(f"为项目 {project_name} 创建临时目录: {project_temp_dir}")
        except Exception as dir_error:
            return jsonify({
                'code': 500,
                'message': f'创建项目临时目录失败：{str(dir_error)}'
            }), 500
        
        # 创建新项目
        new_project = Project(
            project_name=project_name,
            description=data.get('description', ''),
            user_id=user_info['user_id']
        )
        
        # 保存到数据库
        db.session.add(new_project)
        db.session.commit()
        
        # 记录项目创建日志
        create_system_log(
            operation_type='PROJECT_CREATE',  # 操作类型常量
            user_id=user_info['user_id'],
            project_id=new_project.id,
            status='success'
        )
        
        return jsonify({
            'code': 200,
            'message': '项目创建成功',
            'data': {
                'id': new_project.id,
                'project_name': new_project.project_name,
                'description': new_project.description,
                'user_id': new_project.user_id,
                'created_time': new_project.created_time.isoformat()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        
        # 记录项目创建失败日志
        try:
            create_system_log(
                operation_type='PROJECT_CREATE',
                user_id=user_info['user_id'],
                status='failed'
            )
        except Exception as log_error:
            print(f"记录项目创建失败日志失败: {str(log_error)}")
        
        return jsonify({
            'code': 500,
            'message': f'项目创建失败：{str(e)}'
        }), 500

@project_bp.route('/projects/<int:project_id>', methods=['DELETE'])
@jwt_required
def delete_project(project_id):
    """
    删除项目API
    需要JWT认证
    """
    try:
        # 从请求上下文获取用户信息
        user_info = request.user
        
        # 查找项目
        project = Project.query.get(project_id)
        
        if not project:
            return jsonify({
                'code': 404,
                'message': '项目不存在'
            }), 404
        
        # 检查权限：只能删除自己的项目，或者管理员可以删除任何项目
        if project.user_id != user_info['user_id'] and user_info['role'] != 'admin':
            return jsonify({
                'code': 403,
                'message': '没有权限删除此项目'
            }), 403
        
        # 新增：删除项目临时目录
        from app.utils.directory_manager import DirectoryManager
        
        # 获取用户名和项目名
        username = user_info['username']
        project_name = project.project_name
        
        # 删除项目临时目录
        try:
            DirectoryManager.delete_project_directory(username, project_name)
            print(f"删除项目 {project_name} 的临时目录")
        except Exception as dir_error:
            # 目录删除失败不影响数据库操作，只记录日志
            print(f"删除项目临时目录失败：{str(dir_error)}")
        
        # 记录项目删除日志
        create_system_log(
            operation_type='PROJECT_DELETE',  # 操作类型常量
            user_id=user_info['user_id'],
            project_id=project_id,
            status='success'
        )
        
        # 删除项目
        db.session.delete(project)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '项目删除成功'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        
        # 记录项目删除失败日志
        try:
            create_system_log(
                operation_type='PROJECT_DELETE',
                user_id=user_info['user_id'],
                project_id=project_id,
                status='failed'
            )
        except Exception as log_error:
            print(f"记录项目删除失败日志失败: {str(log_error)}")
        
        return jsonify({
            'code': 500,
            'message': f'项目删除失败：{str(e)}'
        }), 500

@project_bp.route('/projects', methods=['GET'])
@jwt_required
def get_projects():
    """
    获取用户项目列表API
    需要JWT认证
    """
    try:
        # 从请求上下文获取用户信息
        user_info = request.user
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # 构建查询：所有用户（包括管理员）只能看到自己的项目
        query = Project.query.filter_by(user_id=user_info['user_id'])
        
        # 按创建时间倒序排列
        query = query.order_by(Project.created_time.desc())
        
        # 分页查询
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # 转换为字典列表
        projects_list = []
        for project in pagination.items:
            projects_list.append({
                'id': project.id,
                'project_name': project.project_name,
                'description': project.description,
                'user_id': project.user_id,
                'created_time': project.created_time.isoformat(),
                'updated_time': project.updated_time.isoformat()
            })
        
        return jsonify({
            'code': 200,
            'message': '获取项目列表成功',
            'data': {
                'projects': projects_list,
                'total': pagination.total,
                'page': page,
                'per_page': per_page,
                'pages': pagination.pages
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取项目列表失败：{str(e)}'
        }), 500

@project_bp.route('/projects/<int:project_id>', methods=['GET'])
@jwt_required
def get_project(project_id):
    """
    获取单个项目详情API
    需要JWT认证
    """
    try:
        # 从请求上下文获取用户信息
        user_info = request.user
        
        # 查找项目
        project = Project.query.get(project_id)
        
        if not project:
            return jsonify({
                'code': 404,
                'message': '项目不存在'
            }), 404
        
        # 检查权限：普通用户只能查看自己的项目，管理员可以查看任何项目
        if project.user_id != user_info['user_id'] and user_info['role'] != 'admin':
            return jsonify({
                'code': 403,
                'message': '没有权限查看此项目'
            }), 403
        
        return jsonify({
            'code': 200,
            'message': '获取项目详情成功',
            'data': {
                'id': project.id,
                'project_name': project.project_name,
                'description': project.description,
                'user_id': project.user_id,
                'created_time': project.created_time.isoformat(),
                'updated_time': project.updated_time.isoformat()
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取项目详情失败：{str(e)}'
        }), 500