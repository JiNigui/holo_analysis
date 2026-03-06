/**
 * IndexedDB缓存工具类
 * 用于存储和检索VOI图像数据，支持大文件存储
 */
class IndexedDBCache {
  constructor() {
    this.dbName = 'VOIImageCache'
    this.version = 1
    this.db = null
  }

  // 打开数据库连接
  async open() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.version)

      request.onerror = () => reject(request.error)
      request.onsuccess = () => {
        this.db = request.result
        resolve(this.db)
      }

      request.onupgradeneeded = (event) => {
        const db = event.target.result

        // 创建对象存储空间
        if (!db.objectStoreNames.contains('images')) {
          const store = db.createObjectStore('images', { keyPath: 'key' })
          store.createIndex('projectId', 'projectId', { unique: false })
          store.createIndex('timestamp', 'timestamp', { unique: false })
        }
      }
    })
  }

  // 存储图像数据
  async storeImage(projectId, filename, data) {
    if (!this.db) await this.open()

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['images'], 'readwrite')
      const store = transaction.objectStore('images')

      const key = `${projectId}_${filename}`
      const item = {
        key: key,
        projectId: projectId,
        filename: filename,
        data: data,
        timestamp: Date.now()
      }

      const request = store.put(item)

      request.onsuccess = () => resolve()
      request.onerror = () => reject(request.error)
    })
  }

  // 获取图像数据
  async getImage(projectId, filename) {
    if (!this.db) await this.open()

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['images'], 'readonly')
      const store = transaction.objectStore('images')
      const key = `${projectId}_${filename}`

      const request = store.get(key)

      request.onsuccess = () => {
        if (request.result) {
          resolve(request.result.data)
        } else {
          resolve(null)
        }
      }
      request.onerror = () => reject(request.error)
    })
  }

  // 检查图像是否存在
  async hasImage(projectId, filename) {
    if (!this.db) await this.open()

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['images'], 'readonly')
      const store = transaction.objectStore('images')
      const key = `${projectId}_${filename}`

      const request = store.get(key)

      request.onsuccess = () => {
        resolve(!!request.result)
      }
      request.onerror = () => reject(request.error)
    })
  }

  // 删除图像数据
  async deleteImage(projectId, filename) {
    if (!this.db) await this.open()

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['images'], 'readwrite')
      const store = transaction.objectStore('images')
      const key = `${projectId}_${filename}`

      const request = store.delete(key)

      request.onsuccess = () => resolve()
      request.onerror = () => reject(request.error)
    })
  }

  // 删除项目所有图像数据
  async deleteProjectImages(projectId) {
    if (!this.db) await this.open()

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['images'], 'readwrite')
      const store = transaction.objectStore('images')
      const index = store.index('projectId')

      const request = index.openCursor(IDBKeyRange.only(projectId))

      request.onsuccess = () => {
        const cursor = request.result
        if (cursor) {
          cursor.delete()
          cursor.continue()
        } else {
          resolve()
        }
      }
      request.onerror = () => reject(request.error)
    })
  }

  // 获取项目所有图像
  async getProjectImages(projectId) {
    if (!this.db) await this.open()

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['images'], 'readonly')
      const store = transaction.objectStore('images')
      const index = store.index('projectId')

      const request = index.getAll(IDBKeyRange.only(projectId))

      request.onsuccess = () => {
        resolve(request.result)
      }
      request.onerror = () => reject(request.error)
    })
  }

  // 清理过期数据（保留最近7天的数据）
  async cleanupExpiredData(retentionDays = 7) {
    if (!this.db) await this.open()

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['images'], 'readwrite')
      const store = transaction.objectStore('images')
      const index = store.index('timestamp')

      const cutoffTime = Date.now() - (retentionDays * 24 * 60 * 60 * 1000)
      const request = index.openCursor(IDBKeyRange.upperBound(cutoffTime))

      request.onsuccess = () => {
        const cursor = request.result
        if (cursor) {
          cursor.delete()
          cursor.continue()
        } else {
          resolve()
        }
      }
      request.onerror = () => reject(request.error)
    })
  }

  // 获取存储统计信息
  async getStorageStats() {
    if (!this.db) await this.open()

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['images'], 'readonly')
      const store = transaction.objectStore('images')

      const request = store.count()

      request.onsuccess = () => {
        resolve({
          totalItems: request.result
        })
      }
      request.onerror = () => reject(request.error)
    })
  }
}

// 创建单例实例
const indexedDBCache = new IndexedDBCache()

export default indexedDBCache
