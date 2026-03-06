from flask import Flask
from .config.config import config
from .models import db
from .api import api_bp
from .utils.session_utils import init_session_manager

# 猴子补丁：修改Werkzeug Request类的默认限制
# 这是解决1000+文件上传限制的正确方法（Werkzeug 2.x版本）
import werkzeug.wrappers.request
werkzeug.wrappers.request.Request.max_form_parts = 2000  # 默认1000，改为2000
werkzeug.wrappers.request.Request.max_form_memory_size = 3 * 1024 * 1024 * 1024  # 3GB

def create_app(config_name='development'):
    """创建Flask应用实例"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # 注意：app.config['MAX_FORM_MEMORY_SIZE'] 和 app.config['MAX_FORM_PARTS']
    # 在Werkzeug中无效，必须使用上面的猴子补丁方式

    # 初始化数据库
    db.init_app(app)

    # 注册蓝图
    app.register_blueprint(api_bp, url_prefix='/api')

    # 初始化会话管理器（用于服务器停止时清理会话）
    init_session_manager(app)

    # 初始化定时任务（仅在非测试环境）
    if app.config.get('ENV') != 'testing' and app.config.get('LOG_CLEANUP_ENABLED', True):
        try:
            from .tasks.log_cleanup import init_scheduler
            scheduler = init_scheduler()
            if scheduler:
                app.logger.info("定时任务调度器初始化成功")
            else:
                app.logger.warning("定时任务调度器初始化失败")
        except Exception as e:
            app.logger.error(f"定时任务初始化异常: {str(e)}")

    return app