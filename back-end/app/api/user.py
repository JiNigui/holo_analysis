from datetime import datetime
from flask import Blueprint, request, jsonify
from app.models import db, User
from app.utils.jwt_utils import generate_token, jwt_required, admin_required
from app.api.logs import create_system_log, LOG_TYPES

user_bp = Blueprint('user', __name__)

@user_bp.route('/login', methods=['POST'])
def login():
    """
    用户登录API
    接受用户名和密码，验证成功后返回JWT token
    """
    # 获取请求数据
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': '用户名和密码不能为空'}), 400
    
    # 查找用户
    user = User.query.filter_by(username=data.get('username')).first()
    
    # 验证用户凭据
    if not user or not user.verify_password(data.get('password')):
        # 记录登录失败日志
        try:
            create_system_log(
                operation_type=LOG_TYPES['USER_LOGIN'],
                user_id=user.id if user else None,
                status='failed'
            )
        except Exception as log_error:
            print(f"记录登录失败日志失败: {str(log_error)}")
        
        return jsonify({'message': '用户名或密码错误'}), 401
    
    # 检查是否已有活跃会话（单点登录验证）
    if user.current_session_id and user.session_created_at:
        # 检查会话是否过期（24小时）
        session_age = datetime.now() - user.session_created_at
        if session_age.total_seconds() <= 24 * 3600:  # 24小时内
            return jsonify({
                'code': 409,
                'message': '账号已在其他地方登录，请先退出其他设备或等待会话过期'
            }), 409
    
    # 更新用户的最后登录时间
    user.last_login = datetime.now()
    
    # 生成唯一会话ID
    import uuid
    session_id = str(uuid.uuid4())
    
    # 记录当前会话信息
    user.current_session_id = session_id
    user.session_created_at = datetime.now()
    
    # 生成JWT token（包含会话ID）
    token = generate_token(user.id, user.username, user.role, session_id)
    
    # 记录用户登录日志
    create_system_log(
        operation_type=LOG_TYPES['USER_LOGIN'],  # 操作类型即操作名称
        user_id=user.id,
        status='success'
    )
    
    # 提交数据库更改
    db.session.commit()
    
    # 返回token和用户信息
    return jsonify({
        'code': 200,
        'message': '登录成功',
        'token': token,
        'data': user.to_dict()
    }), 200

@user_bp.route('/logout', methods=['POST'])
@jwt_required
def logout():
    """
    用户登出API
    清除当前会话信息，实现安全登出
    """
    try:
        # 从请求上下文获取用户信息
        user_info = request.user
        
        # 从数据库获取用户
        user = User.query.get(user_info['user_id'])
        if user:
            # 清除会话信息
            user.current_session_id = None
            user.session_created_at = None
            db.session.commit()
        
        # 记录用户登出日志
        create_system_log(
            operation_type=LOG_TYPES['USER_LOGOUT'],  # 操作类型即操作名称
            user_id=user_info['user_id'],
            status='success'
        )
        
        return jsonify({
            'code': 200,
            'message': '登出成功'
        }), 200
    
    except Exception as e:
        # 记录登出失败日志
        try:
            user_info = request.user
            create_system_log(
                operation_type=LOG_TYPES['USER_LOGOUT'],
                user_id=user_info['user_id'],
                status='failed'
            )
        except Exception as log_error:
            print(f"记录登出失败日志失败: {str(log_error)}")
        
        return jsonify({
            'code': 500,
            'message': f'登出失败: {str(e)}'
        }), 500

@user_bp.route('/force-logout', methods=['POST'])
@admin_required
def force_logout():
    """
    强制下线其他设备API
    清除当前用户的会话信息，强制其他设备下线
    """
    try:
        # 从请求上下文获取用户信息
        user_info = request.user
        
        # 生成新的会话ID
        import uuid
        new_session_id = str(uuid.uuid4())
        
        # 从数据库获取用户
        user = User.query.get(user_info['user_id'])
        if user:
            # 更新会话信息（强制其他设备下线）
            user.current_session_id = new_session_id
            user.session_created_at = datetime.now()
            db.session.commit()
        
        # 记录强制下线日志
        create_system_log(
            operation_type='FORCE_LOGOUT',  # 自定义操作类型
            user_id=user_info['user_id'],
            status='success'
        )
        
        return jsonify({
            'code': 200,
            'message': '强制下线成功，其他设备已下线'
        }), 200
    
    except Exception as e:
        # 记录强制下线失败日志
        try:
            user_info = request.user
            create_system_log(
                operation_type='FORCE_LOGOUT',
                user_id=user_info['user_id'],
                status='failed'
            )
        except Exception as log_error:
            print(f"记录强制下线失败日志失败: {str(log_error)}")
        
        return jsonify({
            'code': 500,
            'message': f'强制下线失败: {str(e)}'
        }), 500

