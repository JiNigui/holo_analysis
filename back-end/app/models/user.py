from datetime import datetime
from . import db
from werkzeug.security import check_password_hash, generate_password_hash

class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # 改为password字段，与数据库一致
    role = db.Column(db.String(20), nullable=False, default='user')  # admin, user
    created_at = db.Column(db.DateTime, default=datetime.now)
    last_login = db.Column(db.DateTime, nullable=True)  # 添加last_login字段
    current_session_id = db.Column(db.String(100), nullable=True)  # 当前会话ID
    session_created_at = db.Column(db.DateTime, nullable=True)  # 会话创建时间
    
    # 关系
    projects = db.relationship('Project', backref='user', lazy=True)
    
    def set_password(self, password):
        """
        设置用户密码（加密）
        :param password: 原始密码
        """
        self.password = generate_password_hash(password)
    
    def verify_password(self, password):
        """
        验证用户密码
        :param password: 待验证的密码
        :return: 验证成功返回True，失败返回False
        """
        return check_password_hash(self.password, password)
    
    def to_dict(self):
        """
        将用户对象转换为字典
        :return: 用户信息字典
        """
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'last_login': self.last_login.strftime('%Y-%m-%d %H:%M:%S') if self.last_login else None,
            'current_session_id': self.current_session_id,
            'session_created_at': self.session_created_at.strftime('%Y-%m-%d %H:%M:%S') if self.session_created_at else None
        }
    
    def __repr__(self):
        return f'<User {self.username}>'