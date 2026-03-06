// 测试前端token状态
console.log('=== 前端Token状态检查 ===');

// 检查localStorage中的token
const tokenMap = localStorage.getItem('token_tab_map');
console.log('localStorage token映射:', tokenMap);

// 检查sessionStorage中的token
const currentTabId = sessionStorage.getItem('current_tab_id');
console.log('当前标签页ID:', currentTabId);

if (currentTabId) {
    const sessionToken = sessionStorage.getItem(`vue_admin_template_token_${currentTabId}`);
    console.log('sessionStorage token:', sessionToken);
}

// 检查store中的token
if (window.$store) {
    console.log('Vuex store token:', window.$store.getters.token);
}

// 测试项目详情API调用
console.log('\n=== 测试项目详情API调用 ===');

// 获取当前URL中的项目ID
const urlParams = new URLSearchParams(window.location.search);
const projectId = urlParams.get('id') || '1';
console.log('当前项目ID:', projectId);

// 测试API调用
async function testProjectAPI() {
    try {
        const response = await fetch(`/api/project/projects/${projectId}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('vue_admin_template_token') || sessionStorage.getItem('vue_admin_template_token')}`,
                'Content-Type': 'application/json'
            }
        });
        
        console.log('API响应状态:', response.status);
        
        if (response.ok) {
            const data = await response.json();
            console.log('项目数据:', data);
            
            if (data.data) {
                console.log('项目名称:', data.data.project_name || data.data.name);
                console.log('创建时间:', data.data.created_time || data.data.createTime);
                console.log('所有字段:', Object.keys(data.data));
            }
        } else {
            console.log('错误响应:', await response.text());
        }
    } catch (error) {
        console.error('API调用失败:', error);
    }
}

testProjectAPI();