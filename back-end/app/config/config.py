import os
from datetime import timedelta

class Config:
    """基础配置类"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 上传文件配置 - 使用相对路径避免中文路径问题
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    # 孔洞分析项目特定上传目录
    HOLE_ANALYSIS_UPLOAD_FOLDER = os.path.join(BASE_DIR, 'hole-analysis', '第1步 原始图像的二值化', 'input')
    # 临时数据存储目录
    INTERMEDIATE_DATA_DIR = os.path.join(BASE_DIR, 'Intermediate_data')
    ALLOWED_EXTENSIONS = {'tiff', 'tif'}
    MAX_CONTENT_LENGTH = 3 * 1024 * 1024 * 1024  # 3GB（支持大量文件批量上传）
    
    # 日志清理配置
    LOG_CLEANUP_ENABLED = True  # 是否启用日志清理
    LOG_CLEANUP_DAYS = 3        # 保留日志天数（默认3天）
    LOG_CLEANUP_SCHEDULE = '0 2 * * *'  # 清理任务执行时间（cron表达式：每天17:15）

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    # 开发环境数据库连接 - 使用MySQL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://root:password@localhost:3306/holo_analysis_sys'

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'test.db')

class ProductionConfig(Config):
    """生产环境配置"""
    # 生产环境应使用真实数据库，这里以MySQL为例
    # 实际部署时请替换为真实的数据库连接信息
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://admin:password@localhost:3306/hole_analysis_db'

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}