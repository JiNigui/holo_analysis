import jwt
import datetime
from flask import current_app
from functools import wraps
from flask import request, jsonify
from app.models import User

def generate_token(user_id, username, role, session_id=None):
    """
    生成JWT token
    :param user_id: 用户ID
    :param username: 用户名
    :param role: 用户角色
    :param session_id: 会话ID（用于单点登录）
    :return: token字符串
    """
    # 设置token过期时间为24小时
    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    
    # 创建payload
    payload = {
        'exp': expiration,
        'iat': datetime.datetime.utcnow(),
        'user_id': user_id,
        'username': username,
        'role': role,
        'session_id': session_id  # 添加会话ID
    }
    
    # 使用密钥签名token
    token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    return token

def verify_token(token):
    """
    验证JWT token
    :param token: token字符串
    :return: 验证成功返回payload，失败返回None
    """
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        # token已过期
        return None
    except jwt.InvalidTokenError:
        # token无效
        return None

def get_user_info_from_token(token):
    """
    从token中获取用户信息
    :param token: token字符串
    :return: 用户信息字典或None
    """
    payload = verify_token(token)
    if payload:
        return {
            'user_id': payload['user_id'],
            'username': payload['username'],
            'role': payload['role'],
            'session_id': payload.get('session_id')  # 添加会话ID
        }
    return None

def jwt_required(f):
    """
    JWT认证装饰器
    用于保护需要认证的API端点
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 从请求头获取token
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'message': '认证失败：未提供token'}), 401
        
        # 验证token
        user_info = get_user_info_from_token(token)
        if not user_info:
            return jsonify({'message': '认证失败：token无效或已过期'}), 401
        
        # 检查会话有效性（单点登录验证）
        user_id = user_info['user_id']
        session_id = user_info.get('session_id')
        
        # 从数据库获取用户信息
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': '认证失败：用户不存在'}), 401
        
        # 检查会话是否过期（超过24小时）
        if user.session_created_at:
            from datetime import datetime
            session_age = datetime.now() - user.session_created_at
            if session_age.total_seconds() > 24 * 3600:  # 24小时
                return jsonify({'message': '认证失败：会话已过期'}), 401
        
        # 将用户信息添加到请求上下文
        request.user = user_info
        
        return f(*args, **kwargs)
    
    return decorated_function

def admin_required(f):
    """
    管理员权限装饰器
    用于保护需要管理员权限的API端点
    """
    @wraps(f)
    @jwt_required  # 先进行JWT认证
    def decorated_function(*args, **kwargs):
        # 检查用户角色
        if request.user.get('role') != 'admin':
            return jsonify({'message': '权限不足：需要管理员权限'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function