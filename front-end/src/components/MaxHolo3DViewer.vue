<template>
  <div class="max-holo-3d-viewer">
    <div class="viewer-container" ref="containerRef">
      <div v-if="loading" class="loading-overlay">
        <div class="loading-spinner">
          <i class="el-icon-loading"></i>
          <span>{{ loadingMessage }}</span>
        </div>
      </div>
      
      <div v-if="error" class="error-overlay">
        <div class="error-message">
          <i class="el-icon-error"></i>
          <p>{{ error }}</p>
          <el-button type="primary" @click="retryLoad">重试</el-button>
        </div>
      </div>
    </div>
    
    <!-- 控制面板 -->
    <div class="control-panel">
      <h3>3D切片控制</h3>
      <div class="control-section">
        <h4>切割平面参数</h4>
        <div class="param-inputs">
          <div class="input-group">
            <label>法向量 X:</label>
            <el-input-number 
              v-model="cutParams.normal[0]" 
              :precision="8" 
              :step="0.1"
              @change="updateSlice"
            ></el-input-number>
          </div>
          <div class="input-group">
            <label>法向量 Y:</label>
            <el-input-number 
              v-model="cutParams.normal[1]" 
              :precision="8" 
              :step="0.1"
              @change="updateSlice"
            ></el-input-number>
          </div>
          <div class="input-group">
            <label>法向量 Z:</label>
            <el-input-number 
              v-model="cutParams.normal[2]" 
              :precision="8" 
              :step="0.1"
              @change="updateSlice"
            ></el-input-number>
          </div>
          <div class="input-group">
            <label>过点 X:</label>
            <el-input-number 
              v-model="cutParams.origin[0]" 
              :precision="8" 
              :step="0.1"
              @change="updateSlice"
            ></el-input-number>
          </div>
          <div class="input-group">
            <label>过点 Y:</label>
            <el-input-number 
              v-model="cutParams.origin[1]" 
              :precision="8" 
              :step="0.1"
              @change="updateSlice"
            ></el-input-number>
          </div>
          <div class="input-group">
            <label>过点 Z:</label>
            <el-input-number 
              v-model="cutParams.origin[2]" 
              :precision="8" 
              :step="0.1"
              @change="updateSlice"
            ></el-input-number>
          </div>
        </div>
      </div>
      
      <div class="control-actions">
        <el-button @click="resetView">重置视角</el-button>
        <el-button @click="autoFitView">自动适配</el-button>
      </div>
    </div>
  </div>
</template>

<script>
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import pako from 'pako'

