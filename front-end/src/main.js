import Vue from 'vue'

import 'normalize.css/normalize.css' // A modern alternative to CSS resets

import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'
import locale from 'element-ui/lib/locale/lang/en' // lang i18n

import '@/styles/index.scss' // global css

import App from './App'
import store from './store'
import router from './router'

import '@/icons' // icon
import '@/permission' // permission control

// 导入智能返回处理
import { setupNavigationGuard } from '@/utils/navigation-guard'

// 导入配置好的axios实例
import request from '@/utils/request'

/**
 * If you don't want to use mock-server
 * you want to use MockJs for mock api
 * you can execute: mockXHR()
 *
 * 现在禁用MockJs，使用真实的后端API
 */
// if (process.env.NODE_ENV === 'development') {
//   const { mockXHR } = require('../mock')
//   mockXHR()
// }

// set ElementUI lang to EN
Vue.use(ElementUI, { locale })
// 如果想要中文版 element-ui，按如下方式声明
// Vue.use(ElementUI)

// 将axios实例挂载到Vue原型上，以便在组件中使用this.$http
Vue.prototype.$http = request

Vue.config.productionTip = false

// 初始化智能返回处理
const navigationGuard = setupNavigationGuard(router)
window.navigationGuard = navigationGuard

new Vue({
  el: '#app',
  router,
  store,
  render: h => h(App)
})
