import os
import sys
from app import create_app
from app.models import db

# 创建应用
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

def init_database():
    """初始化数据库"""
    with app.app_context():
        # 创建所有表
        db.create_all()
        print('数据库表创建成功！')
        
        # 可以在这里添加初始数据
        from app.models.user import User
        
        # 检查是否已有管理员用户
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            # 创建管理员用户
            admin = User(
                username='admin',
                email='admin@example.com',
                role='admin'
            )
            # 使用新的set_password方法设置密码
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print('默认管理员用户创建成功！')
            print('用户名: admin')
            print('密码: admin123')
        else:
            print('管理员用户已存在')
        
        # 检查是否已有普通用户
        normal_user = User.query.filter_by(username='user').first()
        if not normal_user:
            # 创建普通用户
            normal_user = User(
                username='user',
                email='user@example.com',
                role='user'
            )
            # 使用set_password方法设置密码
            normal_user.set_password('user123')
            db.session.add(normal_user)
            db.session.commit()
            print('普通用户创建成功！')
            print('用户名: user')
            print('密码: user123')
        else:
            print('普通用户已存在')

if __name__ == '__main__':
    init_database()