export default {
  name: 'MaxHolo3DViewer',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    projectId: {
      type: Number,
      required: true
    }
  },
  data() {
    return {
      containerRef: null,
      scene: null,
      camera: null,
      renderer: null,
      controls: null,
      sliceMesh: null,
      sliceLines: null,
      loading: false,
      loadingMessage: '正在初始化...',
      error: null,
      cutParams: {
        normal: [-0.78026193, 0.37575434, -0.5],
        origin: [26.21065698, 14.67418985, 11.66648875]
      },
      sliceData: null
    }
  },
  mounted() {
    this.initViewer()
    window.addEventListener('resize', this.onWindowResize)
  },
  watch: {
    visible: {
      immediate: true,
      handler(newVal) {
        if (newVal && this.projectId) {
          // 对话框打开且projectId存在时，自动加载数据
          this.loadSliceData()
        }
      }
    }
  },
  beforeDestroy() {
    this.dispose()
    window.removeEventListener('resize', this.onWindowResize)
  },
  methods: {
    initViewer() {
      this.containerRef = this.$refs.containerRef
      
      // 创建场景
      this.scene = new THREE.Scene()
      this.scene.background = new THREE.Color(0xf0f0f0)
      
      // 创建相机
      const aspect = this.containerRef.clientWidth / this.containerRef.clientHeight
      this.camera = new THREE.PerspectiveCamera(75, aspect, 0.1, 1000)
      this.camera.position.z = 50
      
      // 创建渲染器
      this.renderer = new THREE.WebGLRenderer({ antialias: true })
      this.renderer.setSize(this.containerRef.clientWidth, this.containerRef.clientHeight)
      this.renderer.setPixelRatio(window.devicePixelRatio)
      this.containerRef.appendChild(this.renderer.domElement)
      
      // 添加光源
      const ambientLight = new THREE.AmbientLight(0x404040, 1)
      this.scene.add(ambientLight)
      
      const directionalLight = new THREE.DirectionalLight(0xffffff, 1)
      directionalLight.position.set(1, 1, 1)
      this.scene.add(directionalLight)
      
      // 添加坐标轴辅助
      const axesHelper = new THREE.AxesHelper(20)
      this.scene.add(axesHelper)
      
      // 添加网格辅助
      const gridHelper = new THREE.GridHelper(50, 10)
      this.scene.add(gridHelper)
      
      // 添加控制器
      this.controls = new OrbitControls(this.camera, this.renderer.domElement)
      this.controls.enableDamping = true
      this.controls.dampingFactor = 0.05
      
      // 开始渲染循环
      this.animate()
    },
    
    animate() {
      requestAnimationFrame(this.animate)
      
      if (this.controls) {
        this.controls.update()
      }
      
      if (this.renderer && this.scene && this.camera) {
        this.renderer.render(this.scene, this.camera)
      }
    },
    
    async loadSliceData() {
      this.loading = true
      this.loadingMessage = '正在请求3D切割面数据...'
      this.error = null
      
      try {
        console.log('=== 数据接收阶段开始 ===')
        console.log('1. 开始发送API请求...')
        console.log('请求URL:', '/hole-analysis/max-hole-3d-view')
        console.log('请求参数:', { project_id: this.projectId })
        console.log('当前时间戳:', new Date().toISOString())
        
        // 使用this.$http.post直接发送API请求，与其他组件保持一致
        const response = await this.$http.post('/hole-analysis/max-hole-3d-view', {
          project_id: this.projectId
        }, {
          responseType: 'blob', // 重要：设置为blob以接收压缩数据
          timeout: 1800000 // 30分钟超时，3D模型数据处理需要时间
        })
        
        console.log('2. API请求成功，状态码:', response.status)
        console.log('响应类型:', response.headers['content-type'])
        console.log('响应大小:', response.headers['content-length'], '字节')
        console.log('响应时间:', new Date().toISOString())
        
        // 处理响应数据（检查是gzip压缩的JSON数据还是直接的JSON数据）
            const result = await response.data.arrayBuffer()
            console.log('3. 获取到ArrayBuffer，大小:', result.byteLength, '字节')
            console.log('3.1 ArrayBuffer类型检查:', result.constructor.name)
            
            // 检查数据格式（gzip压缩还是直接JSON）
            const uint8Array = new Uint8Array(result)
            const firstBytes = Array.from(uint8Array.slice(0, 10))
            const firstBytesHex = firstBytes.map(b => b.toString(16).padStart(2, '0')).join(' ')
            const firstBytesAscii = firstBytes.map(b => String.fromCharCode(b)).join('')
            
            console.log('=== 数据格式检测阶段开始 ===')
            console.log('4. 数据格式检测:')
            console.log('4.1 数据前10字节:', firstBytes)
            console.log('4.2 数据前10字节十六进制:', firstBytesHex)
            console.log('4.3 数据前10字节ASCII:', firstBytesAscii)
            
            let jsonData
            
            // 检查是否是gzip格式（gzip文件头：0x1f 0x8b）
            if (uint8Array[0] === 0x1f && uint8Array[1] === 0x8b) {
              console.log('4.4 检测到gzip压缩格式，开始解压缩...')
              const decompressedData = await this.decompressGzip(result)
              console.log('4.5 解压缩成功，数据大小:', decompressedData.length, '字符')
              console.log('4.6 解压缩数据前100字符:', decompressedData.substring(0, 100))
              console.log('4.7 解压缩数据是否包含JSON结构:', decompressedData.includes('{') && decompressedData.includes('}'))
              
              console.log('=== JSON解析阶段开始 ===')
              console.log('5. 开始JSON解析...')
              jsonData = JSON.parse(decompressedData)
            } else {
              // 直接是JSON格式，不需要解压缩
              console.log('4.4 检测到直接JSON格式，跳过解压缩...')
              const textDecoder = new TextDecoder()
              const jsonText = textDecoder.decode(uint8Array)
              console.log('4.5 直接JSON数据大小:', jsonText.length, '字符')
              console.log('4.6 直接JSON数据前100字符:', jsonText.substring(0, 100))
              
              console.log('=== JSON解析阶段开始 ===')
              console.log('5. 开始JSON解析...')
              jsonData = JSON.parse(jsonText)
            }
        console.log('5.1 JSON解析成功，数据结构:', Object.keys(jsonData))
        console.log('5.2 数据详细结构:', {
          是否有points: !!jsonData.points,
          points数量: jsonData.points ? jsonData.points.length : 0,
          是否有lines: !!jsonData.lines,
          lines数量: jsonData.lines ? jsonData.lines.length : 0,
          是否有normal: !!jsonData.normal,
          是否有origin: !!jsonData.origin
        })
        
        // 将后端返回的3D模型数据转换为可渲染的切片数据
        console.log('=== 数据转换阶段开始 ===')
        this.sliceData = this.processSliceDataFromBackend(jsonData)
        console.log('6. 数据转换完成，切片数据结构:', {
          点数量: this.sliceData.n_points,
          线数量: this.sliceData.n_lines,
          法向量: this.sliceData.normal,
          原点: this.sliceData.origin
        })
        
        this.loadingMessage = '正在渲染3D切割面...'
        this.renderSliceData()
        
      } catch (err) {
        console.error('=== 错误发生 ===')
        console.error('加载3D切割面数据失败:', err)
        console.error('错误详情:', {
          名称: err.name,
          消息: err.message,
          错误代码: err.code,
          错误堆栈: err.stack
        })
        console.error('错误发生时间:', new Date().toISOString())
        this.error = err.message || '加载3D切割面数据失败'
      } finally {
        this.loading = false
        console.log('=== 数据接收阶段结束 ===')
      }
    },
    
    // 处理后端返回的3D模型数据，转换为可渲染的切片数据
    processSliceDataFromBackend(backendData) {
      console.log('=== 数据格式验证开始 ===')
      console.log('后端返回的数据结构:', backendData)
      
      // 检查后端返回的数据格式（get_3d_slice_data.py的输出格式）
      if (backendData && backendData.points && Array.isArray(backendData.points)) {
        console.log('✅ points数据存在且为数组')
        
        const points = backendData.points
        const lines = backendData.lines || []
        const normal = backendData.normal || this.cutParams.normal
        const origin = backendData.origin || this.cutParams.origin
        
        console.log(`切片数据: ${points.length}个点, ${lines.length}条线`)
        
        // 验证点数据格式
        if (points.length > 0) {
          const firstPoint = points[0]
          console.log('第一个点数据:', firstPoint)
          console.log('点数据格式验证:', {
            是否为数组: Array.isArray(firstPoint),
            数组长度: Array.isArray(firstPoint) ? firstPoint.length : 'N/A',
            是否为数字: Array.isArray(firstPoint) ? firstPoint.every(val => typeof val === 'number') : 'N/A'
          })
        }
        
        // 验证线数据格式
        if (lines.length > 0) {
          console.log('线数据格式验证:', {
            线数据长度: lines.length,
            是否为数组: Array.isArray(lines),
            前10个元素: lines.slice(0, 10)
          })
        }
        
        // 更新切割参数
        this.cutParams.normal = normal
        this.cutParams.origin = origin
        
        const result = {
          points: points,
          lines: lines,
          n_points: points.length,
          n_lines: lines.length,
          normal: normal,
          origin: origin
        }
        
        console.log('✅ 数据格式验证通过，返回有效切片数据')
        return result
      }
      
      // 如果没有有效的几何数据，返回空数据
      console.warn('❌ 后端返回的数据格式不正确，使用默认参数')
      console.warn('数据格式问题:', {
        是否有backendData: !!backendData,
        是否有points: !!(backendData && backendData.points),
        points是否为数组: !!(backendData && backendData.points && Array.isArray(backendData.points))
      })
      
      return {
        points: [],
        lines: [],
        n_points: 0,
        n_lines: 0,
        normal: this.cutParams.normal,
        origin: this.cutParams.origin
      }
    },
    
    renderSliceData() {
      console.log('=== 3D渲染阶段开始 ===')
      
      // 移除之前的切片
      if (this.sliceMesh) {
        console.log('移除之前的切片点云')
        this.scene.remove(this.sliceMesh)
        this.sliceMesh.geometry.dispose()
        this.sliceMesh.material.dispose()
        this.sliceMesh = null
      }
      
      if (this.sliceLines) {
        console.log('移除之前的切片线')
        this.scene.remove(this.sliceLines)
        this.sliceLines.geometry.dispose()
        this.sliceLines.material.dispose()
        this.sliceLines = null
      }
      
      if (!this.sliceData || !this.sliceData.points || this.sliceData.points.length === 0) {
        console.warn('❌ 切片数据为空或无有效点数据')
        console.warn('切片数据状态:', {
          是否有sliceData: !!this.sliceData,
          是否有points: !!(this.sliceData && this.sliceData.points),
          points数量: this.sliceData ? this.sliceData.points.length : 0
        })
        return
      }
      
      try {
        console.log('开始创建3D几何体...')
        
        // 创建切片几何体
        const geometry = new THREE.BufferGeometry()
        console.log('创建BufferGeometry完成')
        
        const positions = new Float32Array(this.sliceData.points.flat())
        console.log('创建位置数组完成，长度:', positions.length, '个元素')
        console.log('位置数组前10个值:', Array.from(positions.slice(0, 10)))
        
        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
        console.log('设置几何体位置属性完成')
        
        // 创建切片材质
        const material = new THREE.PointsMaterial({
          color: 0xff0000,
          size: 0.2,
          sizeAttenuation: true
        })
        console.log('创建点材质完成')
        
        // 创建点云
        this.sliceMesh = new THREE.Points(geometry, material)
        console.log('创建点云对象完成')
        
        this.scene.add(this.sliceMesh)
        console.log('点云添加到场景完成')
        
        // 如果有线数据，也创建线
        if (this.sliceData.lines && this.sliceData.lines.length > 0) {
          console.log('检测到线数据，开始创建线')
          this.renderSliceLines()
        } else {
          console.log('未检测到线数据，跳过线创建')
        }
        
        // 自动适配视角
        console.log('开始自动适配视角...')
        this.autoFitView()
        console.log('自动适配视角完成')
        
        console.log('✅ 3D渲染完成')
        
      } catch (err) {
        console.error('❌ 渲染切片数据失败:', err)
        console.error('渲染错误详情:', {
          错误类型: err.name,
          错误消息: err.message,
          错误堆栈: err.stack
        })
        this.error = '渲染切片数据失败: ' + err.message
      }
    },
    
    renderSliceLines() {
      console.log('=== 线渲染阶段开始 ===')
      
      if (!this.sliceData || !this.sliceData.lines || this.sliceData.lines.length === 0) {
        console.warn('❌ 线数据为空或无有效线数据')
        console.warn('线数据状态:', {
          是否有sliceData: !!this.sliceData,
          是否有lines: !!(this.sliceData && this.sliceData.lines),
          lines数量: this.sliceData ? this.sliceData.lines.length : 0
        })
        return
      }
      
      try {
        console.log('开始解析线数据...')
        console.log('原始线数据长度:', this.sliceData.lines.length)
        console.log('原始线数据前20个元素:', this.sliceData.lines.slice(0, 20))
        
        // 将线数据转换为线段
        const lineGeometry = new THREE.BufferGeometry()
        const positions = []
        let lineCount = 0
        let validLineCount = 0
        
        // 解析线数据 (VTK格式的lines通常是 [count, idx1, idx2, ..., count, idx1, idx2, ...])
        const lines = this.sliceData.lines
        for (let i = 0; i < lines.length; ) {
          const count = lines[i]
          i++
          
          if (count === 2) {
            // 两点构成一条线段
            const idx1 = lines[i]
            const idx2 = lines[i + 1]
            i += 2
            
            if (idx1 < this.sliceData.points.length && idx2 < this.sliceData.points.length) {
              const point1 = this.sliceData.points[idx1]
              const point2 = this.sliceData.points[idx2]
              
              positions.push(...point1, ...point2)
              validLineCount++
            }
            lineCount++
          } else if (count > 2) {
            // 多点构成折线
            for (let j = 0; j < count - 1; j++) {
              const idx1 = lines[i + j]
              const idx2 = lines[i + j + 1]
              
              if (idx1 < this.sliceData.points.length && idx2 < this.sliceData.points.length) {
                const point1 = this.sliceData.points[idx1]
                const point2 = this.sliceData.points[idx2]
                
                positions.push(...point1, ...point2)
                validLineCount++
              }
            }
            i += count
            lineCount++
          } else {
            i += count
          }
        }
        
        console.log('线数据解析完成:', {
          总线段数: lineCount,
          有效线段数: validLineCount,
          位置数组长度: positions.length,
          顶点数量: positions.length / 3
        })
        
        if (positions.length > 0) {
          console.log('开始创建线几何体...')
          lineGeometry.setAttribute('position', new THREE.BufferAttribute(new Float32Array(positions), 3))
          console.log('线几何体创建完成')
          
          const lineMaterial = new THREE.LineBasicMaterial({
            color: 0x0000ff,
            linewidth: 2
          })
          console.log('线材质创建完成')
          
          this.sliceLines = new THREE.LineSegments(lineGeometry, lineMaterial)
          console.log('线对象创建完成')
          
          this.scene.add(this.sliceLines)
          console.log('线对象添加到场景完成')
          
          console.log('✅ 线渲染完成')
        } else {
          console.warn('❌ 没有有效的线段数据可以渲染')
        }
      } catch (err) {
        console.error('❌ 渲染切片线数据失败:', err)
        console.error('线渲染错误详情:', {
          错误类型: err.name,
          错误消息: err.message,
          错误堆栈: err.stack
        })
      }
    },
    
    updateSlice() {
      if (this.sliceData) {
        this.renderSliceData()
      }
    },
    
    resetView() {
      if (this.controls) {
        this.controls.reset()
      }
    },
    
    autoFitView() {
      if (!this.sliceData || !this.sliceData.points || this.sliceData.points.length === 0) {
        return
      }
      
      // 计算包围盒
      const points = this.sliceData.points
      let minX = Infinity, minY = Infinity, minZ = Infinity
      let maxX = -Infinity, maxY = -Infinity, maxZ = -Infinity
      
      for (const point of points) {
        minX = Math.min(minX, point[0])
        minY = Math.min(minY, point[1])
        minZ = Math.min(minZ, point[2])
        maxX = Math.max(maxX, point[0])
        maxY = Math.max(maxY, point[1])
        maxZ = Math.max(maxZ, point[2])
      }
      
      const center = new THREE.Vector3(
        (minX + maxX) / 2,
        (minY + maxY) / 2,
        (minZ + maxZ) / 2
      )
      
      const size = Math.max(
        maxX - minX,
        maxY - minY,
        maxZ - minZ
      )
      
      const fitHeightDistance = size / (2 * Math.atan(Math.PI * this.camera.fov / 360))
      const fitWidthDistance = fitHeightDistance / this.camera.aspect
      const distance = Math.max(fitHeightDistance, fitWidthDistance)
      
      const direction = this.camera.position.clone().sub(this.controls.target).normalize()
      this.camera.position.copy(center).add(direction.multiplyScalar(distance * 1.5))
      this.controls.target.copy(center)
      
      this.controls.update()
    },
    
    onWindowResize() {
      if (this.containerRef && this.camera && this.renderer) {
        const width = this.containerRef.clientWidth
        const height = this.containerRef.clientHeight
        
        this.camera.aspect = width / height
        this.camera.updateProjectionMatrix()
        
        this.renderer.setSize(width, height)
      }
    },
    
    retryLoad() {
      this.error = null
      this.loadSliceData()
    },
    
    // 解压缩gzip数据
    decompressGzip(compressedData) {
      return new Promise((resolve, reject) => {
        try {
          console.log('=== 解压缩详细过程开始 ===')
          console.log('decompressGzip: 开始解压缩，数据长度:', compressedData.byteLength, '字节')
          
          // 检查数据是否是有效的gzip格式
          const uint8Array = new Uint8Array(compressedData)
          console.log('decompressGzip: 数据前10字节:', Array.from(uint8Array.slice(0, 10)))
          console.log('decompressGzip: 数据前10字节十六进制:', Array.from(uint8Array.slice(0, 10)).map(b => b.toString(16).padStart(2, '0')).join(' '))
          
          // gzip文件头应该是 0x1f 0x8b
          const isGzipFormat = uint8Array[0] === 0x1f && uint8Array[1] === 0x8b
          console.log('decompressGzip: gzip格式检查:', {
            文件头字节1: '0x' + uint8Array[0].toString(16).padStart(2, '0'),
            文件头字节2: '0x' + uint8Array[1].toString(16).padStart(2, '0'),
            是否为gzip格式: isGzipFormat
          })
          
          // 检查压缩方法（第3个字节）
          const compressionMethod = uint8Array[2]
          console.log('decompressGzip: 压缩方法:', {
            字节值: compressionMethod,
            十六进制: '0x' + compressionMethod.toString(16).padStart(2, '0'),
            方法说明: compressionMethod === 8 ? 'DEFLATE' : '未知方法'
          })
          
          // 使用pako库进行gzip解压缩
          if (typeof pako !== 'undefined') {
            console.log('decompressGzip: 使用pako库进行解压缩')
            console.log('decompressGzip: pako版本检查:', {
              pako是否定义: typeof pako !== 'undefined',
              pako是否有ungzip方法: typeof pako.ungzip === 'function'
            })
            
            try {
              console.log('decompressGzip: 调用pako.ungzip...')
              const decompressed = pako.ungzip(uint8Array, { to: 'string' })
              console.log('decompressGzip: pako解压缩成功，解压缩后大小:', decompressed.length, '字符')
              console.log('decompressGzip: 解压缩数据前50字符:', decompressed.substring(0, 50))
              console.log('decompressGzip: 解压缩数据是否包含JSON结构:', decompressed.includes('{') && decompressed.includes('}'))
              resolve(decompressed)
            } catch (pakoError) {
              console.error('decompressGzip: pako解压缩失败:', pakoError)
              console.error('decompressGzip: pako错误详情:', {
                错误名称: pakoError.name,
                错误消息: pakoError.message,
                错误堆栈: pakoError.stack
              })
              reject(pakoError)
            }
          } else {
            console.log('decompressGzip: pako未定义，尝试其他方法')
            console.log('decompressGzip: pako检查:', {
              pako是否定义: typeof pako,
              windowPako是否定义: typeof window.pako
            })
            
            // 如果没有pako，尝试使用浏览器内置的DecompressionStream API
            if ('DecompressionStream' in window) {
              console.log('decompressGzip: 使用浏览器内置DecompressionStream')
              try {
                const decompressionStream = new DecompressionStream('gzip')
                const readableStream = new Response(compressedData).body
                const decompressedStream = readableStream.pipeThrough(decompressionStream)
                
                new Response(decompressedStream).text().then(text => {
                  console.log('decompressGzip: DecompressionStream解压缩成功，大小:', text.length, '字符')
                  resolve(text)
                }).catch(err => {
                  console.error('decompressGzip: DecompressionStream解压缩失败:', err)
                  reject(err)
                })
              } catch (streamError) {
                console.error('decompressGzip: DecompressionStream初始化失败:', streamError)
                reject(streamError)
              }
            } else {
              console.log('decompressGzip: 尝试直接解析（可能不是压缩数据）')
              // 如果都不支持，尝试直接解析（可能不是压缩数据）
              const textDecoder = new TextDecoder()
              const text = textDecoder.decode(uint8Array)
              console.log('decompressGzip: 直接解析成功，文本大小:', text.length, '字符')
              console.log('decompressGzip: 直接解析数据前50字符:', text.substring(0, 50))
              console.log('decompressGzip: 直接解析数据是否包含JSON结构:', text.includes('{') && text.includes('}'))
              resolve(text)
            }
          }
        } catch (error) {
          console.error('decompressGzip: 解压缩过程中发生错误:', error)
          console.error('decompressGzip: 错误详情:', {
            错误名称: error.name,
            错误消息: error.message,
            错误堆栈: error.stack
          })
          reject(error)
        }
      })
    },
    
    dispose() {
      if (this.controls) {
        this.controls.dispose()
      }
      
      if (this.renderer) {
        this.renderer.dispose()
      }
      
      if (this.sliceMesh) {
        this.sliceMesh.geometry.dispose()
        this.sliceMesh.material.dispose()
      }
      
      if (this.sliceLines) {
        this.sliceLines.geometry.dispose()
        this.sliceLines.material.dispose()
      }
      
      if (this.containerRef && this.renderer?.domElement) {
        this.containerRef.removeChild(this.renderer.domElement)
      }
    }
  }
}
</script>

<style scoped>
.max-holo-3d-viewer {
  display: flex;
  height: 100%;
  width: 100%;
}

.viewer-container {
  flex: 1;
  position: relative;
  background: #fff;
  overflow: hidden;
}

.control-panel {
  width: 300px;
  padding: 20px;
  background: #f5f5f5;
  border-left: 1px solid #ddd;
  overflow-y: auto;
}

.control-panel h3 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #333;
}

.control-section {
  margin-bottom: 20px;
}

.control-section h4 {
  margin: 0 0 15px 0;
  color: #555;
  font-size: 14px;
}

.param-inputs {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.input-group {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.input-group label {
  width: 80px;
  font-size: 13px;
  color: #666;
}

.input-group .el-input-number {
  width: 150px;
}

.control-actions {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.loading-overlay,
.error-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

.loading-spinner,
.error-message {
  text-align: center;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.loading-spinner i,
.error-message i {
  font-size: 24px;
  margin-bottom: 10px;
}

.error-message p {
  margin: 10px 0;
  color: #f56c6c;
}

.el-input-number {
  margin-left: 10px;
}
</style>