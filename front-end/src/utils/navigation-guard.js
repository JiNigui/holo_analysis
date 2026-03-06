/**
 * 智能返回导航守卫
 * 功能：防止用户意外返回到登录页面，提供智能返回体验
 */

import { Message, MessageBox } from 'element-ui'
import store from '@/store'

class NavigationGuard {
  constructor() {
    this.loginTime = null
    this.isSystemBoundary = false
    this.systemEntryPath = '/dashboard' // 系统入口页面
    this.loginPath = '/login'
    this.hasInitialized = false // 标记是否已初始化
    this.tabId = null // 标签页唯一标识
    this.currentState = null // 当前历史状态
    this.init()
  }

  init() {
    // 监听浏览器返回/前进事件
    window.addEventListener('popstate', this.handlePopState.bind(this))

    // 监听路由变化
    this.setupRouteListener()

    console.log('智能返回导航守卫已初始化')
  }

  setupRouteListener() {
    // 监听Vue Router路由变化
    if (window.vueRouter) {
      window.vueRouter.afterEach((to, from) => {
        this.handleRouteChange(to, from)
      })
    }
  }

  /**
   * 处理路由变化
   */
  handleRouteChange(to, from) {
    // 记录登录时间
    if (to.path === this.systemEntryPath && from.path === this.loginPath) {
      this.loginTime = Date.now()
      this.isSystemBoundary = false
      console.log('用户登录进入系统，记录登录时间')
    }

    // 检查是否到达系统边界
    this.checkSystemBoundary(to)
  }

  /**
   * 检查是否到达系统边界
   */
  checkSystemBoundary(to) {
    // 如果当前页面是系统入口页面，标记为系统边界
    if (to.path === this.systemEntryPath) {
      this.isSystemBoundary = true
    } else {
      this.isSystemBoundary = false
    }
  }

  /**
   * 处理浏览器返回/前进事件
   */
  handlePopState(event) {
    const currentPath = window.location.pathname
    const hasToken = store.getters.token

    // 只有在用户已登录且当前在系统内时才处理
    if (!hasToken || currentPath === this.loginPath) {
      return
    }

    console.log('检测到popstate事件，当前路径:', currentPath)
    console.log('历史记录状态:', window.history.state)

    // 检查历史状态是否属于当前标签页，避免跨标签页干扰
    const historyState = window.history.state
    if (historyState && !this.isCurrentTabState(historyState)) {
      console.log('检测到其他标签页的历史状态，跳过处理')
      return
    }

    // 检查是否尝试返回到登录页（这是唯一应该显示系统边界提醒的情况）
    if (this.isTryingToReturnToLogin()) {
      console.log('检测到尝试返回登录页，显示系统边界提醒')
      // 立即阻止默认行为并推回当前页面
      event.preventDefault()
      this.stayInSystem()
      this.handleSystemBoundary()
      return
    }

    // 其他情况（正常系统内导航）不显示系统边界提醒，只阻止返回操作
    if (historyState && historyState.from === 'login') {
      console.log('历史记录状态显示来自登录页，阻止返回但不显示提醒')
      event.preventDefault()
      this.stayInSystem()
      return
    }

    // 如果当前路径是系统入口页面，阻止返回但不显示提醒
    if (currentPath === this.systemEntryPath) {
      console.log('当前在系统入口页面，阻止返回但不显示提醒')
      event.preventDefault()
      this.stayInSystem()
      return
    }
  }

  /**
   * 检查是否尝试返回到登录页
   */
  isTryingToReturnToLogin() {
    const historyState = window.history.state
    // 检查历史记录状态，判断是否包含登录页
    return historyState && historyState.from === 'login'
  }

  /**
   * 处理系统退出尝试
   */
  handleSystemExitAttempt() {
    // 检查登录时间，如果是刚登录不久，可能是误操作
    const timeSinceLogin = Date.now() - this.loginTime

    if (timeSinceLogin < 30000) { // 30秒内
      this.showQuickExitConfirm()
    } else {
      this.showExitConfirm()
    }
  }

  /**
   * 处理系统边界
   */
  handleSystemBoundary() {
    this.showStayInSystemConfirm()
  }

  /**
   * 显示快速退出确认（刚登录时）
   */
  showQuickExitConfirm() {
    MessageBox.confirm(
      '您刚刚登录系统，确定要退出吗？可能是误操作。',
      '退出确认',
      {
        confirmButtonText: '确定退出',
        cancelButtonText: '留在系统',
        type: 'warning',
        closeOnClickModal: false
      }
    ).then(() => {
      this.performLogout()
    }).catch(() => {
      this.stayInSystem()
      Message.info('已取消退出，继续使用系统')
    })
  }

