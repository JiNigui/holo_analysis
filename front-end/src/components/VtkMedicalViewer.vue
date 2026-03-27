<template>
  <div class="vtk-medical-viewer">
    <div class="main-content">
      <div ref="renderContainer" class="vtk-render-container" />
      <div v-if="loading" class="loading-overlay">
        <div class="loading-spinner">
          <i class="el-icon-loading" />
          <span>{{ loadingText }}</span>
        </div>
      </div>
    </div>

    <div class="interaction-controls">
      <div class="control-panel">
        <h3>3D交互控制</h3>
        <div class="view-controls">
          <el-button-group>
            <el-button size="small" @click="resetCamera" title="重置视角">
              <i class="el-icon-refresh" />
            </el-button>
            <el-button size="small" @click="toggleWireframe" :type="showWireframe ? 'primary' : 'default'" title="线框/实体模式">
              <i class="el-icon-c-scale-to-original" />
            </el-button>
          </el-button-group>
        </div>

        <div class="voi-controls" v-if="modelLoaded">
          <h4>VOI选择</h4>
          <el-button :type="selectionBoxVisible ? 'warning' : 'primary'" size="small" @click="toggleSelectionBox">{{ selectionBoxVisible ? '隐藏选取框' : '显现选取框' }}</el-button>
          <el-button type="success" size="small" @click="confirmVOISelection" :disabled="!selectionBoxVisible">确认VOI选取</el-button>
          <el-button type="info" size="small" @click="resetSelectionBox" :disabled="!selectionBoxVisible">重置选择框</el-button>
        </div>

        <div class="model-info" v-if="modelLoaded">
          <h4>模型信息</h4>
          <div class="info-item"><label>顶点数:</label><span>{{ modelStats.vertexCount }}</span></div>
          <div class="info-item"><label>面片数:</label><span>{{ modelStats.faceCount }}</span></div>
          <div class="info-item"><label>长(X):</label><span>{{ modelStats.width }}</span></div>
          <div class="info-item"><label>高(Y):</label><span>{{ modelStats.height }}</span></div>
          <div class="info-item"><label>深(Z):</label><span>{{ modelStats.depth }}</span></div>
        </div>

        <div class="axes-legend">
          <h4>坐标轴</h4>
          <div class="axes-item"><span class="axes-x">■</span> X轴（红）— 正前方</div>
          <div class="axes-item"><span class="axes-y">■</span> Y轴（绿）— 正上方</div>
          <div class="axes-item"><span class="axes-z">■</span> Z轴（蓝）— 正左方</div>
        </div>
      </div>
    </div>

    <div v-if="selectedBounds" class="selection-info-panel">
      <div class="info-panel">
        <div class="panel-header"><h4>已选择区域信息</h4></div>
        <div class="panel-content">
          <div class="bounds-item"><label>X范围:</label><span>{{ selectedBounds.xMin.toFixed(2) }} - {{ selectedBounds.xMax.toFixed(2) }}</span></div>
          <div class="bounds-item"><label>Y范围:</label><span>{{ selectedBounds.yMin.toFixed(2) }} - {{ selectedBounds.yMax.toFixed(2) }}</span></div>
          <div class="bounds-item"><label>Z范围:</label><span>{{ selectedBounds.zMin.toFixed(2) }} - {{ selectedBounds.zMax.toFixed(2) }}</span></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls'
import { mergeVertices } from 'three/examples/jsm/utils/BufferGeometryUtils'
import vtkXMLPolyDataReader from '@kitware/vtk.js/IO/XML/XMLPolyDataReader'
import { get3DVtkData, confirmVOISelection as apiConfirmVOI } from '@/api/hole-analysis'

class SelectionBox3D {
  constructor(scene, camera, renderer, controls) {
    this.scene = scene
    this.camera = camera
    this.renderer = renderer
    this.controls = controls
    this.isActive = false
    this.isDragging = false
    this.dragType = null
    this.highlightedObject = null
    this.dragStartMin = new THREE.Vector3()
    this.dragStartMax = new THREE.Vector3()
    this.dragStartPoint = new THREE.Vector3()
    this.dragStartVertexPosition = new THREE.Vector3()
    this.min = new THREE.Vector3(-1, -1, -1)
    this.max = new THREE.Vector3(1, 1, 1)
    this.center = new THREE.Vector3()
    this.size = new THREE.Vector3(2, 2, 2)
    this.createBox()
    this.createControlPoints()
    this.setupEventListeners()
  }

