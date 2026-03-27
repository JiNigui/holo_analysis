import request from '@/utils/request'

// 执行图像二值化处理
export function executeBinaryConversion(projectId) {
  return request({
    url: '/hole-analysis/binary',
    method: 'post',
    data: {
      project_id: projectId
    },
    timeout: 600000 // 10分钟超时，处理大量图片需要时间
  })
}

// 获取孔洞分析结果
export function getHoleAnalysisResults(projectId) {
  return request({
    url: `/hole-analysis/results/${projectId}`,
    method: 'get'
  })
}

// 获取二值化图像列表
export function getBinaryImages(projectId) {
  return request({
    url: `/hole-analysis/binary-images/${projectId}`,
    method: 'get'
  })
}

// 启动VOI选取
export function startVOISelection(projectId) {
  return request({
    url: '/hole-analysis/voi/start',
    method: 'post',
    data: {
      project_id: projectId
    }
  })
}

// 检查VOI选取状态
export function checkVOIStatus(projectId) {
  return request({
    url: '/hole-analysis/voi/status',
    method: 'post',
    data: {
      project_id: projectId
    }
  })
}

// 获取3D模型的VTK数据
export function get3DVtkData(projectId) {
  return request({
    url: `/hole-analysis/projects/${projectId}/3d_data`,
    method: 'get',
    responseType: 'blob', // 重要：设置为blob以接收二进制文件
    timeout: 600000, // 10分钟超时，处理大文件需要更多时间
    // 大文件传输优化
    onDownloadProgress: (progressEvent) => {
      // 可以在这里添加进度显示逻辑
      const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
      console.log(`VTK文件下载进度: ${percentCompleted}%`)
    }
  })
}

// 确认VOI区域选择
export function confirmVOISelection(projectId, selectionBounds) {
  return request({
    url: '/hole-analysis/voi/confirm',
    method: 'post',
    data: {
      project_id: projectId,
      selection_bounds: selectionBounds
    }
  })
}

// 执行孔洞识别（第三步）
export function executeHoleDetection(projectId) {
  return request({
    url: '/hole-analysis/hole-detection',
    method: 'post',
    data: {
      project_id: projectId
    },
    timeout: 3600000 // 1小时超时，孔洞识别需要较长时间
  })
}

// 执行数据预处理（第四步）
export function executeDataPreprocessing(projectId) {
  return request({
    url: '/hole-analysis/preprocess',
    method: 'post',
    data: {
      project_id: projectId
    },
    timeout: 1800000 // 30分钟超时，数据预处理需要时间
  })
}

// 执行目标孔洞分析（第五步）
export function executeTargetHoleAnalysis(projectId) {
  return request({
    url: '/hole-analysis/target-hole-analysis',
    method: 'post',
    data: {
      project_id: projectId
    },
    responseType: 'blob', // 重要：设置为blob以接收图像文件
    timeout: 1800000 // 30分钟超时，目标孔洞分析需要时间
  })
}

// 获取最大孔洞3D视图数据
export function executeMaxHole3DView(projectId) {
  return request({
    url: '/hole-analysis/max-hole-3d-view',
    method: 'post',
    data: {
      project_id: projectId
    },
    responseType: 'blob', // 重要：设置为blob以接收压缩数据
    timeout: 1800000 // 30分钟超时，3D模型数据处理需要时间
  })
}
