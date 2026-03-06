from datetime import datetime
from ..models import db

class OperationLog(db.Model):
    """操作日志模型"""
    __tablename__ = 'operation_logs'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)  # 改为可为NULL
    operation_type = db.Column(db.String(50), nullable=False)  # 操作类型，即操作名称
    status = db.Column(db.String(20), default='success')
    operation_time = db.Column(db.DateTime, default=datetime.now)  # 改为operation_time
    
    # 关系
    user = db.relationship('User', backref='operation_logs', lazy=True)
    project = db.relationship('Project', backref='operation_logs', lazy=True)
    
    def to_dict(self):
        """将操作日志对象转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else '未知用户',
            'project_id': self.project_id,
            'project_name': self.project.project_name if self.project else '无',
            'operation_type': self.operation_type,  # 操作类型即操作名称
            'status': self.status,
            'operation_time': self.operation_time.strftime('%Y-%m-%d %H:%M:%S') if self.operation_time else None
        }
    
    def __repr__(self):
        return f'<OperationLog {self.operation_type} by user {self.user_id}>'