  createBox() {
    const geometry = new THREE.BoxGeometry(this.size.x, this.size.y, this.size.z)
    const edges = new THREE.EdgesGeometry(geometry)
    this.box = new THREE.LineSegments(edges, new THREE.LineBasicMaterial({ color: 0xff0000 }))
    this.box.position.copy(this.center)
    this.box.name = 'selection_box'
    this.scene.add(this.box)
  }

  createControlPoints() {
    this.controlPoints = []
    const vertexGeometry = new THREE.SphereGeometry(3.0, 12, 12)
    const vertexMaterial = new THREE.MeshBasicMaterial({ color: 0xffff00 })
    for (let i = 0; i < 8; i++) {
      const point = new THREE.Mesh(vertexGeometry, vertexMaterial.clone())
      point.name = `control_point_${i}`
      this.controlPoints.push(point)
      this.scene.add(point)
    }
    this.updateControlPoints()
  }

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
    vertices.forEach((vertex, index) => {
      this.controlPoints[index].position.copy(vertex)
    })
    this.updateBox()
  }

  updateBox() {
    this.center.set(
      (this.min.x + this.max.x) * 0.5,
      (this.min.y + this.max.y) * 0.5,
      (this.min.z + this.max.z) * 0.5
    )
    this.size.set(
      this.max.x - this.min.x,
      this.max.y - this.min.y,
      this.max.z - this.min.z
    )
    this.box.geometry.dispose()
    const geometry = new THREE.BoxGeometry(this.size.x, this.size.y, this.size.z)
    const edges = new THREE.EdgesGeometry(geometry)
    this.box.geometry = edges
    this.box.position.copy(this.center)
  }

  setupEventListeners() {
    const canvas = this.renderer.domElement
    this._onMouseDown = this.onMouseDown.bind(this)
    this._onMouseMove = this.onMouseMove.bind(this)
    this._onMouseUp = this.onMouseUp.bind(this)
    this._onMouseEnter = this.onMouseEnter.bind(this)
    this._onMouseLeave = this.onMouseLeave.bind(this)
    canvas.addEventListener('mousedown', this._onMouseDown, true)
    canvas.addEventListener('mousemove', this._onMouseMove, true)
    canvas.addEventListener('mouseup', this._onMouseUp, true)
    canvas.addEventListener('mouseenter', this._onMouseEnter, true)
    canvas.addEventListener('mouseleave', this._onMouseLeave, true)
  }

  onMouseDown(event) {
    if (!this.isActive) return
    const intersects = this.getIntersects(event)
    if (intersects.length > 0) {
      if (this.controls) this.controls.enabled = false
      event.stopPropagation()
      event.preventDefault()
      event.stopImmediatePropagation()
      this.isDragging = true
      const object = intersects[0].object
      this.dragStartMin.copy(this.min)
      this.dragStartMax.copy(this.max)
      if (intersects[0].point) this.dragStartPoint.copy(intersects[0].point)
      if (object.name && object.name.startsWith('control_point_')) {
        this.dragType = 'vertex'
        this.dragIndex = parseInt(object.name.split('_')[2])
        this.dragStartVertexPosition.copy(this.controlPoints[this.dragIndex].position)
      } else if (object.name === 'selection_box') {
        this.dragType = 'face'
      }
      this.startDragFeedback()
      const canvas = this.renderer.domElement
      canvas.style.userSelect = 'none'
      canvas.style.cursor = 'grabbing'
    }
  }

  onMouseMove(event) {
    if (!this.isActive) return
    if (!this.isDragging) {
      this.updateCursor(event)
      return
    }
    const intersects = this.getIntersects(event, true)
    if (intersects.length > 0) {
      const point = intersects[0].point
      if (this.dragType === 'vertex') {
        this.handleVertexDrag(point)
      } else if (this.dragType === 'face') {
        this.handleFaceDrag(point)
      }
    }
    event.stopPropagation()
    event.preventDefault()
    event.stopImmediatePropagation()
  }

  onMouseUp(event) {
    if (!this.isDragging) return
    this.isDragging = false
    this.dragType = null
    this.dragIndex = null
    this.endDragFeedback()
    if (this.controls) this.controls.enabled = true
    const canvas = this.renderer.domElement
    canvas.style.userSelect = ''
    canvas.style.cursor = 'default'
    event.stopPropagation()
    event.preventDefault()
    event.stopImmediatePropagation()
  }

  onMouseEnter(event) {
    if (!this.isActive) return
    this.updateCursor(event)
  }

  onMouseLeave(event) {
    this.renderer.domElement.style.cursor = 'default'
  }

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

  highlightControlPoint(point) {
    this.clearHighlights()
    point.material.color.set(0xffff00)
    this.highlightedObject = point
  }

  highlightSelectionBox() {
    this.clearHighlights()
    this.box.material.color.set(0xffff00)
    this.highlightedObject = this.box
  }

  clearHighlights() {
    if (this.highlightedObject) {
      if (this.highlightedObject.name && this.highlightedObject.name.startsWith('control_point_')) {
        this.highlightedObject.material.color.set(0xffff00)
      } else if (this.highlightedObject.name === 'selection_box') {
        this.highlightedObject.material.color.set(0xff0000)
      }
      this.highlightedObject = null
    }
  }

  startDragFeedback() {
    if (this.dragType === 'vertex') {
      this.controlPoints[this.dragIndex].scale.set(1.5, 1.5, 1.5)
    } else if (this.dragType === 'face') {
      this.box.material.opacity = 0.8
    }
  }

  endDragFeedback() {
    if (this.dragType === 'vertex') {
      this.controlPoints[this.dragIndex].scale.set(1, 1, 1)
    } else if (this.dragType === 'face') {
      this.box.material.opacity = 1.0
    }
    this.clearHighlights()
  }

  handleVertexDrag(point) {
    const vertexIndex = this.dragIndex
    const oppositeVertexMap = [6, 7, 4, 5, 2, 3, 0, 1]
    const oppositeIndex = oppositeVertexMap[vertexIndex]
    const initialVertexPositions = [
      new THREE.Vector3(this.dragStartMin.x, this.dragStartMin.y, this.dragStartMin.z),
      new THREE.Vector3(this.dragStartMax.x, this.dragStartMin.y, this.dragStartMin.z),
      new THREE.Vector3(this.dragStartMax.x, this.dragStartMax.y, this.dragStartMin.z),
      new THREE.Vector3(this.dragStartMin.x, this.dragStartMax.y, this.dragStartMin.z),
      new THREE.Vector3(this.dragStartMin.x, this.dragStartMin.y, this.dragStartMax.z),
      new THREE.Vector3(this.dragStartMax.x, this.dragStartMin.y, this.dragStartMax.z),
      new THREE.Vector3(this.dragStartMax.x, this.dragStartMax.y, this.dragStartMax.z),
      new THREE.Vector3(this.dragStartMin.x, this.dragStartMax.y, this.dragStartMax.z)
    ]
    const oppositePos = initialVertexPositions[oppositeIndex]
    const newMin = new THREE.Vector3(
      Math.min(point.x, oppositePos.x),
      Math.min(point.y, oppositePos.y),
      Math.min(point.z, oppositePos.z)
    )
    const newMax = new THREE.Vector3(
      Math.max(point.x, oppositePos.x),
      Math.max(point.y, oppositePos.y),
      Math.max(point.z, oppositePos.z)
    )
    const minSize = 1.0
    if (newMax.x - newMin.x < minSize || newMax.y - newMin.y < minSize || newMax.z - newMin.z < minSize) {
      this.min.copy(this.dragStartMin)
      this.max.copy(this.dragStartMax)
      return
    }
    this.min.copy(newMin)
    this.max.copy(newMax)
    this.updateControlPoints()
  }

  handleFaceDrag(point) {
    const startCenter = new THREE.Vector3(
      (this.dragStartMin.x + this.dragStartMax.x) * 0.5,
      (this.dragStartMin.y + this.dragStartMax.y) * 0.5,
      (this.dragStartMin.z + this.dragStartMax.z) * 0.5
    )
    const delta = new THREE.Vector3(
      point.x - startCenter.x,
      point.y - startCenter.y,
      point.z - startCenter.z
    )
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
    const boundsLimit = 1000
    if (Math.abs(this.min.x) > boundsLimit || Math.abs(this.max.x) > boundsLimit ||
        Math.abs(this.min.y) > boundsLimit || Math.abs(this.max.y) > boundsLimit ||
        Math.abs(this.min.z) > boundsLimit || Math.abs(this.max.z) > boundsLimit) {
      this.min.set(this.dragStartMin.x, this.dragStartMin.y, this.dragStartMin.z)
      this.max.set(this.dragStartMax.x, this.dragStartMax.y, this.dragStartMax.z)
      return
    }
    this.updateControlPoints()
  }

  getIntersects(event, usePlane = false) {
    const mouse = new THREE.Vector2()
    const rect = this.renderer.domElement.getBoundingClientRect()
    mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1
    mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1
    const raycaster = new THREE.Raycaster()
    raycaster.setFromCamera(mouse, this.camera)
    if (usePlane) {
      const cameraDirection = new THREE.Vector3()
      this.camera.getWorldDirection(cameraDirection)
      let planePoint
      if (this.dragType === 'vertex' && this.dragStartVertexPosition) {
        planePoint = this.dragStartVertexPosition
      } else {
        planePoint = this.center
      }
      const plane = new THREE.Plane()
      plane.setFromNormalAndCoplanarPoint(cameraDirection.negate(), planePoint)
      const intersectPoint = new THREE.Vector3()
      const intersected = raycaster.ray.intersectPlane(plane, intersectPoint)
      return intersected ? [{ point: intersectPoint }] : []
    }
    const objects = [...this.controlPoints, this.box]
    return raycaster.intersectObjects(objects)
  }

  setActive(active) {
    this.isActive = active
    this.box.visible = active
    this.controlPoints.forEach(point => { point.visible = active })
  }

  setInitialBounds(modelBoundingBox) {
    const modelSize = new THREE.Vector3()
    modelBoundingBox.getSize(modelSize)
    const halfSize = modelSize.clone().multiplyScalar(0.5)
    const center = new THREE.Vector3()
    modelBoundingBox.getCenter(center)
    this.min.copy(center).sub(halfSize.multiplyScalar(0.5))
    this.max.copy(center).add(halfSize.multiplyScalar(0.5))
    this.updateControlPoints()
  }

  getSelectionBounds() {
    return {
      min: this.min.clone(),
      max: this.max.clone(),
      center: this.center.clone(),
      size: this.size.clone()
    }
  }

  dispose() {
    const canvas = this.renderer.domElement
    canvas.removeEventListener('mousedown', this._onMouseDown, true)
    canvas.removeEventListener('mousemove', this._onMouseMove, true)
    canvas.removeEventListener('mouseup', this._onMouseUp, true)
    canvas.removeEventListener('mouseenter', this._onMouseEnter, true)
    canvas.removeEventListener('mouseleave', this._onMouseLeave, true)
    this.scene.remove(this.box)
    this.box.geometry.dispose()
    this.box.material.dispose()
    this.controlPoints.forEach(point => {
      this.scene.remove(point)
      point.geometry.dispose()
      point.material.dispose()
    })
  }
}

