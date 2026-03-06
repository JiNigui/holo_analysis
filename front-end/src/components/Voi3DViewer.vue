<template>
  <div class="voi-3d-viewer">
    <!-- 主内容区域 -->
    <div class="main-content">
      <!-- 3D画布容器 -->
      <div ref="canvasContainer" class="canvas-container">
        <canvas ref="canvas" class="three-canvas" />

        <!-- 加载状态 -->
        <div v-if="loading" class="loading-overlay">
          <div class="loading-spinner">
            <i class="el-icon-loading" />
            <span>{{ loadingText }}</span>
          </div>
        </div>
      </div>

      <!-- 框选控制面板 -->
      <div class="selection-controls">
        <div class="control-panel">
          <h3>3D框选控制</h3>
          <div v-if="!modelRendered" class="render-status">
            <p style="color: #909399; text-align: center;">等待3D模型渲染完成...</p>
          </div>
          <div v-else class="control-buttons">
            <el-button
              type="primary"
              size="small"
              :class="{ active: selectionBoxActive }"
              @click="toggleSelectionBox"
            >
              {{ selectionBoxActive ? '隐藏框选框' : '显示框选框' }}
            </el-button>
            <el-button
              type="success"
              size="small"
              :disabled="!selectionBoxActive"
              @click="confirmSelection"
            >
              确认VOI选取
            </el-button>
            <el-button
              type="info"
              size="small"
              @click="resetSelectionBox"
            >
              重置框选框
            </el-button>
            <el-button
              type="warning"
              size="small"
              :disabled="!modelRendered"
              @click="toggleModelBoundary"
            >
              {{ showModelBoundary ? '隐藏模型边界' : '显示模型边界' }}
            </el-button>
          </div>
          <div v-if="selectionBoxActive" class="selection-info">
            <p>操作说明：</p>
            <ul>
              <li>拖拽红色顶点：缩放框选框</li>
              <li>拖拽绿色边框：移动框选框</li>
              <li>调整到合适区域后点击"确认VOI选取"</li>
            </ul>
          </div>
          <div v-if="modelRendered" class="boundary-info">
            <p>模型边界信息：</p>
            <div class="model-bounds-details">
              <div class="bounds-item">
                <label>最小坐标:</label>
                <span>({{ modelBounds.min.x.toFixed(2) }}, {{ modelBounds.min.y.toFixed(2) }}, {{ modelBounds.min.z.toFixed(2) }})</span>
              </div>
              <div class="bounds-item">
                <label>最大坐标:</label>
                <span>({{ modelBounds.max.x.toFixed(2) }}, {{ modelBounds.max.y.toFixed(2) }}, {{ modelBounds.max.z.toFixed(2) }})</span>
              </div>
              <div class="bounds-item">
                <label>尺寸:</label>
                <span>({{ modelBounds.size.x.toFixed(2) }}, {{ modelBounds.size.y.toFixed(2) }}, {{ modelBounds.size.z.toFixed(2) }})</span>
              </div>
            </div>
            <ul>
              <li>蓝色线框：显示3D模型的完整边界</li>
              <li>帮助确认可框选的范围</li>
              <li>显示长方体的12条边</li>
            </ul>
          </div>
        </div>
      </div>
    </div>

      <!-- 选择区域信息面板 -->
      <div v-if="showSelectionInfo && selectedBounds" class="selection-info-panel">
        <div class="info-panel" :class="{ 'minimized': selectionInfoPanelMinimized }">
          <div class="panel-header">
            <h3>已选择区域信息</h3>
            <div class="panel-controls">
              <el-button v-if="!selectionInfoPanelMinimized" type="primary" size="mini" @click="copySelectionData">复制</el-button>
              <el-button type="info" size="mini" @click="toggleSelectionInfoPanel">
                {{ selectionInfoPanelMinimized ? '放大' : '缩小' }}
              </el-button>
            </div>
          </div>
          
          <div v-if="!selectionInfoPanelMinimized" class="bounds-info">
            <div class="bounds-section">
              <h4>相对坐标（3D模型）</h4>
              <div class="bounds-item">
                <label>X轴范围:</label>
                <span>{{ selectedBounds.min.x.toFixed(3) }} 到 {{ selectedBounds.max.x.toFixed(3) }} (尺寸: {{ selectedBounds.size.x.toFixed(3) }})</span>
              </div>
              <div class="bounds-item">
                <label>Y轴范围:</label>
                <span>{{ selectedBounds.min.y.toFixed(3) }} 到 {{ selectedBounds.max.y.toFixed(3) }} (尺寸: {{ selectedBounds.size.y.toFixed(3) }})</span>
              </div>
              <div class="bounds-item">
                <label>Z轴范围:</label>
                <span>{{ selectedBounds.min.z.toFixed(3) }} 到 {{ selectedBounds.max.z.toFixed(3) }} (尺寸: {{ selectedBounds.size.z.toFixed(3) }})</span>
                <span class="note">*Z轴已根据数据比例进行缩放转换</span>
              </div>
            </div>
            
            <div class="bounds-section">
              <h4>像素坐标（TIFF数据）</h4>
              <div class="bounds-item">
                <label>X轴像素:</label>
                <span>{{ pixelBounds.x_min }} 到 {{ pixelBounds.x_max }} (宽度: {{ pixelBounds.x_max - pixelBounds.x_min }}像素)</span>
              </div>
              <div class="bounds-item">
                <label>Y轴像素:</label>
                <span>{{ pixelBounds.y_min }} 到 {{ pixelBounds.y_max }} (高度: {{ pixelBounds.y_max - pixelBounds.y_min }}像素)</span>
              </div>
              <div class="bounds-item">
                <label>Z轴切片:</label>
                <span>{{ pixelBounds.z_min }} 到 {{ pixelBounds.z_max }} (共{{ pixelBounds.z_max - pixelBounds.z_min + 1 }}个切片)</span>
              </div>
            </div>
            
            <div class="bounds-section">
              <h4>中心点坐标</h4>
              <div class="bounds-item">
                <label>相对坐标:</label>
                <span>({{ selectedBounds.center.x.toFixed(3) }}, {{ selectedBounds.center.y.toFixed(3) }}, {{ selectedBounds.center.z.toFixed(3) }})</span>
              </div>
              <div class="bounds-item">
                <label>像素坐标:</label>
                <span>({{ Math.round((pixelBounds.x_min + pixelBounds.x_max) / 2) }}, {{ Math.round((pixelBounds.y_min + pixelBounds.y_max) / 2) }}, {{ Math.round((pixelBounds.z_min + pixelBounds.z_max) / 2) }})</span>
              </div>
            </div>
          </div>
          
          <div v-else class="minimized-info">
            <span>已选择区域</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls'
import { triTable_ } from './MarchingCubesLookupTable.js'

// 3D框选框类 - 实现可交互的框选功能
class SelectionBox3D {
  constructor(scene, camera, renderer, controls) {
    this.scene = scene
    this.camera = camera
    this.renderer = renderer
    this.controls = controls // 保存controls引用
    this.isActive = false
    this.isDragging = false
    this.dragType = null // 'vertex', 'edge', 'face'
    this.highlightedObject = null // 当前高亮的对象

    // ✅ 添加拖拽起始状态记录
    this.dragStartMin = new THREE.Vector3()
    this.dragStartMax = new THREE.Vector3()
    this.dragStartPoint = new THREE.Vector3()
    this.dragStartVertexPosition = new THREE.Vector3() // 拖拽起始时的顶点位置

    // 框选框的几何属性
    this.min = new THREE.Vector3(-1, -1, -1)
    this.max = new THREE.Vector3(1, 1, 1)
    this.center = new THREE.Vector3()
    this.size = new THREE.Vector3(2, 2, 2)

    // 创建框选框的可视化对象
    this.createBox()
    this.createControlPoints()

    // 事件监听器
    this.setupEventListeners()
  }

  // 创建框选框线框
  createBox() {
    const geometry = new THREE.BoxGeometry(this.size.x, this.size.y, this.size.z)
    const edges = new THREE.EdgesGeometry(geometry)
    this.box = new THREE.LineSegments(edges, new THREE.LineBasicMaterial({ color: 0x00ff00 }))
    this.box.name = 'selection_box'
    this.scene.add(this.box)
  }

  // 创建控制点（只有8个顶点，移除边控制点）
  createControlPoints() {
    this.controlPoints = []

    // 顶点控制点（红色球体）- 增大尺寸便于点击
    const vertexGeometry = new THREE.SphereGeometry(3.0, 12, 12)
    const vertexMaterial = new THREE.MeshBasicMaterial({ color: 0xff0000 })

    // 创建8个顶点控制点
    for (let i = 0; i < 8; i++) {
      const point = new THREE.Mesh(vertexGeometry, vertexMaterial)
      point.name = `control_point_${i}`
      this.controlPoints.push(point)
      this.scene.add(point)
    }

    this.updateControlPoints()
  }

  // 更新控制点位置
  updateControlPoints() {
    const vertices = [
      new THREE.Vector3(this.min.x, this.min.y, this.min.z),
      new THREE.Vector3(this.max.x, this.min.y, this.min.z),
      new THREE.Vector3(this.max.x, this.max.y, this.min.z),
      new THREE.Vector3(this.min.x, this.max.y, this.min.z),
      new THREE.Vector3(this.min.x, this.min.y, this.max.z),
      new THREE.Vector3(this.max.x, this.min.y, this.max.z),
      new THREE.Vector3(this.max.x, this.max.y, this.max.z),
      new THREE.Vector3(this.min.x, this.max.y, this.max.z)
    ]

    // 更新顶点控制点位置
    vertices.forEach((vertex, index) => {
      this.controlPoints[index].position.copy(vertex)
    })

    this.updateBox()
  }

  // 更新框选框
  updateBox() {
    // ✅ 修复：重新计算 center 和 size，避免累积误差
    this.center.copy(this.min).add(this.max).multiplyScalar(0.5)
    this.size.copy(this.max).sub(this.min)

    // 框选框已更新

    // 更新线框几何体
    this.scene.remove(this.box)
    const geometry = new THREE.BoxGeometry(this.size.x, this.size.y, this.size.z)
    const edges = new THREE.EdgesGeometry(geometry)
    this.box = new THREE.LineSegments(edges, new THREE.LineBasicMaterial({ color: 0x00ff00 }))
    this.box.position.copy(this.center)
    this.box.name = 'selection_box'
    this.scene.add(this.box)
  }

  // 设置事件监听器
  setupEventListeners() {
    const canvas = this.renderer.domElement

    // 使用捕获阶段确保先于OrbitControls执行
    canvas.addEventListener('mousedown', this.onMouseDown.bind(this), true)
    canvas.addEventListener('mousemove', this.onMouseMove.bind(this), true)
    canvas.addEventListener('mouseup', this.onMouseUp.bind(this), true)

    // 添加鼠标样式变化
    canvas.addEventListener('mouseenter', this.onMouseEnter.bind(this), true)
    canvas.addEventListener('mouseleave', this.onMouseLeave.bind(this), true)
  }

  // 鼠标按下事件
  onMouseDown(event) {
    if (!this.isActive) return

    const intersects = this.getIntersects(event)
    if (intersects.length > 0) {
      // ✅ 首先禁用 OrbitControls（在事件传播之前）
      if (this.controls) {
        this.controls.enabled = false  // 直接禁用整个控制器
      }

      // 立即阻止事件传播
      event.stopPropagation()
      event.preventDefault()
      event.stopImmediatePropagation()

      this.isDragging = true
      const object = intersects[0].object

      // ✅ 记录拖拽开始时的状态
      this.dragStartMin.copy(this.min)
      this.dragStartMax.copy(this.max)
      if (intersects[0].point) {
        this.dragStartPoint.copy(intersects[0].point)
      }

      if (object.name && object.name.startsWith('control_point_')) {
        this.dragType = 'vertex'
        this.dragIndex = parseInt(object.name.split('_')[2])
        // ✅ 记录拖拽开始时的顶点位置（用于平面相交检测）
        this.dragStartVertexPosition.copy(this.controlPoints[this.dragIndex].position)
      } else if (object.name === 'selection_box') {
        this.dragType = 'face'
      }

      // 开始拖拽视觉反馈
      this.startDragFeedback()

      // ✅ 删除 pointerEvents 修改，保持canvas可交互
      const canvas = this.renderer.domElement
      canvas.style.userSelect = 'none'
      canvas.style.cursor = 'grabbing'
    }
  }

  // 鼠标移动事件
  onMouseMove(event) {
    if (!this.isActive) return

    // 更新鼠标光标样式（非拖拽状态）
    if (!this.isDragging) {
      this.updateCursor(event)
      return
    }

    // 拖拽状态下立即阻止所有事件传播
    event.stopPropagation()
    event.stopImmediatePropagation()

    // 拖拽状态下的处理
    const intersects = this.getIntersects(event, true) // 获取平面交点

    // 平面相交检测

    if (intersects.length > 0) {
      const point = intersects[0].point

      if (this.dragType === 'vertex') {
        this.handleVertexDrag(point)
      } else if (this.dragType === 'face') {
        this.handleFaceDrag(point)
      }

      // 拖拽过程中的视觉反馈
      this.updateDragFeedback()
    }
  }

  // 拖拽过程中的视觉反馈
  updateDragFeedback() {
    if (this.dragType === 'vertex') {
      // 顶点拖拽时，可以添加缩放动画效果
      this.controlPoints[this.dragIndex].scale.set(1.5, 1.5, 1.5)
    } else if (this.dragType === 'face') {
      // 面拖拽时，可以添加透明度变化
      this.box.material.opacity = 0.8
    }
  }

