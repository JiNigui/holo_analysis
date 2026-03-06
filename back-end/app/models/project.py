from datetime import datetime
from ..models import db

class Project(db.Model):
    """项目模型"""
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_time = db.Column(db.DateTime, default=datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    hole_data = db.relationship('HoleData', backref='project', lazy=True)
    
    def __repr__(self):
        return f'<Project {self.project_name}>'