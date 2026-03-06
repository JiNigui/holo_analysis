import Vue from 'vue'
import Router from 'vue-router'

Vue.use(Router)

/**
 * Note: sub-menu only appear when route children.length >= 1
 * Detail see: https://panjiachen.github.io/vue-element-admin-site/guide/essentials/router-and-nav.html
 *
 * hidden: true                   if set true, item will not show in the sidebar(default is false)
 * alwaysShow: true               if set true, will always show the root menu
 *                                if not set alwaysShow, when item has more than one children route,
 *                                it will becomes nested mode, otherwise not show the root menu
 * redirect: noRedirect           if set noRedirect will no redirect in the breadcrumb
 * name:'router-name'             the name is used by <keep-alive> (must set!!!)
 * meta : {
    roles: ['admin','editor']    control the page roles (you can set multiple roles)
    title: 'title'               the name show in sidebar and breadcrumb (recommend set)
    icon: 'svg-name'/'el-icon-x' the icon show in the sidebar
    breadcrumb: false            if set false, the item will hidden in breadcrumb(default is true)
    activeMenu: '/example/list'  if set path, the sidebar will highlight the path you set
  }
 */

/**
 * constantRoutes
 * a base page that does not have permission requirements
 * all roles can be accessed
 */
// 引入Layout组件
import Layout from '@/layout'

// 公共路由
export const constantRoutes = [
  {
    path: '/login',
    component: () => import('@/views/login/index'),
    hidden: true
  },
  {
    path: '/404',
    component: () => import('@/views/404'),
    hidden: true
  },
  {
    path: '/',
    redirect: '/dashboard'
  }
]

// 动态路由（基于角色权限）
export const asyncRoutes = [
  // 系统概览
  {
    path: '/dashboard',
    component: Layout,
    redirect: '/dashboard',
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index'),
        meta: {
          title: '系统概览',
          icon: 'dashboard',
          roles: ['user', 'admin']
        }
      }
    ]
  },
  // 个人信息
  {
    path: '/profile',
    component: Layout,
    redirect: '/profile',
    children: [
      {
        path: '',
        name: 'Profile',
        component: () => import('@/views/profile/index'),
        meta: {
          title: '个人信息',
          icon: 'user',
          roles: ['user', 'admin']
        }
      }
    ]
  },
  // 项目列表
  {
    path: '/projects',
    component: Layout,
    redirect: '/projects/index',
    children: [
      {
        path: 'index',
        name: 'Projects',
        component: () => import('@/views/project/index'),
        meta: {
          title: '项目列表',
          icon: 'example',
          roles: ['user', 'admin']
        }
      },
      {
        path: 'create',
        name: 'ProjectCreate',
        component: () => import('@/views/project/create.vue'),
        meta: {
          title: '创建项目',
          noCache: true,
          roles: ['user', 'admin']
        },
        hidden: true
      },
      {
        path: 'detail/:id',
        name: 'ProjectDetail',
        component: () => import('@/views/project/detail.vue'),
        meta: {
          title: '项目详情',
          noCache: true,
          roles: ['user', 'admin']
        },
        hidden: true
      }
    ]
  },
  // VOI选取功能 - 已整合到项目详情页，保留独立路由作为备用
  // 管理员路由
  {
    path: '/admin',
    component: Layout,
    redirect: '/admin/users',
    name: 'Admin',
    meta: {
      title: '管理员功能',
      icon: 'el-icon-setting',
      roles: ['admin']
    },
    children: [
      {
        path: 'users',
        name: 'UserManagement',
        component: () => import('@/views/user/index'),
        meta: {
          title: '用户管理',
          roles: ['admin']
        }
      },
      {
        path: 'create',
        name: 'CreateUser',
        component: () => import('@/views/user/create.vue'),
        meta: {
          title: '添加用户',
          roles: ['admin']
        },
        hidden: true
      },
      {
        path: 'logs',
        name: 'SystemLogs',
        component: () => import('@/views/audit/index'),
        meta: {
          title: '系统日志',
          roles: ['admin']
        }
      }
    ]
  },
  { path: '*', redirect: '/404', hidden: true }
]

const createRouter = () => new Router({
  // mode: 'history', // require service support
  scrollBehavior: () => ({ y: 0 }),
  routes: constantRoutes // 初始只加载公共路由
})

const router = createRouter()

// Detail see: https://github.com/vuejs/vue-router/issues/1234#issuecomment-357941465
export function resetRouter() {
  const newRouter = createRouter()
  router.matcher = newRouter.matcher // reset router
}

export default router

