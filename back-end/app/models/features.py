from datetime import datetime
from ..models import db

class Features(db.Model):
    """单体孔洞特征数据模型（对应第六步形态学分析输出）"""
    __tablename__ = 'features'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    hole_id = db.Column(db.Integer)
    volume = db.Column(db.Float)
    surface_area = db.Column(db.Float)
    equivalent_diameter = db.Column(db.Float)
    sphericity = db.Column(db.Float)
    rectangularity = db.Column(db.Float)
    aspect_ratio = db.Column(db.Float)
    long_edge = db.Column(db.Float)
    center_distance = db.Column(db.Float)
    operation_id = db.Column(db.Integer, db.ForeignKey('operation_logs.id'))
    analysis_time = db.Column(db.DateTime)

    def __repr__(self):
        return f'<Features hole_id={self.hole_id} project_id={self.project_id}>'
