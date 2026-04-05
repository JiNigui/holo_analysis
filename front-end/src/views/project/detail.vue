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

            <!-- 3D孔洞预览（形态清洗后） -->
            <div v-if="showStep4Viewer" style="margin-top: 20px;">
              <div style="font-weight: bold; margin-bottom: 8px; color: #303133;">孔洞3D预览（形态清洗后）</div>
              <div style="height: 65vh; border: 1px solid #dcdfe6; border-radius: 4px; overflow: hidden;">
                <Step4Viewer ref="step4viewer" />
              </div>
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
                系统正在分析目标孔洞，这可能需要较长时间
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

            <!-- 3D数据获取中提示 -->
            <div v-if="fetching3DData" style="margin-top: 15px;">
              <el-alert
                title="正在请求目标孔洞3D显示数据"
                type="info"
                :closable="false"
                show-icon
              >
                <i class="el-icon-loading" style="margin-right: 5px;" />
                正在生成3D模型，请稍候...
              </el-alert>
            </div>

            <!-- 目标孔洞切割3D视图（内嵌） -->
            <div v-if="show3DViewerDialog" style="margin-top: 20px;">
              <div style="font-weight: bold; margin-bottom: 8px; color: #303133;">目标孔洞切割3D效果</div>
              <div style="height: 65vh; border: 1px solid #dcdfe6; border-radius: 4px; overflow: hidden;">
                <HoleCutViewer3D :visible="show3DViewerDialog" :project-id="Number(project.id)" @loaded="onViewer3DLoaded" />
              </div>
            </div>
          </div>
          <!-- 第六步：形态学分析 -->
          <div v-else-if="activeStep === 5">
            <h3>第六步：形态学分析与智能鉴定</h3>
            <div class="step-description">
              <p>对目标孔洞进行形态学特征分析，生成智能鉴定报告和详细参数矩阵。</p>
            </div>

            <!-- 执行按钮 + 下载按钮 -->
            <div class="step-button" style="display: flex; gap: 12px; align-items: center; flex-wrap: wrap;">
              <el-button
                type="primary"
                :disabled="!stepStatus[4] || isAnalyzing"
                :loading="isAnalyzing"
                @click="executeMorphologicalAnalysis"
              >
                {{ isAnalyzing ? '分析中...' : '执行形态学分析' }}
              </el-button>
              <el-button
                v-if="stepStatus[5]"
                type="success"
                @click="downloadBothFiles"
              >
                <i class="el-icon-download" /> 下载分析报告
              </el-button>
            </div>

            <!-- 结果显示区域 -->
            <div v-if="stepStatus[5]" class="morphological-analysis-result">
              <h4>形态学分析结果</h4>

              <!-- 文件切换标签 -->
              <div class="file-switcher">
                <el-button-group>
                  <el-button
                    :type="activeFileType === 'excel' ? 'primary' : 'default'"
                    @click="handleFileTypeSwitch('excel')"
                  >
                    智能鉴定与全局特征
                  </el-button>
                  <el-button
                    :type="activeFileType === 'csv' ? 'primary' : 'default'"
                    @click="handleFileTypeSwitch('csv')"
                  >
                    单体孔洞参数明细
                  </el-button>
                </el-button-group>
              </div>

              <!-- Excel 内容展示（智能鉴定与全局特征 = Sheet 0） -->
              <div v-if="activeFileType === 'excel'" class="excel-content" style="margin-top: 15px;">
                <div v-if="fileContents.excel.parsedData && fileContents.excel.parsedData.sheets && fileContents.excel.parsedData.sheets.length">
                  <!-- 表格 -->
                  <div class="analysis-table-wrap">
                    <table v-if="activeSheetData" class="analysis-table">
                      <thead>
                        <tr>
                          <th v-for="(header, hIdx) in activeSheetData.headers" :key="hIdx">{{ header }}</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="(row, rIdx) in activeSheetData.rows" :key="rIdx">
                          <td v-for="(cell, cIdx) in row" :key="cIdx">{{ cell }}</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                  <div style="margin-top: 8px; font-size: 12px; color: #666;">
                    共 {{ activeSheetData ? activeSheetData.rows.length : 0 }} 行数据
                  </div>
                </div>
                <el-alert v-else title="Excel 文件解析失败或暂无数据" type="warning" :closable="false" show-icon />
              </div>

              <!-- CSV 内容展示 -->
              <div v-if="activeFileType === 'csv'" class="csv-content" style="margin-top: 15px;">
                <div v-if="fileContents.csv.parsedData && fileContents.csv.parsedData.headers && fileContents.csv.parsedData.headers.length">
                  <div class="analysis-table-wrap">
                    <table class="analysis-table">
                      <thead>
                        <tr>
                          <th v-for="(header, hIdx) in fileContents.csv.parsedData.headers" :key="hIdx">{{ header }}</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="(row, rIdx) in fileContents.csv.parsedData.rows" :key="rIdx">
                          <td v-for="(cell, cIdx) in row" :key="cIdx">{{ cell }}</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                  <div style="margin-top: 8px; font-size: 12px; color: #666;">
                    共 {{ fileContents.csv.parsedData.totalRows }} 行数据（含表头）
                  </div>
                </div>
                <el-alert v-else title="CSV 文件解析失败或暂无数据" type="warning" :closable="false" show-icon />
              </div>

              <!-- 分析摘要 -->
              <div v-if="morphologicalAnalysisData" class="analysis-summary" style="margin-top: 20px;">
                <el-alert
                  :title="`分析完成 - ${morphologicalAnalysisData.message}`"
                  type="success"
                  :closable="false"
                  show-icon
                >
                  <p>生成文件：智能鉴定与三维全参数矩阵.xlsx、单体孔洞参数明细.csv</p>
                </el-alert>
              </div>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script>
