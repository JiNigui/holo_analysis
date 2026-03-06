import router from './router'
import store from './store'
import { Message } from 'element-ui'
import NProgress from 'nprogress' // progress bar
import 'nprogress/nprogress.css' // progress bar style
import { getToken } from '@/utils/auth' // get token from cookie
import getPageTitle from '@/utils/get-page-title'
import { checkSession } from '@/api/user'
import sessionManager from '@/utils/session-manager'

NProgress.configure({ showSpinner: false }) // NProgress Configuration

const whiteList = ['/login', '/register'] // no redirect whitelist

// 检查用户是否有权限访问指定路由
export function hasPermission(roles, permissionRoles) {
  if (!permissionRoles) return true // 如果路由没有设置roles，所有角色都可以访问
  if (!roles || !Array.isArray(roles) || roles.length === 0) return false // 如果用户没有角色信息，返回false
  return roles.some(role => permissionRoles.includes(role))
}

router.beforeEach(async(to, from, next) => {
  // start progress bar
  NProgress.start()

  // set page title
  document.title = getPageTitle(to.meta.title)

  // 直接处理白名单路由，避免不必要的token检查
  if (whiteList.indexOf(to.path) !== -1) {
    // 如果是登录页面，确保清除可能无效的token
    if (to.path === '/login' && getToken()) {
      await store.dispatch('user/resetToken')
      // 设置系统为非活动状态
      sessionManager.setSystemActive(false)
    }
    next()
    NProgress.done()
    return
  }

  // determine whether the user has logged in
  const hasToken = getToken()

  if (hasToken) {
    // 检查用户信息是否已经设置（登录时或页面刷新时）
    // 放宽检查条件：只要有token且用户信息获取成功即可，不强制要求roles.length > 0
    const hasUserInfo = store.getters.name || (store.getters.roles && store.getters.roles.length > 0)

    if (hasUserInfo) {
      // 用户信息已存在，检查权限并导航
      if (hasPermission(store.getters.roles, to.meta.roles)) {
        // 检查是否需要替换历史记录（从登录页面跳转过来）
        if (from.path === '/login' && to.path !== '/login') {
          // 从登录页面跳转过来，替换历史记录
          if (window.navigationGuard && !window.navigationGuard.hasInitialized) {
            console.log('登录后跳转，执行历史记录替换')
            window.navigationGuard.replaceHistoryAfterLogin()
          } else {
            console.log('当前标签页已初始化过历史记录，跳过重复操作')
          }
        }

        // 额外保护：如果当前路径是登录页，立即跳转到系统入口
        if (to.path === '/login' && window.navigationGuard) {
          console.log('检测到意外跳转到登录页，立即跳回系统')
          next({ path: '/dashboard', replace: true })
          return
        }

        // 检查会话有效性（防止账号在其他地方登录）
        try {
          // 使用专门的会话检查API验证会话有效性
          await checkSession()
          // 会话有效，设置系统为活动状态
          sessionManager.setSystemActive(true)
          next()
        } catch (error) {
          // 会话无效，清除token并跳转到登录页
          await store.dispatch('user/resetToken')
          // 设置系统为非活动状态
          sessionManager.setSystemActive(false)
          Message.error('账号已在其他地方登录，请重新登录')
          next(`/login?redirect=${to.path}`)
          NProgress.done()
        }
      } else {
        // 没有权限，重定向到404页面
        next({ path: '/404', replace: true })
      }
    } else {
      try {
        // 登录成功后，需要获取用户信息并生成权限路由
        await store.dispatch('user/getInfo')

        // 获取用户信息后，生成权限路由
        const { roles } = store.getters
        const accessRoutes = await store.dispatch('permission/generateRoutes', roles)

        // 动态添加权限路由到router实例
        router.addRoutes(accessRoutes)

        // 设置系统为活动状态
        sessionManager.setSystemActive(true)

        // 确保路由添加完成后再进行跳转
        // 使用next()让Vue Router重新匹配当前路由
        if (to.path === '/login' || to.path === '/') {
          // 对于登录页或根路径，直接跳转到dashboard
          next({ path: '/dashboard', replace: true })
        } else {
          // 对于其他路径，重新匹配当前路由
          next({ ...to, replace: true })
        }
      } catch (error) {
        // remove token and go to login page to re-login
        await store.dispatch('user/resetToken')
        Message.error(error || '登录状态已过期，请重新登录')
        next(`/login?redirect=${to.path}`)
        NProgress.done()
      }
    }
  } else {
    /* has no token*/

    if (whiteList.indexOf(to.path) !== -1) {
      // in the free login whitelist, go directly
      next()
    } else {
      // other pages that do not have permission to access are redirected to the login page.
      next(`/login?redirect=${to.path}`)
      NProgress.done()
    }
  }
})

router.afterEach(() => {
  // finish progress bar
  NProgress.done()
})