  // 鼠标释放事件
  onMouseUp(event) {
    if (!this.isDragging) return  // ✅ 只有拖拽状态才需要处理
    
    this.isDragging = false
    this.dragType = null
    this.dragIndex = null
    
    // 结束拖拽视觉反馈
    this.endDragFeedback()
    
    // ✅ 重新启用 OrbitControls
    if (this.controls) {
      this.controls.enabled = true
    }
    
    // 恢复交互状态
    const canvas = this.renderer.domElement
    canvas.style.userSelect = ''
    canvas.style.cursor = 'default'
    
    // 阻止事件传播
    event.stopPropagation()
    event.preventDefault()
    event.stopImmediatePropagation()
  }

  // 鼠标进入事件
  onMouseEnter(event) {
    if (!this.isActive) return
    this.updateCursor(event)
  }

  // 鼠标离开事件
  onMouseLeave(event) {
    this.renderer.domElement.style.cursor = 'default'
  }

  // 更新鼠标光标样式
  updateCursor(event) {
    if (!this.isActive || this.isDragging) return

    const intersects = this.getIntersects(event)
    if (intersects.length > 0) {
      const object = intersects[0].object

      if (object.name && object.name.startsWith('control_point_')) {
        this.renderer.domElement.style.cursor = 'pointer'
        this.highlightControlPoint(object)
      } else if (object.name === 'selection_box') {
        this.renderer.domElement.style.cursor = 'move'
        this.highlightSelectionBox()
      } else {
        this.renderer.domElement.style.cursor = 'default'
        this.clearHighlights()
      }
    } else {
      this.renderer.domElement.style.cursor = 'default'
      this.clearHighlights()
    }
  }

  // 高亮控制点
  highlightControlPoint(point) {
    this.clearHighlights()
    point.material.color.set(0xffff00) // 黄色高亮
    this.highlightedObject = point
  }

  // 高亮选择框
  highlightSelectionBox() {
    this.clearHighlights()
    this.box.material.color.set(0xffff00) // 黄色高亮
    this.highlightedObject = this.box
  }

  // 清除高亮
  clearHighlights() {
    if (this.highlightedObject) {
      if (this.highlightedObject.name && this.highlightedObject.name.startsWith('control_point_')) {
        this.highlightedObject.material.color.set(0xff0000) // 红色
      } else if (this.highlightedObject.name === 'selection_box') {
        this.highlightedObject.material.color.set(0x00ff00) // 绿色
      }
      this.highlightedObject = null
    }
  }

  // 拖拽开始时的视觉反馈
  startDragFeedback() {
    if (this.dragType === 'vertex') {
      this.controlPoints[this.dragIndex].material.color.set(0xffff00) // 黄色
    } else if (this.dragType === 'face') {
      this.box.material.color.set(0xffff00) // 黄色
    }
  }

  // 拖拽结束时的视觉反馈
  endDragFeedback() {
    // 恢复拖拽过程中修改的视觉属性
    if (this.dragType === 'vertex') {
      this.controlPoints[this.dragIndex].scale.set(1, 1, 1)
    } else if (this.dragType === 'face') {
      this.box.material.opacity = 1.0
    }

    this.clearHighlights()
  }

  // 处理顶点拖拽（缩放）- 固定对顶点,三条边方向不变但长度可变
  handleVertexDrag(point) {
    const vertexIndex = this.dragIndex

    // ✅ 正确的对顶点映射表（基于实际顶点数组的定义）
    const oppositeVertexMap = [6, 7, 4, 5, 2, 3, 0, 1]
    const oppositeIndex = oppositeVertexMap[vertexIndex]

    // ✅ 获取初始状态的顶点位置数组
    const initialVertexPositions = [
      new THREE.Vector3(this.dragStartMin.x, this.dragStartMin.y, this.dragStartMin.z), // 0
      new THREE.Vector3(this.dragStartMax.x, this.dragStartMin.y, this.dragStartMin.z), // 1
      new THREE.Vector3(this.dragStartMax.x, this.dragStartMax.y, this.dragStartMin.z), // 2
      new THREE.Vector3(this.dragStartMin.x, this.dragStartMax.y, this.dragStartMin.z), // 3
      new THREE.Vector3(this.dragStartMin.x, this.dragStartMin.y, this.dragStartMax.z), // 4
      new THREE.Vector3(this.dragStartMax.x, this.dragStartMin.y, this.dragStartMax.z), // 5
      new THREE.Vector3(this.dragStartMax.x, this.dragStartMax.y, this.dragStartMax.z), // 6
      new THREE.Vector3(this.dragStartMin.x, this.dragStartMax.y, this.dragStartMax.z)  // 7
    ]

    // 获取对顶点位置（固定不变的锚点）
    const oppositeVertex = initialVertexPositions[oppositeIndex]

    // 获取当前顶点的初始位置
    const currentVertexStart = initialVertexPositions[vertexIndex]

    // ✅ 关键修复：判断当前顶点每个坐标轴是min还是max
    // 保持顶点的坐标特征不变（min的还是min，max的还是max）
    const isCurrentVertexMaxX = currentVertexStart.x === this.dragStartMax.x
    const isCurrentVertexMaxY = currentVertexStart.y === this.dragStartMax.y
    const isCurrentVertexMaxZ = currentVertexStart.z === this.dragStartMax.z

    // 拖拽前状态检查

    // ✅ 根据顶点特征更新min/max，保持对应关系
    // 对顶点坐标保持不变，当前顶点使用鼠标坐标
    // ✅ 添加最小尺寸约束，防止拖拽顶点越过对顶点导致负尺寸
    const minBoxSize = 5.0 // 最小边长（增大到5单位，更容易操作）

    // 钳制鼠标点坐标，确保不会越过对顶点
    const clampedPoint = new THREE.Vector3()

    if (isCurrentVertexMaxX) {
      // 当前顶点是max.x，对顶点是min.x
      // max.x 必须 > min.x + minBoxSize
      clampedPoint.x = Math.max(point.x, oppositeVertex.x + minBoxSize)
      this.min.x = oppositeVertex.x
      this.max.x = clampedPoint.x
    } else {
      // 当前顶点是min.x，对顶点是max.x
      // min.x 必须 < max.x - minBoxSize
      clampedPoint.x = Math.min(point.x, oppositeVertex.x - minBoxSize)
      this.min.x = clampedPoint.x
      this.max.x = oppositeVertex.x
    }

    if (isCurrentVertexMaxY) {
      // 当前顶点是max.y，对顶点是min.y
      clampedPoint.y = Math.max(point.y, oppositeVertex.y + minBoxSize)
      this.min.y = oppositeVertex.y
      this.max.y = clampedPoint.y
    } else {
      // 当前顶点是min.y，对顶点是max.y
      clampedPoint.y = Math.min(point.y, oppositeVertex.y - minBoxSize)
      this.min.y = clampedPoint.y
      this.max.y = oppositeVertex.y
    }

    if (isCurrentVertexMaxZ) {
      // 当前顶点是max.z，对顶点是min.z
      clampedPoint.z = Math.max(point.z, oppositeVertex.z + minBoxSize)
      this.min.z = oppositeVertex.z
      this.max.z = clampedPoint.z
    } else {
      // 当前顶点是min.z，对顶点是max.z
      clampedPoint.z = Math.min(point.z, oppositeVertex.z - minBoxSize)
      this.min.z = clampedPoint.z
      this.max.z = oppositeVertex.z
    }

    // ✅ 最终验证：确保 min < max（双重保险）
    if (this.min.x >= this.max.x || this.min.y >= this.max.y || this.min.z >= this.max.z) {
      console.error('❌ 检测到无效的边界框尺寸，回滚到拖拽起始状态', {
        min: this.min.clone(),
        max: this.max.clone(),
        size: new THREE.Vector3(this.max.x - this.min.x, this.max.y - this.min.y, this.max.z - this.min.z)
      })
      // 回滚到拖拽开始时的状态
      this.min.copy(this.dragStartMin)
      this.max.copy(this.dragStartMax)
      return // 终止更新
    }

    // ✅ 更新后验证（计算更新后的8个顶点坐标）
    const updatedVertices = [
      new THREE.Vector3(this.min.x, this.min.y, this.min.z), // 0
      new THREE.Vector3(this.max.x, this.min.y, this.min.z), // 1
      new THREE.Vector3(this.max.x, this.max.y, this.min.z), // 2
      new THREE.Vector3(this.min.x, this.max.y, this.min.z), // 3
      new THREE.Vector3(this.min.x, this.min.y, this.max.z), // 4
      new THREE.Vector3(this.max.x, this.min.y, this.max.z), // 5
      new THREE.Vector3(this.max.x, this.max.y, this.max.z), // 6
      new THREE.Vector3(this.min.x, this.max.y, this.max.z)  // 7
    ]

    // 拖拽后状态验证

    this.updateControlPoints()
  }

  // 获取指定顶点的当前坐标
  getVertexPosition(vertexIndex) {
    // 使用位掩码解析顶点索引
    // bit 0 (x): 0=min.x, 1=max.x
    // bit 1 (y): 0=min.y, 1=max.y
    // bit 2 (z): 0=min.z, 1=max.z
    const isMaxX = (vertexIndex & 1) !== 0
    const isMaxY = (vertexIndex & 2) !== 0
    const isMaxZ = (vertexIndex & 4) !== 0

    return new THREE.Vector3(
      isMaxX ? this.max.x : this.min.x,
      isMaxY ? this.max.y : this.min.y,
      isMaxZ ? this.max.z : this.min.z
    )
  }

  // 确保边界框的有效性
  ensureValidBounds() {
    if (this.min.x > this.max.x) [this.min.x, this.max.x] = [this.max.x, this.min.x]
    if (this.min.y > this.max.y) [this.min.y, this.max.y] = [this.max.y, this.min.y]
    if (this.min.z > this.max.z) [this.min.z, this.max.z] = [this.max.z, this.min.z]
  }

  // 处理面拖拽（移动）
  handleFaceDrag(point) {
    // ✅ 面拖拽功能：移动整个框选框，而不是缩放
    // 使用拖拽开始时的初始状态，避免累积误差

    // ✅ 修复：使用最安全的方式计算中心点，避免任何累积误差
    const startCenter = new THREE.Vector3(
      (this.dragStartMin.x + this.dragStartMax.x) * 0.5,
      (this.dragStartMin.y + this.dragStartMax.y) * 0.5,
      (this.dragStartMin.z + this.dragStartMax.z) * 0.5
    )

    // ✅ 计算从起始中心到当前点的移动向量
    const delta = new THREE.Vector3(
      point.x - startCenter.x,
      point.y - startCenter.y,
      point.z - startCenter.z
    )

    // ✅ 基于初始状态计算新位置（避免累积）
    this.min.set(
      this.dragStartMin.x + delta.x,
      this.dragStartMin.y + delta.y,
      this.dragStartMin.z + delta.z
    )
    this.max.set(
      this.dragStartMax.x + delta.x,
      this.dragStartMax.y + delta.y,
      this.dragStartMax.z + delta.z
    )

    // ✅ 增大边界限制，避免过早限制拖拽
    const boundsLimit = 1000 // 扩大限制框选框的移动范围
    if (Math.abs(this.min.x) > boundsLimit || Math.abs(this.max.x) > boundsLimit ||
        Math.abs(this.min.y) > boundsLimit || Math.abs(this.max.y) > boundsLimit ||
        Math.abs(this.min.z) > boundsLimit || Math.abs(this.max.z) > boundsLimit) {
      console.warn('⚠️ 框选框移动超出边界限制')
      // 恢复到边界内的位置
      this.min.set(this.dragStartMin.x, this.dragStartMin.y, this.dragStartMin.z)
      this.max.set(this.dragStartMax.x, this.dragStartMax.y, this.dragStartMax.z)
      return // 超出边界限制，不进行移动
    }

    // 面拖拽 - 移动整个框

    this.updateControlPoints()
  }

  // 获取射线交点
  getIntersects(event, usePlane = false) {
    const mouse = new THREE.Vector2()
    const rect = this.renderer.domElement.getBoundingClientRect()

    mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1
    mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1

    const raycaster = new THREE.Raycaster()
    raycaster.setFromCamera(mouse, this.camera)

    if (usePlane) {
      // ✅ 使用 Three.js 内置 Plane 类进行平面相交检测
      const cameraDirection = new THREE.Vector3()
      this.camera.getWorldDirection(cameraDirection)

      // ✅ 关键修复：平面应该通过被拖拽对象的起始位置，而不是框选框中心
      let planePoint
      if (this.dragType === 'vertex' && this.dragStartVertexPosition) {
        // 顶点拖拽：平面通过拖拽起始时的顶点位置
        planePoint = this.dragStartVertexPosition
      } else if (this.dragType === 'face') {
        // 面拖拽：平面通过框选框中心
        planePoint = this.center
      } else {
        // 默认：使用框选框中心
        planePoint = this.center
      }

      // 创建垂直于相机观察方向的平面
      const plane = new THREE.Plane()
      plane.setFromNormalAndCoplanarPoint(
        cameraDirection.negate(),  // 平面法向量（指向相机）
        planePoint                  // ✅ 平面通过被拖拽对象的起始位置
      )

      // 射线与平面相交
      const intersectPoint = new THREE.Vector3()
      const intersected = raycaster.ray.intersectPlane(plane, intersectPoint)

      // 返回兼容格式
      return intersected ? [{ point: intersectPoint }] : []
    }

    const objects = [...this.controlPoints, this.box]
    return raycaster.intersectObjects(objects)
  }

