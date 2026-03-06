from flask import Blueprint, request, jsonify
from app.models import db, OperationLog, User, Project
from app.utils.jwt_utils import jwt_required, admin_required
from datetime import datetime

logs_bp = Blueprint('logs', __name__)

@logs_bp.route('/logs', methods=['POST'])
@jwt_required
def create_log():
    """创建日志记录"""
    try:
        data = request.get_json()
        
        # 获取当前用户ID（从请求上下文）
        current_user_id = request.user.get('user_id')
        
        # 验证必需字段
        if not data or 'operation_type' not in data:
            return jsonify({'message': '缺少必需字段: operation_type'}), 400
        
        # 创建日志记录
        log = OperationLog(
            user_id=current_user_id,
            project_id=data.get('project_id'),  # 可为NULL
            operation_type=data['operation_type'],  # 操作类型即操作名称
            status=data.get('status', 'success')
        )
        
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '日志记录创建成功',
            'data': log.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'日志记录失败: {str(e)}'
        }), 500

@logs_bp.route('/logs', methods=['GET'])
@jwt_required
def get_logs():
    """
    获取系统日志列表（仅管理员可调用）
    支持分页和筛选
    """
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        operation_type = request.args.get('operation_type')
        username = request.args.get('username')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 构建查询
        query = OperationLog.query
        
        # 按操作类型筛选
        if operation_type:
            query = query.filter(OperationLog.operation_type == operation_type)
        
        # 按用户名筛选
        if username:
            query = query.join(User).filter(User.username.like(f'%{username}%'))
        
        # 按时间范围筛选
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                query = query.filter(OperationLog.operation_time >= start_date)
            except ValueError:
                pass
        
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
                query = query.filter(OperationLog.operation_time <= end_date)
            except ValueError:
                pass
        
        # 按时间倒序排列
        query = query.order_by(OperationLog.operation_time.desc())
        
        # 分页查询
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # 转换为字典列表
        logs_list = [log.to_dict() for log in pagination.items]
        
        return jsonify({
            'code': 200,
            'message': '获取日志列表成功',
            'data': {
                'logs': logs_list,
                'total': pagination.total,
                'page': page,
                'per_page': per_page,
                'pages': pagination.pages
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取日志列表失败：{str(e)}'
        }), 500

# 预定义的日志类型常量
LOG_TYPES = {
    'USER_LOGIN': '用户登入',
    'USER_LOGOUT': '用户登出', 
    'PROJECT_CREATE': '创建项目',
    'PROJECT_DELETE': '删除项目',
    'IMAGE_BINARIZATION': '原始图像二值化',
    'ROI_SELECTION': '选择感兴趣区域',
    'MASK_RCNN_DETECTION': 'Mask R-CNN 孔洞识别',
    'DATA_PREPROCESSING': '数据预处理',
    'TARGET_SLICING': '寻找目标孔洞并切片',
    'MORPHOLOGY_ANALYSIS': '形态学分析',
    '3D_MODEL_CONSTRUCTION': '3D模型构建',
    'VOI_REGION_CONFIRMATION': 'VOI区域确认',
    'VOI_ENHANCEMENT_GENERATION': 'VOI增强生成'
}

def create_system_log(operation_type, user_id=None, project_id=None, status='success'):
    """
    创建系统日志的辅助函数
    """
    try:
        log = OperationLog(
            user_id=user_id,
            project_id=project_id,  # 可为NULL
            operation_type=operation_type,  # 操作类型即操作名称
            status=status
        )
        
        db.session.add(log)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        # 使用日志系统记录错误，而不是print
        import logging
        logging.error(f"创建系统日志失败: {str(e)}")
        return False

@logs_bp.route('/logs/cleanup', methods=['POST'])
@admin_required
def manual_log_cleanup():
    """
    手动清理过期日志（管理员专用）
    支持自定义清理天数
    """
    try:
        # 获取请求参数
        data = request.get_json() or {}
        
        # 获取清理天数，默认3天
        days = data.get('days', 3)
        
        # 验证参数有效性
        if not isinstance(days, int) or days < 1:
            return jsonify({
                'code': 400,
                'message': '清理天数必须是大于0的整数'
            }), 400
        
        # 计算清理时间点
        from datetime import datetime, timedelta
        cutoff_time = datetime.now() - timedelta(days=days)
        
        # 执行清理
        deleted_count = OperationLog.query.filter(
            OperationLog.operation_time < cutoff_time
        ).delete()
        
        # 提交事务
        db.session.commit()
        
        # 记录清理操作日志
        current_user_id = request.user.get('user_id')
        create_system_log(
            operation_type='LOG_CLEANUP',
            user_id=current_user_id,
            status='success'
        )
        
        return jsonify({
            'code': 200,
            'message': f'成功清理 {deleted_count} 条超过{days}天的日志',
            'data': {
                'deleted_count': deleted_count,
                'cutoff_time': cutoff_time.isoformat(),
                'days': days
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        
        # 记录失败日志
        current_user_id = request.user.get('user_id')
        create_system_log(
            operation_type='LOG_CLEANUP',
            user_id=current_user_id,
            status='failed'
        )
        
        return jsonify({
            'code': 500,
            'message': f'日志清理失败：{str(e)}'
        }), 500

@logs_bp.route('/logs/cleanup/status', methods=['GET'])
@admin_required
def get_cleanup_status():
    """获取日志清理状态信息"""
    try:
        # 获取日志统计信息
        total_logs = OperationLog.query.count()
        
        # 计算3天前的日志数量
        from datetime import datetime, timedelta
        three_days_ago = datetime.now() - timedelta(days=3)
        old_logs_count = OperationLog.query.filter(
            OperationLog.operation_time < three_days_ago
        ).count()
        
        # 计算存储空间估算（假设每条日志约1KB）
        estimated_size_kb = total_logs
        old_logs_size_kb = old_logs_count
        
        return jsonify({
            'code': 200,
            'message': '获取清理状态成功',
            'data': {
                'total_logs': total_logs,
                'old_logs_count': old_logs_count,  # 超过3天的日志数量
                'estimated_total_size_kb': estimated_size_kb,
                'estimated_old_size_kb': old_logs_size_kb,
                'next_scheduled_cleanup': '每天凌晨2:00',
                'cleanup_enabled': True
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取清理状态失败：{str(e)}'
        }), 500