// 简化的Web Worker用于测试
self.onmessage = function(event) {
  const { type, data } = event.data
  
  if (type === 'test') {
    try {
      console.log('✅ 简单Web Worker启动成功')
      
      // 发送开始消息
      self.postMessage({
        type: 'started',
        message: '简单Worker测试启动'
      })
      
      // 模拟处理过程
      for (let i = 0; i <= 100; i++) {
        setTimeout(() => {
          self.postMessage({
            type: 'progress',
            progress: i / 100
          })
          
          if (i === 100) {
            self.postMessage({
              type: 'completed',
              data: { message: '测试完成' }
            })
          }
        }, i * 100)
      }
      
    } catch (error) {
      self.postMessage({
        type: 'error',
        error: error.message
      })
    }
  }
}