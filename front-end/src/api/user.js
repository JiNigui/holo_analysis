import request from '@/utils/request'

// 登录功能API - 向后端JWT认证接口发送请求
export function login(data) {
  return request({
    url: '/user/login',
    method: 'post',
    data
  })
}

// 获取用户信息API - 与后端保持一致，使用profile接口
export function getInfo() {
  return request({
    url: '/user/profile',
    method: 'get'
  })
}

// 退出登录功能API
export function logout() {
  return request({
    url: '/user/logout',
    method: 'post'
  })
}

// 注册功能API
export function register(data) {
  return request({
    url: '/user/register',
    method: 'post',
    data
  })
}

// 获取用户列表API
export function getUsers() {
  return request({
    url: '/user/users',
    method: 'get'
  })
}

// 获取用户详情API - 复用profile接口
// 注意：后端目前只有profile接口，如需更多用户详情，需要后端添加相应接口
export function getUserDetail() {
  // 复用profile接口
  return request({
    url: '/user/profile',
    method: 'get'
  })
}

// 删除用户API
export function deleteUser(userId) {
  return request({
    url: `/user/users/${userId}`,
    method: 'delete'
  })
}

// 编辑用户API
export function updateUser(userId, data) {
  return request({
    url: `/user/users/${userId}`,
    method: 'put',
    data
  })
}

// 修改当前用户个人信息API
export function updateProfile(data) {
  return request({
    url: '/user/profile',
    method: 'put',
    data
  })
}

// 强制下线其他设备API
export function forceLogout() {
  return request({
    url: '/user/force-logout',
    method: 'post'
  })
}

// 检查会话有效性API
export function checkSession() {
  return request({
    url: '/user/check-session',
    method: 'get'
  })
}
