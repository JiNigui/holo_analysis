from flask import Blueprint, jsonify
from flask_cors import CORS

api_bp = Blueprint('api', __name__)

# 启用CORS支持
CORS(api_bp)

# 导入各个API模块的Blueprint
from .user import user_bp
from .project import project_bp
from .hole_analysis import hole_analysis_bp
from .logs import logs_bp
from .session import session_bp
from .upload import upload_bp

# 注册子蓝图
api_bp.register_blueprint(user_bp, url_prefix='/user')
api_bp.register_blueprint(project_bp, url_prefix='/project')
api_bp.register_blueprint(hole_analysis_bp, url_prefix='/hole-analysis')
api_bp.register_blueprint(logs_bp, url_prefix='/logs')
api_bp.register_blueprint(session_bp, url_prefix='/session')
api_bp.register_blueprint(upload_bp, url_prefix='/upload')


@api_bp.app_errorhandler(404)
def not_found_error(error):
    """处理404错误"""
    return jsonify({'message': '请求的资源不存在'}), 404


@api_bp.app_errorhandler(500)
def internal_error(error):
    """处理500错误"""
    return jsonify({'message': '服务器内部错误'}), 500


@api_bp.app_errorhandler(400)
def bad_request_error(error):
    """处理400错误"""
    return jsonify({'message': '请求参数错误'}), 400


@api_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        'status': 'healthy',
        'service': 'hole-analysis-api'
    }), 200