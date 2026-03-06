from app import create_app
from app.models import db, OperationLog
import os

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
with app.app_context():
    # 检查表是否存在
    print('检查operation_logs表是否存在...')
    try:
        count = OperationLog.query.count()
        print(f'操作日志表存在，共有{count}条记录')
        
        # 检查前几条记录
        logs = OperationLog.query.limit(5).all()
        for log in logs:
            print(f'日志ID: {log.id}, 操作类型: {log.operation_type}, 用户ID: {log.user_id}')
    except Exception as e:
        print(f'查询失败: {e}')
        
    # 检查表结构
    print('\n检查表结构...')
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    columns = inspector.get_columns('operation_logs')
    for col in columns:
        col_name = col['name']
        col_type = str(col['type'])
        col_nullable = col['nullable']
        print(f'列名: {col_name}, 类型: {col_type}, 可空: {col_nullable}')