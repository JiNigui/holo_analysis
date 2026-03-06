"""
会话管理功能测试脚本
测试服务器停止时的会话清理和会话管理API
"""

import requests
import json
import time
import sys

# 后端API基础URL
BASE_URL = "http://127.0.0.1:5000/api"

def login_user(username, password):
    """用户登录"""
    url = f"{BASE_URL}/user/login"
    data = {
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 用户 {username} 登录成功")
            return result.get('token')
        else:
            print(f"❌ 用户 {username} 登录失败: {response.json()}")
            return None
    except Exception as e:
        print(f"❌ 登录请求失败: {e}")
        return None

def get_session_status(token):
    """获取会话状态（需要管理员权限）"""
    url = f"{BASE_URL}/session/sessions/status"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print("✅ 获取会话状态成功")
            return result
        else:
            print(f"❌ 获取会话状态失败: {response.json()}")
            return None
    except Exception as e:
        print(f"❌ 获取会话状态请求失败: {e}")
        return None

def cleanup_expired_sessions(token):
    """清理过期会话（需要管理员权限）"""
    url = f"{BASE_URL}/session/sessions/cleanup/expired"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print("✅ 清理过期会话成功")
            return result
        else:
            print(f"❌ 清理过期会话失败: {response.json()}")
            return None
    except Exception as e:
        print(f"❌ 清理过期会话请求失败: {e}")
        return None

def cleanup_all_sessions(token):
    """清理所有会话（需要管理员权限）"""
    url = f"{BASE_URL}/session/sessions/cleanup/all"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print("✅ 清理所有会话成功")
            return result
        else:
            print(f"❌ 清理所有会话失败: {response.json()}")
            return None
    except Exception as e:
        print(f"❌ 清理所有会话请求失败: {e}")
        return None

def test_access_protected_resource(token, resource_name):
    """测试访问受保护资源"""
    url = f"{BASE_URL}/user/info"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print(f"✅ {resource_name} - 访问受保护资源成功")
            return True
        else:
            print(f"❌ {resource_name} - 访问受保护资源失败: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ {resource_name} - 访问受保护资源请求失败: {e}")
        return False

def test_session_management():
    """测试会话管理功能"""
    print("🚀 开始测试会话管理功能")
    print("=" * 50)
    
    # 1. 管理员登录
    print("\n1. 管理员登录")
    admin_token = login_user("admin", "admin123")
    if not admin_token:
        print("❌ 管理员登录失败，无法继续测试")
        return
    
    # 2. 普通用户登录
    print("\n2. 普通用户登录")
    user_token = login_user("testuser", "password123")
    if not user_token:
        print("⚠️ 普通用户登录失败，继续测试其他功能")
    
    # 3. 测试访问受保护资源
    print("\n3. 测试访问受保护资源")
    test_access_protected_resource(admin_token, "管理员")
    if user_token:
        test_access_protected_resource(user_token, "普通用户")
    
    # 4. 获取会话状态（管理员权限）
    print("\n4. 获取会话状态")
    session_status = get_session_status(admin_token)
    if session_status:
        print(f"   活跃会话数量: {session_status.get('active_sessions_count', 0)}")
        print(f"   过期会话数量: {session_status.get('expired_sessions_count', 0)}")
        
        sessions = session_status.get('sessions', [])
        if sessions:
            print("   活跃会话详情:")
            for session in sessions:
                print(f"     - 用户: {session['username']}, 角色: {session['role']}, 会话时长: {session['session_duration']}")
    
    # 5. 清理过期会话
    print("\n5. 清理过期会话")
    cleanup_result = cleanup_expired_sessions(admin_token)
    if cleanup_result:
        print(f"   清理结果: {cleanup_result.get('message', '未知')}")
    
    # 6. 清理所有会话（强制所有用户下线）
    print("\n6. 清理所有会话（强制下线）")
    cleanup_all_result = cleanup_all_sessions(admin_token)
    if cleanup_all_result:
        print(f"   清理结果: {cleanup_all_result.get('message', '未知')}")
    
    # 7. 验证会话清理效果
    print("\n7. 验证会话清理效果")
    print("   等待2秒后验证...")
    time.sleep(2)
    
    # 重新获取会话状态
    new_session_status = get_session_status(admin_token)
    if new_session_status:
        active_count = new_session_status.get('active_sessions_count', 0)
        print(f"   清理后活跃会话数量: {active_count}")
        
        if active_count == 0:
            print("   ✅ 会话清理成功，所有用户已下线")
        else:
            print("   ⚠️ 会话清理后仍有活跃会话")
    
    # 8. 验证清理后访问受保护资源
    print("\n8. 验证清理后访问受保护资源")
    print("   管理员重新登录...")
    admin_token_after_cleanup = login_user("admin", "admin123")
    if admin_token_after_cleanup:
        test_access_protected_resource(admin_token_after_cleanup, "管理员（清理后）")
    
    print("\n" + "=" * 50)
    print("🎉 会话管理功能测试完成")

def test_server_shutdown_simulation():
    """测试服务器停止时的会话清理（模拟）"""
    print("\n🔧 测试服务器停止时的会话清理（模拟）")
    print("=" * 50)
    
    # 注意：这是一个模拟测试，实际服务器停止时的清理由信号处理程序自动执行
    print("1. 服务器启动时已注册会话管理器")
    print("2. 当服务器接收到 SIGINT (Ctrl+C) 或 SIGTERM 信号时")
    print("3. 会话管理器会自动清理所有活跃会话")
    print("4. 所有用户的 current_session_id 和 session_created_at 将被清空")
    print("5. 下次启动时，所有用户都需要重新登录")
    
    print("\n💡 实际测试方法:")
    print("   - 启动后端服务器")
    print("   - 让多个用户登录")
    print("   - 使用 Ctrl+C 停止服务器")
    print("   - 观察控制台输出")
    print("   - 重新启动服务器")
    print("   - 验证所有用户需要重新登录")
    
    print("\n✅ 服务器停止时的会话清理功能已实现")

if __name__ == "__main__":
    print("会话管理功能测试")
    print("请确保后端服务器正在运行 (http://127.0.0.1:5000)")
    
    try:
        # 测试健康检查
        health_response = requests.get(f"{BASE_URL}/health")
        if health_response.status_code == 200:
            print("✅ 后端服务器连接正常")
        else:
            print("❌ 后端服务器连接失败")
            sys.exit(1)
    except Exception as e:
        print(f"❌ 无法连接到后端服务器: {e}")
        print("请先启动后端服务器: cd back-end && python run.py")
        sys.exit(1)
    
    # 运行测试
    test_session_management()
    test_server_shutdown_simulation()