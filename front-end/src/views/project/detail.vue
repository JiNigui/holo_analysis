<template>
  <div class="project-detail-container">
    <div class="project-detail-header">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/projects/index' }">我的项目</el-breadcrumb-item>
        <el-breadcrumb-item>项目详情</el-breadcrumb-item>
      </el-breadcrumb>
      <h2>{{ project.name }}</h2>
      <div class="project-info">
        <span>创建时间：{{ project.createTime }}</span>
        <el-button type="success" @click="handleExport">导出数据</el-button>
      </div>
    </div>
    <div class="project-detail-content">
      <el-card>
        <!-- 步骤按钮导航 -->
        <div class="step-buttons-container">
          <div class="step-buttons">
            <el-button
              v-for="(step, index) in stepNames"
              :key="index"
              :type="activeStep === index ? 'primary' : 'default'"
              :class="{ 'active-step': activeStep === index, 'completed-step': stepStatus[index] }"
              :disabled="index > 0 && !stepStatus[index - 1]"
              @click="navigateToStep(index)"
            >
              {{ step }}
              <i v-if="stepStatus[index]" class="el-icon-check" style="margin-left: 5px;" />
            </el-button>
          </div>
          <div class="step-progress">
            <span>进度：{{ completedSteps }}/{{ totalSteps }}</span>
          </div>
        </div>
        <div class="step-content">
          <!-- 第一步：图像二值化 -->
          <div v-if="activeStep === 0">
            <h3>第一步：图像二值化</h3>
            <div class="step-description">
              <p>将输入的灰度/彩色图像通过阈值分割等技术转换为仅包含黑白像素的二值图像。</p>
            </div>
            <el-upload
              ref="upload"
              class="upload-demo"
              action="/upload"
              :http-request="handleAutoUpload"
              :on-change="handleFileChange"
              :on-success="handleBatchUploadSuccess"
              :on-error="handleUploadError"
              :before-upload="beforeUpload"
              :show-file-list="false"
              :multiple="true"
              :auto-upload="false"
              accept=".tif,.tiff"
              drag
            >
              <i class="el-icon-upload" />
              <div class="el-upload__text">将图像文件拖到此处，或<em>点击选择文件</em></div>
              <div slot="tip" class="el-upload__tip">
                <span v-if="!uploading">支持tif/tiff格式，可批量上传多个文件，选择后自动上传</span>
              </div>
            </el-upload>
            <!-- 上传进度条 -->
            <div v-if="uploading" class="upload-progress-container" style="margin-top: 15px;">
              <div class="upload-progress-info" style="margin-bottom: 8px; color: #409eff; font-weight: bold;">
                <i class="el-icon-loading" />
                正在上传 {{ uploadFileCount }} 个文件，请稍候...
              </div>
              <el-progress
                :percentage="uploadProgress"
                :stroke-width="18"
                :text-inside="true"
                status="success"
              />
            </div>
            <div v-if="uploadResult" class="upload-info" style="margin-top: 20px;">
              <el-alert
                :title="uploadResult.title"
                :type="uploadResult.type"
                :closable="false"
                show-icon
              >
                <p>{{ uploadResult.message }}</p>
              </el-alert>
            </div>
            <div class="step-button">
              <el-button type="primary" :disabled="!uploadedFiles[0] || uploadedFiles[0].length === 0" @click="executeStep(0)">执行图像二值化</el-button>
            </div>
          </div>
          <div v-if="activeStep === 1" class="step-content">
            <h3>第二步：选取VOI</h3>
            <p>请选择感兴趣区域(VOI)进行后续分析</p>

            <!-- 3D可视化区域 -->
            <div class="voi-visualization-area">
              <div class="voi-controls">
                <el-button
                  :disabled="loadingBatchData"
                  type="primary"
                  @click="load3DModelData"
                >
                  {{ loadingBatchData ? '正在构建...' : voiDataLoaded ? '重新构建模型' : '加载数据构建3D模型' }}
                </el-button>
              </div>

              <!-- 3D可视化组件 -->
              <div class="voi-3d-container">
                <VtkMedicalViewer
                  v-if="voiDataLoaded"
                  ref="vtkviewer"
                  :project-id="String(project.id)"
                  :voi-bounds="voiBounds"
                  @model-rendered="handleModelRendered"
                  @selection-completed="handleVOISelectionCompleted"
                />
                <div v-else class="no-data-prompt">
                  <i class="el-icon-picture-outline" />
                  <p>点击"加载数据构建3D模型"按钮开始构建3D可视化</p>
                </div>
              </div>

              <!-- 数据状态信息 -->
              <div class="data-status-info">
                <el-alert
                  v-if="voi3DModelRendered"
                  title="3D模型渲染成功"
                  type="success"
                  :closable="false"
                  show-icon
                >
                  <span>3D模型已成功渲染，可在视图中进行VOI选取</span>
                </el-alert>
                <el-alert
                  v-else-if="voiDataLoaded"
                  title="正在进行3D可视化"
                  type="info"
                  :closable="false"
                  show-icon
                >
                  <span>数据已接收，正在加载和渲染3D模型...</span>
                </el-alert>
              </div>
            </div>

            <!-- VOI选取状态显示 -->
            <div class="voi-status-info">
              <el-alert
                v-if="voiDataLoaded && isVOIConfirmed()"
                title="VOI选取已完成"
                type="success"
                :closable="false"
                show-icon
              >
                <span>VOI区域已确认，可进行下一步操作</span>
              </el-alert>
              <el-alert
                v-else-if="voiDataLoaded"
                title="等待VOI选取"
                type="info"
                :closable="false"
                show-icon
              >
                <span>请在3D视图中框选并确认VOI区域</span>
              </el-alert>
            </div>
          </div>
          <!-- 第三步：孔洞识别 -->
          <div v-else-if="activeStep === 2">
            <h3>第三步：孔洞识别</h3>
            <div class="step-description">
              <p>基于二值化后的图像，系统将自动识别图像中的孔洞。</p>
            </div>
            <el-button
              type="primary"
              :disabled="!stepStatus[1] || holeDetectionLoading"
              @click="executeStep(2)"
            >
              执行孔洞识别
            </el-button>
            
            <!-- 孔洞识别等待提示 -->
            <div v-if="holeDetectionLoading" class="hole-detection-loading" style="margin-top: 15px;">
              <el-alert
                title="孔洞识别正在进行中，请耐心等待……"
                type="info"
                :closable="false"
                show-icon
              >
                <i class="el-icon-loading" style="margin-right: 5px;" />
                系统正在处理图像数据，这可能需要几分钟时间
              </el-alert>
            </div>
          </div>
          <!-- 第四步：数据预处理 -->
          <div v-else-if="activeStep === 3">
            <h3>第四步：数据预处理</h3>
            <div class="step-description">
              <p>对识别出的孔洞数据进行清洗、过滤和标准化处理。</p>
            </div>
            <el-button
              type="primary"
              :disabled="!stepStatus[2] || dataPreprocessingLoading"
              @click="executeStep(3)"
            >
              执行数据预处理
            </el-button>
            
            <!-- 数据预处理等待提示 -->
            <div v-if="dataPreprocessingLoading" class="data-preprocessing-loading" style="margin-top: 15px;">
              <el-alert
                title="数据预处理正在进行中，请耐心等待……"
                type="info"
                :closable="false"
                show-icon
              >
                <i class="el-icon-loading" style="margin-right: 5px;" />
                系统正在处理数据，这可能需要几分钟时间
              </el-alert>
            </div>
          </div>
          <!-- 第五步：寻找目标孔洞 -->
          <div v-else-if="activeStep === 4">
            <h3>第五步：寻找目标孔洞</h3>
            <div class="step-description">
              <p>根据设定的条件筛选和定位目标孔洞。</p>
            </div>
            <div class="step-buttons-row">
              <el-button
                type="primary"
                :disabled="!stepStatus[3] || targetHoleAnalysisLoading"
                @click="executeStep(4)"
              >
                执行目标孔洞分析
              </el-button>
              
              <!-- 最大孔洞切割3D效果按钮 -->
              <el-button
                type="success"
                :disabled="!stepStatus[4] || !targetHoleResultImage"
                @click="showMaxHole3DView"
              >
                最大孔洞切割3D效果
              </el-button>
            </div>
            
            <!-- 目标孔洞分析等待提示 -->
            <div v-if="targetHoleAnalysisLoading" class="target-hole-analysis-loading" style="margin-top: 15px;">
              <el-alert
                title="目标孔洞分析正在进行中，请耐心等待……"
                type="info"
                :closable="false"
                show-icon
              >
                <i class="el-icon-loading" style="margin-right: 5px;" />
                系统正在分析目标孔洞并生成切片图像，这可能需要较长时间
              </el-alert>
              
              <!-- 实时进度条 -->
              <div v-if="showProgressBar" class="target-hole-analysis-progress" style="margin-top: 15px;">
                <div class="progress-info" style="margin-bottom: 8px; color: #409eff; font-weight: bold;">
                  {{ currentProgressStatus }}
                </div>
                <el-progress
                  :percentage="currentProgress"
                  :stroke-width="18"
                  :text-inside="true"
                  status="success"
                />
                <div class="progress-details" style="margin-top: 8px; font-size: 12px; color: #666;">
                  <span>{{ currentProgressMessage }}</span>
                </div>
              </div>
            </div>
            
            <!-- 目标孔洞分析结果图像显示 -->
            <div v-if="targetHoleResultImage" class="target-hole-result" style="margin-top: 20px;">
              <h4>目标孔洞分析结果</h4>
              <div class="result-image-container">
                <img 
                  :src="targetHoleResultImage" 
                  alt="目标孔洞分析结果"
                  class="result-image"
                  style="max-width: 100%; max-height: 500px; border: 1px solid #ddd; border-radius: 4px;"
                />
                <div class="image-info" style="margin-top: 10px; color: #666; font-size: 14px;">
                  <p>目标孔洞切片图像 - 显示目标孔洞的2D投影和切割平面位置</p>
                </div>
              </div>
            </div>
            
            <!-- 最大孔洞3D视图对话框 -->
            <el-dialog
              :visible.sync="show3DViewerDialog"
              title="最大孔洞切割3D效果"
              width="90%"
              :fullscreen="false"
              :close-on-click-modal="false"
              :close-on-press-escape="false"
              @opened="on3DViewerDialogOpen"
            >
              <div style="height: 70vh;">
                <MaxHolo3DViewer :visible="show3DViewerDialog" :project-id="Number(project.id)" />
              </div>
            </el-dialog>
          </div>
          <!-- 第六步：形态学分析 -->
          <div v-else-if="activeStep === 5">
            <h3>第六步：形态学分析</h3>
            <div class="step-description">
              <p>对目标孔洞进行形态学特征分析，生成分析报告。</p>
            </div>
            <el-button
              type="primary"
              :disabled="!stepStatus[4]"
              @click="executeStep(5)"
            >
              执行形态学分析
            </el-button>
            <div v-if="stepStatus[5]" class="analysis-result">
              <h4>分析结果</h4>
              <el-table :data="analysisData" style="width: 100%">
                <el-table-column prop="feature" label="特征" />
                <el-table-column prop="value" label="数值" />
              </el-table>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script>
