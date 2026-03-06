from datetime import datetime
from ..models import db

class HoleData(db.Model):
    """孔洞数据模型"""
    __tablename__ = 'hole_data'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    analysis_result = db.Column(db.JSON)  # 存储分析结果的JSON数据
    hole_count = db.Column(db.Integer, default=0)
    average_size = db.Column(db.Float)
    max_size = db.Column(db.Float)
    min_size = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f'<HoleData id={self.id} project_id={self.project_id}>'