import request from '@/utils/request'

// 获取项目列表
export function getProjects() {
  return request({
    url: '/project/projects',
    method: 'get'
  })
}

// 获取单个项目详情
export function getProject(projectId) {
  return request({
    url: `/project/projects/${projectId}`,
    method: 'get'
  })
}

// 创建项目
export function createProject(data) {
  return request({
    url: '/project/projects',
    method: 'post',
    data
  })
}

// 删除项目
export function deleteProject(projectId) {
  return request({
    url: `/project/projects/${projectId}`,
    method: 'delete'
  })
}
