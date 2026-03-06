"""
定时日志清理任务模块
功能：自动清理超过3天的操作日志
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app import create_app
from app.models import db, OperationLog
from datetime import datetime, timedelta
import logging

def cleanup_old_logs():
    """
    清理超过3天的旧日志
    创建独立的应用上下文，确保数据库连接正确
    """
    # 创建独立的应用实例（避免信号处理问题）
    app = create_app()
    
    # 禁用会话管理器的信号处理（避免线程问题）
    app.config['DISABLE_SESSION_SIGNALS'] = True
    
    with app.app_context():
        try:
            # 计算3天前的时间点（使用当前本地时间）
            current_time = datetime.now()
            three_days_ago = current_time - timedelta(days=3)
            
            # 记录详细的清理信息
            logging.info(f"开始清理超过3天的旧日志")
            logging.info(f"当前时间: {current_time}")
            logging.info(f"清理时间点（3天前）: {three_days_ago}")
            
            # 先查询符合条件的日志数量（用于验证）
            logs_to_delete = OperationLog.query.filter(
                OperationLog.operation_time < three_days_ago
            ).count()
            
            logging.info(f"找到 {logs_to_delete} 条超过3天的日志需要清理")
            
            # 查询并删除超过3天的日志
            deleted_count = OperationLog.query.filter(
                OperationLog.operation_time < three_days_ago
            ).delete()
            
            # 提交事务
            db.session.commit()
            
            # 验证删除结果
            remaining_logs = OperationLog.query.filter(
                OperationLog.operation_time < three_days_ago
            ).count()
            
            # 计算实际删除数量（更可靠的方式）
            actual_deleted = logs_to_delete - remaining_logs
            
            # 记录清理结果
            logging.info(f"日志清理完成：成功删除了 {actual_deleted} 条超过3天的旧日志")
            logging.info(f"清理后剩余超过3天的日志数量: {remaining_logs}")
            
            if actual_deleted != logs_to_delete:
                logging.warning(f"删除数量不一致：预期删除 {logs_to_delete} 条，实际删除 {actual_deleted} 条")
            else:
                logging.info(f"删除验证成功：预期删除 {logs_to_delete} 条，实际删除 {actual_deleted} 条")
            
            return deleted_count
            
        except Exception as e:
            # 发生错误时回滚事务
            db.session.rollback()
            logging.error(f"日志清理失败：{str(e)}")
            raise

def init_scheduler():
    """
    初始化定时任务调度器
    配置每天北京时间17:15执行日志清理任务
    """
    try:
        # 创建后台调度器
        scheduler = BackgroundScheduler()
        
        # 添加日志清理任务
        # 使用cron表达式：每天北京时间17:15执行
        scheduler.add_job(
            func=cleanup_old_logs,
            trigger=CronTrigger(hour=2, minute=0),  # 每天17:15执行
            id='log_cleanup',
            name='清理过期操作日志',
            replace_existing=True,
            misfire_grace_time=300,  # 允许5分钟的延迟
            max_instances=1          # 只允许一个实例运行
        )
        
        # 启动调度器
        scheduler.start()
        
        logging.info("定时任务调度器初始化成功，日志清理任务已注册")
        logging.info("清理任务执行时间：每天北京时间17:15")
        
        return scheduler
        
    except Exception as e:
        logging.error(f"定时任务调度器初始化失败：{str(e)}")
        return None

def manual_cleanup(days=3):
    """
    手动执行日志清理（用于测试或管理）
    :param days: 清理多少天前的日志，默认3天
    :return: 删除的日志数量
    """
    # 创建独立的应用实例（避免信号处理问题）
    app = create_app()
    
    # 禁用会话管理器的信号处理（避免线程问题）
    app.config['DISABLE_SESSION_SIGNALS'] = True
    
    with app.app_context():
        try:
            # 计算清理时间点（使用当前本地时间）
            current_time = datetime.now()
            cutoff_time = current_time - timedelta(days=days)
            
            # 记录详细的清理信息
            logging.info(f"手动清理开始：删除{days}天前的日志")
            logging.info(f"当前时间: {current_time}")
            logging.info(f"清理时间点（{days}天前）: {cutoff_time}")
            
            # 先查询符合条件的日志数量（用于验证）
            logs_to_delete = OperationLog.query.filter(
                OperationLog.operation_time < cutoff_time
            ).count()
            
            logging.info(f"找到 {logs_to_delete} 条超过{days}天的日志需要清理")
            
            deleted_count = OperationLog.query.filter(
                OperationLog.operation_time < cutoff_time
            ).delete()
            
            db.session.commit()
            
            # 验证删除结果
            remaining_logs = OperationLog.query.filter(
                OperationLog.operation_time < cutoff_time
            ).count()
            
            # 计算实际删除数量（更可靠的方式）
            actual_deleted = logs_to_delete - remaining_logs
            
            logging.info(f"手动清理完成：删除了 {actual_deleted} 条超过{days}天的日志")
            logging.info(f"清理后剩余超过{days}天的日志数量: {remaining_logs}")
            
            if actual_deleted != logs_to_delete:
                logging.warning(f"删除数量不一致：预期删除 {logs_to_delete} 条，实际删除 {actual_deleted} 条")
            else:
                logging.info(f"删除验证成功：预期删除 {logs_to_delete} 条，实际删除 {actual_deleted} 条")
            
            return deleted_count
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"手动清理失败：{str(e)}")
            raise

# 测试函数（开发环境使用）
# 注意：此函数仅用于开发环境测试，生产环境应移除或注释掉
def test_cleanup():
    """测试日志清理功能"""
    print("=== 测试日志清理功能 ===")
    
    # 测试手动清理1分钟前的日志（用于快速验证）
    try:
        one_minute_ago = datetime.now() - timedelta(minutes=1)
        
        # 测试函数需要独立的应用实例
        from app import create_app
        app = create_app()
        with app.app_context():
            # 先创建一条测试日志
            from app.models import OperationLog
            test_log = OperationLog(
                user_id=1,
                operation_type="TEST_CLEANUP",
                status="success",
                operation_time=one_minute_ago
            )
            db.session.add(test_log)
            db.session.commit()
            
            print("测试日志创建成功")
            
            # 执行清理
            deleted_count = OperationLog.query.filter(
                OperationLog.operation_time < one_minute_ago
            ).delete()
            
            db.session.commit()
            
            print(f"测试清理完成：删除了 {deleted_count} 条日志")
            
    except Exception as e:
        print(f"测试失败：{str(e)}")