export default {
  name: 'VtkMedicalViewer',
  props: {
    projectId: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      threeRenderer: null,
      scene: null,
      camera: null,
      controls: null,
      animFrameId: null,
      modelMesh: null,
      loading: false,
      loadingText: '正在加载3D模型...',
      modelLoaded: false,
      showWireframe: false,
      selectionBoxVisible: false,
      selectedBounds: null,
      selectionBox: null,
      modelStats: { vertexCount: 0, faceCount: 0, width: 0, height: 0, depth: 0 },
      modelBounds: { xMin: 0, xMax: 0, yMin: 0, yMax: 0, zMin: 0, zMax: 0 }
    }
  },
  mounted() {
    this.$nextTick(() => {
      this.initThreeRenderer()
    })
  },
  beforeDestroy() {
    if (this.animFrameId) {
      cancelAnimationFrame(this.animFrameId)
    }
    if (this.selectionBox) {
      this.selectionBox.dispose()
    }
    if (this.controls) {
      this.controls.dispose()
    }
    if (this.threeRenderer) {
      this.threeRenderer.dispose()
    }
  },
  methods: {
    initThreeRenderer() {
      const container = this.$refs.renderContainer
      if (!container) {
        console.error('渲染容器未找到')
        return
      }

      const width = container.offsetWidth
      const height = container.offsetHeight
      console.log('Three.js渲染器初始化，容器尺寸:', width, 'x', height)

      this.scene = new THREE.Scene()
      this.scene.background = new THREE.Color(0xffffff)

      this.camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100000)
      this.camera.position.set(0, 0, 1000)

      this.threeRenderer = new THREE.WebGLRenderer({ antialias: true })
      this.threeRenderer.setSize(width, height)
      this.threeRenderer.setPixelRatio(window.devicePixelRatio)
      container.appendChild(this.threeRenderer.domElement)

      // 纯环境光，避免方向光在透明模型上产生白色高光
      const ambientLight = new THREE.AmbientLight(0xffffff, 1.0)
      this.scene.add(ambientLight)

      this.controls = new OrbitControls(this.camera, this.threeRenderer.domElement)
      this.controls.enableDamping = true
      this.controls.dampingFactor = 0.05

      // 添加坐标轴辅助（长度500，模型加载后会更新）
      this.axesHelper = new THREE.AxesHelper(500)
      this.scene.add(this.axesHelper)

      this.animate()
      console.log('Three.js渲染器初始化完成')
    },

    animate() {
      this.animFrameId = requestAnimationFrame(this.animate)
      if (this.controls) this.controls.update()
      if (this.threeRenderer && this.scene && this.camera) {
        this.threeRenderer.render(this.scene, this.camera)
      }
    },

    async load3DModelData() {
      try {
        this.loading = true
        this.loadingText = '正在请求3D模型数据...'

        const response = await get3DVtkData(this.projectId)

        if (response.status === 200) {
          this.loadingText = '正在解析VTP文件...'
          await this.loadVTPFromBlob(response.data)
          this.modelLoaded = true
          this.$emit('model-rendered')
          this.$message.success('3D模型加载成功')
          return true
        } else {
          throw new Error('获取3D模型数据失败')
        }
      } catch (error) {
        console.error('加载3D模型失败:', error)
        this.$message.error('加载3D模型失败: ' + error.message)
        return false
      } finally {
        this.loading = false
      }
    },

    loadVTPFromBlob(blobData) {
      return new Promise((resolve, reject) => {
        const fileReader = new FileReader()

        fileReader.onload = (e) => {
          try {
            const arrayBuffer = e.target.result
            console.log('ArrayBuffer大小:', arrayBuffer.byteLength, 'bytes')

            const reader = vtkXMLPolyDataReader.newInstance()
            reader.parseAsArrayBuffer(arrayBuffer)
            const polyData = reader.getOutputData(0)

            if (!polyData || polyData.getNumberOfPoints() === 0) {
              throw new Error('VTP数据无效或顶点数为0')
            }

            const nPoints = polyData.getNumberOfPoints()
            const nPolys = polyData.getNumberOfPolys ? polyData.getNumberOfPolys() : 0
            console.log(`解析成功: 顶点=${nPoints}, 面=${nPolys}`)

            this.modelStats.vertexCount = nPoints
            this.modelStats.faceCount = nPolys

            const geometry = this.vtpToThreeGeometry(polyData)

            if (this.modelMesh) {
              this.scene.remove(this.modelMesh)
              this.modelMesh.geometry.dispose()
              this.modelMesh.material.dispose()
            }

            const material = new THREE.MeshLambertMaterial({
              color: 0x4488cc,
              side: THREE.FrontSide,
              transparent: true,
              opacity: 0.4,
              depthWrite: false
            })

            this.modelMesh = new THREE.Mesh(geometry, material)
            // X轴方向压缩为0.5倍
            this.modelMesh.scale.set(0.5, 1, 1)
            this.scene.add(this.modelMesh)

            geometry.computeBoundingBox()
            const box = geometry.boundingBox
            const center = new THREE.Vector3(
              (box.min.x + box.max.x) * 0.5 * 0.5,
              (box.min.y + box.max.y) * 0.5,
              (box.min.z + box.max.z) * 0.5
            )
            const size = new THREE.Vector3(
              (box.max.x - box.min.x) * 0.5,
              box.max.y - box.min.y,
              box.max.z - box.min.z
            )
            const maxDim = Math.max(size.x, size.y, size.z)

            this.modelBounds = {
              xMin: box.min.x, xMax: box.max.x,
              yMin: box.min.y, yMax: box.max.y,
              zMin: box.min.z, zMax: box.max.z
            }
            this.modelStats.width = (box.max.x - box.min.x).toFixed(1)
            this.modelStats.height = (box.max.y - box.min.y).toFixed(1)
            this.modelStats.depth = (box.max.z - box.min.z).toFixed(1)

            // X轴朝正前方(-Z方向)，Y轴朝正上方，Z轴朝正左方(-X方向)
            // 相机从X轴正方向看向模型中心（即从前方看）
            this.controls.target.copy(center)
            this.camera.position.set(
              center.x + maxDim * 2,
              center.y,
              center.z
            )
            this.camera.up.set(0, 1, 0)
            this.camera.near = maxDim * 0.001
            this.camera.far = maxDim * 10
            this.camera.updateProjectionMatrix()
            this.controls.update()

            // 更新坐标轴大小
            if (this.axesHelper) {
              this.scene.remove(this.axesHelper)
              this.axesHelper = new THREE.AxesHelper(maxDim * 0.5)
              this.axesHelper.position.copy(center)
              this.scene.add(this.axesHelper)
            }

            console.log('模型加载完成，中心:', center, '最大尺寸:', maxDim)
            resolve(true)
          } catch (err) {
            console.error('VTP解析失败:', err)
            reject(err)
          }
        }

        fileReader.onerror = () => reject(new Error('文件读取失败'))
        fileReader.readAsArrayBuffer(blobData)
      })
    },

    vtpToThreeGeometry(polyData) {
      const geometry = new THREE.BufferGeometry()

      const vtkPoints = polyData.getPoints()
      const pointsData = vtkPoints.getData()
      geometry.setAttribute('position', new THREE.BufferAttribute(new Float32Array(pointsData), 3))

      const polys = polyData.getPolys()
      if (polys && polys.getNumberOfCells() > 0) {
        const polysData = polys.getData()
        const indices = []
        let i = 0
        while (i < polysData.length) {
          const n = polysData[i]
          i++
          if (n === 3) {
            indices.push(polysData[i], polysData[i + 1], polysData[i + 2])
          } else if (n === 4) {
            indices.push(polysData[i], polysData[i + 1], polysData[i + 2])
            indices.push(polysData[i], polysData[i + 2], polysData[i + 3])
          }
          i += n
        }
        geometry.setIndex(indices)
      }

      geometry.computeVertexNormals()
      // 合并重复顶点，使法线平滑
      const merged = mergeVertices(geometry)
      merged.computeVertexNormals()
      return merged
    },

    resetCamera() {
      if (!this.modelMesh || !this.camera || !this.controls) return
      const box = new THREE.Box3().setFromObject(this.modelMesh)
      const center = new THREE.Vector3()
      box.getCenter(center)
      const size = new THREE.Vector3()
      box.getSize(size)
      const maxDim = Math.max(size.x, size.y, size.z)
      this.controls.target.copy(center)
      this.camera.position.set(center.x, center.y, center.z + maxDim * 1.5)
      this.camera.updateProjectionMatrix()
      this.controls.update()
    },

    toggleWireframe() {
      this.showWireframe = !this.showWireframe
      if (this.modelMesh) {
        this.modelMesh.material.wireframe = this.showWireframe
      }
    },

    toggleSelectionBox() {
      if (!this.selectionBox) {
        this.selectionBox = new SelectionBox3D(this.scene, this.camera, this.threeRenderer, this.controls)
        const bbox = new THREE.Box3().setFromObject(this.modelMesh)
        this.selectionBox.setInitialBounds(bbox)
      }
      this.selectionBoxVisible = !this.selectionBoxVisible
      this.selectionBox.setActive(this.selectionBoxVisible)
    },

    async confirmVOISelection() {
      if (!this.selectionBoxVisible || !this.selectionBox) return
      const bounds = this.selectionBox.getSelectionBounds()

      // modelBounds 是 geometry 原始包围盒（scale前），最大值即原始数据尺寸
      const totalSlices = this.modelBounds.xMax  // Three.js X对应切片索引
      const imageHeight = this.modelBounds.yMax  // Three.js Y对应图像行
      const imageWidth  = this.modelBounds.zMax  // Three.js Z对应图像列

      // X轴×2还原0.5缩放，Y/Z直接使用世界坐标
      const pixelBounds = {
        z_min: Math.round(bounds.min.x * 2),
        z_max: Math.round(bounds.max.x * 2),
        y_min: Math.round(bounds.min.y),
        y_max: Math.round(bounds.max.y),
        x_min: Math.round(bounds.min.z),
        x_max: Math.round(bounds.max.z)
      }
      console.log('modelBounds:', JSON.stringify(this.modelBounds))
      console.log('bounds(世界坐标):', JSON.stringify({ min: bounds.min, max: bounds.max }))
      console.log('pixelBounds(发给后端):', JSON.stringify(pixelBounds))
      this.selectedBounds = {
        xMin: pixelBounds.x_min, xMax: pixelBounds.x_max,
        yMin: pixelBounds.y_min, yMax: pixelBounds.y_max,
        zMin: pixelBounds.z_min, zMax: pixelBounds.z_max
      }
      try {
        const response = await apiConfirmVOI(this.projectId, pixelBounds)
        this.selectionBoxVisible = false
        this.selectionBox.setActive(false)
        this.$emit('selection-completed', this.selectedBounds)
        const msg = response.data && response.data.message ? response.data.message : 'VOI区域数据保存成功'
        this.$message.success(msg)
      } catch (error) {
        console.error('确认VOI选取失败:', error)
        this.$message.error('确认VOI选取失败: ' + error.message)
      }
    },

    resetSelectionBox() {
      if (!this.selectionBox || !this.modelMesh) return
      const bbox = new THREE.Box3().setFromObject(this.modelMesh)
      this.selectionBox.setInitialBounds(bbox)
      this.$message.info('选择框已重置')
    }
  }
}
</script>