import * as XLSX from 'xlsx'
import { getProject } from '@/api/project'
import { executeBinaryConversion, executeHoleDetection, executeDataPreprocessing, executeTargetHoleAnalysis, getTargetHoleProgress, executeMorphologicalAnalysis } from '@/api/hole-analysis'
import { getToken } from '@/utils/auth'
import VtkMedicalViewer from '@/components/VtkMedicalViewer.vue'
import HoleCutViewer3D from '@/components/HoleCutViewer3D.vue'
import Step4Viewer from '@/components/Step4Viewer.vue'

export default {
  name: 'ProjectDetail',
  components: {
    VtkMedicalViewer,
    HoleCutViewer3D,
    Step4Viewer
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
      showStep4Viewer: false, // 是否显示第四步3D预览
      targetHoleAnalysisLoading: false, // 目标孔洞分析是否正在进行中
      targetHoleResultImage: null, // 目标孔洞分析结果图像URL
      show3DViewerDialog: false, // 是否显示3D视图对话框
      // 第六步相关数据
      isAnalyzing: false, // 是否正在执行形态学分析
      activeFileType: 'excel', // 当前显示的文件类型：excel 或 csv
      activeSheetIndex: 0, // 当前选中的Excel Sheet索引
      morphologicalAnalysisData: null, // 形态学分析结果数据
      // 文件内容数据
      fileContents: {
        excel: {
          content: null,
          parsedData: null,
          filename: ''
        },
        csv: {
          content: null,
          parsedData: null,
          filename: ''
        }
      },

      // 实时进度显示相关数据
      showProgressBar: false, // 是否显示进度条
      currentProgress: 0, // 当前进度百分比
      currentProgressStatus: '请求发送中...', // 当前状态文字
      currentProgressMessage: '正在初始化API调用', // 当前详细消息
      progressTimer: null, // 轮询定时器
      pollCount: 0, // 轮询次数
      fetching3DData: false, // 是否正在获取3D数据

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
    },
    activeSheetData() {
      const sheets = this.fileContents.excel.parsedData && this.fileContents.excel.parsedData.sheets
      if (!sheets || sheets.length === 0) return null
      // 上层按钮 excel -> Sheet 0（智能鉴定与全局特征），csv -> Sheet 1（单体孔洞参数明细）
      const idx = this.activeFileType === 'csv' ? 1 : 0
      return sheets[idx] || null
    }
  },
  created() {
    this.loadProjectData()
  },
  beforeDestroy() {
    this.stopProgressPolling()
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
        } else if (stepIndex === 5) {
          // 第六步：形态学分析
          await this.executeMorphologicalAnalysis()
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

        // 调用后端API（返回 blob：VTP 文件）
        const response = await executeDataPreprocessing(projectId)

        if (response && response.status === 200) {
          // 更新步骤状态
          this.$set(this.stepStatus, 3, true)
          this.$forceUpdate()

          // 隐藏等待提示
          this.dataPreprocessingLoading = false

          this.$message({
            message: '数据预处理完成，正在加载3D模型...',
            type: 'success',
            duration: 3000,
            showClose: true
          })

          // 显示3D预览区域并加载模型
          this.showStep4Viewer = true
          await this.$nextTick()
          if (this.$refs.step4viewer) {
            await this.$refs.step4viewer.loadFromBlob(response.data)
          }
        } else {
          throw new Error('数据预处理执行失败')
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
      const projectId = this.project.id
      if (!projectId) {
        this.$message.error('项目ID不存在')
        return
      }

      this.targetHoleAnalysisLoading = true
      this.showProgressBar = true
      this.targetHoleResultImage = null
      this.currentProgress = 0
      this.currentProgressStatus = '请求发送中...'
      this.currentProgressMessage = '正在初始化API调用'
      this.pollCount = 0
      this.stopProgressPolling()

      try {
        const res = await executeTargetHoleAnalysis(projectId)
        if (res.code !== 200) {
          throw new Error(res.message || '启动分析失败')
        }
        this.currentProgressStatus = '请求已接受'
        this.currentProgressMessage = '服务器已接受分析请求，开始处理...'
        this.startProgressPolling(projectId)
      } catch (error) {
        this.targetHoleAnalysisLoading = false
        this.showProgressBar = false
        this.$message.error(error.message || '目标孔洞分析启动失败')
      }
    },

    // 启动轮询
    startProgressPolling(projectId) {
      this.progressTimer = setInterval(async() => {
        this.pollCount++
        // 超过300次（约10分钟）超时停止
        if (this.pollCount > 300) {
          this.stopProgressPolling()
          this.targetHoleAnalysisLoading = false
          this.showProgressBar = false
          this.$message.error('目标孔洞分析超时（超过10分钟）')
          return
        }
        try {
          const res = await getTargetHoleProgress(projectId)
          if (res.code !== 200) return
          const data = res.data
          this.currentProgress = data.progress || 0
          this.currentProgressStatus = data.status || ''
          this.currentProgressMessage = data.message || ''

          // 错误状态（progress===0 且已轮询过几次）
          if (data.progress === 0 && this.pollCount > 3 && data.status && data.status !== '等待开始') {
            this.stopProgressPolling()
            this.targetHoleAnalysisLoading = false
            this.showProgressBar = false
            this.$message.error('目标孔洞分析失败: ' + data.status)
            return
          }

          // 完成
          if (data.progress >= 100) {
            this.stopProgressPolling()
            this.currentProgress = 100
            this.currentProgressStatus = '目标孔洞分析成功'
            this.currentProgressMessage = '分析完成，正在获取3D数据...'
            this.$set(this.stepStatus, 4, true)
            setTimeout(() => {
              this.showProgressBar = false
              this.targetHoleAnalysisLoading = false
              this.fetching3DData = true
              this.show3DViewerDialog = true
            }, 1000)
          }
        } catch (e) {
          console.error('轮询进度失败:', e)
        }
      }, 2000)
    },

    // 停止轮询
    stopProgressPolling() {
      if (this.progressTimer) {
        clearInterval(this.progressTimer)
        this.progressTimer = null
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

    // 3D视图加载完成回调
    onViewer3DLoaded() {
      this.fetching3DData = false
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

    // 执行形态学分析（第六步）
    async executeMorphologicalAnalysis() {
      if (this.isAnalyzing) {
        this.$message.warning('正在执行形态学分析，请稍候')
        return
      }

      this.isAnalyzing = true
      this.$message.info('开始执行形态学分析，请稍候...')

      try {
        const projectId = this.project.id
        if (!projectId) {
          this.$message.error('项目ID不存在')
          return
        }

        // 调用后端API执行形态学分析（与其他步骤保持一致）
        const response = await executeMorphologicalAnalysis(projectId)

        if (response && response.code === 200) {
          // 保存分析结果数据
          this.morphologicalAnalysisData = response.data
          
          // 将文件内容存储到SessionStorage（确保用户数据隔离）
          try {
            const storageKey = `morphological_analysis_${projectId}`
            const storageData = {
              excel_content: response.data.excel_content,
              csv_content: response.data.csv_content,
              excel_filename: response.data.excel_filename,
              csv_filename: response.data.csv_filename,
              generated_time: new Date().toISOString()
            }
            sessionStorage.setItem(storageKey, JSON.stringify(storageData))
            console.log('文件内容已存储到SessionStorage')
          } catch (storageError) {
            console.error('存储到SessionStorage失败:', storageError)
          }
          
          // 解析文件内容并存储到组件数据中
          this.parseFileContents(response.data)
          
          // 标记第六步为完成状态
          this.$set(this.stepStatus, 5, true)
          
          // 强制重新计算进度
          this.$nextTick(() => {
            this.$forceUpdate()
          })
          
          this.$message.success('形态学分析执行完成，文件内容已接收并解析')
        } else {
          throw new Error(response?.message || '形态学分析执行失败')
        }
      } catch (error) {
        console.error('执行形态学分析失败:', error)
        this.$message.error(`形态学分析执行失败: ${error.message || '未知错误'}`)
      } finally {
        this.isAnalyzing = false
      }
    },

    // 下载形态学分析文件（从SessionStorage直接下载）- 已由 downloadBothFiles 替代，保留以备兼容
    async downloadFile(fileType) {
      try {
        const projectId = this.project.id
        if (!projectId) {
          this.$message.error('项目ID不存在')
          return
        }

        // 从SessionStorage获取文件内容
        const storageKey = `morphological_analysis_${projectId}`
        const storageData = sessionStorage.getItem(storageKey)
        
        if (!storageData) {
          this.$message.error('文件内容不存在，请先执行形态学分析')
          return
        }

        const parsedData = JSON.parse(storageData)
        const fileContent = fileType === 'excel' ? parsedData.excel_content : parsedData.csv_content
        const filename = fileType === 'excel' ? parsedData.excel_filename : parsedData.csv_filename

        if (!fileContent) {
          this.$message.error(`${fileType === 'excel' ? 'Excel' : 'CSV'}文件内容不存在`)
          return
        }

        // 将base64内容转换为Blob
        const binaryContent = atob(fileContent)
        const bytes = new Uint8Array(binaryContent.length)
        for (let i = 0; i < binaryContent.length; i++) {
          bytes[i] = binaryContent.charCodeAt(i)
        }
        
        const blob = new Blob([bytes], { 
          type: fileType === 'excel' ? 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' : 'text/csv' 
        })
        
        // 创建下载链接
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = filename
        
        // 触发下载
        document.body.appendChild(link)
        link.click()
        
        // 清理资源
        window.URL.revokeObjectURL(url)
        document.body.removeChild(link)
        
        this.$message.success(`开始下载${fileType === 'excel' ? 'Excel报告' : 'CSV明细'}`)
      } catch (error) {
        console.error('下载文件失败:', error)
        this.$message.error(`下载文件失败: ${error.message || '未知错误'}`)
      }
    },

    // 处理文件类型切换
    handleFileTypeSwitch(fileType) {
      this.activeFileType = fileType
      console.log(`切换到${fileType === 'excel' ? 'Excel报告' : 'CSV明细'}`)
    },

    // 解析文件内容（Excel 使用 SheetJS，CSV 解析为表格数据）
    parseFileContents(data) {
      try {
        // 解析 Excel
        if (data.excel_content) {
          this.fileContents.excel.content = data.excel_content
          this.fileContents.excel.filename = data.excel_filename
          try {
            const binaryStr = atob(data.excel_content)
            const bytes = new Uint8Array(binaryStr.length)
            for (let i = 0; i < binaryStr.length; i++) {
              bytes[i] = binaryStr.charCodeAt(i)
            }
            const workbook = XLSX.read(bytes, { type: 'array' })
            const sheets = workbook.SheetNames.map(name => {
              const ws = workbook.Sheets[name]
              const jsonData = XLSX.utils.sheet_to_json(ws, { header: 1, defval: '' })
              const headers = (jsonData[0] || []).map(h => String(h))
              const rows = jsonData.slice(1).map(row => row.map(c => (c === null || c === undefined) ? '' : String(c)))
              return { name, headers, rows }
            })
            this.fileContents.excel.parsedData = { sheets }
            this.activeSheetIndex = 0
          } catch (excelError) {
            console.error('Excel 解析失败:', excelError)
            this.fileContents.excel.parsedData = { sheets: [] }
          }
        }

        // 解析 CSV
        if (data.csv_content) {
          this.fileContents.csv.content = data.csv_content
          this.fileContents.csv.filename = data.csv_filename
          try {
            let csvText
            try {
              csvText = decodeURIComponent(escape(atob(data.csv_content)))
            } catch (e) {
              csvText = atob(data.csv_content)
            }
            const allLines = csvText.split('\n').filter(l => l.trim())
            const headers = allLines[0] ? allLines[0].split(',').map(h => h.trim()) : []
            const rows = allLines.slice(1).map(line => line.split(',').map(c => c.trim()))
            this.fileContents.csv.parsedData = { headers, rows, totalRows: allLines.length }
          } catch (csvError) {
            console.error('CSV 解析失败:', csvError)
            this.fileContents.csv.parsedData = { headers: [], rows: [], totalRows: 0 }
          }
        }

        console.log('文件内容解析完成')
      } catch (error) {
        console.error('文件内容解析失败:', error)
      }
    },

    // 一次性下载 Excel 和 CSV 两个文件
    async downloadBothFiles() {
      try {
        const projectId = this.project.id
        const storageKey = `morphological_analysis_${projectId}`
        const storageData = sessionStorage.getItem(storageKey)

        if (!storageData) {
          this.$message.error('文件内容不存在，请先执行形态学分析')
          return
        }

        const parsedData = JSON.parse(storageData)

        const downloadBlob = (base64, filename, mimeType) => {
          const binary = atob(base64)
          const bytes = new Uint8Array(binary.length)
          for (let i = 0; i < binary.length; i++) {
            bytes[i] = binary.charCodeAt(i)
          }
          const blob = new Blob([bytes], { type: mimeType })
          const url = window.URL.createObjectURL(blob)
          const link = document.createElement('a')
          link.href = url
          link.download = filename
          document.body.appendChild(link)
          link.click()
          window.URL.revokeObjectURL(url)
          document.body.removeChild(link)
        }

        if (parsedData.excel_content && parsedData.excel_filename) {
          downloadBlob(
            parsedData.excel_content,
            parsedData.excel_filename,
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
          )
        }

        // 短暂延迟，避免部分浏览器拦截连续下载
        await new Promise(resolve => setTimeout(resolve, 600))

        if (parsedData.csv_content && parsedData.csv_filename) {
          downloadBlob(parsedData.csv_content, parsedData.csv_filename, 'text/csv;charset=utf-8;')
        }

        this.$message.success('已开始下载 Excel 报告和 CSV 明细')
      } catch (error) {
        console.error('下载文件失败:', error)
        this.$message.error(`下载失败: ${error.message || '未知错误'}`)
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

/* 分析结果表格样式 */
.analysis-table-wrap {
  overflow-x: auto;
  max-height: 500px;
  overflow-y: auto;
  border: 1px solid #ebeef5;
  border-radius: 4px;
}

.analysis-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  white-space: nowrap;
}

.analysis-table th,
.analysis-table td {
  border: 1px solid #ebeef5;
  padding: 6px 12px;
  text-align: left;
}

.analysis-table thead th {
  background: #f5f7fa;
  font-weight: 600;
  color: #606266;
  position: sticky;
  top: 0;
  z-index: 1;
}

.analysis-table tbody tr:hover {
  background: #f0f8ff;
}
</style>