import { getProject } from '@/api/project'
import { executeBinaryConversion, executeHoleDetection, executeDataPreprocessing, executeTargetHoleAnalysis } from '@/api/hole-analysis'
import { getToken } from '@/utils/auth'
import VtkMedicalViewer from '@/components/VtkMedicalViewer.vue'
import MaxHolo3DViewer from '@/components/MaxHolo3DViewer.vue'

export default {
  name: 'ProjectDetail',
  components: {
    VtkMedicalViewer,
    MaxHolo3DViewer
  },
  data() {
    return {
      project: {
        id: '',
        name: '孔洞分析项目',
        createTime: '2024-01-15 14:30:00'
      },
      activeStep: 0,
      stepNames: ['图像二值化', '选取VOI', '孔洞识别', '数据预处理', '寻找目标孔洞', '形态学分析'],
      //stepStatus: [false, false, false, false, false, false], // 记录每个步骤是否已完成
      stepStatus: [true, true, true, true, true, true], // 测试流程用
      uploadedFiles: { 0: [], 1: [], 2: [], 3: [], 4: [], 5: [] }, // 每个步骤对应的上传文件信息
      uploading: false, // 是否正在上传
      uploadProgress: 0, // 上传进度百分比
      uploadFileCount: 0, // 上传文件数量
      uploadResult: null, // 上传结果
      analysisData: [
        { feature: '孔洞总数', value: 0 },
        { feature: '平均面积', value: 0 },
        { feature: '最大直径', value: 0 },
        { feature: '最小直径', value: 0 },
        { feature: '孔洞密度', value: 0 }
      ],
      executingStep: false, // 是否正在执行步骤
      operationLogs: [], // 操作日志
      holeDetectionLoading: false, // 孔洞识别是否正在进行中
      dataPreprocessingLoading: false, // 数据预处理是否正在进行中
      targetHoleAnalysisLoading: false, // 目标孔洞分析是否正在进行中
      targetHoleResultImage: null, // 目标孔洞分析结果图像URL
      show3DViewerDialog: false, // 是否显示3D视图对话框

      // 实时进度显示相关数据
      showProgressBar: false, // 是否显示进度条
      currentProgress: 0, // 当前进度百分比
      currentProgressStatus: '请求发送中...', // 当前状态文字
      currentProgressMessage: '正在初始化API调用', // 当前详细消息
      sseConnection: null, // SSE连接对象
      processingCompleted: false, // 处理是否已完成

      // 3D可视化相关数据
      voiDataLoaded: false, // VOI数据是否已加载
      loadingBatchData: false, // 是否正在加载批次数据
      voi3DModelRendered: false, // 3D模型是否已渲染成功
      voiSliceCount: 0, // VOI切片数量
      voiBounds: { // VOI边界坐标
        xMin: 0,
        xMax: 100,
        yMin: 0,
        yMax: 100,
        zMin: 0,
        zMax: 100
      }
    }
  },
  computed: {
    completedSteps() {
      return this.stepStatus.filter(status => status).length
    },
    totalSteps() {
      return this.stepNames.length
    }
  },
  created() {
    this.loadProjectData()
  },
  methods: {
    async loadProjectData() {
      try {
        const projectId = this.$route.params.id
        // 使用封装的API函数获取项目数据
        const response = await getProject(projectId)

        // request.js 拦截器已经返回了 response.data，所以这里直接使用 response
        // 后端返回格式: { code: 200, message: '...', data: {...} }
        if (response && response.code === 200 && response.data) {
          const projectData = response.data
          // 映射后端字段到前端字段
          this.project = {
            id: projectData.id,
            name: projectData.project_name || projectData.name || '未命名项目',
            createTime: this.formatDateTime(projectData.created_time) || new Date().toLocaleString('zh-CN'),
            description: projectData.description || '',
            userId: projectData.user_id
          }
          this.projectId = projectId // 设置projectId用于上传
        } else {
          // API返回错误
          const errorMsg = response?.message || '获取项目信息失败'
          this.$message.error(errorMsg)
          console.error('获取项目信息失败:', response)
          // 使用默认值
          this.project = {
            id: projectId,
            name: `孔洞分析项目-${projectId}`,
            createTime: new Date().toLocaleString('zh-CN')
          }
        }
      } catch (error) {
        console.error('获取项目信息失败:', error)
        const errorMsg = error.response?.data?.message || error.message || '获取项目信息失败'
        this.$message.error(errorMsg)
        // 使用默认值
        const projectId = this.$route.params.id
        this.project = {
          id: projectId,
          name: `孔洞分析项目-${projectId}`,
          createTime: new Date().toLocaleString('zh-CN')
        }
      }
    },
    // 格式化日期时间
    formatDateTime(dateTimeString) {
      if (!dateTimeString) return ''
      try {
        const date = new Date(dateTimeString)
        // 格式化为：YYYY-MM-DD HH:mm:ss
        const year = date.getFullYear()
        const month = String(date.getMonth() + 1).padStart(2, '0')
        const day = String(date.getDate()).padStart(2, '0')
        const hours = String(date.getHours()).padStart(2, '0')
        const minutes = String(date.getMinutes()).padStart(2, '0')
        const seconds = String(date.getSeconds()).padStart(2, '0')
        return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
      } catch (error) {
        console.error('日期格式化失败:', error)
        return dateTimeString
      }
    },
    // 导航到指定步骤
    navigateToStep(stepIndex) {
      // 检查是否可以导航到该步骤
      if (stepIndex > 0 && !this.stepStatus[stepIndex - 1]) {
        this.$message.warning(`请先完成"${this.stepNames[stepIndex - 1]}"步骤`)
        return
      }
      this.activeStep = stepIndex
      // 切换步骤时清空上传结果提示
      this.uploadResult = null
    },
    // 执行步骤
    async executeStep(stepIndex) {
      if (this.executingStep) {
        this.$message.warning('正在执行其他操作，请稍候')
        return
      }

      this.executingStep = true
      this.$message.info(`开始执行：${this.stepNames[stepIndex]}`)

      try {
        if (stepIndex === 0) {
          // 第一步：图像二值化
          await this.executeBinaryConversion()
        } else if (stepIndex === 1) {
          // 第二步：VOI选取 - 检查是否已确认VOI
          if (!this.isVOIConfirmed()) {
            throw new Error('请先在3D视图中确认VOI选择')
          }

          // VOI选取已经在3D视图中完成，直接标记为完成
          this.$set(this.stepStatus, stepIndex, true)
          this.$message.success('VOI选取已完成')

          // 强制重新计算进度
          this.$nextTick(() => {
            // 立即更新进度显示
            this.$forceUpdate()
            console.log('✅ VOI选取完成，当前进度:', this.completedSteps, '/', this.totalSteps)
          })

          // 导航到下一步
          this.navigateToStep(2)
        } else if (stepIndex === 2) {
          // 第三步：孔洞识别
          await this.executeHoleDetection()
        } else if (stepIndex === 3) {
          // 第四步：数据预处理
          await this.executeDataPreprocessing()
        } else if (stepIndex === 4) {
          // 第五步：目标孔洞分析
          await this.executeTargetHoleAnalysis()
        } else {
          // 其他步骤暂时保持模拟
          await new Promise(resolve => setTimeout(resolve, 2000))
          this.$set(this.stepStatus, stepIndex, true)
          
          // 立即更新进度显示
          this.$forceUpdate()
          
          this.$message.success(`${this.stepNames[stepIndex]}执行完成`)
        }
      } catch (error) {
        console.error(`执行步骤${stepIndex}失败:`, error)
        this.$message.error(`${this.stepNames[stepIndex]}执行失败: ${error.message || '未知错误'}`)
      } finally {
        this.executingStep = false
      }
    },

    // 执行图像二值化
    async executeBinaryConversion() {
      try {
        const projectId = this.project.id
        if (!projectId) {
          throw new Error('项目ID不存在')
        }

        // 调用后端API
        const response = await executeBinaryConversion(projectId)

        if (response && response.code === 200) {
          // 使用Vue.set确保响应式更新
          this.$set(this.stepStatus, 0, true)

          // 立即更新进度显示
          this.$forceUpdate()

          // 显示成功消息提示
          this.$message({
            message: response.message || '图像二值化处理完成',
            type: 'success',
            duration: 5000,
            showClose: true
          })

          // 显示详细的处理结果
          const processedFiles = response.data?.processed_files || 0
          this.uploadResult = {
            type: 'success',
            title: '✓ 图像二值化处理成功',
            message: `已成功处理 ${processedFiles} 个图像文件，二值化结果已保存到输出目录`
          }
        } else {
          throw new Error(response?.message || '图像二值化处理失败')
        }
      } catch (error) {
        console.error('图像二值化处理失败:', error)

        // 显示错误提示
        this.uploadResult = {
          type: 'error',
          title: '✗ 图像二值化处理失败',
          message: error.message || '处理过程中发生错误，请检查后端日志'
        }

        throw error
      }
    },

    // 执行孔洞识别（第三步）
    async executeHoleDetection() {
      try {
        const projectId = this.project.id
        if (!projectId) {
          throw new Error('项目ID不存在')
        }

        // 显示等待提示
        this.holeDetectionLoading = true

        // 调用后端API
        const response = await executeHoleDetection(projectId)

        if (response && response.code === 200) {
          // 检查后端实际执行状态
          const operationResult = response.data?.operation_result || {}
          
          if (operationResult.status === 'success') {
            // 使用Vue.set确保响应式更新
            this.$set(this.stepStatus, 2, true)

            // 立即更新进度显示
            this.$forceUpdate()

            // 隐藏等待提示
            this.holeDetectionLoading = false

            // 显示成功消息提示
            this.$message({
              message: operationResult.message || '孔洞识别完成',
              type: 'success',
              duration: 5000,
              showClose: true
            })

            // 显示详细的处理结果
            const inputFilesCount = response.data?.input_files_count || 0
            
            this.uploadResult = {
              type: 'success',
              title: '✓ 孔洞识别完成',
              message: `已成功识别 ${inputFilesCount} 个切片文件中的孔洞，识别结果已保存到输出目录`
            }

            // 不自动跳转，只更新步骤状态，让下一步按钮可用
          } else {
            // 后端执行失败
            throw new Error(operationResult.message || '孔洞识别处理失败')
          }
        } else {
          throw new Error(response?.message || '孔洞识别处理失败')
        }
      } catch (error) {
        console.error('孔洞识别处理失败:', error)

        // 隐藏等待提示
        this.holeDetectionLoading = false

        // 显示错误消息提示
        this.$message({
          message: error.message || '孔洞识别失败',
          type: 'error',
          duration: 5000,
          showClose: true
        })

        // 显示错误提示
        this.uploadResult = {
          type: 'error',
          title: '✗ 孔洞识别处理失败',
          message: error.message || '处理过程中发生错误，请检查后端日志'
        }

        throw error
      }
    },

    // 执行数据预处理（第四步）
    async executeDataPreprocessing() {
      try {
        const projectId = this.project.id
        if (!projectId) {
          throw new Error('项目ID不存在')
        }

        // 显示等待提示
        this.dataPreprocessingLoading = true

        // 调用后端API
        const response = await executeDataPreprocessing(projectId)

        if (response && response.code === 200) {
          // 检查后端实际执行状态
          const operationResult = response.data?.operation_result || {}
          
          if (operationResult.status === 'success') {
            // 更新步骤状态
            this.$set(this.stepStatus, 3, true)
            
            // 立即更新进度显示
            this.$forceUpdate()

            // 隐藏等待提示
            this.dataPreprocessingLoading = false

            // 显示成功消息提示
            this.$message({
              message: operationResult.message || '数据预处理执行成功',
              type: 'success',
              duration: 1000,
              showClose: true
            })

            // 显示详细的处理结果
            const inputFilesCount = response.data?.input_files_count || 0
            const outputFilesCount = response.data?.output_files_count || 0
            
            this.uploadResult = {
              type: 'success',
              title: '✓ 数据预处理执行成功',
              message: `已成功处理 ${inputFilesCount} 个掩码文件，生成 ${outputFilesCount} 个预处理结果文件`
            }

            // 不自动跳转，只更新步骤状态，让下一步按钮可用
          } else {
            // 后端执行失败
            throw new Error(operationResult.message || '数据预处理执行失败')
          }
        } else {
          throw new Error(response?.message || '数据预处理执行失败')
        }
      } catch (error) {
        console.error('数据预处理执行失败:', error)

        // 隐藏等待提示
        this.dataPreprocessingLoading = false

        // 显示错误消息提示
        this.$message({
          message: error.message || '数据预处理执行失败',
          type: 'error',
          duration: 5000,
          showClose: true
        })

        // 显示错误提示
        this.uploadResult = {
          type: 'error',
          title: '✗ 数据预处理执行失败',
          message: error.message || '处理过程中发生错误，请检查后端日志'
        }

        throw error
      }
    },

    // 执行目标孔洞分析（第五步）
    async executeTargetHoleAnalysis() {
      try {
        const projectId = this.project.id
        if (!projectId) {
          throw new Error('项目ID不存在')
        }

        // 显示等待提示和进度条
        this.targetHoleAnalysisLoading = true
        this.showProgressBar = true
        this.targetHoleResultImage = null // 清空之前的图像

        // 重置进度状态
        this.currentProgress = 0
        this.currentProgressStatus = '请求发送中...'
        this.currentProgressMessage = '正在初始化API调用'

        // 建立SSE连接 - 这将自动触发API调用
        this.connectToProgressSSE(projectId)

        // 不再需要手动调用API，SSE连接会自动触发triggerTargetHoleAnalysis
        console.log('SSE连接已建立，等待进度更新...')
        
      } catch (error) {
        console.error('目标孔洞分析初始化失败:', error)

        // 隐藏等待提示和进度条
        this.targetHoleAnalysisLoading = false
        this.showProgressBar = false

        // 关闭SSE连接
        this.closeSSEConnection()

        // 显示错误消息提示
        this.$message({
          message: error.message || '目标孔洞分析初始化失败',
          type: 'error',
          duration: 5000,
          showClose: true
        })

        // 显示错误提示
        this.uploadResult = {
          type: 'error',
          title: '✗ 目标孔洞分析初始化失败',
          message: error.message || '处理过程中发生错误，请检查后端日志'
        }

        throw error
      }
    },

    // 文件选择变化时触发（用户选择文件后自动上传）
    handleFileChange(file, fileList) {
      // 计算总文件大小
      const totalSize = fileList.reduce((sum, file) => sum + file.size, 0)
      const maxSize = 3 * 1024 * 1024 * 1024 // 3GB

      // 检查总大小是否超过限制
      if (totalSize > maxSize) {
        const totalSizeGB = (totalSize / 1024 / 1024 / 1024).toFixed(2)
        this.$message.error(`文件总大小 ${totalSizeGB}GB 超过限制（最大3GB），请减少文件数量`)
        // 清空文件列表
        if (this.$refs.upload) {
          this.$refs.upload.clearFiles()
        }
        return
      }

      // 等待一小段时间，确保所有文件都添加到列表中
      setTimeout(() => {
        if (fileList.length > 0 && !this.uploading) {
          this.uploadFilesAutomatically(fileList)
        }
      }, 100)
    },
    // 自动上传文件
    uploadFilesAutomatically(fileList) {
      if (fileList.length === 0) {
        return
      }

      this.uploading = true
      this.uploadResult = null
      this.uploadProgress = 0
      this.uploadFileCount = fileList.length

      // 创建FormData对象
      const formData = new FormData()

      // 添加所有文件
      fileList.forEach(fileItem => {
        formData.append('files', fileItem.raw)
      })

      // 添加其他参数
      formData.append('project_id', this.projectId)
      formData.append('step', 'step1')
      formData.append('clear_old', 'true') // 清除旧文件

      // 创建XMLHttpRequest
      const xhr = new XMLHttpRequest()

      // 上传进度事件
      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
          this.uploadProgress = Math.round((e.loaded / e.total) * 100)
        }
      })

      // 上传完成事件
      xhr.addEventListener('load', () => {
        this.uploading = false
        if (xhr.status === 200) {
          try {
            const response = JSON.parse(xhr.responseText)
            this.handleBatchUploadSuccess(response)
            // 清空上传组件的文件列表
            if (this.$refs.upload) {
              this.$refs.upload.clearFiles()
            }
          } catch (error) {
            this.handleUploadError(new Error('响应解析失败'))
          }
        } else {
          try {
            const response = JSON.parse(xhr.responseText)
            this.handleUploadError(new Error(response.message || '上传失败'))
          } catch (error) {
            this.handleUploadError(new Error('上传失败'))
          }
        }
      })

      // 上传错误事件
      xhr.addEventListener('error', () => {
        this.uploading = false
        this.uploadProgress = 0
        this.handleUploadError(new Error('网络错误，上传失败'))
      })

      // 发送请求 - 使用axios实例确保代理配置生效
      const token = getToken()
      if (!token) {
        this.uploading = false
        this.uploadProgress = 0
        this.handleUploadError(new Error('未登录，请先登录'))
        return
      }

      // 使用项目中的request工具发送请求，确保代理配置生效
      this.$http({
        url: '/upload/images/batch',
        method: 'post',
        data: formData,
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.lengthComputable) {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
            this.uploadProgress = progress
          }
        }
      }).then(response => {
        this.handleBatchUploadSuccess(response)
        // 清空上传组件的文件列表
        if (this.$refs.upload) {
          this.$refs.upload.clearFiles()
        }
      }).catch(error => {
        if (error.response) {
          this.handleUploadError(new Error(error.response.data.message || '上传失败'))
        } else {
          this.handleUploadError(new Error('网络错误，上传失败'))
        }
      })
    },
    // http-request方法（el-upload组件需要，但不会被调用）
    handleAutoUpload(options) {
      // 这个方法不会被调用，因为我们在handleFileChange中手动上传
      // 但el-upload组件需要这个方法
      return Promise.resolve()
    },
    // 批量上传成功处理
    handleBatchUploadSuccess(response) {
      if (response.code === 200) {
        const data = response.data
        // 只显示一个成功提示
        this.uploadResult = {
          type: 'success',
          title: '所有文件上传成功',
          message: `成功上传 ${data.uploaded_count} 个文件${data.failed_count > 0 ? `，${data.failed_count} 个文件失败` : ''}`
        }

        // 记录上传的文件信息
        if (!this.uploadedFiles[0]) {
          this.uploadedFiles[0] = []
        }
        this.uploadedFiles[0] = data.uploaded_files.map(file => ({
          filename: file.filename,
          filePath: file.file_path,
          relativePath: file.relative_path,
          projectId: this.projectId,
          step: 'step1',
          originalName: file.filename
        }))

        // 标记步骤为可执行状态
        this.stepStatus[0] = true

        // 清空文件列表
        this.fileList = []

        // 重置上传状态
        this.uploading = false
        this.uploadProgress = 0
      } else {
        this.handleUploadError(new Error(response.message || '文件上传失败'))
      }
    },
    // 文件上传前验证
    beforeUpload(file) {
      // 支持的文件扩展名
      const allowedExtensions = ['.tif', '.tiff']
      const fileExtension = '.' + file.name.split('.').pop().toLowerCase()
      const isAllowedType = allowedExtensions.includes(fileExtension)
      if (!isAllowedType) {
        this.$message.error(`不支持的文件格式: ${fileExtension}，请上传tif/tiff格式的图像文件!`)
        return false
      }
      return true
    },
    handleUploadError(error) {
      this.uploading = false
      this.uploadResult = {
        type: 'error',
        title: '文件上传失败',
        message: error.message || '文件上传失败，请重试'
      }
      this.$message.error(error.message || '文件上传失败')
      // 清空上传组件的文件列表
      if (this.$refs.upload) {
        this.$refs.upload.clearFiles()
      }
    },
    handleExport() {
      this.$message.success('数据导出成功')
    },

    // 加载3D模型数据
    async load3DModelData() {
      if (!this.stepStatus[0]) {
        this.$message.warning('请先完成图像二值化步骤')
        return
      }

      // 防止重复加载
      if (this.loadingBatchData) {
        return
      }

      try {
        this.loadingBatchData = true
        this.$message.info('正在构建3D模型，请稍候...')

        // 设置VOI数据加载状态为true，显示3D可视化组件
        this.voiDataLoaded = true

        // 等待VtkMedicalViewer组件渲染完成
        await this.$nextTick()

        // 直接调用后端API获取VTK数据
        if (this.$refs.vtkviewer) {
          // 设置VOI边界信息
          this.voiBounds = {
            xMin: 0,
            xMax: 512,
            yMin: 0,
            yMax: 512,
            zMin: 0,
            zMax: 999
          }

          // 直接调用VTK组件的模型加载方法
          const loadResult = await this.$refs.vtkviewer.load3DModelData()

          // 只有在3D模型真正构建成功后才显示成功提示
          if (loadResult === true) {
            this.$message.success('3D模型构建成功并已显示在画布上')
          } else {
            throw new Error('3D模型构建失败')
          }
        } else {
          throw new Error('VTK可视化组件初始化失败')
        }
      } catch (error) {
        console.error('构建3D模型失败:', error)
        this.$message.error('构建3D模型失败，请重试')
        // 如果加载失败，重置状态
        this.voiDataLoaded = false
      } finally {
        // 无论成功还是失败，都重置加载状态
        this.loadingBatchData = false
      }
    },

    // 检查VOI选择是否已确认
    isVOIConfirmed() {
      if (!this.$refs.vtkviewer) {
        return false
      }

      // 检查VtkMedicalViewer组件中是否有已确认的选择区域
      return this.$refs.vtkviewer.selectedBounds !== null
    },

    // 处理3D模型渲染成功事件
    handleModelRendered() {
      this.voi3DModelRendered = true
      this.$message.success('3D模型渲染成功')
    },

    // 处理VOI选择完成事件
    handleVOISelectionCompleted(bounds) {
      console.log('✅ VOI选择完成事件触发，边界数据:', bounds)
      
      // 自动标记第二步为完成状态
      this.$set(this.stepStatus, 1, true)
      
      // 强制重新计算进度
      this.$nextTick(() => {
        this.$forceUpdate()
        console.log('✅ VOI选择完成，当前进度:', this.completedSteps, '/', this.totalSteps)
      })
      
      this.$message.success('VOI选取已完成，可进行下一步操作')
    },

    // 调用后端API确认VOI选择（实际实现）
    async confirmVOIWithBackend() {
      try {
        // 这里应该调用后端API确认VOI选择
        // const response = await this.$http.post('/voi/confirm', {
        //   project_id: this.project.id,
        //   voi_bounds: this.voiBounds
        // })

        // if (response.data.code === 200) {
        //   this.voiConfirmed = true
        //   this.$message.success('VOI选择已确认并保存')
        // } else {
        //   throw new Error(response.data.message)
        // }

      } catch (error) {
        console.error('确认VOI选择失败:', error)
        this.$message.error('确认VOI选择失败，请重试')
      }
    },

    // 显示最大孔洞3D视图
    showMaxHole3DView() {
      console.log('=== 开始显示最大孔洞3D视图 ===')
      console.log('当前项目ID:', this.project.id)
      console.log('按钮点击前 show3DViewerDialog:', this.show3DViewerDialog)
      
      this.show3DViewerDialog = true
      
      console.log('按钮点击后 show3DViewerDialog:', this.show3DViewerDialog)
      // 注意：子组件的mounted会在Vue异步渲染后执行，因此这里的"结束"日志会先于子组件的初始化日志
      console.log('=== 父组件操作完成，等待子组件初始化 ===')
    },
    
    // 3D视图对话框打开事件处理
    on3DViewerDialogOpen() {
      console.log('=== 3D视图对话框已打开，子组件初始化完成 ===')
      console.log('=== 显示最大孔洞3D视图流程结束 ===')
      // 模型加载通过visible prop的watch自动触发，无需手动调用
    },

    // 连接到SSE进度推送
    connectToProgressSSE(projectId) {
      try {
        // 如果已有连接，先关闭
        if (this.sseConnection) {
          this.sseConnection.close()
          this.sseConnection = null
        }

        // 重置所有进度相关状态
        this.processingCompleted = false
        this.currentProgress = 0
        this.currentProgressStatus = '请求发送中...'
        this.currentProgressMessage = '正在初始化API调用'

        // 获取token并构建SSE连接URL
        const token = getToken()
        const sseUrl = `/api/hole-analysis/target-hole-analysis-progress?project_id=${projectId}&token=${token}`
        
        // 创建EventSource连接
        this.sseConnection = new EventSource(sseUrl)

        // 设置连接超时检测
        const connectionTimeout = setTimeout(() => {
          if (this.sseConnection && this.sseConnection.readyState === EventSource.CONNECTING) {
            console.warn('SSE连接超时，尝试重新连接')
            this.sseConnection.close()
            this.sseConnection = null
            this.currentProgressStatus = '连接超时'
            this.currentProgressMessage = '与服务器建立连接超时，正在重试...'
            
            // 延迟重连
            setTimeout(() => {
              if (this.targetHoleAnalysisLoading) {
                this.connectToProgressSSE(projectId)
              }
            }, 3000)
          }
        }, 10000) // 10秒连接超时

        // 连接建立成功
        this.sseConnection.onopen = (event) => {
          clearTimeout(connectionTimeout)
          console.log('SSE连接已建立', event)
          this.currentProgressStatus = '连接已建立'
          this.currentProgressMessage = '开始接收进度更新'
          
          // SSE连接成功后，立即触发目标孔洞分析API调用
          this.triggerTargetHoleAnalysis(projectId)
        }

        // 接收进度更新
        this.sseConnection.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            console.log('收到SSE消息:', data)

            if (data.type === 'progress') {
              // 更新进度信息
              this.currentProgress = data.progress
              this.currentProgressStatus = data.status
              this.currentProgressMessage = data.message
              
              
            } else if (data.type === 'image') {
              // 接收到PNG图像数据
              console.log('接收到PNG图像数据')
              
              // 标记处理已完成
              this.processingCompleted = true
              
              // 更新进度到100%
              this.currentProgress = 100
              this.currentProgressStatus = '分析完成'
              this.currentProgressMessage = data.message
              
              // 显示PNG图像
              if (data.image_data) {
                const imageUrl = `data:image/png;base64,${data.image_data}`
                this.targetHoleResultImage = imageUrl
                console.log('PNG图像已显示')
              }
              
              // 更新步骤状态为已完成
              this.$set(this.stepStatus, 4, true)
              
              // 立即移除错误监听器，避免服务器关闭连接时触发错误处理
              if (this.sseConnection) {
                this.sseConnection.onerror = null
                console.log('已移除SSE错误监听器，准备安全关闭连接')
              }
              
              // 延迟关闭连接
              setTimeout(() => {
                this.closeSSEConnection()
                this.showProgressBar = false
                this.targetHoleAnalysisLoading = false
                this.$message.success('目标孔洞分析完成')
              }, 2000)
              
            } else if (data.type === 'completed') {
              // 分析完成（没有PNG图像的情况）
              this.currentProgress = 100
              this.currentProgressStatus = '分析完成'
              this.currentProgressMessage = data.message
              
              // 更新步骤状态为已完成
              this.$set(this.stepStatus, 4, true)
              
              // 立即移除错误监听器，避免服务器关闭连接时触发错误处理
              if (this.sseConnection) {
                this.sseConnection.onerror = null
                console.log('已移除SSE错误监听器，准备安全关闭连接')
              }
              
              // 延迟关闭连接
              setTimeout(() => {
                this.closeSSEConnection()
                this.showProgressBar = false
                this.targetHoleAnalysisLoading = false
                this.$message.success('目标孔洞分析完成')
              }, 2000)
              
            } else if (data.type === 'connected') {
              console.log('SSE连接确认:', data.message)
            }
          } catch (error) {
            console.error('解析SSE消息失败:', error)
          }
        }

        // 处理连接错误
    this.sseConnection.onerror = (event) => {
      console.error('SSE连接错误事件:', event)
      
      // 检查连接状态，避免在连接已关闭时重复处理错误
      if (!this.sseConnection || this.sseConnection.readyState === EventSource.CLOSED) {
        console.log('SSE连接已关闭，忽略错误事件')
        return
      }
      
      // 检查是否已经完成处理，如果是则忽略错误（这是正常关闭）
      if (this.processingCompleted || this.currentProgress >= 100) {
        console.log('处理已完成，忽略连接错误（正常关闭）')
        // 不调用closeSSEConnection()，因为可能已经关闭了
        // 只清理引用
        this.sseConnection = null
        return
      }
      
      // 更精确的错误类型判断
      const readyState = this.sseConnection.readyState
      
      // 情况1: 连接正在建立时出错 (真正的网络错误)
      if (readyState === EventSource.CONNECTING) {
        console.error('检测到网络连接错误，尝试重连')
        
        // 更新错误状态
        this.currentProgressStatus = '连接错误'
        this.currentProgressMessage = '与服务器的连接出现问题，正在尝试重连...'
        
        // 关闭当前连接
        this.closeSSEConnection()
        
        // 延迟重连，避免过于频繁的重连尝试
        setTimeout(() => {
          if (this.targetHoleAnalysisLoading && !this.processingCompleted && this.currentProgress < 100) {
            console.log('尝试重新连接SSE...')
            this.connectToProgressSSE(projectId)
          }
        }, 3000)
      }
      // 情况2: 连接已打开但收到错误 (可能是服务器端错误或正常关闭)
      else if (readyState === EventSource.OPEN) {
        console.log('SSE连接已打开但收到错误事件，可能是服务器端问题或正常关闭')
        
        // 检查是否是服务器端错误（HTTP状态码错误）
        if (event && event.target && event.target.status) {
          const status = event.target.status
          if (status >= 400) {
            console.error(`服务器返回错误状态码: ${status}`)
            this.currentProgressStatus = '服务器错误'
            this.currentProgressMessage = `服务器返回错误: ${status}`
          }
        }
        
        // 等待一小段时间，如果连接仍然打开则可能是真正的错误
        setTimeout(() => {
          if (this.sseConnection && this.sseConnection.readyState === EventSource.OPEN) {
            console.error('SSE连接仍然打开，可能是真正的错误，尝试重连')
            this.currentProgressStatus = '连接错误'
            this.currentProgressMessage = '连接出现问题，正在尝试重连...'
            this.closeSSEConnection()
            setTimeout(() => {
              if (this.targetHoleAnalysisLoading && !this.processingCompleted && this.currentProgress < 100) {
                this.connectToProgressSSE(projectId)
              }
            }, 2000)
          } else {
            console.log('SSE连接已正常关闭，无需重连')
            this.closeSSEConnection()
          }
        }, 1000)
      }
      // 情况3: 连接正在关闭中，这是正常情况
      else if (readyState === EventSource.CLOSED) {
        console.log('SSE连接正在关闭中，这是正常情况，忽略错误')
        this.sseConnection = null
      }
      // 情况4: 其他状态，直接关闭连接
      else {
        console.log('SSE连接处于未知状态，安全关闭连接')
        this.closeSSEConnection()
      }
    }

      } catch (error) {
        console.error('建立SSE连接失败:', error)
        this.$message.error('无法建立实时进度连接')
      }
    },

    // 触发目标孔洞分析API调用
    async triggerTargetHoleAnalysis(projectId) {
      try {
        console.log('开始调用目标孔洞分析API...')
        
        // 更新状态为API调用中
        this.currentProgressStatus = 'API调用中'
        this.currentProgressMessage = '正在向服务器发送分析请求'
        
        // 使用原生的fetch API来调用后端，以便更好地控制响应处理
        const response = await fetch(`/api/hole-analysis/target-hole-analysis`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${getToken()}`
          },
          body: JSON.stringify({
            project_id: projectId
          })
        })

        if (!response.ok) {
          const errorText = await response.text()
          console.error('API调用HTTP错误:', response.status, errorText)
          throw new Error(`HTTP ${response.status}: ${errorText}`)
        }

        const result = await response.json()
        
        if (result.code === 200) {
          console.log('目标孔洞分析API调用成功')
          this.currentProgressStatus = '请求已接受'
          this.currentProgressMessage = '服务器已接受分析请求，开始处理...'
          // 进度更新将通过SSE推送，无需额外处理
        } else {
          console.error('目标孔洞分析API调用失败:', result.message)
          this.$message.error(`目标孔洞分析失败: ${result.message}`)
          
          // 更新错误状态
          this.currentProgressStatus = 'API调用失败'
          this.currentProgressMessage = `API调用失败: ${result.message}`
          
          // 关闭SSE连接
          this.closeSSEConnection()
          this.showProgressBar = false
          this.targetHoleAnalysisLoading = false
        }
        
      } catch (error) {
        console.error('调用目标孔洞分析API失败:', error)
        this.$message.error('调用目标孔洞分析API失败')
        
        // 更新错误状态
        this.currentProgressStatus = 'API调用异常'
        this.currentProgressMessage = `API调用异常: ${error.message}`
        
        // 关闭SSE连接
        this.closeSSEConnection()
        this.showProgressBar = false
        this.targetHoleAnalysisLoading = false
      }
    },

    // 关闭SSE连接
    closeSSEConnection() {
      if (this.sseConnection) {
        // 先移除所有事件监听器，避免在关闭过程中触发错误事件
        this.sseConnection.onmessage = null
        this.sseConnection.onerror = null
        this.sseConnection.onopen = null
        
        // 检查连接状态，如果已经关闭则不需要再次关闭
        if (this.sseConnection.readyState !== EventSource.CLOSED) {
          this.sseConnection.close()
        }
        
        this.sseConnection = null
        console.log('SSE连接已安全关闭')
      }
    }

  }
}
</script>
<style scoped>
.project-detail-container {
  padding: 20px;
}

.project-detail-header h2 {
  margin: 10px 0;
  color: #303133;
}

.project-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  color: #606266;
}

/* 步骤按钮容器样式 */
.step-buttons-container {
  margin-bottom: 30px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 4px;
}

.step-buttons {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
  flex-wrap: wrap;
}

.step-buttons .el-button {
  min-width: 120px;
  position: relative;
  transition: all 0.3s ease;
}

.step-buttons .el-button.active-step {
  border: 2px solid #409eff;
  font-weight: bold;
}

.step-buttons .el-button.completed-step {
  background-color: #f0f9ff;
  border-color: #409eff;
}

.step-buttons .el-button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.step-progress {
  text-align: right;
  font-size: 14px;
  color: #606266;
}

.step-content {
  padding: 30px 0;
}

.step-content h3 {
  margin-bottom: 20px;
  color: #303133;
  border-left: 4px solid #409eff;
  padding-left: 10px;
}

.step-description {
  margin-bottom: 20px;
  color: #606266;
  line-height: 1.6;
}

.step-button {
  margin-top: 20px;
}

.analysis-result {
  margin-top: 30px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 4px;
}

.analysis-result h4 {
  margin-bottom: 15px;
  color: #303133;
}

.upload-demo {
  margin: 20px 0;
}

.upload-info {
  margin: 20px 0;
}

.uploaded-file-info {
  margin: 10px 0;
}

.uploaded-file-info p {
  margin: 5px 0;
  font-size: 14px;
}

.upload-count {
  margin-top: 10px;
  font-weight: bold;
  color: #409eff;
}
</style>