@user_bp.route('/check-session', methods=['GET'])
@jwt_required
def check_session():
    """
    检查会话有效性API
    专门用于前端导航守卫验证会话状态
    如果会话无效（账号在其他地方登录），返回401错误
    """
    # 从请求上下文获取用户信息
    user_info = request.user
    
    # 从数据库获取最新的用户信息
    user = User.query.get(user_info['user_id'])
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    
    # 检查会话ID是否匹配
    if user.current_session_id != user_info.get('session_id'):
        return jsonify({'message': '账号已在其他地方登录'}), 401
    
    # 检查会话是否过期（超过24小时）
    if user.session_created_at:
        session_age = datetime.now() - user.session_created_at
        if session_age.total_seconds() > 24 * 3600:  # 24小时
            return jsonify({'message': '会话已过期'}), 401
    
    return jsonify({
        'code': 200,
        'message': '会话有效'
    }), 200

@user_bp.route('/profile', methods=['GET', 'PUT'])
@jwt_required
def profile():
    """
    获取和修改用户个人信息
    需要JWT认证
    """
    # 从请求上下文获取用户信息
    # 这些信息是在jwt_required装饰器中添加的
    user_info = request.user
    
    # 从数据库获取最新的用户信息
    user = User.query.get(user_info['user_id'])
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    
    if request.method == 'GET':
        """获取用户个人信息"""
        return jsonify({
            'code': 200,
            'message': '获取用户信息成功',
            'data': user.to_dict()
        }), 200
    
    elif request.method == 'PUT':
        """修改用户个人信息"""
        try:
            # 获取请求数据
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'code': 400,
                    'message': '请求数据不能为空'
                }), 400
            
            # 获取密码相关字段
            old_password = data.get('old_password') or data.get('oldPassword')
            new_password = data.get('new_password') or data.get('newPassword')
            
            # 如果提供了密码相关字段，必须验证旧密码
            if old_password or new_password:
                if not old_password or not new_password:
                    return jsonify({'code': 400, 'message': '修改密码需要提供旧密码和新密码'}), 400
                
                # 验证旧密码
                if not user.verify_password(old_password):
                    return jsonify({'code': 400, 'message': '旧密码错误'}), 400
                
                # 设置新密码
                user.set_password(new_password)
                
                # 修改密码后，不更新会话ID，保持当前会话有效
                # 这样当前用户可以继续使用，其他设备的会话也继续有效
                # 只有当用户主动登出或会话过期时，才能重新登录
            else:
                return jsonify({
                    'code': 400,
                    'message': '没有检测到任何修改'
                }), 400
            
            # 保存到数据库
            db.session.commit()
            
            # 记录用户修改密码日志
            create_system_log(
                operation_type='USER_PASSWORD_CHANGE',
                user_id=user_info['user_id'],
                status='success'
            )
            
            return jsonify({
                'code': 200,
                'message': '密码修改成功'
            }), 200
            
        except Exception as e:
            db.session.rollback()
            
            # 记录密码修改失败日志
            try:
                create_system_log(
                    operation_type='USER_PASSWORD_CHANGE',
                    user_id=user_info['user_id'],
                    status='failed'
                )
            except Exception as log_error:
                print(f"记录密码修改失败日志失败: {str(log_error)}")
            
            return jsonify({
                'code': 500,
                'message': f'密码修改失败：{str(e)}'
            }), 500

