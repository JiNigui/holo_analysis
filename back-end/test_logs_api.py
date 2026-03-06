import requests
import json

# 基础URL
BASE_URL = "http://127.0.0.1:5000/api"

# 登录获取token
def login():
    login_data = {
        "username": "admin",
        "password": "admin234"
    }
    
    response = requests.post(f"{BASE_URL}/user/login", json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        print("登录成功!")
        print(f"完整响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
        
        # 检查token在哪个字段
        if 'token' in data:
            token = data['token']
        elif 'data' in data and 'token' in data['data']:
            token = data['data']['token']
        else:
            print("未找到token字段")
            return None
            
        print(f"Token: {token[:50]}...")
        return token
    else:
        print(f"登录失败: {response.status_code}")
        print(response.text)
        return None

# 测试获取日志
def test_get_logs(token):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(
        f"{BASE_URL}/logs/logs?page=1&per_page=10", 
        headers=headers
    )
    
    print(f"\n获取日志API响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("获取日志成功!")
        print(f"返回数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
    else:
        print(f"获取日志失败: {response.text}")

# 主测试函数
def main():
    print("开始测试日志API...")
    
    # 登录获取token
    token = login()
    if not token:
        print("登录失败，无法继续测试")
        return
    
    # 测试获取日志
    test_get_logs(token)

if __name__ == "__main__":
    main()