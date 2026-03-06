from datetime import datetime
from ..models import db

class Features(db.Model):
    """特征数据模型"""
    __tablename__ = 'features'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    hole_id = db.Column(db.Integer)
    area = db.Column(db.Float)
    perimeter = db.Column(db.Float)
    width = db.Column(db.Float)
    height = db.Column(db.Float)
    aspect_ratio = db.Column(db.Float)
    circularity = db.Column(db.Float)
    center_x = db.Column(db.Float)
    center_y = db.Column(db.Float)
    confidence = db.Column(db.Float)
    detail_data = db.Column(db.Text)
    centroid_x = db.Column(db.Float)
    volume = db.Column(db.Float)
    operation_id = db.Column(db.Integer, db.ForeignKey('operation_logs.id'))
    created_at = db.Column(db.DateTime, default=datetime.now)
    analysis_time = db.Column(db.DateTime)
    
    # 关系
    project = db.relationship('Project', backref='features', lazy=True)
    operation_log = db.relationship('OperationLog', backref='features', lazy=True)
    
    def __repr__(self):
        return f'<Features for project {self.project_id}>'