  /**
   * 显示退出确认对话框
   */
  showExitConfirm() {
    MessageBox.confirm(
      '确定要退出系统吗？退出后将需要重新登录。',
      '退出确认',
      {
        confirmButtonText: '确定退出',
        cancelButtonText: '取消',
        type: 'warning',
        closeOnClickModal: false
      }
    ).then(() => {
      this.performLogout()
    }).catch(() => {
      this.stayInSystem()
    })
  }

  /**
   * 显示留在系统确认
   */
  showStayInSystemConfirm() {
    MessageBox.confirm(
      '您已到达系统边界，继续返回将退出系统。是否确定退出？',
      '系统边界',
      {
        confirmButtonText: '退出系统',
        cancelButtonText: '留在系统',
        type: 'info',
        closeOnClickModal: false
      }
    ).then(() => {
      this.performLogout()
    }).catch(() => {
      this.stayInSystem()
      Message.info('已取消退出，继续使用系统')
    })
  }

  /**
   * 执行退出登录
   */
  performLogout() {
    store.dispatch('user/logout').then(() => {
      // 使用replace而不是push，避免产生新的历史记录
      if (window.vueRouter) {
        window.vueRouter.replace(this.loginPath)
      } else {
        window.location.replace(this.loginPath)
      }
      Message.success('已安全退出系统')
    })
  }

  /**
   * 停留在系统内
   */
  stayInSystem() {
    console.log('执行stayInSystem，保持用户在系统内')

    // 创建新的历史状态，包含标签页唯一标识
    const newState = {
      from: 'system',
      timestamp: Date.now(),
      isSystemPage: true,
      preventBack: true,
      tabId: this.tabId // 添加标签页唯一标识
    }

    // 只推入一个历史记录，避免过度填充历史栈
    window.history.pushState(newState, '', window.location.href)

    console.log('已添加历史记录，当前历史长度:', window.history.length)

    // 额外保护：如果当前路径是登录页，立即跳转到系统入口
    if (window.location.pathname === this.loginPath) {
      console.log('检测到意外跳转到登录页，立即跳回系统')
      if (window.vueRouter) {
        window.vueRouter.replace(this.systemEntryPath)
      }
    }
  }

  /**
   * 登录成功后调用，替换登录页历史记录
   */
  onLoginSuccess() {
    // 替换登录页的历史记录，避免可以返回到登录页
    window.history.replaceState(
      { from: 'login', timestamp: Date.now() },
      '',
      this.systemEntryPath
    )

    this.loginTime = Date.now()
    this.isSystemBoundary = true

    console.log('登录成功，已替换历史记录')
  }

  /**
   * 登录后替换历史记录，防止返回登录页面
   */
  replaceHistoryAfterLogin() {
    console.log('Replacing history after login')

    // 检查当前标签页是否已经初始化过，避免多个标签页冲突
    if (this.hasInitialized) {
      console.log('当前标签页已初始化过历史记录，跳过重复操作')
      return
    }

    // 获取当前路由信息
    const currentPath = window.location.pathname
    const currentSearch = window.location.search
    const currentHash = window.location.hash

    // 创建新的历史状态，包含标签页唯一标识
    const newState = {
      timestamp: Date.now(),
      path: currentPath,
      search: currentSearch,
      hash: currentHash,
      isSystemPage: true,
      from: 'system',
      tabId: this.generateTabId() // 添加标签页唯一标识
    }

    // 首先替换当前历史记录，移除登录页面的历史记录
    window.history.replaceState(newState, '', window.location.href)

    // 然后推入一个新的历史记录，确保系统概览页面成为历史栈的起点
    window.history.pushState(newState, '', window.location.href)

    // 标记当前标签页已初始化
    this.hasInitialized = true
    this.currentState = newState
    this.isSystemBoundary = true
    this.loginTime = Date.now()

    console.log('History replaced after login, current state:', this.currentState)
    console.log('History length after replacement:', window.history.length)
  }

  /**
   * 生成标签页唯一标识
   */
  generateTabId() {
    if (!this.tabId) {
      this.tabId = 'tab_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
    }
    return this.tabId
  }

  /**
   * 检查当前历史状态是否属于当前标签页
   */
  isCurrentTabState(state) {
    return state && state.tabId === this.tabId
  }

  /**
   * 销毁实例
   */
  destroy() {
    window.removeEventListener('popstate', this.handlePopState)
    console.log('智能返回导航守卫已销毁')
  }
}

// 创建单例实例
let navigationGuardInstance = null

export function setupNavigationGuard(router) {
  if (!navigationGuardInstance) {
    // 将router实例挂载到window，方便访问
    window.vueRouter = router
    navigationGuardInstance = new NavigationGuard()
  }
  return navigationGuardInstance
}

export function getNavigationGuard() {
  return navigationGuardInstance
}

export default NavigationGuard
