/**
 * RLE (Run-Length Encoding) 解码器
 * 用于解码后端返回的行程编码体素数据
 */

export class RLEDecoder {
  /**
   * 解码RLE数据为三维数组
   * @param {string} rleData - RLE编码的字符串
   * @param {number[]} dimensions - 三维数组的维度 [depth, height, width]
   * @returns {number[][][]} 解码后的三维数组
   */
  static decode(rleData, dimensions) {
    if (!rleData || !dimensions || dimensions.length !== 3) {
      throw new Error('无效的RLE数据或维度参数')
    }

    const [depth, height, width] = dimensions
    const totalVoxels = depth * height * width

    // 初始化三维数组
    const result = this.create3DArray(depth, height, width)

    // 解析RLE数据
    const runs = this.parseRLEData(rleData)

    // 验证数据完整性
    const totalDecodedVoxels = runs.reduce((sum, run) => sum + run.length, 0)
    if (totalDecodedVoxels !== totalVoxels) {
      throw new Error(`RLE数据不完整: 期望${totalVoxels}个体素，实际${totalDecodedVoxels}个`)
    }

    // 填充三维数组
    let currentIndex = 0
    for (const run of runs) {
      for (let i = 0; i < run.length; i++) {
        const z = Math.floor(currentIndex / (height * width))
        const y = Math.floor((currentIndex % (height * width)) / width)
        const x = currentIndex % width

        result[z][y][x] = run[i]
        currentIndex++
      }
    }

    return result
  }

  /**
   * 创建三维数组
   * @param {number} depth - 深度
   * @param {number} height - 高度
   * @param {number} width - 宽度
   * @returns {number[][][]} 初始化的三维数组
   */
  static create3DArray(depth, height, width) {
    const array = []
    for (let z = 0; z < depth; z++) {
      const plane = []
      for (let y = 0; y < height; y++) {
        const row = new Array(width).fill(0)
        plane.push(row)
      }
      array.push(plane)
    }
    return array
  }

  /**
   * 解析RLE数据
   * @param {string} rleData - RLE编码字符串
   * @returns {number[][]} 解析后的运行序列
   */
  static parseRLEData(rleData) {
    const runs = []

    // 支持多种RLE格式：
    // 1. 标准格式: "3:1,5:0,2:1" 表示3个1, 5个0, 2个1
    // 2. 简化格式: "1,1,1,0,0,0,0,0,1,1"

    if (rleData.includes(':')) {
      // 标准RLE格式
      const runStrings = rleData.split(',')
      for (const runString of runStrings) {
        const [countStr, valueStr] = runString.split(':')
        const count = parseInt(countStr, 10)
        const value = parseInt(valueStr, 10)

        if (isNaN(count) || isNaN(value)) {
          throw new Error(`无效的RLE格式: ${runString}`)
        }

        runs.push(new Array(count).fill(value))
      }
    } else {
      // 简化格式 - 直接数值序列
      const values = rleData.split(',').map(val => parseInt(val, 10))

      // 转换为运行长度编码
      let currentRun = []
      let currentValue = values[0]

      for (const value of values) {
        if (value === currentValue) {
          currentRun.push(value)
        } else {
          runs.push([...currentRun])
          currentRun = [value]
          currentValue = value
        }
      }

      if (currentRun.length > 0) {
        runs.push(currentRun)
      }
    }

    return runs
  }

  /**
   * 将三维数组编码为RLE格式
   * @param {number[][][]} array3D - 三维数组
   * @returns {string} RLE编码字符串
   */
  static encode(array3D) {
    if (!array3D || !array3D.length) {
      return ''
    }

    const flatArray = []

    // 展平三维数组
    for (let z = 0; z < array3D.length; z++) {
      for (let y = 0; y < array3D[z].length; y++) {
        for (let x = 0; x < array3D[z][y].length; x++) {
          flatArray.push(array3D[z][y][x])
        }
      }
    }

    // 进行运行长度编码
    const runs = []
    let currentValue = flatArray[0]
    let currentCount = 1

    for (let i = 1; i < flatArray.length; i++) {
      if (flatArray[i] === currentValue) {
        currentCount++
      } else {
        runs.push(`${currentCount}:${currentValue}`)
        currentValue = flatArray[i]
        currentCount = 1
      }
    }

    // 添加最后一个运行
    runs.push(`${currentCount}:${currentValue}`)

    return runs.join(',')
  }

  /**
   * 验证RLE数据格式
   * @param {string} rleData - RLE编码字符串
   * @returns {boolean} 是否为有效的RLE格式
   */
  static validate(rleData) {
    if (!rleData || typeof rleData !== 'string') {
      return false
    }

    try {
      if (rleData.includes(':')) {
        // 标准格式验证
        const runs = rleData.split(',')
        for (const run of runs) {
          const parts = run.split(':')
          if (parts.length !== 2) return false

          const count = parseInt(parts[0], 10)
          const value = parseInt(parts[1], 10)

          if (isNaN(count) || isNaN(value) || count <= 0) {
            return false
          }
        }
      } else {
        // 简化格式验证
        const values = rleData.split(',')
        for (const val of values) {
          const num = parseInt(val, 10)
          if (isNaN(num)) return false
        }
      }

      return true
    } catch (error) {
      return false
    }
  }

  /**
   * 计算RLE数据的压缩比
   * @param {string} rleData - RLE编码字符串
   * @param {number[]} dimensions - 原始数据维度
   * @returns {number} 压缩比 (原始大小 / 压缩后大小)
   */
  static calculateCompressionRatio(rleData, dimensions) {
    if (!rleData || !dimensions) {
      return 1
    }

    const [depth, height, width] = dimensions
    const originalSize = depth * height * width * 4 // 假设每个体素4字节
    const compressedSize = rleData.length * 2 // 假设每个字符2字节

    return originalSize / compressedSize
  }
}

export default RLEDecoder
