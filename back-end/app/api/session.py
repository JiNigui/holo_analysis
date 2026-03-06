"""
会话管理API
支持管理员清理过期会话和查看会话状态
"""

from flask import Blueprint, jsonify, request
from app.models import User, db
from app.utils.jwt_utils import jwt_required, get_user_info_from_token
from datetime import datetime, timedelta

session_bp = Blueprint('session', __name__)

@session_bp.route('/sessions/status', methods=['GET'])
@jwt_required
def get_session_status():
    """
    获取当前会话状态信息
    """
    try:
        # 获取当前用户信息
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_info = get_user_info_from_token(token)
        
        if not user_info:
            return jsonify({'error': '无效的token'}), 401
        
        # 检查用户权限（仅管理员可以查看会话状态）
        user = User.query.get(user_info['user_id'])
        if not user or user.role != 'admin':
            return jsonify({'error': '权限不足'}), 403
        
        # 获取活跃会话统计
        active_sessions_count = User.query.filter(
            User.current_session_id.isnot(None)
        ).count()
        
        # 获取过期会话统计（24小时以上）
        twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
        expired_sessions_count = User.query.filter(
            User.current_session_id.isnot(None),
            User.session_created_at < twenty_four_hours_ago
        ).count()
        
        # 获取活跃会话详情
        active_sessions = User.query.filter(
            User.current_session_id.isnot(None)
        ).all()
        
        sessions_info = []
        for user in active_sessions:
            sessions_info.append({
                'user_id': user.id,
                'username': user.username,
                'role': user.role,
                'session_created_at': user.session_created_at.strftime('%Y-%m-%d %H:%M:%S') if user.session_created_at else None,
                'session_duration': str(datetime.now() - user.session_created_at) if user.session_created_at else None
            })
        
        return jsonify({
            'active_sessions_count': active_sessions_count,
            'expired_sessions_count': expired_sessions_count,
            'sessions': sessions_info
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取会话状态失败: {str(e)}'}), 500

@session_bp.route('/sessions/cleanup/expired', methods=['POST'])
@jwt_required
def cleanup_expired_sessions():
    """
    清理过期会话（24小时以上）
    """
    try:
        # 获取当前用户信息
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_info = get_user_info_from_token(token)
        
        if not user_info:
            return jsonify({'error': '无效的token'}), 401
        
        # 检查用户权限（仅管理员可以清理会话）
        user = User.query.get(user_info['user_id'])
        if not user or user.role != 'admin':
            return jsonify({'error': '权限不足'}), 403
        
        # 计算24小时前的时间
        twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
        
        # 查找过期会话
        expired_sessions = User.query.filter(
            User.current_session_id.isnot(None),
            User.session_created_at < twenty_four_hours_ago
        ).all()
        
        cleaned_count = 0
        cleaned_users = []
        
        if expired_sessions:
            for user in expired_sessions:
                cleaned_users.append({
                    'user_id': user.id,
                    'username': user.username
                })
                
                # 清除会话信息
                user.current_session_id = None
                user.session_created_at = None
                cleaned_count += 1
            
            # 提交数据库更改
            db.session.commit()
        
        return jsonify({
            'message': f'成功清理 {cleaned_count} 个过期会话',
            'cleaned_users': cleaned_users
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'清理过期会话失败: {str(e)}'}), 500

@session_bp.route('/sessions/cleanup/all', methods=['POST'])
@jwt_required
def cleanup_all_sessions():
    """
    清理所有活跃会话（强制所有用户下线）
    """
    try:
        # 获取当前用户信息
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_info = get_user_info_from_token(token)
        
        if not user_info:
            return jsonify({'error': '无效的token'}), 401
        
        # 检查用户权限（仅管理员可以清理所有会话）
        user = User.query.get(user_info['user_id'])
        if not user or user.role != 'admin':
            return jsonify({'error': '权限不足'}), 403
        
        # 获取所有有活跃会话的用户
        users_with_sessions = User.query.filter(
            User.current_session_id.isnot(None)
        ).all()
        
        cleaned_count = 0
        cleaned_users = []
        
        if users_with_sessions:
            for user in users_with_sessions:
                cleaned_users.append({
                    'user_id': user.id,
                    'username': user.username
                })
                
                # 清除会话信息
                user.current_session_id = None
                user.session_created_at = None
                cleaned_count += 1
            
            # 提交数据库更改
            db.session.commit()
        
        return jsonify({
            'message': f'成功清理 {cleaned_count} 个活跃会话，所有用户已下线',
            'cleaned_users': cleaned_users
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'清理所有会话失败: {str(e)}'}), 500

@session_bp.route('/sessions/cleanup/user/<int:user_id>', methods=['POST'])
@jwt_required
def cleanup_user_session(user_id):
    """
    清理指定用户的会话（强制指定用户下线）
    """
    try:
        # 获取当前用户信息
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_info = get_user_info_from_token(token)
        
        if not user_info:
            return jsonify({'error': '无效的token'}), 401
        
        # 检查用户权限（仅管理员可以清理其他用户会话）
        current_user = User.query.get(user_info['user_id'])
        if not current_user or current_user.role != 'admin':
            return jsonify({'error': '权限不足'}), 403
        
        # 查找目标用户
        target_user = User.query.get(user_id)
        if not target_user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 检查目标用户是否有活跃会话
        if not target_user.current_session_id:
            return jsonify({'message': '该用户当前没有活跃会话'}), 200
        
        # 清除会话信息
        target_user.current_session_id = None
        target_user.session_created_at = None
        
        # 提交数据库更改
        db.session.commit()
        
        return jsonify({
            'message': f'成功清理用户 {target_user.username} 的会话',
            'user_id': target_user.id,
            'username': target_user.username
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'清理用户会话失败: {str(e)}'}), 500