<template>
  <div class="step4-viewer">
    <div class="viewer-main">
      <div ref="renderContainer" class="vtk-render-container" />
      <div v-if="loading" class="loading-overlay">
        <div class="loading-spinner">
          <i class="el-icon-loading" />
          <span>{{ loadingText }}</span>
        </div>
      </div>
    </div>

    <div class="viewer-controls">
      <div class="control-panel">
        <h3>3D孔洞预览</h3>
        <div class="view-controls">
          <el-button-group>
            <el-button size="small" title="重置视角" @click="resetCamera">
              <i class="el-icon-refresh" /> 重置视角
            </el-button>
            <el-button size="small" :type="showWireframe ? 'primary' : 'default'" title="线框/实体模式" @click="toggleWireframe">
              线框模式
            </el-button>
          </el-button-group>
        </div>

        <div v-if="modelLoaded" class="model-info">
          <h4>模型信息</h4>
          <div class="info-item"><label>顶点数:</label><span>{{ modelStats.vertexCount }}</span></div>
          <div class="info-item"><label>面片数:</label><span>{{ modelStats.faceCount }}</span></div>
          <div class="info-item"><label>X尺寸:</label><span>{{ modelStats.width }}</span></div>
          <div class="info-item"><label>Y尺寸:</label><span>{{ modelStats.height }}</span></div>
          <div class="info-item"><label>Z尺寸:</label><span>{{ modelStats.depth }}</span></div>
        </div>

        <div class="axes-legend">
          <h4>坐标轴</h4>
          <div class="axes-item"><span class="axes-x">■</span> X轴（红）</div>
          <div class="axes-item"><span class="axes-y">■</span> Y轴（绿）</div>
          <div class="axes-item"><span class="axes-z">■</span> Z轴（蓝）</div>
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

export default {
  name: 'Step4Viewer',
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
      modelStats: { vertexCount: 0, faceCount: 0, width: '0', height: '0', depth: '0' },
      axesHelper: null
    }
  },
  mounted() {
    this.$nextTick(() => {
      this.initThreeRenderer()
    })
  },
  beforeDestroy() {
    if (this.animFrameId) cancelAnimationFrame(this.animFrameId)
    if (this.controls) this.controls.dispose()
    if (this.threeRenderer) this.threeRenderer.dispose()
  },
  methods: {
    initThreeRenderer() {
      const container = this.$refs.renderContainer
      if (!container) return
      const width = container.offsetWidth || 800
      const height = container.offsetHeight || 500

      this.scene = new THREE.Scene()
      // 深海军蓝背景：科学可视化行业标准，与暖色模型形成强对比
      // 冷白色背景：纯净科研风格，与深蓝模型形成鲜明对比
      this.scene.background = new THREE.Color(0xf5f7fa)

      this.camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100000)
      this.camera.position.set(0, 0, 1000)

      this.threeRenderer = new THREE.WebGLRenderer({ antialias: true })
      this.threeRenderer.setSize(width, height)
      this.threeRenderer.setPixelRatio(window.devicePixelRatio)
      // sRGB 色彩空间，颜色更准确
      if (THREE.SRGBColorSpace !== undefined) {
        this.threeRenderer.outputColorSpace = THREE.SRGBColorSpace
      }
      container.appendChild(this.threeRenderer.domElement)

      // 多光源配置：亮色背景需要适度调低主光，避免模型过曝
      // 环境光（明亮填充，亮背景下需要更强环境光保证阴影面不过暗）
      const ambientLight = new THREE.AmbientLight(0xffffff, 0.5)
      this.scene.add(ambientLight)

      // 主方向光：右上前方，适度强度，产生清晰阴影与高光
      const dirLight1 = new THREE.DirectionalLight(0xffffff, 0.75)
      dirLight1.position.set(1.5, 2.0, 1.5)
      this.scene.add(dirLight1)

      // 补光：左下后方，冷蓝色，防止背面全黑，增加层次感
      const dirLight2 = new THREE.DirectionalLight(0x8899dd, 0.3)
      dirLight2.position.set(-1.5, -0.5, -1.0)
      this.scene.add(dirLight2)

      this.controls = new OrbitControls(this.camera, this.threeRenderer.domElement)
      this.controls.enableDamping = true
      this.controls.dampingFactor = 0.05

      this.axesHelper = new THREE.AxesHelper(500)
      this.scene.add(this.axesHelper)

      this.animate()
    },

    animate() {
      this.animFrameId = requestAnimationFrame(this.animate)
      if (this.controls) this.controls.update()
      if (this.threeRenderer && this.scene && this.camera) {
        this.threeRenderer.render(this.scene, this.camera)
      }
    },

    async loadFromBlob(blob) {
      try {
        this.loading = true
        this.loadingText = '正在解析VTP文件...'
        await this.loadVTPFromBlob(blob)
        this.modelLoaded = true
        this.$emit('loaded')
        this.$message.success('3D孔洞模型加载成功')
      } catch (error) {
        console.error('加载3D模型失败:', error)
        this.$message.error('加载3D模型失败: ' + error.message)
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
            console.log('[Step4Viewer] ArrayBuffer大小:', arrayBuffer.byteLength, 'bytes')

            const reader = vtkXMLPolyDataReader.newInstance()
            reader.parseAsArrayBuffer(arrayBuffer)
            const polyData = reader.getOutputData(0)

            if (!polyData || polyData.getNumberOfPoints() === 0) {
              throw new Error('VTP数据无效或顶点数为0')
            }

            const nPoints = polyData.getNumberOfPoints()
            const nPolys = polyData.getNumberOfPolys ? polyData.getNumberOfPolys() : 0
            console.log(`[Step4Viewer] 解析成功: 顶点=${nPoints}, 面=${nPolys}`)

            this.modelStats.vertexCount = nPoints
            this.modelStats.faceCount = nPolys

            const geometry = this.vtpToThreeGeometry(polyData)

            if (this.modelMesh) {
              this.scene.remove(this.modelMesh)
              this.modelMesh.geometry.dispose()
              this.modelMesh.material.dispose()
            }

            const material = new THREE.MeshPhongMaterial({
              // 深蓝色：亮白背景下高辨识度，工程蓝科研感强，与背景形成鲜明对比
              color: 0x1565c0,
              // 关闭自发光：亮色背景下自发光会导致暗面色彩失真
              emissive: new THREE.Color(0x000000),
              // 深灰镜面高光：避免白色高光在白色背景中消失，深灰高光轮廓更清晰
              specular: new THREE.Color(0x333333),
              // 适中光泽度
              shininess: 50,
              // 双面渲染：孔洞内部表面也能被看到，对展示腔体结构至关重要
              side: THREE.DoubleSide,
              transparent: true,
              // 0.85 透明度：大部分不透明保持清晰度，轻微透明可看到重叠孔洞
              opacity: 0.85,
              depthWrite: true
            })

            this.modelMesh = new THREE.Mesh(geometry, material)
            this.scene.add(this.modelMesh)

            geometry.computeBoundingBox()
            const box = geometry.boundingBox
            const center = new THREE.Vector3(
              (box.min.x + box.max.x) * 0.5,
              (box.min.y + box.max.y) * 0.5,
              (box.min.z + box.max.z) * 0.5
            )
            const size = new THREE.Vector3(
              box.max.x - box.min.x,
              box.max.y - box.min.y,
              box.max.z - box.min.z
            )
            const maxDim = Math.max(size.x, size.y, size.z)

            this.modelStats.width = (box.max.x - box.min.x).toFixed(1)
            this.modelStats.height = (box.max.y - box.min.y).toFixed(1)
            this.modelStats.depth = (box.max.z - box.min.z).toFixed(1)

            this.controls.target.copy(center)
            this.camera.position.set(center.x + maxDim * 2, center.y, center.z)
            this.camera.up.set(0, 1, 0)
            this.camera.near = maxDim * 0.001
            this.camera.far = maxDim * 10
            this.camera.updateProjectionMatrix()
            this.controls.update()

            if (this.axesHelper) {
              this.scene.remove(this.axesHelper)
              this.axesHelper = new THREE.AxesHelper(maxDim * 0.5)
              this.axesHelper.position.copy(center)
              this.scene.add(this.axesHelper)
            }

            console.log('[Step4Viewer] 模型加载完成，中心:', center, '最大尺寸:', maxDim)
            resolve(true)
          } catch (err) {
            console.error('[Step4Viewer] VTP解析失败:', err)
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
      this.camera.position.set(center.x + maxDim * 2, center.y, center.z)
      this.camera.updateProjectionMatrix()
      this.controls.update()
    },

    toggleWireframe() {
      this.showWireframe = !this.showWireframe
      if (this.modelMesh) {
        this.modelMesh.material.wireframe = this.showWireframe
      }
    }
  }
}
</script>