@user_bp.route('/register', methods=['POST'])
@admin_required
def register():
    """
    用户注册API（仅管理员可调用）
    接受用户名、密码、角色，创建新用户
    """
    # 获取请求数据
    data = request.get_json()
    
    # 验证必填字段
    if not data or not data.get('username') or not data.get('password') or not data.get('role'):
        return jsonify({'message': '用户名、密码和角色不能为空'}), 400
    
    # 验证角色有效性
    if data.get('role') not in ['admin', 'user']:
        return jsonify({'message': '角色必须是admin或user'}), 400
    
    # 检查用户名是否已存在
    existing_user = User.query.filter_by(username=data.get('username')).first()
    if existing_user:
        return jsonify({'message': '用户名已存在'}), 400
    
    # 创建新用户
    new_user = User(
        username=data.get('username'),
        role=data.get('role')
    )
    
    # 设置加密密码
    new_user.set_password(data.get('password'))
    
    try:
        # 保存到数据库
        db.session.add(new_user)
        db.session.commit()
        
        # 记录用户注册日志（由管理员操作）
        current_user_info = request.user
        create_system_log(
            operation_type='USER_REGISTER',
            user_id=current_user_info['user_id'],  # 管理员ID
            status='success'
        )
        
        return jsonify({
            'code': 200,
            'message': '用户注册成功',
            'data': new_user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        
        # 记录用户注册失败日志
        try:
            current_user_info = request.user
            create_system_log(
                operation_type='USER_REGISTER',
                user_id=current_user_info['user_id'],  # 管理员ID
                status='failed'
            )
        except Exception as log_error:
            print(f"记录用户注册失败日志失败: {str(log_error)}")
        
        return jsonify({
            'code': 500,
            'message': f'注册失败：{str(e)}'
        }), 500

@user_bp.route('/users', methods=['GET'])
@admin_required
def get_all_users():
    """
    获取所有用户列表（仅管理员可调用）
    """
    try:
        # 获取所有用户
        users = User.query.all()
        
        # 转换为字典列表
        users_list = [user.to_dict() for user in users]
        
        return jsonify({
            'code': 200,
            'message': '获取用户列表成功',
            'data': users_list
        }), 200
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取用户列表失败：{str(e)}'
        }), 500

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """
    删除用户（仅管理员可调用）
    处理外键约束：先删除关联数据，再删除用户
    """
    try:
        # 查找要删除的用户
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'code': 404,
                'message': '用户不存在'
            }), 404
        
        # 防止删除当前登录的管理员自己
        current_user_info = request.user
        if user.id == current_user_info['user_id']:
            return jsonify({
                'code': 400,
                'message': '不能删除当前登录的用户'
            }), 400
        
        # 处理外键约束：先删除关联数据
        # 1. 删除用户相关的操作日志
        from app.models.operation_logs import OperationLog
        OperationLog.query.filter_by(user_id=user_id).delete()
        
        # 2. 删除用户相关的项目（这会自动删除项目相关的hole_data和features）
        from app.models.project import Project
        from app.models.hole_data import HoleData
        from app.models.features import Features
        
        # 获取用户的所有项目
        user_projects = Project.query.filter_by(user_id=user_id).all()
        
        for project in user_projects:
            # 删除项目相关的features数据
            Features.query.filter_by(project_id=project.id).delete()
            # 删除项目相关的hole_data数据
            HoleData.query.filter_by(project_id=project.id).delete()
            # 删除项目
            db.session.delete(project)
        
        # 3. 删除用户
        db.session.delete(user)
        db.session.commit()
        
        # 记录用户删除日志（由管理员操作）
        current_user_info = request.user
        create_system_log(
            operation_type='USER_DELETE',
            user_id=current_user_info['user_id'],  # 管理员ID
            status='success'
        )
        
        return jsonify({
            'code': 200,
            'message': '用户删除成功'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        
        # 记录用户删除失败日志
        try:
            current_user_info = request.user
            create_system_log(
                operation_type='USER_DELETE',
                user_id=current_user_info['user_id'],  # 管理员ID
                status='failed'
            )
        except Exception as log_error:
            print(f"记录用户删除失败日志失败: {str(log_error)}")
        
        return jsonify({
            'code': 500,
            'message': f'删除用户失败：{str(e)}'
        }), 500

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    """
    编辑用户信息（仅管理员可调用）
    """
    try:
        # 获取请求数据
        data = request.get_json()
        
        # 查找要编辑的用户
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'code': 404,
                'message': '用户不存在'
            }), 404
        
        # 验证角色有效性
        if data.get('role') and data.get('role') not in ['admin', 'user']:
            return jsonify({
                'code': 400,
                'message': '角色必须是admin或user'
            }), 400
        
        # 更新用户信息
        if data.get('username'):
            # 检查用户名是否已存在（排除当前用户）
            existing_user = User.query.filter(
                User.username == data.get('username'),
                User.id != user_id
            ).first()
            if existing_user:
                return jsonify({
                    'code': 400,
                    'message': '用户名已存在'
                }), 400
            user.username = data.get('username')
        
        if data.get('role'):
            user.role = data.get('role')
        
        if data.get('password'):
            user.set_password(data.get('password'))
        
        # 保存到数据库
        db.session.commit()
        
        # 记录管理员修改用户信息日志
        current_user_info = request.user
        create_system_log(
            operation_type='USER_UPDATE',
            user_id=current_user_info['user_id'],  # 管理员ID
            status='success'
        )
        
        return jsonify({
            'code': 200,
            'message': '用户信息更新成功',
            'data': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        
        # 记录用户信息修改失败日志
        try:
            current_user_info = request.user
            create_system_log(
                operation_type='USER_UPDATE',
                user_id=current_user_info['user_id'],  # 管理员ID
                status='failed'
            )
        except Exception as log_error:
            print(f"记录用户信息修改失败日志失败: {str(log_error)}")
        
        return jsonify({
            'code': 500,
            'message': f'更新用户信息失败：{str(e)}'
        }), 500