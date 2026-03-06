// 会话管理工具 - 支持多标签页会话隔离
const TokenKey = 'vue_admin_template_token'

// 生成标签页唯一标识
function generateTabId() {
  return 'tab_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now()
}

// 获取当前标签页ID
function getCurrentTabId() {
  let tabId = sessionStorage.getItem('current_tab_id')
  if (!tabId) {
    tabId = generateTabId()
    sessionStorage.setItem('current_tab_id', tabId)
  }
  return tabId
}

// 存储标签页token映射
function getTokenMap() {
  const mapStr = localStorage.getItem('token_tab_map')
  return mapStr ? JSON.parse(mapStr) : {}
}

// 更新标签页token映射
function updateTokenMap(tabId, token) {
  const map = getTokenMap()
  if (token) {
    map[tabId] = token
  } else {
    delete map[tabId]
  }
  localStorage.setItem('token_tab_map', JSON.stringify(map))
}

export function getToken() {
  // 优先从sessionStorage获取当前标签页的token
  const tabId = getCurrentTabId()
  const sessionToken = sessionStorage.getItem(`${TokenKey}_${tabId}`)

  if (sessionToken) {
    return sessionToken
  }

  // 如果sessionStorage没有，从localStorage的映射中获取
  const map = getTokenMap()
  const mapToken = map[tabId]

  if (mapToken) {
    // 同步到sessionStorage
    sessionStorage.setItem(`${TokenKey}_${tabId}`, mapToken)
    return mapToken
  }

  return null
}

export function setToken(token) {
  const tabId = getCurrentTabId()

  // 存储到sessionStorage（当前标签页）
  sessionStorage.setItem(`${TokenKey}_${tabId}`, token)

  // 更新localStorage的标签页映射
  updateTokenMap(tabId, token)

  // 设置页面可见性监听，处理标签页关闭
  if (!window.tokenVisibilityHandler) {
    window.tokenVisibilityHandler = function() {
      if (document.visibilityState === 'hidden') {
        // 页面不可见时，清理当前标签页的token映射
        const currentTabId = getCurrentTabId()
        const map = getTokenMap()
        delete map[currentTabId]
        localStorage.setItem('token_tab_map', JSON.stringify(map))
      }
    }
    document.addEventListener('visibilitychange', window.tokenVisibilityHandler)
  }
}

export function removeToken() {
  const tabId = getCurrentTabId()

  // 从sessionStorage移除
  sessionStorage.removeItem(`${TokenKey}_${tabId}`)

  // 从localStorage映射中移除
  updateTokenMap(tabId, null)

  // 清理页面可见性监听
  if (window.tokenVisibilityHandler) {
    document.removeEventListener('visibilitychange', window.tokenVisibilityHandler)
    window.tokenVisibilityHandler = null
  }
}

// 清理过期的标签页token映射
export function cleanupExpiredTokens() {
  const map = getTokenMap()
  const now = Date.now()
  let changed = false

  for (const tabId in map) {
    // 检查标签页是否过期（超过24小时）
    const timestamp = parseInt(tabId.split('_').pop())
    if (now - timestamp > 24 * 60 * 60 * 1000) {
      delete map[tabId]
      changed = true
    }
  }

  if (changed) {
    localStorage.setItem('token_tab_map', JSON.stringify(map))
  }
}
