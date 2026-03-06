import axios from 'axios'
// 导入 axios 库，这是一个流行的 HTTP 客户端库，用于在浏览器和 Node.js 中发送 HTTP 请求。在 Vue 项目中，我们通常用它来与后端 API 交互。
import { MessageBox, Message } from 'element-ui'
// 从 Element UI 组件库导入消息提示组件。Element UI 是 Vue 的一个常用 UI 组件库。
import store from '@/store'
// 导入 Vuex store 实例。Vuex 是 Vue 的状态管理库，这里用来访问全局状态（如用户 token）。
import { getToken } from '@/utils/auth'
// 从 @/utils/auth.js 文件导入 getToken 函数，这个函数用于从存储（如 Cookie）中获取用户的认证令牌。

// 创建 axios 实例
const service = axios.create({
  // 使用环境变量或默认值作为API基础路径，方便不同环境部署
  // 开发环境：使用代理，baseURL设置为/api，代理会转发到后端
  // 生产环境：可以设置为完整的后端地址
  baseURL: process.env.VUE_APP_BASE_API || '/api', // 开发环境使用代理，添加/api前缀
  withCredentials: true, // 发送cookies，支持跨域请求
  timeout: 600000 // 10分钟超时，适应VOI选取等耗时操作（600秒）
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    // do something before request is sent

    if (store.getters.token) {
      // 使用标准的Authorization头传递JWT令牌
      config.headers['Authorization'] = 'Bearer ' + getToken()
    }
    return config
  },
  error => {
    // do something with request error
    console.log(error) // for debug
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  /**
   * 获取响应数据
   */
  response => {
    // 检查是否是二进制响应（如ZIP文件下载）
    const contentType = response.headers['content-type'] || ''
    const isBinaryResponse = contentType.includes('application/zip') ||
                            contentType.includes('application/octet-stream') ||
                            response.config.responseType === 'blob'

    // 如果是二进制响应，直接返回原始响应对象
    if (isBinaryResponse) {
      return response
    }

    const res = response.data

    // 根据孔洞分析软件的后端API设计，调整响应判断逻辑
    // 假设后端返回格式为: { success: true/false, data: any, message: string }
    if (typeof res.success === 'boolean') {
      if (!res.success) {
        Message({
          message: res.message || '操作失败',
          type: 'error',
          duration: 5 * 1000
        })
        return Promise.reject(new Error(res.message || '操作失败'))
      }
      return res // 返回完整响应对象，确保action中可以正确解构response.data
    }

    // 兼容原有格式
    if (res.code !== undefined) {
      // token相关错误码
      if (res.code === 401 || res.code === 403 || res.code === 50008 || res.code === 50012 || res.code === 50014) {
        // 未授权或token过期，需要重新登录
        MessageBox.confirm('登录已过期，请重新登录', '确认退出', {
          confirmButtonText: '重新登录',
          cancelButtonText: '取消',
          type: 'warning'
        }).then(() => {
          store.dispatch('user/resetToken').then(() => {
            location.reload()
          })
        })
        return Promise.reject(new Error('登录已过期'))
      }

      // 其他错误
      if (res.code !== 200 && res.code !== 20000) {
        Message({
          message: res.message || '请求失败',
          type: 'error',
          duration: 5 * 1000
        })
        return Promise.reject(new Error(res.message || '请求失败'))
      }
    }

    return res
  },
  error => {
    console.log('请求错误:', error) // 更详细的错误日志

    // 分类处理不同类型的错误
    let errorMessage = '网络错误，请稍后重试'

    if (error.response) {
      // 服务器返回错误状态码
      switch (error.response.status) {
        case 400:
          errorMessage = '请求参数错误'
          break
        case 401:
          errorMessage = '未授权，请重新登录'
          // 跳转到登录页面
          store.dispatch('user/resetToken').then(() => {
            location.reload()
          })
          break
        case 403:
          errorMessage = '拒绝访问'
          break
        case 404:
          errorMessage = '请求的资源不存在'
          break
        case 408:
          errorMessage = '请求超时'
          break
        case 500:
          errorMessage = '服务器内部错误'
          break
        case 501:
          errorMessage = '服务器未实现该请求'
          break
        case 502:
          errorMessage = '网关错误'
          break
        case 503:
          errorMessage = '服务不可用'
          break
        case 504:
          errorMessage = '网关超时'
          break
        default:
          errorMessage = `请求失败 (${error.response.status})`
      }

      // 显示错误消息
      Message({
        message: errorMessage,
        type: 'error',
        duration: 5 * 1000
      })
    } else if (error.request) {
      // 请求已发出但没有收到响应
      Message({
        message: '服务器无响应，请检查网络连接',
        type: 'error',
        duration: 5 * 1000
      })
    } else {
      // 请求配置出错
      Message({
        message: error.message || '请求失败',
        type: 'error',
        duration: 5 * 1000
      })
    }

    return Promise.reject(error)
  }
)

export default service
