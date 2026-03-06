// 测试用户登录状态和token
console.log('=== 前端登录状态检查 ===');

// 检查token存储
const tokenKey = 'vue_admin_template_token';
const currentTabId = sessionStorage.getItem('current_tab_id');
console.log('当前标签页ID:', currentTabId);

// 检查sessionStorage中的token
if (currentTabId) {
  const sessionToken = sessionStorage.getItem(`${tokenKey}_${currentTabId}`);
  console.log('SessionStorage Token:', sessionToken ? '存在' : '不存在');
  if (sessionToken) {
    console.log('Token长度:', sessionToken.length);
  }
}

// 检查localStorage中的token映射
const tokenMapStr = localStorage.getItem('token_tab_map');
console.log('LocalStorage Token映射:', tokenMapStr ? '存在' : '不存在');
if (tokenMapStr) {
  const tokenMap = JSON.parse(tokenMapStr);
  console.log('Token映射数量:', Object.keys(tokenMap).length);
  console.log('Token映射内容:', tokenMap);
}

// 检查Vuex store中的用户状态
if (window.store) {
  const token = window.store.getters.token;
  console.log('Vuex Store Token:', token ? '存在' : '不存在');
  if (token) {
    console.log('Vuex Token长度:', token.length);
  }
}

console.log('=== 检查完成 ===');

// 测试API调用
async function testApiCall() {
  try {
    console.log('测试项目详情API调用...');
    const projectId = 1; // 测试项目ID
    
    // 获取token
    const token = sessionStorage.getItem(`${tokenKey}_${currentTabId}`) || 
                  (tokenMapStr && JSON.parse(tokenMapStr)[currentTabId]);
    
    if (!token) {
      console.log('❌ 未找到有效token，请先登录系统');
      return;
    }
    
    console.log('使用Token进行API调用...');
    
    const response = await fetch(`/api/project/${projectId}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    console.log('API响应状态:', response.status);
    console.log('API响应头:', Object.fromEntries(response.headers.entries()));
    
    if (response.ok) {
      const data = await response.json();
      console.log('API响应数据:', data);
    } else {
      console.log('API调用失败:', response.statusText);
    }
  } catch (error) {
    console.error('API测试错误:', error);
  }
}

// 执行测试
testApiCall();