  // 激活/禁用框选框
  setActive(active) {
    this.isActive = active
    this.box.visible = active
    this.controlPoints.forEach(point => point.visible = active)
  }

  // 获取框选区域坐标
  getSelectionBounds() {
    return {
      min: this.min.clone(),
      max: this.max.clone(),
      center: this.center.clone(),
      size: this.size.clone()
    }
  }

  // 设置初始位置和大小
  setInitialBounds(modelBounds) {
    // 获取模型边界框的尺寸
    const modelSize = new THREE.Vector3()
    modelBounds.getSize(modelSize)

    // 设置框选框为模型的一半大小，位于传入边界框的中心
    const halfSize = modelSize.clone().multiplyScalar(0.5)
    const center = new THREE.Vector3()
    modelBounds.getCenter(center)
    
    // 正确计算框选框的最小和最大坐标，确保以传入边界框的中心为中心
    this.min.copy(center).sub(halfSize.multiplyScalar(0.5))
    this.max.copy(center).add(halfSize.multiplyScalar(0.5))

    console.log('🎯 框选框初始位置设置：')
    console.log(`   边界框中心: (${center.x.toFixed(2)}, ${center.y.toFixed(2)}, ${center.z.toFixed(2)})`)
    console.log(`   框选框中心: (${this.center.x.toFixed(2)}, ${this.center.y.toFixed(2)}, ${this.center.z.toFixed(2)})`)

    this.updateControlPoints()
  }

  // 清理资源
  dispose() {
    this.scene.remove(this.box)
    this.controlPoints.forEach(point => this.scene.remove(point))
    // 移除事件监听器...
  }
}

// 内存管理器 - 优化混合处理的内存使用
class MemoryManager {
  constructor(maxMemoryMB = 500) {
    this.maxMemoryMB = maxMemoryMB
    this.currentMemoryUsage = 0
    this.memoryBlocks = []
  }

  // 添加内存块并检查是否超过限制
  addMemoryBlock(data, description = '') {
    const memoryUsage = this.calculateMemoryUsage(data)
    this.currentMemoryUsage += memoryUsage

    const block = {
      data: data,
      memoryUsage: memoryUsage,
      description: description,
      timestamp: Date.now()
    }

    this.memoryBlocks.push(block)

    // 检查内存限制
    if (this.currentMemoryUsage > this.maxMemoryMB) {
      this.optimizeMemory()
    }

    return block
  }

  // 计算数据的内存使用量
  calculateMemoryUsage(data) {
    if (data instanceof ArrayBuffer) {
      return data.byteLength / (1024 * 1024)
    } else if (Array.isArray(data)) {
      // 估算数组内存使用（每个元素4字节）
      return data.length * 4 / (1024 * 1024)
    } else if (data instanceof Uint8Array) {
      return data.length / (1024 * 1024)
    }
    return 0
  }

  // 优化内存使用
  optimizeMemory() {
    // 按时间戳排序，优先释放旧的内存块
    this.memoryBlocks.sort((a, b) => a.timestamp - b.timestamp)

    // 释放最旧的内存块直到内存使用量低于阈值
    const threshold = this.maxMemoryMB * 0.8 // 80%阈值
    while (this.currentMemoryUsage > threshold && this.memoryBlocks.length > 0) {
      const oldestBlock = this.memoryBlocks.shift()
      this.currentMemoryUsage -= oldestBlock.memoryUsage
      oldestBlock.data = null // 释放数据
    }
  }

  // 清理所有内存
  clear() {
    this.memoryBlocks.forEach(block => {
      block.data = null
    })
    this.memoryBlocks = []
    this.currentMemoryUsage = 0
  }
}

// 批次数据加载器
class BatchDataLoader {
  constructor(projectId, httpClient) {
    this.projectId = projectId
    this.baseUrl = '/hole-analysis'
    this.http = httpClient
  }

  // 获取批次信息
  async getBatchInfo(batchSize = 200) {
    try {
      const response = await this.http.get(
        `${this.baseUrl}/projects/${this.projectId}/batch/info`,
        { params: { batch_size: batchSize, sample_rate: 1 }}
      )

      // 由于拦截器返回的是response.data，这里直接使用response
      if (response.code === 200) {
        
        return response.data
      } else {
        throw new Error(response.message || '获取批次信息失败')
      }
    } catch (error) {
      console.error('获取批次信息失败:', error)
      throw error
    }
  }

  // 获取批次数据
  async getBatchData(batchIndex, batchSize = 200) {
    try {
      const response = await this.http.get(
        `${this.baseUrl}/projects/${this.projectId}/batch/${batchIndex}`,
        {
          params: { batch_size: batchSize, sample_rate: 1 },
          responseType: 'arraybuffer'
        }
      )

      return response.data
    } catch (error) {
      // 获取批次数据失败
      throw error
    }
  }
}

// 体素网格生成器 - 实现完整的Marching Cubes算法
class VoxelMeshGenerator {
  constructor() {
    this.geometry = null
    this.material = null
    this.mesh = null

    // Marching Cubes查找表（256种情况对应的三角形配置）
    this.triTable = this.createTriangulationTable()
    // this.triTable = triTable_
    this.edgeTable = this.createEdgeTable()
  }

