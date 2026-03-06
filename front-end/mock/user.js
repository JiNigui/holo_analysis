
// 模拟数据库中的用户信息
const users = [
  // 管理员账号，用户ID为00001
  {
    id: '00001',
    username: 'admin',
    password: 'admin123', // 实际项目中应该使用加密后的密码
    roles: ['admin'],
    introduction: '我是超级管理员',
    avatar: 'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif',
    name: '超级管理员',
    createTime: '2023-01-01 00:00:00'
  },
  // 普通用户账号，用户ID为00002
  {
    id: '00002',
    username: 'user',
    password: '123456', // 实际项目中应该使用加密后的密码
    roles: ['user'],
    introduction: '我是普通用户',
    avatar: 'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif',
    name: '普通用户',
    createTime: '2023-01-02 00:00:00'
  }
]

// 模拟生成用户token
const generateToken = (username) => {
  return `${username}-${Date.now()}`
}

// 存储token和用户的映射关系
const tokenMap = new Map()

// 生成新用户ID（自增）
const generateUserId = () => {
  const maxId = Math.max(...users.map(user => parseInt(user.id)), 0)
  return String(maxId + 1).padStart(5, '0')
}

module.exports = [
  // 用户登录
  {
    url: '/api/user/login',
    type: 'post',
    response: config => {
      const { username, password } = config.body
      
      // 在模拟数据库中查找用户
      const user = users.find(u => u.username === username)
      
      // 验证用户是否存在
      if (!user) {
        return {
          code: 60204,
          message: '用户名不存在'
        }
      }
      
      // 验证密码
      if (user.password !== password) {
        return {
          code: 60204,
          message: '密码错误'
        }
      }
      
      // 生成token并保存映射关系
      const token = generateToken(username)
      tokenMap.set(token, user)
      
      return {
        code: 20000,
        data: {
          token
        }
      }
    }
  },

  // 获取用户信息
  {
    url: '/api/user/info\.*',
    type: 'get',
    response: config => {
      const { token } = config.query
      
      // 先尝试从tokenMap中查找用户
      let user = tokenMap.get(token)
      
      // 如果tokenMap中找不到，尝试从token中解析用户名（token格式：username-timestamp）
      if (!user) {
        // 解析token获取用户名
        const tokenParts = token.split('-')
        if (tokenParts.length >= 1) {
          const username = tokenParts[0]
          // 从用户列表中查找
          user = users.find(u => u.username === username)
          // 如果找到用户，重新建立映射关系
          if (user) {
            tokenMap.set(token, user)
          }
        }
      }
      
      // 如果仍然找不到用户
      if (!user) {
        return {
          code: 50008,
          message: '登录失败，无法获取用户详情'
        }
      }
      
      // 返回用户信息，不包含敏感信息
      return {
        code: 20000,
        data: {
          roles: user.roles,
          introduction: user.introduction,
          avatar: user.avatar,
          name: user.name,
          id: user.id,
          userId: user.id // 确保userId字段也存在
        }
      }
    }
  },

  // 用户登出
  {
    url: '/api/user/logout',
    type: 'post',
    response: config => {
      // 支持从params或header中获取token
      let token = config.query?.token || ''
      
      // 如果params中没有token，尝试从header中获取
      if (!token) {
        token = config.headers?.authorization?.split(' ')[1] || ''
      }
      
      // 清除token映射
      if (token) {
        tokenMap.delete(token)
      }
      return {
        code: 20000,
        data: 'success'
      }
    }
  },
  
  // 新增：用户注册
  {
    url: '/api/user/register',
    type: 'post',
    response: config => {
      const { username, password } = config.body
      
      // 检查用户名是否已存在
      if (users.some(user => user.username === username)) {
        return {
          code: 60205,
          message: '用户名已存在，请更换用户名'
        }
      }
      
      // 检查必填字段
      if (!username || !password) {
        return {
          code: 40001,
          message: '用户名和密码不能为空'
        }
      }
      
      // 创建新用户
      const newUser = {
        id: generateUserId(),
        username,
        password, // 实际项目中应该使用加密后的密码
        roles: ['user'], // 默认为普通用户角色
        introduction: '我是普通用户',
        avatar: 'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif',
        name: username,
        createTime: new Date().toLocaleString('zh-CN')
      }
      
      // 将新用户添加到模拟数据库
      users.push(newUser)
      
      return {
        code: 20000,
        message: '注册成功',
        data: {
          userId: newUser.id
        }
      }
    }
  },
  
  // 新增：获取用户详情
  {
    url: '/api/user/detail',
    type: 'get',
    response: config => {
      const token = config.headers.authorization?.split(' ')[1] || ''
      
      // 通过token查找用户
      const user = tokenMap.get(token)
      
      if (!user) {
        return {
          code: 50008,
          message: '未登录或登录已过期'
        }
      }
      
      // 返回详细用户信息
      return {
        code: 20000,
        data: {
          id: user.id,
          username: user.username,
          name: user.name,
          roles: user.roles,
          createTime: user.createTime,
          avatar: user.avatar,
          introduction: user.introduction
        }
      }
    }
  }
]
