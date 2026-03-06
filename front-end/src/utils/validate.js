/**
 * Created by PanJiaChen on 16/11/18.
 */

/**
 * @param {string} path
 * @returns {Boolean}
 */
export function isExternal(path) {
  return /^(https?:|mailto:|tel:)/.test(path)
}

/**
 * @param {string} str
 * @returns {Boolean}
 */
export function validUsername(str) {
  // 只做基本格式验证：用户名不能为空，长度在3-20个字符之间
  // 真正的用户名存在性验证应该在后端进行
  if (!str || str.trim().length === 0) {
    return false
  }
  const trimmedStr = str.trim()
  return trimmedStr.length >= 3 && trimmedStr.length <= 20
}
