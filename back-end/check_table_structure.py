from app import create_app, db

app = create_app()

with app.app_context():
    # 检查所有表名
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print('数据库中的所有表:')
    for table in tables:
        print(f'- {table}')
    print()
    
    # 检查users表结构
    if 'users' in tables:
        print('users表结构:')
        columns = inspector.get_columns('users')
        for column in columns:
            name = column['name']
            col_type = column['type']
            print(f'{name}: {col_type}')
    
    # 检查模型定义
    from app.models.user import User
    print('\n模型定义的字段:')
    for column in User.__table__.columns:
        print(f'{column.name}: {column.type}')
    
    # 检查表名
    print(f'\nUser模型的表名: {User.__tablename__}')
    
    # 检查字段差异
    print('\n需要添加的字段:')
    model_fields = {col.name for col in User.__table__.columns}
    if 'users' in tables:
        db_fields = {col['name'] for col in inspector.get_columns('users')}
        missing_fields = model_fields - db_fields
        if missing_fields:
            for field in missing_fields:
                print(f'- {field}')
        else:
            print('所有字段都已存在')