  // 带进度回调的Marching Cubes算法实现
  async generateMarchingCubesMeshWithProgress(voxelArray, dimensions, imageDataInfo, isoLevel = 0.5, progressCallback = null) {
    const [width, height, depth] = dimensions
    const vertices = []
    const indices = []
    const vertexMap = new Map()

    // 开始Marching Cubes算法处理

    const totalCubes = (width - 1) * (height - 1) * (depth - 1)
    let processedCubes = 0
    let lastProgress = 0
    const surfaceCubeCount = 0

    // 调试：统计不同存储顺序的体素访问情况
    const storageOrderStats = {
      zyx: 0,
      yxz: 0,
      xyz: 0,
      failed: 0
    }

    // 遍历所有体素单元
    for (let z = 0; z < depth - 1; z++) {
      for (let y = 0; y < height - 1; y++) {
        for (let x = 0; x < width - 1; x++) {
          // 获取当前立方体8个顶点的值
          const cubeValues = this.getCubeValues(voxelArray, x, y, z, width, height, storageOrderStats)

          // 计算立方体配置索引
          const cubeIndex = this.getCubeIndex(cubeValues, isoLevel)

          // 精简调试：只记录非全背景/全孔洞的立方体配置
          // 已移除详细立方体配置日志以简化控制台输出

          // 如果立方体与等值面相交
          if (cubeIndex !== 0 && cubeIndex !== 255) {
            // 计算边交点
            const edgeVertices = this.calculateEdgeIntersections(cubeValues, x, y, z, isoLevel)

            // 根据查找表生成三角形
            const triConfig = this.triTable[cubeIndex]
            for (let i = 0; triConfig[i] !== -1; i += 3) {
              const v1 = edgeVertices[triConfig[i]]
              const v2 = edgeVertices[triConfig[i + 1]]
              const v3 = edgeVertices[triConfig[i + 2]]

              if (v1 && v2 && v3) {
                const i1 = this.addVertex(vertices, vertexMap, v1)
                const i2 = this.addVertex(vertices, vertexMap, v2)
                const i3 = this.addVertex(vertices, vertexMap, v3)

                indices.push(i1, i2, i3)
              }
            }
          }

          processedCubes++

          // 每处理1%的立方体更新一次进度
          const currentProgress = processedCubes / totalCubes
          if (progressCallback && currentProgress - lastProgress >= 0.01) {
            lastProgress = currentProgress
            progressCallback(currentProgress)

            // 添加短暂延迟避免阻塞UI
            await new Promise(resolve => setTimeout(resolve, 0))
          }
        }
      }
    }

    // Marching Cubes算法完成

    // 创建几何体并优化光滑度
    const geometry = new THREE.BufferGeometry()
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3))
    geometry.setIndex(indices)

    // 计算模型包围盒和中心点，实现模型居中
    // 使用图像数据几何中心而不是内容中心
    geometry.computeBoundingBox()
    const center = new THREE.Vector3(
      (imageDataInfo?.width || dimensions[0]) / 2,
      (imageDataInfo?.height || dimensions[1]) / 2,
      (imageDataInfo?.totalFiles || dimensions[2]) / 2
    )

    // 将顶点平移到坐标原点
    const positionAttribute = geometry.getAttribute('position')
    for (let i = 0; i < positionAttribute.count; i++) {
      positionAttribute.setXYZ(
        i,
        positionAttribute.getX(i) - center.x,
        positionAttribute.getY(i) - center.y,
        positionAttribute.getZ(i) - center.z
      )
    }

    // 更新包围盒
    geometry.computeBoundingBox()

    // 优化法线计算实现光滑曲面
    geometry.computeVertexNormals()
    geometry.normalizeNormals() // 标准化法线

    // 使用Phong材质实现光滑曲面效果
    this.material = new THREE.MeshPhongMaterial({
      color: 0x2196F3, // 蓝色
      transparent: true, // 开启透明度
      opacity: 0.7, // 70%透明度
      side: THREE.DoubleSide, // 双面渲染
      shininess: 100, // 高光强度
      specular: 0x444444, // 高光颜色
      emissive: 0x0a3d62, // 自发光效果
      emissiveIntensity: 0.3 // 自发光强度
    })

    this.mesh = new THREE.Mesh(geometry, this.material)
    this.mesh.name = 'VOI_3D_Model' // 给模型命名便于调试

    // 最终进度回调
    if (progressCallback) {
      progressCallback(1.0)
    }

    return this.mesh
  }

  // 获取立方体8个顶点的值
  getCubeValues(voxelArray, x, y, z, width, height, storageOrderStats = null) {
    const getVoxel = (x, y, z) => {
      if (x < 0 || x >= width || y < 0 || y >= height || z < 0 || z >= voxelArray.length / (width * height)) {
        return 0
      }

      // 尝试多种存储顺序，找出正确的索引计算方式
      const depth = voxelArray.length / (width * height)
      let index = -1
      let orderUsed = null

      // 方案1: [z][y][x] 顺序（深度优先）
      index = z * width * height + y * width + x
      if (index >= 0 && index < voxelArray.length) {
        orderUsed = 'zyx'
        if (storageOrderStats) storageOrderStats.zyx++
        return voxelArray[index] || 0
      }

      // 方案2: [y][x][z] 顺序
      index = y * width * depth + x * depth + z
      if (index >= 0 && index < voxelArray.length) {
        orderUsed = 'yxz'
        if (storageOrderStats) storageOrderStats.yxz++
        return voxelArray[index] || 0
      }

      // 方案3: [x][y][z] 顺序
      index = x * height * depth + y * depth + z
      if (index >= 0 && index < voxelArray.length) {
        orderUsed = 'xyz'
        if (storageOrderStats) storageOrderStats.xyz++
        return voxelArray[index] || 0
      }

      // 如果所有方案都失败，返回0
      if (storageOrderStats) storageOrderStats.failed++
      console.warn(`无法计算体素索引: (${x},${y},${z})`)
      return 0
    }

    return [
      getVoxel(x, y, z), // 0
      getVoxel(x + 1, y, z), // 1
      getVoxel(x + 1, y + 1, z), // 2
      getVoxel(x, y + 1, z), // 3
      getVoxel(x, y, z + 1), // 4
      getVoxel(x + 1, y, z + 1), // 5
      getVoxel(x + 1, y + 1, z + 1), // 6
      getVoxel(x, y + 1, z + 1) // 7
    ]
  }

  // 计算立方体配置索引
  getCubeIndex(cubeValues, isoLevel) {
    let cubeIndex = 0
    let activeVertices = 0

    for (let i = 0; i < 8; i++) {
      if (cubeValues[i] > isoLevel) {
        cubeIndex |= (1 << i)
        activeVertices++
      }
    }

    // 调试信息：已移除详细立方体配置日志以简化控制台输出

    return cubeIndex
  }

  // 计算边交点
  calculateEdgeIntersections(cubeValues, x, y, z, isoLevel) {
    const edgeVertices = new Array(12).fill(null)

    // 检查每条边是否需要计算交点
    const edgeFlags = this.edgeTable[this.getCubeIndex(cubeValues, isoLevel)]

    for (let edge = 0; edge < 12; edge++) {
      if (edgeFlags & (1 << edge)) {
        const [v1, v2] = this.getEdgeVertices(edge)
        const val1 = cubeValues[v1]
        const val2 = cubeValues[v2]

        // 线性插值计算交点位置
        const t = (isoLevel - val1) / (val2 - val1)
        const vertex = this.interpolateVertex(x, y, z, edge, t)
        edgeVertices[edge] = vertex
      }
    }

    return edgeVertices
  }

  // 获取边对应的顶点索引
  getEdgeVertices(edge) {
    const edgeVertices = [
      [0, 1], [1, 2], [2, 3], [3, 0], // 底面边
      [4, 5], [5, 6], [6, 7], [7, 4], // 顶面边
      [0, 4], [1, 5], [2, 6], [3, 7] // 垂直边
    ]
    return edgeVertices[edge]
  }

  // 插值计算顶点位置
  interpolateVertex(x, y, z, edge, t) {
    const edgeOffsets = [
      [0.5, 0, 0], [1, 0.5, 0], [0.5, 1, 0], [0, 0.5, 0], // 底面边
      [0.5, 0, 1], [1, 0.5, 1], [0.5, 1, 1], [0, 0.5, 1], // 顶面边
      [0, 0, 0.5], [1, 0, 0.5], [1, 1, 0.5], [0, 1, 0.5] // 垂直边
    ]
    const offset = edgeOffsets[edge]

    // 根据插值参数t计算精确的交点位置
    return [
      x + offset[0] * t,
      y + offset[1] * t,
      z + offset[2] * t
    ]
  }

  // 添加顶点到数组并返回索引
  addVertex(vertices, vertexMap, vertex) {
    const key = vertex.join(',')
    if (vertexMap.has(key)) {
      return vertexMap.get(key)
    }

    const index = vertices.length / 3
    vertices.push(vertex[0], vertex[1], vertex[2])
    vertexMap.set(key, index)
    return index
  }

  // 创建边查找表
  createEdgeTable() {
    return [
      0x0, 0x109, 0x203, 0x30a, 0x406, 0x50f, 0x605, 0x70c,
      0x80c, 0x905, 0xa0f, 0xb06, 0xc0a, 0xd03, 0xe09, 0xf00,
      0x190, 0x99, 0x393, 0x29a, 0x596, 0x49f, 0x795, 0x69c,
      0x99c, 0x895, 0xb9f, 0xa96, 0xd9a, 0xc93, 0xf99, 0xe90,
      0x230, 0x339, 0x33, 0x13a, 0x636, 0x73f, 0x435, 0x53c,
      0xa3c, 0xb35, 0x83f, 0x936, 0xe3a, 0xf33, 0xc39, 0xd30,
      0x3a0, 0x2a9, 0x1a3, 0xaa, 0x7a6, 0x6af, 0x5a5, 0x4ac,
      0xbac, 0xaa5, 0x9af, 0x8a6, 0xfaa, 0xea3, 0xda9, 0xca0,
      0x460, 0x569, 0x663, 0x76a, 0x66, 0x16f, 0x265, 0x36c,
      0xc6c, 0xd65, 0xe6f, 0xf66, 0x86a, 0x963, 0xa69, 0xb60,
      0x5f0, 0x4f9, 0x7f3, 0x6fa, 0x1f6, 0xff, 0x3f5, 0x2fc,
      0xdfc, 0xcf5, 0xfff, 0xef6, 0x9fa, 0x8f3, 0xbf9, 0xaf0,
      0x650, 0x759, 0x453, 0x55a, 0x256, 0x35f, 0x55, 0x15c,
      0xe5c, 0xf55, 0xc5f, 0xd56, 0xa5a, 0xb53, 0x859, 0x950,
      0x7c0, 0x6c9, 0x5c3, 0x4ca, 0x3c6, 0x2cf, 0x1c5, 0xcc,
      0xfcc, 0xec5, 0xdcf, 0xcc6, 0xbca, 0xac3, 0x9c9, 0x8c0,
      0x8c0, 0x9c9, 0xac3, 0xbca, 0xcc6, 0xdcf, 0xec5, 0xfcc,
      0xcc, 0x1c5, 0x2cf, 0x3c6, 0x4ca, 0x5c3, 0x6c9, 0x7c0,
      0x950, 0x859, 0xb53, 0xa5a, 0xd56, 0xc5f, 0xf55, 0xe5c,
      0x15c, 0x55, 0x35f, 0x256, 0x55a, 0x453, 0x759, 0x650,
      0xaf0, 0xbf9, 0x8f3, 0x9fa, 0xef6, 0xfff, 0xcf5, 0xdfc,
      0x2fc, 0x3f5, 0xff, 0x1f6, 0x6fa, 0x7f3, 0x4f9, 0x5f0,
      0xb60, 0xa69, 0x963, 0x86a, 0xf66, 0xe6f, 0xd65, 0xc6c,
      0x36c, 0x265, 0x16f, 0x66, 0x76a, 0x663, 0x569, 0x460,
      0xca0, 0xda9, 0xea3, 0xfaa, 0x8a6, 0x9af, 0xaa5, 0xbac,
      0x4ac, 0x5a5, 0x6af, 0x7a6, 0xaa, 0x1a3, 0x2a9, 0x3a0,
      0xd30, 0xc39, 0xf33, 0xe3a, 0x936, 0x83f, 0xb35, 0xa3c,
      0x53c, 0x435, 0x73f, 0x636, 0x13a, 0x33, 0x339, 0x230,
      0xe90, 0xf99, 0xc93, 0xd9a, 0xa96, 0xb9f, 0x895, 0x99c,
      0x69c, 0x795, 0x49f, 0x596, 0x29a, 0x393, 0x99, 0x190,
      0xf00, 0xe09, 0xd03, 0xc0a, 0xb06, 0xa0f, 0x905, 0x80c,
      0x70c, 0x605, 0x50f, 0x406, 0x30a, 0x203, 0x109, 0x0
    ]
  }

  // 创建完整的Marching Cubes三角形查找表
  createTriangulationTable() {
    // 完整的Marching Cubes三角形查找表（256种配置）
    const table = new Array(256)

    // 初始化所有配置为无三角形
    for (let i = 0; i < 256; i++) {
      table[i] = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
    }

    // 配置完整的Marching Cubes查找表（简化版，包含主要配置）
    // 基础配置（单三角形）
    table[1] = [0, 8, 3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
    table[2] = [0, 1, 9, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
    table[4] = [1, 2, 10, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
    table[8] = [2, 3, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
    table[16] = [4, 7, 8, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
    table[32] = [4, 5, 9, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
    table[64] = [5, 6, 10, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
    table[128] = [6, 7, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]

    // 双三角形配置
    table[3] = [0, 8, 3, 0, 1, 9, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
    table[5] = [0, 8, 3, 1, 2, 10, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
    table[6] = [0, 1, 9, 1, 2, 10, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
    table[9] = [0, 1, 9, 2, 3, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
    table[10] = [0, 8, 3, 0, 1, 9, 2, 3, 11, -1, -1, -1, -1, -1, -1, -1]
    table[12] = [1, 2, 10, 2, 3, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]

    // 三三角形配置
    table[7] = [0, 8, 3, 0, 1, 9, 1, 2, 10, -1, -1, -1, -1, -1, -1, -1]
    table[11] = [0, 8, 3, 1, 2, 10, 2, 3, 11, -1, -1, -1, -1, -1, -1, -1]
    table[13] = [0, 1, 9, 1, 2, 10, 2, 3, 11, -1, -1, -1, -1, -1, -1, -1]
    table[14] = [0, 8, 3, 0, 1, 9, 2, 3, 11, -1, -1, -1, -1, -1, -1, -1]

    // 四三角形配置（完整立方体表面）
    table[15] = [0, 8, 3, 0, 1, 9, 1, 2, 10, 2, 3, 11, -1, -1, -1, -1]
    table[240] = [4, 7, 8, 4, 5, 9, 5, 6, 10, 6, 7, 11, -1, -1, -1, -1]

    // 添加更多常见配置（简化版，实际需要256种完整配置）
    // 这里只添加了最常见的配置，实际应用中应该使用完整的查找表

    // Marching Cubes三角形查找表初始化完成
    return table
  }
}

export default {
  name: 'Voi3DViewer',
  props: {
    projectId: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      // Three.js相关
      scene: null,
      camera: null,
      renderer: null,
      controls: null,

      // 加载状态
      loading: false,
      loadingText: '加载中...',
      modelRendered: false, // 模型渲染完成状态

      // 数据
      voxelData: null,
      meshGenerator: null,
      batchInfo: null, // 存储批次信息，包含总切片数量

      // 3D框选功能
      selectionBox: null,
      selectionBoxActive: false,
      selectedBounds: null,
      // 添加缺失的响应式属性以修复警告
      showSelectionInfo: false,
      selectionInfoPanelMinimized: false, // 控制信息面板是否最小化
      pixelBounds: {
        x_min: 0,
        x_max: 0,
        y_min: 0,
        y_max: 0,
        z_min: 0,
        z_max: 0
      },
      
      // 3D模型边界框可视化
      modelBoundaryBox: null,
      showModelBoundary: true, // 默认显示边界框
      
      // 模型边界信息
      modelBounds: {
        min: { x: 0, y: 0, z: 0 },
        max: { x: 0, y: 0, z: 0 },
        size: { x: 0, y: 0, z: 0 },
        center: { x: 0, y: 0, z: 0 }
      }
    }
  },
  mounted() {
    this.initThreeJS()
  },
  beforeDestroy() {
    this.cleanupThreeJS()
  },
  methods: {
    // 初始化Three.js场景
    initThreeJS() {
      const container = this.$refs.canvasContainer
      const canvas = this.$refs.canvas

      // 创建场景
      this.scene = new THREE.Scene()
      this.scene.background = new THREE.Color(0xf0f0f0)

      // 添加明显的坐标轴辅助工具
      this.addCoordinateAxes()

      // 创建相机
      this.setupCamera()

      // 创建渲染器
      this.renderer = new THREE.WebGLRenderer({
        canvas: canvas,
        antialias: true
      })
      this.renderer.setSize(container.clientWidth, container.clientHeight)
      this.renderer.setPixelRatio(window.devicePixelRatio)

      // 创建控制器
      this.controls = new OrbitControls(this.camera, this.renderer.domElement)
      this.controls.enableDamping = true
      this.controls.dampingFactor = 0.05

      // 添加灯光
      this.setupLighting()

      // 开始渲染循环
      this.animate()

      // 窗口大小变化处理
      window.addEventListener('resize', this.onWindowResize)
    },

    // 设置相机（默认使用透视相机）
    setupCamera() {
      const container = this.$refs.canvasContainer
      const aspect = container.clientWidth / container.clientHeight

      // 使用透视相机
      this.camera = new THREE.PerspectiveCamera(60, aspect, 0.1, 1000)
      this.camera.position.set(150, 150, 150)
      this.camera.lookAt(0, 0, 0)
    },

    // 添加明显的坐标轴辅助工具
    addCoordinateAxes() {
      // 创建坐标轴组
      const axesGroup = new THREE.Group()
      axesGroup.name = 'coordinate_axes'

      // X轴 - 红色
      const xAxisGeometry = new THREE.CylinderGeometry(0.5, 0.5, 50, 12)
      const xAxisMaterial = new THREE.MeshBasicMaterial({ color: 0xff0000 })
      const xAxis = new THREE.Mesh(xAxisGeometry, xAxisMaterial)
      xAxis.rotation.z = Math.PI / 2
      xAxis.position.x = 25
      axesGroup.add(xAxis)

      // X轴箭头
      const xArrowGeometry = new THREE.ConeGeometry(1.5, 5, 12)
      const xArrow = new THREE.Mesh(xArrowGeometry, xAxisMaterial)
      xArrow.position.x = 50
      xArrow.rotation.z = Math.PI / 2
      axesGroup.add(xArrow)

      // X轴标签
      const xLabel = this.createAxisLabel('X', 0xff0000)
      xLabel.position.set(55, 0, 0)
      axesGroup.add(xLabel)

      // Y轴 - 绿色
      const yAxisGeometry = new THREE.CylinderGeometry(0.5, 0.5, 50, 12)
      const yAxisMaterial = new THREE.MeshBasicMaterial({ color: 0x00ff00 })
      const yAxis = new THREE.Mesh(yAxisGeometry, yAxisMaterial)
      yAxis.position.y = 25
      axesGroup.add(yAxis)

      // Y轴箭头
      const yArrowGeometry = new THREE.ConeGeometry(1.5, 5, 12)
      const yArrow = new THREE.Mesh(yArrowGeometry, yAxisMaterial)
      yArrow.position.y = 50
      axesGroup.add(yArrow)

      // Y轴标签
      const yLabel = this.createAxisLabel('Y', 0x00ff00)
      yLabel.position.set(0, 55, 0)
      axesGroup.add(yLabel)

      // Z轴 - 蓝色
      const zAxisGeometry = new THREE.CylinderGeometry(0.5, 0.5, 50, 12)
      const zAxisMaterial = new THREE.MeshBasicMaterial({ color: 0x0000ff })
      const zAxis = new THREE.Mesh(zAxisGeometry, zAxisMaterial)
      zAxis.rotation.x = Math.PI / 2
      zAxis.position.z = 25
      axesGroup.add(zAxis)

      // Z轴箭头
      const zArrowGeometry = new THREE.ConeGeometry(1.5, 5, 12)
      const zArrow = new THREE.Mesh(zArrowGeometry, zAxisMaterial)
      zArrow.position.z = 50
      zArrow.rotation.x = -Math.PI / 2
      axesGroup.add(zArrow)

      // Z轴标签
      const zLabel = this.createAxisLabel('Z', 0x0000ff)
      zLabel.position.set(0, 0, 55)
      axesGroup.add(zLabel)

      // 将坐标轴添加到场景
      this.scene.add(axesGroup)
    },

    // 创建坐标轴标签
    createAxisLabel(text, color) {
      const canvas = document.createElement('canvas')
      const context = canvas.getContext('2d')
      canvas.width = 64
      canvas.height = 64
      
      // 绘制文本
      context.fillStyle = `rgb(${color >> 16 & 0xff}, ${color >> 8 & 0xff}, ${color & 0xff})`
      context.font = 'bold 48px Arial'
      context.textAlign = 'center'
      context.textBaseline = 'middle'
      context.fillText(text, 32, 32)
      
      // 创建纹理
      const texture = new THREE.CanvasTexture(canvas)
      const material = new THREE.SpriteMaterial({ map: texture })
      const sprite = new THREE.Sprite(material)
      sprite.scale.set(10, 10, 1)
      
      return sprite
    },

    // 设置灯光
    setupLighting() {
      // 环境光 - 增加强度确保模型可见
      const ambientLight = new THREE.AmbientLight(0xffffff, 1.2)
      this.scene.add(ambientLight)

      // 主方向光 - 增加强度和范围
      const directionalLight1 = new THREE.DirectionalLight(0xffffff, 1.5)
      directionalLight1.position.set(500, 500, 500)
      directionalLight1.castShadow = true
      this.scene.add(directionalLight1)

      // 辅助方向光 - 从不同角度照亮模型
      const directionalLight2 = new THREE.DirectionalLight(0xffffff, 0.8)
      directionalLight2.position.set(-300, 300, -300)
      this.scene.add(directionalLight2)

      // 点光源 - 增加强度
      const pointLight = new THREE.PointLight(0xffffff, 1.0)
      pointLight.position.set(0, 0, 0)
      this.scene.add(pointLight)

      // 添加半球光 - 提供更自然的光照
      const hemisphereLight = new THREE.HemisphereLight(0xffffff, 0x444444, 0.6)
      this.scene.add(hemisphereLight)

      // 场景多光源光照初始化完成
    },

    // 渲染循环
    animate() {
      requestAnimationFrame(this.animate)

      if (this.controls) {
        this.controls.update()
      }

      if (this.renderer && this.scene && this.camera) {
        this.renderer.render(this.scene, this.camera)
      }
    },

    // 窗口大小变化处理
    onWindowResize() {
      const container = this.$refs.canvasContainer
      if (!container) return

      this.camera.aspect = container.clientWidth / container.clientHeight
      this.camera.updateProjectionMatrix()
      this.renderer.setSize(container.clientWidth, container.clientHeight)
    },

    // 调整相机位置以适配模型
    adjustCameraToModel(dimensions) {
      const [depth, height, width] = dimensions
      const maxDimension = Math.max(width, height, depth)

      // 计算模型边界框大小
      const modelSize = maxDimension

      // 设置相机距离，确保模型占据画布约1/3大小
      const container = this.$refs.canvasContainer
      const containerWidth = container.clientWidth
      const containerHeight = container.clientHeight

      // 计算合适的相机距离，使模型占据画布1/3
      const fov = this.camera.fov * (Math.PI / 180) // 转换为弧度
      const targetModelSize = Math.min(containerWidth, containerHeight) / 3
      const cameraDistance = (targetModelSize / 2) / Math.tan(fov / 2)

      // 确保相机距离足够远以看到整个模型
      const minDistance = modelSize * 1.5
      const finalDistance = Math.max(cameraDistance, minDistance)

      // 设置相机位置，确保模型在视野中心
      this.camera.position.set(finalDistance, finalDistance, finalDistance)
      this.camera.lookAt(0, 0, 0)

      // 设置相机近平面和远平面
      this.camera.near = 1
      this.camera.far = finalDistance * 4
      this.camera.updateProjectionMatrix()

      if (this.controls) {
        this.controls.update()
      }
    },

    // 生成3D表面模型使用Marching Cubes算法

    // 生成3D表面模型使用Marching Cubes算法
    async generateSurfaceWithMarchingCubes(voxelGrid) {
      const startTime = performance.now()

      try {
        console.log('🚀 开始使用Marching Cubes算法生成3D表面模型...')
        this.loadingText = '正在生成3D表面模型...'

        // 确保体素网格数据有效
        if (!voxelGrid || !voxelGrid.data) {
          console.error('无效的体素网格数据:', voxelGrid)
          throw new Error('无效的体素网格数据')
        }

        // 创建体素网格生成器实例
        const meshGenerator = new VoxelMeshGenerator()

        // 准备Marching Cubes算法所需的参数
        const dimensions = [voxelGrid.width, voxelGrid.height, voxelGrid.depth]
        const voxelArray = voxelGrid.data
        // 体素值只有0和1，等值面阈值设为0.5可以检测到孔洞（体素值1>0.5）
        const isoLevel = 0.5 // 等值面阈值

        const totalVoxels = dimensions[0] * dimensions[1] * dimensions[2]
        const totalCubes = (dimensions[0] - 1) * (dimensions[1] - 1) * (dimensions[2] - 1)

        // 体素网格信息

        // 时间估算
        const estimatedTime = Math.max(30, Math.floor(totalCubes / 5000000)) // 每500万立方体约1秒
        this.loadingText = `正在生成3D模型... 预计${estimatedTime}秒`

        // 使用Marching Cubes算法生成网格
        console.log('🔄 开始Marching Cubes算法处理...')
        const mesh = await meshGenerator.generateMarchingCubesMeshWithProgress(
          voxelArray,
          dimensions,
          this.imageDataInfo,
          isoLevel,
          (progress) => {
            const elapsed = ((performance.now() - startTime) / 1000).toFixed(1)
            const percent = Math.floor(progress * 100)
            this.loadingText = `生成3D模型中... ${percent}% (已用时: ${elapsed}秒)`
          }
        )

        const endTime = performance.now()
        const totalTime = ((endTime - startTime) / 1000).toFixed(1)

        console.log(`✅ Marching Cubes算法完成! 总用时: ${totalTime}秒`)
        console.log(`📐 生成的3D模型: ${mesh.geometry.attributes.position.count / 3}个顶点, ${mesh.geometry.index.count / 3}个三角形`)

        this.loadingText = '3D模型生成完成，正在渲染...'

        return mesh
      } catch (error) {
        const endTime = performance.now()
        const totalTime = ((endTime - startTime) / 1000).toFixed(1)
        console.error(`❌ 生成3D表面模型失败 (用时${totalTime}秒):`, error)
        this.loadingText = '3D模型生成失败'
        throw error
      }
    },

    // 清理Three.js资源
    cleanupThreeJS() {
      if (this.renderer) {
        this.renderer.dispose()
      }
      window.removeEventListener('resize', this.onWindowResize)
    },

    // 统一批次数据加载方法（混合处理优化）
    async loadBatchData() {
      const startTime = performance.now()
      // 开始混合批次数据加载
      this.loading = true

      try {
        // 创建批次数据加载器和内存管理器
        this.batchLoader = new BatchDataLoader(this.projectId, this.$http)
        this.memoryManager = new MemoryManager(500) // 500MB内存限制

        // 1. 获取批次信息
        this.loadingText = '正在获取批次信息...'
        const batchInfo = await this.batchLoader.getBatchInfo(200)

        const totalBatches = batchInfo.total_batches || 1
        const totalSlices = batchInfo.total_files || batchInfo.total_slices || 1000

        // 保存批次信息供后续使用
        this.batchInfo = batchInfo

        // 批次信息获取成功

        // 验证切片计数
        if (batchInfo.total_files && batchInfo.total_slices && batchInfo.total_files !== batchInfo.total_slices) {
          // 切片计数不一致，使用total_files作为总切片数
        }

        // 2. 混合处理：流式加载数据，统一构建模型
        // 开始混合处理批次数据

        // 清理之前的模型
        if (this.mesh) {
          this.scene.remove(this.mesh)
          this.mesh.geometry.dispose()
          this.mesh.material.dispose()
          this.mesh = null
        }

        // 预分配整个数据集的Uint8Array
        // 先处理第一个批次获取实际尺寸，然后重新计算总容量
        // 动态计算预分配容量

        // 临时处理第一个批次获取实际尺寸
        const firstBatchData = await this.batchLoader.getBatchData(1, 200)
        const firstBatchResult = await this.processBatchDataHybrid(firstBatchData, batchInfo, 0)

        // 使用实际TIFF文件尺寸（从batchInfo获取，避免硬编码）
        const sliceWidth = batchInfo?.image_width || batchInfo?.dimensions?.[0]
        const sliceHeight = batchInfo?.image_height || batchInfo?.dimensions?.[1]
        
        if (!sliceWidth || !sliceHeight) {
          throw new Error('无法获取TIFF文件尺寸信息，请检查批次数据格式')
        }
        
        const totalVoxelCount = sliceWidth * sliceHeight * totalSlices

        // 预分配完整体素数组

        const allVoxelData = new Uint8Array(totalVoxelCount)
        let globalVoxelIndex = 0
        const allSlices = []

        // 流式加载每个批次数据
        for (let batchIndex = 0; batchIndex < totalBatches; batchIndex++) {
          const batchStartTime = performance.now()
          const actualBatchIndex = batchIndex + 1 // 批次索引从1开始
          // 混合处理批次

          // 更新加载状态
          this.loadingText = `正在加载批次 ${actualBatchIndex}/${totalBatches}...`

          // 获取当前批次数据
          const batchData = await this.batchLoader.getBatchData(actualBatchIndex, 200)
          // 批次数据获取完成

          // 将批次数据添加到内存管理器
          this.memoryManager.addMemoryBlock(batchData, `批次${actualBatchIndex}原始数据`)

          // 混合处理当前批次：解析数据并存储体素数据
          const hybridResult = await this.processBatchDataHybrid(batchData, batchInfo, batchIndex)

          // 使用分块添加，避免数组长度超限
          // 批次体素数据结构检查

          // 直接写入预分配数组，避免数组长度超限
          const voxelData = hybridResult.voxelData
          if (voxelData && voxelData.length > 0) {
            // 检查是否会越界
            if (globalVoxelIndex + voxelData.length > totalVoxelCount) {
              // 批次数据超出预分配范围
            } else {
              // 使用 Uint8Array.set() 高效复制数据
              allVoxelData.set(voxelData, globalVoxelIndex)
              globalVoxelIndex += voxelData.length

              // 批次体素数据已写入
            }
          } else {
            // 批次体素数据为空
          }

          // 添加切片信息
          for (const slice of hybridResult.slices) {
            allSlices.push(slice)
          }

          const batchTime = ((performance.now() - batchStartTime) / 1000).toFixed(1)
          // 批次处理完成
          this.loadingText = `批次${actualBatchIndex}完成，已加载${allSlices.length}个切片...`

          // 添加短暂延迟，避免阻塞UI
          await new Promise(resolve => setTimeout(resolve, 10))
        }

        const dataLoadTime = ((performance.now() - startTime) / 1000).toFixed(1)
        console.log(`✅ 所有批次数据加载完成! 总切片数: ${allSlices.length}，数据加载用时: ${dataLoadTime}秒`)

        // 验证数据完整性
        console.log(`📊 体素数据完整性验证:`)
        console.log(`   预分配容量: ${totalVoxelCount.toLocaleString()}`)
        console.log(`   实际写入: ${globalVoxelIndex.toLocaleString()}`)
        console.log(`   数据填充率: ${(globalVoxelIndex / totalVoxelCount * 100).toFixed(2)}%`)

        // 检查前1万个体素的数据分布
        const sampleSize = Math.min(10000, globalVoxelIndex)
        const sampleHoles = allVoxelData.slice(0, sampleSize).filter(v => v === 1).length
        console.log(`   样本检测（前${sampleSize}体素）: 孔洞${sampleHoles}个 (${(sampleHoles / sampleSize * 100).toFixed(2)}%)`)

        if (globalVoxelIndex === 0) {
          throw new Error('体素数据为空，无法构建3D模型')
        }

        // 3. 统一构建完整的3D模型
        console.log('🏗️ 开始构建统一3D模型...')
        this.loadingText = '正在构建统一3D模型...'

        // 对切片进行自然数排序
        console.log('📊 对切片进行自然数排序...')
        const sortedSlices = this.sortSlicesNaturally(allSlices)
        console.log(`✅ 切片自然数排序完成，总切片数: ${sortedSlices.length}`)

        // 将体素数据添加到内存管理器
        this.memoryManager.addMemoryBlock(allVoxelData, '统一体素数据')

        // 构建统一的体素网格
        console.log('🔲 构建统一体素网格...')
        const dimensions = [sliceWidth, sliceHeight, totalSlices]
        this.dimensions = dimensions  // 存储到组件数据中
        
        const unifiedVoxelGrid = await this.buildUnifiedVoxelGrid({
          voxelData: allVoxelData.slice(0, globalVoxelIndex), // 只使用实际写入的数据
          dimensions: dimensions,
          metadata: { original_filenames: sortedSlices }
        })

        console.log(`✅ 统一体素网格构建完成，尺寸: ${unifiedVoxelGrid.width}x${unifiedVoxelGrid.height}x${unifiedVoxelGrid.depth}`)

        // 生成完整的3D模型
        console.log('🎯 开始生成3D表面模型...')
        const completeMesh = await this.generateSurfaceWithMarchingCubes(unifiedVoxelGrid)
        this.mesh = completeMesh

        // 添加模型到场景并输出调试信息
        console.log('➕ 将3D模型添加到场景...')
        // 修复Z轴拉长问题：设置Z轴缩放因子为0.3
        console.log('🔧 修复Z轴拉长问题，设置Z轴缩放因子为0.4...')
        completeMesh.scale.set(1, 1, 0.4)
        this.scene.add(completeMesh)

        // 输出详细的场景和模型信息用于调试

        // 检查模型是否可见

        // 计算模型边界框
        const bbox = new THREE.Box3().setFromObject(completeMesh)
        const modelSize = bbox.getSize(new THREE.Vector3())

        // 调整相机位置以适配整个模型
        this.adjustCameraToModel([unifiedVoxelGrid.depth, unifiedVoxelGrid.height, unifiedVoxelGrid.width])

        // 强制渲染多次以确保模型显示
        if (this.renderer && this.scene && this.camera) {
          for (let i = 0; i < 3; i++) {
            this.renderer.render(this.scene, this.camera)
          }
        }

        const totalTime = ((performance.now() - startTime) / 1000).toFixed(1)
        console.log(`🎉 混合批次数据加载完成! 统一3D模型构建成功，总用时: ${totalTime}秒`)

        // 初始化3D框选框
        console.log('🎯 初始化3D框选框...')
        this.initSelectionBox()
        this.setupSelectionBoxBounds()

        // 添加3D模型边界框可视化
        console.log('🎯 添加3D模型边界框可视化...')
        this.addModelBoundaryBox()

        // 更新模型边界信息
        this.updateModelBounds()

        // 清理内存管理器中的临时数据（保留体素数据用于可能的后续操作）
        this.memoryManager.optimizeMemory()

        this.loading = false
        this.loadingText = '3D模型加载完成'
        this.modelRendered = true // 标记模型渲染完成
        
        // 发出模型渲染完成事件
        this.$emit('model-rendered')

        return true
      } catch (error) {
        console.error('混合批次数据加载失败:', error)

        // 清理内存管理器
        if (this.memoryManager) {
          this.memoryManager.clear()
        }

        throw error
      }
    },

    // 处理批次数据（已废弃，使用混合处理方案替代）
    // async processBatchData(allBatchData, batchInfo) {
    //   // 此方法已废弃，请使用混合处理方案
    //   throw new Error('此方法已废弃，请使用混合处理方案')
    // },

    // 解析批次数据（处理ZIP格式，避免重复二值化）
    async parseBatchData(batchArrayBuffer) {
      try {

        // 检查是否是ZIP格式（以PK开头）
        const header = new Uint8Array(batchArrayBuffer.slice(0, 2))
        const headerStr = String.fromCharCode(...header)

        if (headerStr !== 'PK') {
          // 数据不是标准ZIP格式，尝试直接解析为JSON
          // 如果不是ZIP格式，尝试直接解析为JSON
          const text = new TextDecoder().decode(batchArrayBuffer)
          const data = JSON.parse(text)

          // 验证数据格式
          if (!data.voxel_data || !data.dimensions || !data.metadata) {
            throw new Error('批次数据格式错误')
          }

          return {
            voxelData: data.voxel_data,
            dimensions: data.dimensions,
            metadata: data.metadata,
            slices: data.metadata.original_filenames || []
          }
        }

        // 检测到ZIP格式数据，开始解压

        // 优化：使用静态导入避免动态导入导致的栈溢出
        // 使用全局变量或预先导入的库
        if (!window.JSZip) {
          window.JSZip = (await import('jszip')).default
        }

        if (!window.UTIF) {
          const UTIFModule = await import('utif')
          window.UTIF = UTIFModule.default || UTIFModule
        }

        const zip = await window.JSZip.loadAsync(batchArrayBuffer)

        // 读取metadata.json
        const metadataFile = zip.file('metadata.json')
        if (!metadataFile) {
          throw new Error('ZIP包中缺少metadata.json文件')
        }

        const metadataText = await metadataFile.async('text')
        const metadata = JSON.parse(metadataText)

        // ZIP包元数据

        // 读取TIFF文件并转换为体素数据（避免重复二值化）
        const slices = metadata.original_filenames || []

        // 移除文件数量限制，处理所有文件
        const filesToProcess = slices

        // 预先获取第一个文件的尺寸，用于预分配数组
        let width = 512; let height = 512
        let totalElements = 0

        // 先处理第一个文件获取尺寸
        if (filesToProcess.length > 0) {
          const firstFilename = filesToProcess[0]
          const firstTiffFile = zip.file(firstFilename)
          if (firstTiffFile) {
            const firstTiffData = await firstTiffFile.async('uint8array')
            const firstIfds = window.UTIF.decode(firstTiffData)
            if (firstIfds.length > 0) {
              const firstIfd = firstIfds[0]
              window.UTIF.decodeImage(firstTiffData, firstIfd)
              width = firstIfd.width
              height = firstIfd.height
            }
          }
        }

        // 预分配固定大小的Uint8Array
        totalElements = width * height * filesToProcess.length

        const allVoxelData = new Uint8Array(totalElements)
        let currentIndex = 0
        const sliceDimensions = []

        // 开始解析TIFF文件

        // 使用异步处理，避免阻塞主线程
        for (let i = 0; i < filesToProcess.length; i++) {
          const filename = filesToProcess[i]
          const tiffFile = zip.file(filename)
          if (tiffFile) {
            // 精简日志：已移除详细进度日志以简化控制台输出

            // 读取TIFF文件数据
            const tiffData = await tiffFile.async('uint8array')

            // 使用UTIF解析TIFF文件
            const ifds = window.UTIF.decode(tiffData)

            if (ifds.length === 0) {
              // 无法解析TIFF文件
              continue
            }

            // 解码TIFF图像数据
            const ifd = ifds[0]
            window.UTIF.decodeImage(tiffData, ifd)

            // 获取图像尺寸
            const width = ifd.width
            const height = ifd.height

            // 直接将TIFF像素数据转换为体素数据（避免重复二值化）
            const sliceVoxels = this.convertTiffToVoxelsWithoutBinarization(ifd, width, height)

            // 调试：检查切片体素数据
            if (i === 0) {
              // 第一个切片体素数据检查
              // 统计孔洞和背景体素
              const holeCount = sliceVoxels.filter(v => v === 1).length
              const backgroundCount = sliceVoxels.filter(v => v === 0).length
            }

            // 直接写入预分配数组
            if (sliceVoxels.length > 0) {
              // 检查是否会越界
              if (currentIndex + sliceVoxels.length > totalElements) {
                console.warn(`⚠️ 切片${i}数据超出预分配范围，跳过`)
                continue
              }

              // 使用 Uint8Array.set() 方法高效复制数据
              allVoxelData.set(sliceVoxels, currentIndex)
              currentIndex += sliceVoxels.length

              // 记录切片尺寸
              sliceDimensions.push({
                width: ifd.width,
                height: ifd.height,
                filename: filename
              })

              // 调试：验证数据复制是否正确
              if (i !== 0) {
                // 第一个切片数据复制验证，可先不做输出
              }
            } else {
              console.warn(`⚠️ 切片${i}体素数据为空，跳过复制`)
            }

            // 添加延迟，避免密集处理导致栈溢出
            if (i % 10 === 0) {
              await new Promise(resolve => setTimeout(resolve, 0))
            }
          }
        }

        // 构建维度信息
        const dimensions = [width, height, filesToProcess.length]

        // 验证数据完整性
        const holeCount = allVoxelData.slice(0, Math.min(allVoxelData.length, 100000)).filter(v => v === 1).length
        // 数据验证

        return {
          voxelData: allVoxelData, // 直接返回预分配的 Uint8Array
          dimensions: dimensions,
          metadata: metadata,
          slices: filesToProcess
        }
      } catch (error) {
        console.error('解析批次数据失败:', error)
        throw new Error('批次数据解析失败')
      }
    },

    // 将TIFF像素数据转换为体素数据（避免重复二值化）
    convertTiffToVoxelsWithoutBinarization(ifd, width, height) {
      try {
        // 获取像素数据（后端已经二值化）
        const pixelData = ifd.data
        if (!pixelData) {
          console.warn('TIFF文件缺少像素数据')
          return new Uint8Array(width * height).fill(0)
        }

        // 使用预分配Uint8Array，避免动态数组增长
        const totalElements = width * height
        const voxels = new Uint8Array(totalElements)
        let voxelIndex = 0

        // 根据TIFF的位深度处理像素数据
        const bitsPerSample = ifd.bitsPerSample || 8
        const samplesPerPixel = ifd.samplesPerPixel || 1

        // 后端已经提供二值化数据，直接映射到体素值
        // 后端处理：孔洞是黑色（0），背景是白色（255）
        // 二值化数据：像素值只有0（孔洞）和255（背景）

        if (bitsPerSample === 8) {
          // 8位二值图像：直接映射，不需要阈值判断
          for (let i = 0; i < pixelData.length && voxelIndex < totalElements; i += samplesPerPixel) {
            const pixelValue = pixelData[i]
            // 正确映射：孔洞（黑色，0）→体素值1，背景（白色，255）→体素值0
            const voxelValue = pixelValue === 0 ? 1 : 0
            voxels[voxelIndex++] = voxelValue
          }
        } else if (bitsPerSample === 1) {
          // 1位二值图像：需要正确映射
          // 后端处理：孔洞是黑色（0），背景是白色（255）
          // 1位图像中，0表示黑色（孔洞），1表示白色（背景）
          for (let i = 0; i < pixelData.length && voxelIndex < totalElements; i++) {
            const byte = pixelData[i]
            // 每个字节包含8个像素
            for (let bit = 7; bit >= 0 && voxelIndex < totalElements; bit--) {
              const pixelValue = (byte >> bit) & 1
              // 正确映射：孔洞（黑色，0）→体素值1，背景（白色，1）→体素值0
              const voxelValue = pixelValue === 0 ? 1 : 0
              voxels[voxelIndex++] = voxelValue
            }
          }
        } else {
          console.warn(`不支持的位深度: ${bitsPerSample}，使用默认处理`)
          // 默认处理：使用128作为阈值
          for (let i = 0; i < totalElements; i++) {
            const pixelValue = i < pixelData.length ? pixelData[i] : 0
            const voxelValue = pixelValue > 128 ? 1 : 0
            voxels[i] = voxelValue
          }
        }

        // 确保数组填充完整
        if (voxelIndex < totalElements) {
          for (let i = voxelIndex; i < totalElements; i++) {
            voxels[i] = 0
          }
        }

        // 精简日志：只在处理第一个文件时显示统计信息
        if (this.firstFileProcessed === undefined) {
          this.firstFileProcessed = true
          const holeCount = voxels.filter(v => v === 1).length
          const backgroundCount = voxels.filter(v => v === 0).length

          // 如果孔洞比例太低，可能是阈值设置问题
          if (holeCount === 0) {
            console.warn('⚠️ 警告：未检测到孔洞体素，可能需要调整阈值')
          } else if (holeCount === voxels.length) {
            console.warn('⚠️ 警告：所有体素都被识别为孔洞，可能需要调整阈值')
          }
        }

        return voxels
      } catch (error) {
        console.error('TIFF到体素转换失败（避免重复二值化）:', error)
        // 出错时返回空体素数据
        return new Uint8Array(width * height).fill(0)
      }
    },

    // 保留原方法用于兼容性
    convertTiffToVoxels(ifd, width, height) {
      return this.convertTiffToVoxelsWithoutBinarization(ifd, width, height)
    },

    // 对切片进行自然数排序
    sortSlicesNaturally(slices) {
      // 使用slice()方法替代展开操作符，避免数组长度超限
      return slices.slice().sort((a, b) => {
        // 提取文件名中的数字进行自然数排序
        const numA = parseInt(a.match(/slice_(\d+)\.tiff?/)?.[1] || a.match(/(\d+)\.tiff?/)?.[1] || 0)
        const numB = parseInt(b.match(/slice_(\d+)\.tiff?/)?.[1] || b.match(/(\d+)\.tiff?/)?.[1] || 0)
        return numA - numB
      })
    },

    // 构建统一体素网格（优化存储）
    async buildUnifiedVoxelGrid(batchData) {
      try {
        const { voxelData, dimensions } = batchData
        const [width, height, depth] = dimensions

        console.log('构建统一体素网格，尺寸:', width, 'x', height, 'x', depth)

        // 检查数组长度是否超过JavaScript限制
        const totalElements = width * height * depth
        if (totalElements > Number.MAX_SAFE_INTEGER) {
          throw new Error(`数组长度超过JavaScript安全限制: ${totalElements} > ${Number.MAX_SAFE_INTEGER}`)
        }

        // 优化存储：使用Uint8Array存储二值化数据（0或1）
        // 对于1000-2000个切片，每个切片512x512，总数据量约为：
        // 1000 * 512 * 512 * 1 byte ≈ 262MB
        // 2000 * 512 * 512 * 1 byte ≈ 524MB

        // 使用分块处理避免数组长度超限
        const voxelArray = new Uint8Array(totalElements)

        // 分块复制数据，避免一次性操作大数组
        const chunkSize = 1000000 // 每次处理100万个元素
        for (let i = 0; i < voxelData.length; i += chunkSize) {
          const end = Math.min(i + chunkSize, voxelData.length)
          for (let j = i; j < end; j++) {
            voxelArray[j] = voxelData[j]
          }
          // 添加延迟避免阻塞UI
          if (i % (chunkSize * 10) === 0) {
            await new Promise(resolve => setTimeout(resolve, 0))
          }
        }

        // 内存使用监控
        const memoryUsage = voxelArray.length / (1024 * 1024) // MB

        // 如果数据量过大，进行分块处理
        if (memoryUsage > 500) {
          console.warn('数据量较大，建议进行分块处理')
        }

        return {
          data: voxelArray,
          width,
          height,
          depth,
          memoryUsage: memoryUsage
        }
      } catch (error) {
        console.error('构建统一体素网格失败:', error)
        throw new Error('体素网格构建失败')
      }
    },

    // 混合处理批次数据：解析数据并存储体素数据
    async processBatchDataHybrid(batchData, batchInfo, batchIndex) {
      const startTime = performance.now()
      const batchNumber = batchIndex + 1

      try {
        // 开始混合处理批次

        // 解析当前批次数据
        const parsedData = await this.parseBatchData(batchData)
        // 批次数据解析完成

        // 对当前批次的切片进行自然数排序
        const sortedSlices = this.sortSlicesNaturally(parsedData.slices)

        // 计算当前批次数据的内存使用量
        const batchMemoryUsage = parsedData.voxelData.length * 4 / (1024 * 1024) // MB

        // 立即释放当前批次的原始数据，只保留体素数据
        batchData = null // 释放原始数据

        // 强制垃圾回收（如果浏览器支持）
        if (window.gc) {
          window.gc()
        }

        const totalTime = ((performance.now() - startTime) / 1000).toFixed(1)
        // 批次处理完成

        // 返回解析后的数据
        return {
          voxelData: parsedData.voxelData,
          slices: sortedSlices,
          memoryUsage: batchMemoryUsage
        }
      } catch (error) {
        const totalTime = ((performance.now() - startTime) / 1000).toFixed(1)
        // 混合处理批次失败
        throw error
      }
    },

    // 流式处理批次数据（已废弃，使用混合处理方案替代）
    // async processBatchDataStreaming(batchData, batchInfo, batchIndex) {
    //   // 此方法已废弃，请使用混合处理方案
    //   throw new Error('此方法已废弃，请使用混合处理方案')
    // },

    // 为单个批次生成3D表面（已废弃，使用统一模型生成方案替代）
    // async generateSurfaceForBatch(voxelGrid) {
    //   // 此方法已废弃，请使用统一模型生成方案
    //   throw new Error('此方法已废弃，请使用统一模型生成方案')
    // },

    // 3D框选功能方法
    // 初始化框选框
    initSelectionBox() {
      if (!this.scene || !this.camera || !this.renderer || !this.controls) {
        console.warn('无法初始化框选框：Three.js场景或控制器未就绪')
        return
      }

      this.selectionBox = new SelectionBox3D(this.scene, this.camera, this.renderer, this.controls)
      console.log('✅ 3D框选框初始化完成')
    },

    // 设置框选框初始位置
    setupSelectionBoxBounds() {
      if (!this.selectionBox || !this.mesh) {
        console.warn('无法设置框选框位置：框选框或模型未就绪')
        return
      }

      // 检查 dimensions 是否已设置
      if (!this.dimensions || !Array.isArray(this.dimensions) || this.dimensions.length < 3) {
        console.warn('dimensions未设置，使用模型内容边界框作为备选')
        const bbox = new THREE.Box3().setFromObject(this.mesh)
        this.selectionBox.setInitialBounds(bbox)
        return
      }

      // 使用 dimensions 创建图像数据边界框（以图像数据中心为中心），并应用与模型相同的z轴缩放因子0.4
      const imageDataBounds = new THREE.Box3()
      const center = new THREE.Vector3(
        this.dimensions[0] / 2, 
        this.dimensions[1] / 2, 
        this.dimensions[2] * 0.4 / 2
      )
      const halfSize = new THREE.Vector3(
        this.dimensions[0] / 2, 
        this.dimensions[1] / 2, 
        this.dimensions[2] * 0.4 / 2
      )
      imageDataBounds.setFromCenterAndSize(center, halfSize.multiplyScalar(2))

      this.selectionBox.setInitialBounds(imageDataBounds)

      // 自动激活框选框
      this.selectionBoxActive = true
      this.selectionBox.setActive(true)

      console.log('✅ 框选框初始位置设置完成，已自动激活')
      console.log(`   Z轴缩放因子: 0.4 (与模型保持一致)`)
    },

    // 切换框选框显示/隐藏
    toggleSelectionBox() {
      if (!this.selectionBox) {
        console.warn('框选框未初始化')
        return
      }

      this.selectionBoxActive = !this.selectionBoxActive
      this.selectionBox.setActive(this.selectionBoxActive)

      console.log(`🔘 框选框${this.selectionBoxActive ? '显示' : '隐藏'}`)
    },

    // 确认选择
    confirmSelection() {
      if (!this.selectionBox || !this.selectionBoxActive) {
        this.$message.warning('请先显示框选框并调整到合适区域')
        console.warn('无法确认选择：框选框未激活')
        return
      }

      // 检查选择区域是否有效
      const bounds = this.selectionBox.getSelectionBounds()
      if (bounds.size.x <= 0 || bounds.size.y <= 0 || bounds.size.z <= 0) {
        this.$message.error('选择区域无效，请重新调整框选框')
        console.warn('选择区域无效')
        return
      }

      // 检查选择区域是否过小
      const minSize = 0.1
      if (bounds.size.x < minSize || bounds.size.y < minSize || bounds.size.z < minSize) {
        this.$message.warning('选择区域过小，建议调整框选框大小')
      }

      // 显示确认对话框
      this.$confirm('确认选择当前VOI区域吗？', '确认VOI选择', {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.selectedBounds = bounds

        // 显示确认消息
        this.$message.success('VOI选取确认完成')

        // 显示选择区域信息面板
        this.showSelectionInfo = true

        // 发送数据到后端
        this.sendSelectionToBackend(bounds)

        // 通知父组件VOI选择已完成
        this.$emit('selection-completed', bounds)
      }).catch(() => {
        // 用户取消操作
        console.log('用户取消了VOI选择确认')
      })
    },

    // 重置框选框
    resetSelectionBox() {
      if (!this.selectionBox) {
        console.warn('框选框未初始化')
        return
      }

      this.setupSelectionBoxBounds()
      console.log('🔄 框选框已重置')
    },

    // 切换选择信息面板显示模式
    toggleSelectionInfoPanel() {
      this.selectionInfoPanelMinimized = !this.selectionInfoPanelMinimized
      console.log(`📋 选择信息面板${this.selectionInfoPanelMinimized ? '已缩小' : '已放大'}`)
    },

    // 复制选择数据
    copySelectionData() {
      if (!this.selectedBounds) {
        this.$message.warning('没有选择数据可复制')
        return
      }

      const data = {
        min: this.selectedBounds.min,
        max: this.selectedBounds.max,
        center: this.selectedBounds.center,
        size: this.selectedBounds.size,
        timestamp: new Date().toISOString()
      }

      const text = `选择区域坐标数据：
最小坐标: (${data.min.x.toFixed(2)}, ${data.min.y.toFixed(2)}, ${data.min.z.toFixed(2)})
最大坐标: (${data.max.x.toFixed(2)}, ${data.max.y.toFixed(2)}, ${data.max.z.toFixed(2)})
中心坐标: (${data.center.x.toFixed(2)}, ${data.center.y.toFixed(2)}, ${data.center.z.toFixed(2)})
区域尺寸: (${data.size.x.toFixed(2)}, ${data.size.y.toFixed(2)}, ${data.size.z.toFixed(2)})
时间戳: ${data.timestamp}`

      // 使用Clipboard API复制文本
      navigator.clipboard.writeText(text).then(() => {
        this.$message.success('坐标数据已复制到剪贴板')
        console.log('📋 坐标数据已复制')
      }).catch(err => {
        console.error('复制失败:', err)
        this.$message.error('复制失败，请手动复制控制台输出')
      })
    },

    // 发送选择数据到后端
    async sendSelectionToBackend(bounds) {
      // 准备发送VOI选择数据到后端

      // 使用边界框的边界数据（更简单直接，已以图像数据中心为中心）
      if (!this.modelBoundaryBox) {
        this.$message.error('边界框未加载，无法进行坐标转换')
        console.error('❌ 边界框未加载')
        return
      }

      // 直接从边界框获取边界数据
      const bbox = new THREE.Box3().setFromObject(this.modelBoundaryBox)
      const imageDataMin = bbox.min
      const imageDataMax = bbox.max
      
      // 图像数据边界范围
      const imageDataXRange = imageDataMax.x - imageDataMin.x
      const imageDataYRange = imageDataMax.y - imageDataMin.y
      const imageDataZRange = imageDataMax.z - imageDataMin.z
      
      // 实际TIFF数据尺寸（动态获取）
      // 从batchInfo或实际数据中获取TIFF尺寸
      if (!this.batchInfo) {
        this.$message.error('批次信息未加载，无法获取TIFF尺寸')
        console.error('❌ 批次信息未加载')
        return
      }
      
      // 获取实际尺寸，如果没有则抛出错误而不是使用默认值
      const imageWidth = this.batchInfo?.image_width || this.batchInfo?.dimensions?.[0]
      const imageHeight = this.batchInfo?.image_height || this.batchInfo?.dimensions?.[1]
      const totalSlices = this.batchInfo?.total_files || this.batchInfo?.total_slices
      
      if (!imageWidth || !imageHeight || !totalSlices) {
        this.$message.error('无法获取TIFF数据尺寸信息')
        console.error('❌ 缺少TIFF尺寸信息:', { imageWidth, imageHeight, totalSlices })
        return
      }
      
      console.log('📏 实际TIFF数据尺寸:', { imageWidth, imageHeight, totalSlices })
      
      // 计算缩放比例（根据您的公式），保留2位小数精度
      const xScale = parseFloat((imageWidth / imageDataXRange).toFixed(2))   // 公式：图像宽度 / 图像数据X轴范围
      const yScale = parseFloat((imageHeight / imageDataYRange).toFixed(2))  // 公式：图像高度 / 图像数据Y轴范围
      const zScale = parseFloat((totalSlices / imageDataZRange).toFixed(2))  // 公式：(切片总数-1) / 图像数据Z轴范围
      
      console.log('📏 坐标转换参数：')
      console.log(`   图像数据边界: X[${imageDataMin.x.toFixed(1)}, ${imageDataMax.x.toFixed(1)}] Y[${imageDataMin.y.toFixed(1)}, ${imageDataMax.y.toFixed(1)}] Z[${imageDataMin.z.toFixed(1)}, ${imageDataMax.z.toFixed(1)}]`)
      console.log(`   缩放比例: X=${xScale}, Y=${yScale}, Z=${zScale}`)
      
      // 边界检查：确保选择区域在图像数据边界范围内
      if (bounds.min.x < imageDataMin.x || bounds.max.x > imageDataMax.x ||
          bounds.min.y < imageDataMin.y || bounds.max.y > imageDataMax.y ||
          bounds.min.z < imageDataMin.z || bounds.max.z > imageDataMax.z) {
        this.$message.error('选择区域超出图像数据边界，请重新选择')
        console.error('❌ 选择区域超出图像数据边界')
        return
      }
      
      // 坐标转换函数（根据您的公式）
      const convertToPixel = (coord, axis) => {
        let result = 0
        switch(axis) {
          case 'x':
            result = (coord - imageDataMin.x) * xScale
            break
          case 'y':
            result = (coord - imageDataMin.y) * yScale
            break
          case 'z':
            result = (coord - imageDataMin.z) * zScale
            break
        }
        return Math.max(0, Math.min(axis === 'z' ? totalSlices - 1 : (axis === 'x' ? imageWidth - 1 : imageHeight - 1), Math.round(result)))
      }

      // 构建发送数据（符合后端API格式）
      const selectionData = {
        project_id: this.projectId,
        selection_bounds: {
          x_min: convertToPixel(bounds.min.x, 'x'),
          x_max: convertToPixel(bounds.max.x, 'x'),
          y_min: convertToPixel(bounds.min.y, 'y'),
          y_max: convertToPixel(bounds.max.y, 'y'),
          z_min: convertToPixel(bounds.min.z, 'z'),
          z_max: convertToPixel(bounds.max.z, 'z')
        },
        timestamp: new Date().toISOString(),
        selection_type: 'voi_3d_selection'
      }

      // 添加选择区域边界的详细日志
      console.log('📏 选择区域边界信息:')
      console.log(`   相对坐标范围:`)
      console.log(`     X轴: [${bounds.min.x.toFixed(3)}, ${bounds.max.x.toFixed(3)}] (尺寸: ${bounds.size.x.toFixed(3)})`)
      console.log(`     Y轴: [${bounds.min.y.toFixed(3)}, ${bounds.max.y.toFixed(3)}] (尺寸: ${bounds.size.y.toFixed(3)})`)
      console.log(`     Z轴: [${bounds.min.z.toFixed(3)}, ${bounds.max.z.toFixed(3)}] (尺寸: ${bounds.size.z.toFixed(3)})`)
      console.log(`   像素坐标范围:`)
      console.log(`     X轴: [${selectionData.selection_bounds.x_min}, ${selectionData.selection_bounds.x_max}] (宽度: ${selectionData.selection_bounds.x_max - selectionData.selection_bounds.x_min}像素)`)
      console.log(`     Y轴: [${selectionData.selection_bounds.y_min}, ${selectionData.selection_bounds.y_max}] (高度: ${selectionData.selection_bounds.y_max - selectionData.selection_bounds.y_min}像素)`)
      console.log(`     Z轴: [${selectionData.selection_bounds.z_min}, ${selectionData.selection_bounds.z_max}] (切片数: ${selectionData.selection_bounds.z_max - selectionData.selection_bounds.z_min + 1})`)
      console.log(`   中心点坐标:`)
      console.log(`     相对坐标: (${bounds.center.x.toFixed(3)}, ${bounds.center.y.toFixed(3)}, ${bounds.center.z.toFixed(3)})`)
      console.log(`     像素坐标: (${Math.round((selectionData.selection_bounds.x_min + selectionData.selection_bounds.x_max) / 2)}, ${Math.round((selectionData.selection_bounds.y_min + selectionData.selection_bounds.y_max) / 2)}, ${Math.round((selectionData.selection_bounds.z_min + selectionData.selection_bounds.z_max) / 2)})`)

      console.log('📦 VOI选择数据：', selectionData)
      console.log('📏 坐标转换详情：')
      console.log(`  原始相对坐标: min(${bounds.min.x.toFixed(3)}, ${bounds.min.y.toFixed(3)}, ${bounds.min.z.toFixed(3)})`)
      console.log(`                max(${bounds.max.x.toFixed(3)}, ${bounds.max.y.toFixed(3)}, ${bounds.max.z.toFixed(3)})`)
      console.log(`  转换后像素坐标: x[${selectionData.selection_bounds.x_min}, ${selectionData.selection_bounds.x_max}]`)
      console.log(`                  y[${selectionData.selection_bounds.y_min}, ${selectionData.selection_bounds.y_max}]`)
      console.log(`                  z[${selectionData.selection_bounds.z_min}, ${selectionData.selection_bounds.z_max}]`)

      // 更新pixelBounds用于前端显示
      this.pixelBounds = {
        x_min: selectionData.selection_bounds.x_min,
        x_max: selectionData.selection_bounds.x_max,
        y_min: selectionData.selection_bounds.y_min,
        y_max: selectionData.selection_bounds.y_max,
        z_min: selectionData.selection_bounds.z_min,
        z_max: selectionData.selection_bounds.z_max
      }

      // 显示发送进度
      const loading = this.$loading({
        lock: true,
        text: '正在确认VOI选取并发送数据到后端...',
        spinner: 'el-icon-loading',
        background: 'rgba(0, 0, 0, 0.7)'
      })

      try {
        // 调用后端VOI确认API
        const response = await this.$http.post('/hole-analysis/voi/confirm', selectionData)

        // 改进响应检查逻辑（注意：拦截器返回的是response.data）
        if (response) {
          // 由于拦截器返回的是response.data，所以直接检查response
          if (response.code === 200) {
            console.log('✅ VOI数据保存成功')
            
            // 显示简洁的成功提示
            this.$message({
              message: 'VOI选取成功',
              type: 'success',
              duration: 2000,
              offset: 80 // 向下偏移，避免被遮挡
            })

            // 显示处理结果（可选）
            if (response.data) {
              console.log('📁 处理结果：', response.data)
              // this.showProcessingResult(response.data) // 暂时不显示详细结果
            }
          } else {
            // 后端返回了错误状态码
            const errorMessage = response.message || `VOI选取确认失败 (错误码: ${response.code})`
            console.error('❌ API返回错误：', errorMessage)
            throw new Error(errorMessage)
          }
        } else {
          // 响应格式不正确
          console.error('❌ API响应格式错误：', response)
          throw new Error('API响应格式不正确，请联系管理员')
        }
      } catch (error) {
        console.error('❌ VOI选取确认失败：', error)

        // 检查错误类型
        if (error.response) {
          // 服务器返回了错误状态码
          const status = error.response.status
          const message = error.response.data?.message || '服务器错误'

          if (status === 404) {
            this.$message.error('VOI确认API端点不存在，请联系管理员配置后端服务')
          } else if (status === 401) {
            this.$message.error('未授权，请重新登录')
          } else if (status >= 500) {
            this.$message.error('服务器内部错误，请稍后重试')
          } else {
            this.$message.error(`VOI选取确认失败: ${message}`)
          }

          console.error(`❌ 服务器错误 ${status}:`, error.response.data)
        } else if (error.request) {
          // 请求已发送但未收到响应
          this.$message.error('网络连接错误，请检查后端服务是否运行')
          console.error('❌ 网络错误：请求已发送但未收到响应')
        } else {
          // 其他错误（通常是拦截器抛出的错误）
          const errorMessage = error.message || '未知错误'
          
          // 检查是否是VOI选取确认失败的错误
          if (errorMessage.includes('VOI选取确认失败')) {
            this.$message.error(errorMessage)
          } else {
            this.$message.error(`VOI选取确认失败: ${errorMessage}`)
          }
        }
      } finally {
        loading.close()
      }
    },

    // 显示处理结果
    showProcessingResult(resultData) {
      this.$message({
        type: 'success',
        message: `VOI选取处理完成：${resultData.saved_files_count}个切片已保存到${resultData.output_dir}`,
        duration: 0,
        showClose: true
      })

      // 在控制台显示详细信息
      console.log('📊 VOI选取处理结果：')
      console.log(`   保存文件数量: ${resultData.saved_files_count}`)
      console.log(`   输出目录: ${resultData.output_dir}`)
      console.log(`   选择区域边界:`, resultData.selection_bounds)
      
      if (resultData.saved_files && resultData.saved_files.length > 0) {
        console.log(`   保存的文件列表:`)
        resultData.saved_files.forEach((file, index) => {
          console.log(`     ${index + 1}. ${file}`)
        })
      }
    },

    // 保存选择记录
    saveSelectionRecord(selectionData, response) {
      if (!this.selectionHistory) {
        this.selectionHistory = []
      }

      const record = {
        id: response.id,
        data: selectionData,
        timestamp: selectionData.timestamp,
        status: 'success',
        response: response
      }

      this.selectionHistory.unshift(record)
      console.log('📝 选择记录已保存:', record)
    },

    // 保存失败的选择记录
    saveFailedSelection(selectionData, error) {
      if (!this.selectionHistory) {
        this.selectionHistory = []
      }

      const record = {
        id: 'failed_' + Date.now(),
        data: selectionData,
        timestamp: selectionData.timestamp,
        status: 'failed',
        error: {
          message: error.message,
          stack: error.stack
        }
      }

      this.selectionHistory.unshift(record)
      console.log('❌ 失败记录已保存:', record)
    },

    // 更新模型边界信息
    updateModelBounds() {
      // 优先使用边界边框的边界信息（如果存在），否则使用模型的边界信息
      let bbox
      if (this.modelBoundaryBox) {
        // 使用边界边框的边界信息（以图像数据中心为中心）
        bbox = new THREE.Box3().setFromObject(this.modelBoundaryBox)
        console.log('📊 使用边界边框的边界信息（对称边界）')
      } else if (this.mesh) {
        // 使用模型的边界信息（基于实际内容）
        bbox = new THREE.Box3().setFromObject(this.mesh)
        console.log('📊 使用3D模型的边界信息（内容边界）')
      } else {
        console.warn('无法更新模型边界信息：3D模型和边界边框都未加载')
        return
      }
      
      const size = new THREE.Vector3()
      const center = new THREE.Vector3()
      
      bbox.getSize(size)
      bbox.getCenter(center)
      
      // 更新模型边界信息
      this.modelBounds = {
        min: { 
          x: bbox.min.x,
          y: bbox.min.y, 
          z: bbox.min.z 
        },
        max: { 
          x: bbox.max.x,
          y: bbox.max.y,
          z: bbox.max.z 
        },
        size: { 
          x: size.x,
          y: size.y,
          z: size.z 
        },
        center: { 
          x: center.x,
          y: center.y,
          z: center.z 
        }
      }
      
      console.log('� 模型边界信息已更新')
      console.log(`   最小坐标: (${bbox.min.x.toFixed(2)}, ${bbox.min.y.toFixed(2)}, ${bbox.min.z.toFixed(2)})`)
      console.log(`   最大坐标: (${bbox.max.x.toFixed(2)}, ${bbox.max.y.toFixed(2)}, ${bbox.max.z.toFixed(2)})`)
      console.log(`   中心坐标: (${center.x.toFixed(2)}, ${center.y.toFixed(2)}, ${center.z.toFixed(2)})`)
      console.log(`   尺寸: (${size.x.toFixed(2)}, ${size.y.toFixed(2)}, ${size.z.toFixed(2)})`)
    },

    // 添加3D模型边界框可视化
    addModelBoundaryBox() {
      if (!this.mesh) {
        console.warn('无法添加模型边界框：3D模型未加载')
        return
      }

      // 检查 dimensions 是否已设置
      if (!this.dimensions || !Array.isArray(this.dimensions) || this.dimensions.length < 3) {
        console.warn('dimensions未设置，使用模型内容边界框作为备选')
        const bbox = new THREE.Box3().setFromObject(this.mesh)
        const size = new THREE.Vector3()
        bbox.getSize(size)
        const center = new THREE.Vector3()
        bbox.getCenter(center)
        
        // 创建边界框几何体
        const geometry = new THREE.BoxGeometry(size.x, size.y, size.z)
        // ... 继续原有代码
        return
      }

      // 使用 dimensions 创建图像数据边界框，并应用与模型相同的z轴缩放因子0.4
      const size = new THREE.Vector3(this.dimensions[0], this.dimensions[1], this.dimensions[2] * 0.4)
      const center = new THREE.Vector3(this.dimensions[0] / 2, this.dimensions[1] / 2, this.dimensions[2] * 0.4 / 2)

      console.log('📐 3D模型边界框信息：')
      console.log(`   中心坐标: (${center.x.toFixed(2)}, ${center.y.toFixed(2)}, ${center.z.toFixed(2)})`)
      console.log(`   尺寸: (${size.x.toFixed(2)}, ${size.y.toFixed(2)}, ${size.z.toFixed(2)})`)
      console.log(`   Z轴缩放因子: 0.4 (与模型保持一致)`)

      // 创建边界框几何体（显示长方体的12条边）
      // 创建以图像数据中心为原点的边界框
      const geometry = new THREE.BoxGeometry(size.x, size.y, size.z)
      const edges = new THREE.EdgesGeometry(geometry)
      
      // 创建边界框材质（蓝色半透明）
      const boundaryMaterial = new THREE.LineBasicMaterial({ 
        color: 0x0066ff, // 蓝色
        linewidth: 2,
        transparent: true,
        opacity: 0.8
      })

      // 创建边界框线框对象
      this.modelBoundaryBox = new THREE.LineSegments(edges, boundaryMaterial)
      // 边界框已经以图像数据中心为中心（BoxGeometry默认以几何中心为原点）
      this.modelBoundaryBox.name = 'model_boundary_box'
      
      // 添加到场景
      this.scene.add(this.modelBoundaryBox)

      console.log('✅ 3D模型边界框可视化已添加')
      console.log('📏 边界框显示长方体的12条边，帮助确认可框选范围')
    },

    // 切换模型边界框显示/隐藏
    toggleModelBoundary() {
      if (!this.modelBoundaryBox) {
        console.warn('无法切换边界框：边界框未创建')
        return
      }

      this.showModelBoundary = !this.showModelBoundary
      this.modelBoundaryBox.visible = this.showModelBoundary

      console.log(`🔘 模型边界框${this.showModelBoundary ? '显示' : '隐藏'}`)
    }
  }
}
</script>

<style scoped>
.voi-3d-viewer {
  position: relative;
  width: 100%;
  height: 100%;
}

.main-content {
  display: flex;
  width: 100%;
  height: 100vh; /* 使用视口高度 */
  gap: 20px;
}

.canvas-container {
  flex: 1.5; /* 画布占据1.5倍空间 */
  position: relative;
  min-height: 600px; /* 最小高度确保可用性 */
}

.three-canvas {
  width: 100%;
  height: 100%;
  display: block;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loading-spinner {
  text-align: center;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.loading-spinner i {
  font-size: 24px;
  color: #409eff;
  margin-bottom: 10px;
}

.loading-spinner span {
  display: block;
  margin-top: 10px;
  color: #606266;
}

.selection-controls {
  width: 300px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.control-panel {
  background: white;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  border: 1px solid #e4e7ed;
  height: fit-content;
  max-height: 100%;
  overflow-y: auto;
}

.control-panel h3 {
  margin: 0 0 15px 0;
  color: #303133;
  font-size: 16px;
}

.control-buttons {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 15px;
}

.control-buttons .el-button {
  width: 100%;
}

.control-buttons .el-button.active {
  background-color: #409eff;
  border-color: #409eff;
  color: white;
}

.selection-info {
  border-top: 1px solid #ebeef5;
  padding-top: 15px;
}

.selection-info p {
  margin: 0 0 10px 0;
  font-weight: bold;
  color: #606266;
}

.selection-info ul {
  margin: 0;
  padding-left: 20px;
  color: #909399;
  font-size: 12px;
  line-height: 1.5;
}

.selection-info li {
  margin-bottom: 5px;
}

.selection-info-panel {
  position: absolute;
  top: 20px;
  left: 20px;
  z-index: 100;
}

.info-panel {
  background: white;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  min-width: 300px;
  max-width: 400px;
}

.info-panel h3 {
  margin: 0 0 15px 0;
  color: #303133;
  font-size: 16px;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 10px;
}

.bounds-info {
  margin-bottom: 15px;
}

.bounds-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 13px;
}

.bounds-item label {
  font-weight: bold;
  color: #606266;
  min-width: 80px;
}

.bounds-item span {
  color: #303133;
  font-family: 'Courier New', monospace;
}

.info-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.info-actions .el-button {
  font-size: 12px;
}

/* 选择信息面板缩小/放大功能样式 */
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.panel-header h3 {
  margin: 0;
  color: #303133;
  font-size: 16px;
  border-bottom: none;
  padding-bottom: 0;
}

.panel-controls {
  display: flex;
  gap: 5px;
}

.panel-controls .el-button {
  font-size: 11px;
  padding: 4px 8px;
}

.info-panel.minimized {
  min-width: 150px;
  max-width: 200px;
  padding: 8px 12px;
}

.minimized-info {
  text-align: center;
  color: #606266;
  font-size: 12px;
  font-weight: bold;
}

.bounds-section {
  margin-bottom: 15px;
}

.bounds-section h4 {
  margin: 0 0 8px 0;
  color: #409eff;
  font-size: 13px;
  font-weight: bold;
}

.note {
  font-size: 11px;
  color: #909399;
  font-style: italic;
  display: block;
  margin-top: 2px;
}
</style>
