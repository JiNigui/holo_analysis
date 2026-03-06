"""
会话管理工具类
负责服务器停止时的会话清理
"""

from flask import current_app
from app.models import User, db
from datetime import datetime, timedelta
import atexit
import signal
import sys

class SessionManager:
    """会话管理器"""
    
    def __init__(self, app=None):
        self.is_shutting_down = False
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """初始化应用"""
        self.app = app
        self.setup_shutdown_handlers()
    
    def setup_shutdown_handlers(self):
        """设置服务器停止时的处理程序"""
        # 检查是否禁用信号处理（用于定时任务等后台线程）
        if self.app and self.app.config.get('DISABLE_SESSION_SIGNALS', False):
            print("会话管理器已初始化（信号处理已禁用）")
            return
            
        # 注册程序退出时的清理函数
        atexit.register(self.cleanup_sessions_on_shutdown)
        
        # 注册信号处理程序（仅在主线程中有效）
        try:
            signal.signal(signal.SIGINT, self.signal_handler)  # Ctrl+C
            signal.signal(signal.SIGTERM, self.signal_handler)  # 终止信号
            print("会话管理器已初始化，已注册服务器停止处理程序")
        except ValueError as e:
            # 在非主线程中设置信号处理器会失败，这是正常现象
            print(f"会话管理器已初始化（信号处理受限: {str(e)}）")
    
    def signal_handler(self, signum, frame):
        """信号处理函数"""
        print(f"接收到信号 {signum}，开始清理会话...")
        self.is_shutting_down = True
        self.cleanup_all_sessions()
        sys.exit(0)
    
    def cleanup_sessions_on_shutdown(self):
        """服务器停止时清理所有会话"""
        if not self.is_shutting_down:
            print("服务器停止，开始清理所有用户会话...")
            self.cleanup_all_sessions()
    
    def cleanup_all_sessions(self):
        """清理所有用户的会话"""
        try:
            # 使用应用上下文进行数据库操作
            if self.app:
                with self.app.app_context():
                    # 获取所有有活跃会话的用户
                    users_with_sessions = User.query.filter(
                        User.current_session_id.isnot(None)
                    ).all()
                    
                    if users_with_sessions:
                        print(f"发现 {len(users_with_sessions)} 个用户有活跃会话，开始清理...")
                        
                        for user in users_with_sessions:
                            # 记录清理日志
                            print(f"清理用户 {user.username} 的会话")
                            
                            # 清除会话信息
                            user.current_session_id = None
                            user.session_created_at = None
                        
                        # 提交数据库更改
                        db.session.commit()
                        print("所有用户会话已清理完成")
                    else:
                        print("没有发现活跃的用户会话")
            else:
                print("警告：无法清理会话，应用上下文不可用")
                
        except Exception as e:
            print(f"清理会话时发生错误: {e}")
            # 发生错误时回滚
            if self.app:
                with self.app.app_context():
                    db.session.rollback()
    
    def cleanup_expired_sessions(self):
        """清理过期的会话（24小时以上）"""
        try:
            # 使用应用上下文进行数据库操作
            if self.app:
                with self.app.app_context():
                    # 计算24小时前的时间
                    twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
                    
                    # 查找过期会话
                    expired_sessions = User.query.filter(
                        User.current_session_id.isnot(None),
                        User.session_created_at < twenty_four_hours_ago
                    ).all()
                    
                    if expired_sessions:
                        print(f"发现 {len(expired_sessions)} 个过期会话，开始清理...")
                        
                        for user in expired_sessions:
                            print(f"清理用户 {user.username} 的过期会话")
                            user.current_session_id = None
                            user.session_created_at = None
                        
                        db.session.commit()
                        print("过期会话清理完成")
                    else:
                        print("没有发现过期会话")
            else:
                print("警告：无法清理过期会话，应用上下文不可用")
                
        except Exception as e:
            print(f"清理过期会话时发生错误: {e}")
            if self.app:
                with self.app.app_context():
                    db.session.rollback()
    
    def get_active_sessions_count(self):
        """获取当前活跃会话数量"""
        try:
            if self.app:
                with self.app.app_context():
                    count = User.query.filter(
                        User.current_session_id.isnot(None)
                    ).count()
                    return count
            else:
                print("警告：无法获取活跃会话数量，应用上下文不可用")
                return 0
        except Exception as e:
            print(f"获取活跃会话数量时发生错误: {e}")
            return 0

# 创建全局会话管理器实例
session_manager = SessionManager()

def init_session_manager(app=None):
    """初始化会话管理器"""
    if app:
        session_manager.init_app(app)
    return session_manager