from datetime import datetime
from ..models import db

class HoleData(db.Model):
    """孔洞全局统计数据模型（对应第六步形态学分析输出，智能鉴定与全局特征）"""
    __tablename__ = 'hole_data'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    total_number_of_voids = db.Column(db.Integer, nullable=False)
    void_space_density = db.Column(db.Float)
    total_void_volume = db.Column(db.Float)
    total_void_surface_area = db.Column(db.Float)
    maximum_volume = db.Column(db.Float)
    mean_volume = db.Column(db.Float)
    minimum_volume = db.Column(db.Float)
    maximum_surface_area = db.Column(db.Float)
    mean_surface_area = db.Column(db.Float)
    minimum_surface_area = db.Column(db.Float)
    maximum_equivalent_diameter = db.Column(db.Float)
    mean_equivalent_diameter = db.Column(db.Float)
    minimum_equivalent_diameter = db.Column(db.Float)
    maximum_sphericity = db.Column(db.Float)
    mean_sphericity = db.Column(db.Float)
    minimum_sphericity = db.Column(db.Float)
    maximum_rectangularity = db.Column(db.Float)
    mean_rectangularity = db.Column(db.Float)
    minimum_rectangularity = db.Column(db.Float)
    maximum_aspect_ratio = db.Column(db.Float)
    mean_aspect_ratio = db.Column(db.Float)
    minimum_aspect_ratio = db.Column(db.Float)
    maximum_long_edge = db.Column(db.Float)
    mean_long_edge = db.Column(db.Float)   # 注意：与SQL保持一致，列名有typo
    minimum_long_edge = db.Column(db.Float)
    maximum_center_distance = db.Column(db.Float)
    mean_center_distance = db.Column(db.Float)
    minimum_center_distance = db.Column(db.Float)
    maximum_void_volume_fraction = db.Column(db.Float)
    volume_coefficient_of_variation = db.Column(db.Float)
    volume_gini_coefficient = db.Column(db.Float)
    maximum_volume_jump_ratio = db.Column(db.Float)

    def __repr__(self):
        return f'<HoleData id={self.id} project_id={self.project_id}>'
