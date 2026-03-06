import { constantRoutes, asyncRoutes } from '@/router'

const state = {
  routes: [],
  addRoutes: []
}

const mutations = {
  SET_ROUTES: (state, routes) => {
    state.addRoutes = routes.filter(route => !constantRoutes.find(c => c.path === route.path))
    state.routes = constantRoutes.concat(routes) // 合并constantRoutes和过滤后的动态路由
  }
}

const actions = {
  generateRoutes({ commit }, roles) {
    return new Promise(resolve => {
      let accessedRoutes = []

      // 定义内部的hasPermission函数
      const hasPermission = (userRoles, permissionRoles) => {
        if (!permissionRoles) return true
        if (!userRoles || !Array.isArray(userRoles) || userRoles.length === 0) return false
        return userRoles.some(role => permissionRoles.includes(role))
      }

      // 递归过滤子路由
      const filterAsyncRoutes = (routes, roles) => {
        const res = []

        routes.forEach(route => {
          // 复制路由对象
          const tmp = { ...route }

          // 只检查权限，不检查hidden属性，因为hidden路由也需要被加载（只是不在菜单显示）
          if (hasPermission(roles, tmp.meta && tmp.meta.roles)) {
            // 如果有子路由，递归过滤
            if (tmp.children && tmp.children.length > 0) {
              tmp.children = filterAsyncRoutes(tmp.children, roles)
            }
            res.push(tmp)
          }
        })

        return res
      }

      // 只过滤asyncRoutes，constantRoutes在SET_ROUTES中合并
      accessedRoutes = filterAsyncRoutes(asyncRoutes, roles)

      commit('SET_ROUTES', accessedRoutes)
      resolve(accessedRoutes)
    })
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions
}
