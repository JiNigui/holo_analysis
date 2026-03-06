import request from '@/utils/request'

/**
 * VOI相关API接口
 */

/**
 * 获取TIFF文件列表
 * @param {Number} projectId - 项目ID
 */
export function getTiffFiles(projectId) {
  return request({
    url: '/hole-analysis/voi/tiff-files',
    method: 'get',
    params: { project_id: projectId }
  })
}

/**
 * 获取单个TIFF文件
 * @param {String} filename - 文件名
 */
export function getTiffFile(filename) {
  return request({
    url: `/hole-analysis/voi/binary-file/${filename}`,
    method: 'get',
    responseType: 'blob'
  })
}

/**
 * 保存裁剪后的VOI区域数据
 * @param {Object} data - 裁剪数据
 */
export function saveCroppedVolume(data) {
  return request({
    url: '/hole-analysis/voi/save-crop',
    method: 'post',
    data: data
  })
}

/**
 * 获取VOI处理状态
 */
export function getVOIStatus() {
  return request({
    url: '/hole-analysis/voi/status',
    method: 'get'
  })
}
