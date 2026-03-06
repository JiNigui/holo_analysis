import request from '@/utils/request'

// 获取系统日志列表
export function getLogs(params) {
  return request({
    url: '/logs/logs',
    method: 'get',
    params
  })
}

// 创建系统日志记录
export function createLog(data) {
  return request({
    url: '/logs/logs',
    method: 'post',
    data
  })
}

// 日志类型常量
export const LOG_TYPES = {
  USER_LOGIN: '用户登入',
  USER_LOGOUT: '用户登出',
  PROJECT_CREATE: '创建项目',
  PROJECT_DELETE: '删除项目',
  IMAGE_BINARIZATION: '原始图像二值化',
  ROI_SELECTION: '选择感兴趣区域',
  MASK_RCNN_DETECTION: 'Mask R-CNN 孔洞识别',
  DATA_PREPROCESSING: '数据预处理',
  TARGET_SLICING: '寻找目标孔洞并切片',
  MORPHOLOGY_ANALYSIS: '形态学分析'
}