<style scoped>
.step4-viewer {
  display: flex;
  height: 100%;
  min-height: 500px;
  border: 1px solid #d0d7e3;
  border-radius: 4px;
  overflow: hidden;
}

.viewer-main {
  flex: 1;
  position: relative;
  min-width: 0;
  background: #f5f7fa;
}

.vtk-render-container {
  width: 100%;
  height: 100%;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(245, 247, 250, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loading-spinner {
  text-align: center;
  color: #1565c0;
}

.loading-spinner i {
  font-size: 28px;
  margin-bottom: 10px;
  display: block;
}

.loading-spinner span {
  display: block;
  font-size: 15px;
  color: #4a6080;
}

.viewer-controls {
  width: 220px;
  background: #eef1f7;
  border-left: 1px solid #d0d7e3;
  padding: 12px;
  overflow-y: auto;
  flex-shrink: 0;
}

.control-panel h3 {
  margin-top: 0;
  color: #1565c0;
  border-bottom: 1px solid #d0d7e3;
  padding-bottom: 8px;
  font-size: 14px;
}

.view-controls {
  margin-bottom: 16px;
}

.model-info,
.axes-legend {
  margin-bottom: 16px;
  padding: 10px;
  background: #ffffff;
  border-radius: 4px;
  border: 1px solid #d0d7e3;
}

.model-info h4,
.axes-legend h4 {
  margin-top: 0;
  margin-bottom: 8px;
  color: #4a6080;
  font-size: 13px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
  font-size: 12px;
}

.info-item label {
  font-weight: bold;
  color: #4a6080;
}

.info-item span {
  color: #1e2d45;
}

.axes-item {
  font-size: 12px;
  margin-bottom: 3px;
  color: #1e2d45;
}

.axes-x { color: #ff5555; font-size: 14px; }
.axes-y { color: #22aa22; font-size: 14px; }
.axes-z { color: #1565c0; font-size: 14px; }
</style>
