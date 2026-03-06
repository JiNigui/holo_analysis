import { login, logout, getInfo } from '@/api/user'
import { createLog, LOG_TYPES } from '@/api/logs'
import { getToken, setToken, removeToken } from '@/utils/auth'
import { resetRouter } from '@/router'
// - API 函数 ：从 @/api/user 导入用户相关的 API 调用函数（登录、登出、获取用户信息）
// - 认证工具 ：从 @/utils/auth 导入处理 token 的工具函数
// - 路由工具 ：从 @/router 导入重置路由的函数

// 状态初始化
const getDefaultState = () => {
  return {
    token: getToken(),
    name: '',
    avatar: '',
    roles: [], // 新增角色信息
    userId: '', // 新增用户ID
    userInfo: {}, // 新增用户详细信息
    tabId: '' // 新增标签页ID，用于会话隔离
  }
}

const state = getDefaultState()

const mutations = {
  RESET_STATE: (state) => {
    // 重置状态，但保留从存储中读取的token
    const defaultState = getDefaultState()
    // 确保token始终从存储中获取最新值
    state.token = defaultState.token
    state.name = ''
    state.avatar = ''
    state.roles = []
    state.userId = ''
    state.userInfo = {}
    state.tabId = ''
  },
  SET_TOKEN: (state, token) => {
    state.token = token
  },
  SET_NAME: (state, name) => {
    state.name = name
  },
  SET_AVATAR: (state, avatar) => {
    state.avatar = avatar
  },
  SET_ROLES: (state, roles) => {
    state.roles = roles
  },
  SET_USERID: (state, userId) => {
    state.userId = userId
  },
  SET_USERINFO: (state, userInfo) => {
    state.userInfo = userInfo
  },
  SET_TABID: (state, tabId) => {
    state.tabId = tabId
  }
}

const actions = {
  // 用户登录 - 适配JWT认证
  login({ commit }, userInfo) {
    const { username, password } = userInfo
    return new Promise((resolve, reject) => {
      login({ username: username.trim(), password: password }).then(response => {
        // 处理后端返回的数据格式：{ message, token, user }
        let token = null
        let userData = null

        // 处理不同的响应格式
        if (typeof response === 'object') {
          // 后端返回格式：{ message: '登录成功', token: 'xxx', user: {...} }
          // 适配后端实际返回格式
          token = response.token || response.data?.token
          userData = response.user || response.data?.user
        } else {
          token = response
        }

        if (!token) {
          return reject(new Error('登录失败：未获取到token'))
        }

        // 设置token到store和cookie
        commit('SET_TOKEN', token)
        setToken(token)

        // 如果登录响应中包含了用户信息，直接设置到store中
        if (userData) {
          const userId = userData.id || userData.userId
          const username = userData.username || userData.name
          const role = userData.role || userData.roles || []
          const roles = Array.isArray(role) ? role : [role]
          const avatar = userData.avatar || `https://api.dicebear.com/7.x/initials/svg?seed=${encodeURIComponent(username)}`

          commit('SET_USERID', userId)
          commit('SET_NAME', username)
          commit('SET_ROLES', roles)
          commit('SET_USERINFO', userData)
          commit('SET_AVATAR', avatar)

          // 登录成功后记录日志（异步，不阻塞登录流程）
          createLog({
            operation_type: LOG_TYPES.USER_LOGIN, // 操作类型即操作名称
            user_id: userId,
            status: 'success'
          }).catch(error => {
            console.error('记录登录日志失败:', error)
          })
        }

        resolve(response) // 返回完整的响应数据
      }).catch(error => {
        reject(error)
      })
    })
  },

  // 获取用户详细信息 - 复用getInfo
  getUserDetail({ dispatch }) {
    // 复用getInfo方法，保持代码一致性
    return dispatch('getInfo')
  },

  // 获取用户信息 - 适配后端JWT用户信息接口
  getInfo({ commit, state }) {
    return new Promise((resolve, reject) => {
      getInfo().then(response => {
        // 处理后端返回的用户信息，后端返回格式为 { message, user: { id, username, email, role } }
        // 适配后端实际返回格式
        const userData = response.user || response.data || response

        if (!userData) {
          return reject('获取用户信息失败')
        }

        // 从用户数据中提取信息，适配后端JWT返回格式
        const userId = userData.id || userData.userId
        const username = userData.username || userData.name
        const role = userData.role || userData.roles || []
        // 将后端单个role转换为roles数组，适配前端路由权限控制
        const roles = Array.isArray(role) ? role : [role]
        // 设置用户信息到store
        commit('SET_USERID', userId)
        commit('SET_NAME', username)
        commit('SET_ROLES', roles)
        commit('SET_USERINFO', userData)
        // 为没有头像的用户设置默认头像
        const avatar = userData.avatar || `https://api.dicebear.com/7.x/initials/svg?seed=${encodeURIComponent(username)}`
        commit('SET_AVATAR', avatar)
        resolve(userData)
      }).catch(error => {
        reject(error)
      })
    })
  },

  // 登出 - 适配JWT认证
  logout({ commit, state }) {
    return new Promise((resolve, reject) => {
      // 在登出前记录日志（在清除token之前）
      const userId = state.userId
      const username = state.name

      // 先记录登出日志（在token有效时）
      const logPromise = userId && username ? createLog({
        operation_type: LOG_TYPES.USER_LOGOUT, // 操作类型即操作名称
        user_id: userId,
        status: 'success'
      }).catch(error => {
        console.warn('记录登出日志失败（不影响登出）:', error)
      }) : Promise.resolve()

      // 调用后端logout接口
      logPromise.then(() => {
        return logout().catch(error => {
          console.warn('登出请求失败（继续清除本地状态）:', error)
        })
      }).then(() => {
        // 清除本地token和状态
        removeToken() // 删除cookie中的token
        resetRouter()
        commit('RESET_STATE')

        // 设置系统为非活动状态
        if (window.sessionManager) {
          window.sessionManager.setSystemActive(false)
        }

        resolve()
      }).catch(error => {
        // 确保无论如何都清除本地状态
        removeToken()
        resetRouter()
        commit('RESET_STATE')

        // 设置系统为非活动状态
        if (window.sessionManager) {
          window.sessionManager.setSystemActive(false)
        }

        resolve() // 仍然返回成功，确保用户能退出
      })
    })
  },

  // 重置 token
  resetToken({ commit }) {
    return new Promise(resolve => {
      removeToken() // must remove  token  first
      commit('RESET_STATE')
      resolve()
    })
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions
}

