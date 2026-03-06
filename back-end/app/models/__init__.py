from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# 导入所有模型，确保它们被注册
from .user import User
from .project import Project
from .hole_data import HoleData
from .operation_logs import OperationLog