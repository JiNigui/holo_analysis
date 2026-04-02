<template>
  <div ref="container" class="hole-cut-viewer-3d" />
</template>

<script>
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls'
import { mergeVertices } from 'three/examples/jsm/utils/BufferGeometryUtils'
import vtkXMLPolyDataReader from '@kitware/vtk.js/IO/XML/XMLPolyDataReader'
import { getVoiSurface, getCutPlaneParams } from '@/api/hole-analysis'

export default {
  name: 'HoleCutViewer3D',
  props: {
    projectId: {
      type: Number,
      required: true
    },
    visible: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      renderer: null,
      scene: null,
      camera: null,
      controls: null,
      animFrameId: null,
      loading: false
    }
  },
  watch: {
    visible(val) {
      if (val) {
        this.$nextTick(() => this.init())
      } else {
        this.dispose()
      }
    }
  },
  mounted() {
    if (this.visible) {
      this.$nextTick(() => this.init())
    }
  },
  beforeDestroy() {
    this.dispose()
  },
  methods: {
    async init() {
      this.initThreeRenderer()
      this.loading = true
      try {
        const [blobRes, paramsRes] = await Promise.all([
          getVoiSurface(this.projectId),
          getCutPlaneParams(this.projectId)
        ])
        const blob = blobRes.data || blobRes
        const arrayBuffer = await blob.arrayBuffer()
        const geometry = this.vtpToThreeGeometry(arrayBuffer)
        const params = paramsRes.data || paramsRes
        this.buildScene(geometry, params.normal, params.origin)
        this.$emit('loaded')
      } catch (e) {
        console.error('[HoleCutViewer3D] 加载失败:', e)
        this.$message && this.$message.error('3D数据加载失败: ' + e.message)
        this.$emit('loaded')
      } finally {
        this.loading = false
      }
    },

    initThreeRenderer() {
      const container = this.$refs.container
      if (!container) return
      const width = container.clientWidth || 800
      const height = container.clientHeight || 600

      this.scene = new THREE.Scene()
      this.scene.background = new THREE.Color(0xf5f7fa)

      this.camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100000)
      this.camera.position.set(0, 0, 3000)

      this.renderer = new THREE.WebGLRenderer({ antialias: true })
      this.renderer.setSize(width, height)
      this.renderer.localClippingEnabled = true
      container.appendChild(this.renderer.domElement)

      this.controls = new OrbitControls(this.camera, this.renderer.domElement)
      this.controls.enableDamping = true

      const ambientLight = new THREE.AmbientLight(0xffffff, 0.5)
      this.scene.add(ambientLight)
      const dirLight = new THREE.DirectionalLight(0xffffff, 0.75)
      dirLight.position.set(1.5, 2.0, 1.5)
      this.scene.add(dirLight)
      const dirLight2 = new THREE.DirectionalLight(0x8899dd, 0.3)
      dirLight2.position.set(-1.5, -0.5, -1.0)
      this.scene.add(dirLight2)

      this.animate()
    },

    animate() {
      this.animFrameId = requestAnimationFrame(this.animate)
      if (this.controls) this.controls.update()
      if (this.renderer && this.scene && this.camera) {
        this.renderer.render(this.scene, this.camera)
      }
    },

    vtpToThreeGeometry(arrayBuffer) {
      const reader = vtkXMLPolyDataReader.newInstance()
      reader.parseAsArrayBuffer(arrayBuffer)
      const polyData = reader.getOutputData(0)

      const points = polyData.getPoints().getData()
      const polys = polyData.getPolys().getData()

      const positions = []
      const indices = []
      let i = 0
      while (i < polys.length) {
        const n = polys[i++]
        if (n === 3) {
          indices.push(polys[i], polys[i + 1], polys[i + 2])
        }
        i += n
      }
      for (let j = 0; j < points.length; j++) {
        positions.push(points[j])
      }

      const geometry = new THREE.BufferGeometry()
      geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3))
      geometry.setIndex(indices)
      const merged = mergeVertices(geometry)
      merged.computeVertexNormals()
      return merged
    },

    buildScene(geometry, normal, origin) {
      // 清除旧场景对象（保留灯光）
      const toRemove = this.scene.children.filter(c => c.isMesh || c.isLine || c.isSprite)
      toRemove.forEach(c => this.scene.remove(c))

      // x轴缩放0.5
      geometry.applyMatrix4(new THREE.Matrix4().makeScale(0.5, 1, 1))
      geometry.computeBoundingBox()
      const box = geometry.boundingBox
      const center = new THREE.Vector3()
      box.getCenter(center)
      const size = new THREE.Vector3()
      box.getSize(size)

      if (!normal || !origin) {
        const mat = new THREE.MeshPhongMaterial({
          color: 0x1565c0, specular: new THREE.Color(0x333333), shininess: 50,
          transparent: true, opacity: 0.85, side: THREE.DoubleSide
        })
        const mesh = new THREE.Mesh(geometry, mat)
        this.scene.add(mesh)
        this.addAxes(center, size)
        this.fitCamera(box)
        return
      }

      const planeNormal = new THREE.Vector3(...normal).normalize()
      // origin也要做x轴0.5缩放
      const planeOrigin = new THREE.Vector3(origin[0] * 0.5, origin[1], origin[2])
      const planeConstant = -planeNormal.dot(planeOrigin)

      // 间距：沿法向量方向各偏移 gapHalf
      const gapHalf = Math.max(size.x, size.y, size.z) * 0.20

      // 上半部分（法向量正方向偏移）
      const clipAbove = new THREE.Plane(planeNormal.clone(), planeConstant - gapHalf)
      const matAbove = new THREE.MeshPhongMaterial({
        color: 0x1565c0, specular: new THREE.Color(0x333333), shininess: 50,
        transparent: true, opacity: 0.85,
        side: THREE.DoubleSide, clippingPlanes: [clipAbove]
      })
      const meshAbove = new THREE.Mesh(geometry, matAbove)
      meshAbove.position.addScaledVector(planeNormal, gapHalf)
      this.scene.add(meshAbove)

      // 下半部分（法向量负方向偏移）
      const clipBelow = new THREE.Plane(planeNormal.clone().negate(), -planeConstant - gapHalf)
      const matBelow = new THREE.MeshPhongMaterial({
        color: 0xbf360c, specular: new THREE.Color(0x333333), shininess: 50,
        transparent: true, opacity: 0.85,
        side: THREE.DoubleSide, clippingPlanes: [clipBelow]
      })
      const meshBelow = new THREE.Mesh(geometry, matBelow)
      meshBelow.position.addScaledVector(planeNormal, -gapHalf)
      this.scene.add(meshBelow)

      // 切面辅助平面（半透明正方形）
      const planeSize = Math.max(size.x, size.y, size.z) * 2.0
      const planeGeo = new THREE.PlaneGeometry(planeSize, planeSize)
      const planeMat = new THREE.MeshBasicMaterial({
        color: 0x90caf9, transparent: true, opacity: 0.15, side: THREE.DoubleSide
      })
      const planeMesh = new THREE.Mesh(planeGeo, planeMat)
      planeMesh.position.copy(planeOrigin)
      planeMesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 0, 1), planeNormal)
      this.scene.add(planeMesh)

      // 正方形边框线
      const edgeGeo = new THREE.EdgesGeometry(planeGeo)
      const edgeMat = new THREE.LineBasicMaterial({ color: 0x1565c0, linewidth: 2 })
      const edgeLine = new THREE.LineSegments(edgeGeo, edgeMat)
      edgeLine.position.copy(planeOrigin)
      edgeLine.quaternion.copy(planeMesh.quaternion)
      this.scene.add(edgeLine)

      // 计算切面与模型的交线（孔洞截面轮廓）
      const contourLines = this.computeSliceContour(geometry, planeNormal, planeOrigin)
      if (contourLines) this.scene.add(contourLines)

      this.addAxes(center, size)
      this.fitCamera(box)
    },

    // 计算切面与模型三角面的交线段，生成截面轮廓
    computeSliceContour(geometry, planeNormal, planeOrigin) {
      const posAttr = geometry.attributes.position
      const index = geometry.index
      const segments = []
      const d = (v) => planeNormal.dot(v) - planeNormal.dot(planeOrigin)

      const vA = new THREE.Vector3()
      const vB = new THREE.Vector3()
      const vC = new THREE.Vector3()

      const interpEdge = (v0, v1, d0, d1) => {
        const t = d0 / (d0 - d1)
        return new THREE.Vector3().lerpVectors(v0, v1, t)
      }

      const count = index ? index.count : posAttr.count
      for (let i = 0; i < count; i += 3) {
        const ia = index ? index.getX(i) : i
        const ib = index ? index.getX(i + 1) : i + 1
        const ic = index ? index.getX(i + 2) : i + 2

        vA.fromBufferAttribute(posAttr, ia)
        vB.fromBufferAttribute(posAttr, ib)
        vC.fromBufferAttribute(posAttr, ic)

        const dA = d(vA), dB = d(vB), dC = d(vC)
        const pts = []

        if (dA * dB < 0) pts.push(interpEdge(vA, vB, dA, dB))
        if (dB * dC < 0) pts.push(interpEdge(vB, vC, dB, dC))
        if (dC * dA < 0) pts.push(interpEdge(vC, vA, dC, dA))

        if (pts.length === 2) {
          segments.push(pts[0], pts[1])
        }
      }

      if (segments.length === 0) return null

      const geo = new THREE.BufferGeometry().setFromPoints(segments)
      const mat = new THREE.LineBasicMaterial({ color: 0xff6d00, linewidth: 2 })
      return new THREE.LineSegments(geo, mat)
    },

    addAxes(center, size) {
      const axisLen = Math.max(size.x, size.y, size.z) * 0.6

      const makeAxis = (dir, color) => {
        const points = [center.clone(), center.clone().addScaledVector(dir, axisLen)]
        const geo = new THREE.BufferGeometry().setFromPoints(points)
        const mat = new THREE.LineBasicMaterial({ color, linewidth: 3 })
        return new THREE.Line(geo, mat)
      }

      // X轴红，Y轴绿，Z轴蓝
      this.scene.add(makeAxis(new THREE.Vector3(1, 0, 0), 0xff0000))
      this.scene.add(makeAxis(new THREE.Vector3(0, 1, 0), 0x00ff00))
      this.scene.add(makeAxis(new THREE.Vector3(0, 0, 1), 0x0000ff))

      // 坐标轴标签（用Sprite）
      const makeLabel = (text, pos, color) => {
        const canvas = document.createElement('canvas')
        canvas.width = 64; canvas.height = 64
        const ctx = canvas.getContext('2d')
        ctx.fillStyle = color
        ctx.font = 'bold 48px Arial'
        ctx.textAlign = 'center'
        ctx.textBaseline = 'middle'
        ctx.fillText(text, 32, 32)
        const tex = new THREE.CanvasTexture(canvas)
        const mat = new THREE.SpriteMaterial({ map: tex, depthTest: false })
        const sprite = new THREE.Sprite(mat)
        sprite.position.copy(pos)
        sprite.scale.set(axisLen * 0.08, axisLen * 0.08, 1)
        return sprite
      }

      this.scene.add(makeLabel('X', center.clone().addScaledVector(new THREE.Vector3(1, 0, 0), axisLen * 1.15), '#ff4444'))
      this.scene.add(makeLabel('Y', center.clone().addScaledVector(new THREE.Vector3(0, 1, 0), axisLen * 1.15), '#44ff44'))
      this.scene.add(makeLabel('Z', center.clone().addScaledVector(new THREE.Vector3(0, 0, 1), axisLen * 1.15), '#4488ff'))
    },

    fitCamera(box) {
      const center = new THREE.Vector3()
      box.getCenter(center)
      const size = new THREE.Vector3()
      box.getSize(size)
      const maxDim = Math.max(size.x, size.y, size.z)
      const fov = this.camera.fov * (Math.PI / 180)
      const dist = (maxDim / 2) / Math.tan(fov / 2) * 1.8

      this.camera.position.set(center.x, center.y, center.z + dist)
      this.camera.near = dist * 0.001
      this.camera.far = dist * 10
      this.camera.updateProjectionMatrix()
      this.controls.target.copy(center)
      this.controls.update()
    },

    dispose() {
      if (this.animFrameId) {
        cancelAnimationFrame(this.animFrameId)
        this.animFrameId = null
      }
      if (this.renderer) {
        const container = this.$refs.container
        if (container && this.renderer.domElement.parentNode === container) {
          container.removeChild(this.renderer.domElement)
        }
        this.renderer.dispose()
        this.renderer = null
      }
      this.scene = null
      this.camera = null
      this.controls = null
    }
  }
}
</script>

<style scoped>
.hole-cut-viewer-3d {
  width: 100%;
  height: 100%;
  min-height: 500px;
  background: #f5f7fa;
}
</style>