<style scoped>
.vtk-medical-viewer {
  display: flex;
  height: 600px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.main-content {
  flex: 1;
  position: relative;
}

.vtk-render-container {
  width: 100%;
  height: 100%;
}

.loading-overlay {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loading-spinner {
  text-align: center;
  color: white;
}

.loading-spinner i {
  font-size: 24px;
  margin-bottom: 10px;
}

.loading-spinner span {
  display: block;
  font-size: 16px;
}

.interaction-controls {
  width: 260px;
  background: #f5f7fa;
  border-left: 1px solid #e0e0e0;
  padding: 15px;
  overflow-y: auto;
}

.control-panel h3 {
  margin-top: 0;
  color: #303133;
  border-bottom: 1px solid #e0e0e0;
  padding-bottom: 10px;
}

.view-controls {
  margin-bottom: 20px;
}

.voi-controls,
.model-info,
.axes-legend {
  margin-bottom: 20px;
  padding: 15px;
  background: white;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
}

.voi-controls h4,
.model-info h4,
.axes-legend h4 {
  margin-top: 0;
  color: #606266;
}

.axes-item {
  font-size: 13px;
  margin-bottom: 4px;
  color: #303133;
}

.axes-x { color: #ff3333; font-size: 16px; }
.axes-y { color: #33cc33; font-size: 16px; }
.axes-z { color: #3399ff; font-size: 16px; }

.info-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
  font-size: 14px;
}

.info-item label {
  font-weight: bold;
  color: #606266;
}

.selection-info-panel {
  position: absolute;
  top: 10px;
  right: 280px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 10px;
}

.panel-header h4 {
  margin: 0 0 8px 0;
  color: #303133;
}

.bounds-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
  font-size: 12px;
}

.bounds-item label {
  font-weight: bold;
  color: #606266;
  margin-right: 8px;
}
</style>
