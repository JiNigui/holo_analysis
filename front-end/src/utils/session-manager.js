/**
 * 会话管理器
 * 负责检测用户离开系统并自动清理会话
 */

import { removeToken } from '@/utils/auth'
import store from '@/store'

class SessionManager {
  constructor() {
    this.isSystemActive = false
    this.sessionTimeout = null
    this.pageHideTime = null
    this.maxInactiveTime = 30 * 60 * 1000 // 30分钟无操作视为离开
    this.init()
  }

  /**
   * 初始化会话管理器
   */
  init() {
    // 监听页面可见性变化
    this.setupVisibilityListener()
    // 监听页面卸载事件
    this.setupUnloadListener()
    // 监听用户活动
    this.setupActivityListener()
    // 监听路由变化
    this.setupRouteListener()
    console.log('会话管理器已初始化')
  }

  /**
   * 设置页面可见性监听
   */
  setupVisibilityListener() {
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        // 页面隐藏（切换到其他标签页、最小化等）
        this.handlePageHide()
      } else {
        // 页面重新显示
        this.handlePageShow()
      }
    })
  }

  /**
   * 设置页面卸载监听
   */
  setupUnloadListener() {
    // 移除页面卸载时的会话清理，因为页面刷新应该保持登录状态
    // 只在用户主动关闭标签页或浏览器时才清理会话
    window.addEventListener('beforeunload', (event) => {
      // 这里可以添加一些清理逻辑，但不应该清除token
      // 保持用户登录状态，让路由守卫来处理会话验证
      console.log('页面即将卸载，保持会话状态')
    })

    window.addEventListener('unload', () => {
      // 页面卸载时也不清理会话，保持登录状态
      console.log('页面卸载完成，会话状态保持')
    })
  }

  /**
   * 设置用户活动监听
   */
  setupActivityListener() {
    const activityEvents = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart']
    activityEvents.forEach(eventName => {
      document.addEventListener(eventName, () => {
        this.handleUserActivity()
      }, { passive: true })
    })
  }

  /**
   * 设置路由变化监听
   */
  setupRouteListener() {
    // 监听路由变化，检测是否离开系统
    if (window.vueRouter) {
      window.vueRouter.beforeEach((to, from, next) => {
        // 检查是否从系统页面跳转到登录页面
        if (this.isSystemPage(from.path) && to.path === '/login') {
          this.handleSystemExit()
        }
        next()
      })
    }
  }

  /**
   * 判断是否为系统页面
   */
  isSystemPage(path) {
    const systemPages = ['/dashboard', '/profile', '/projects', '/audit', '/users']
    return systemPages.some(systemPath => path.startsWith(systemPath))
  }
  /**
   * 处理页面隐藏
   */
  handlePageHide() {
    this.pageHideTime = Date.now()
    console.log('页面隐藏，开始计时')
    // 设置超时检查
    this.sessionTimeout = setTimeout(() => {
      if (this.isSystemActive && this.pageHideTime) {
        const hiddenDuration = Date.now() - this.pageHideTime
        if (hiddenDuration >= this.maxInactiveTime) {
          console.log('页面长时间隐藏，自动清理会话')
          this.cleanupSession()
        }
      }
    }, this.maxInactiveTime)
  }
  /**
   * 处理页面显示
   */
  handlePageShow() {
    this.pageHideTime = null
    if (this.sessionTimeout) {
      clearTimeout(this.sessionTimeout)
      this.sessionTimeout = null
    }
    console.log('页面重新显示')
  }
  /**
   * 处理页面卸载
   */
  handlePageUnload() {
    console.log('页面卸载，清理会话')
    this.cleanupSession()
  }
  /**
   * 处理用户活动
   */
  handleUserActivity() {
    // 重置超时计时器
    if (this.sessionTimeout) {
      clearTimeout(this.sessionTimeout)
      this.sessionTimeout = null
    }
  }
  /**
   * 处理系统退出
   */
  handleSystemExit() {
    console.log('检测到系统退出，清理会话')
    this.cleanupSession()
  }
  /**
   * 设置系统活动状态
   */
  setSystemActive(active) {
    this.isSystemActive = active
    if (active) {
      console.log('系统进入活动状态')
    } else {
      console.log('系统进入非活动状态')
      this.cleanupSession()
    }
  }
  /**
   * 清理会话
   */
  cleanupSession() {
    if (!this.isSystemActive) return
    console.log('开始清理会话')
    // 清除token
    removeToken()
    // 重置store状态
    if (store && store.dispatch) {
      store.dispatch('user/resetToken').catch(() => {
        // 如果store不可用，直接清除localStorage
        localStorage.removeItem('vuex')
      })
    }
    // 清除本地存储的用户数据
    localStorage.removeItem('currentUser')
    this.isSystemActive = false
    console.log('会话清理完成')
  }
  /**
   * 销毁会话管理器
   */
  destroy() {
    if (this.sessionTimeout) {
      clearTimeout(this.sessionTimeout)
      this.sessionTimeout = null
    }
    // 移除事件监听器
    document.removeEventListener('visibilitychange', this.handleVisibilityChange)
    window.removeEventListener('beforeunload', this.handleBeforeUnload)
    window.removeEventListener('unload', this.handleUnload)
    console.log('会话管理器已销毁')
  }
}

// 创建全局会话管理器实例
const sessionManager = new SessionManager()

// 暴露到全局，方便其他模块访问
if (typeof window !== 'undefined') {
  window.sessionManager = sessionManager
}

export default sessionManager
