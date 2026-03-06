<template>
  <div class="project-create-container">
    <div class="project-create-header">
      <h2>创建项目</h2>
    </div>
    <div class="project-create-content">
      <el-card>
        <el-form ref="projectForm" :model="projectForm" :rules="rules" label-width="100px">
          <el-form-item label="项目名称" prop="name">
            <el-input v-model="projectForm.name" placeholder="请输入项目名称" />
          </el-form-item>
          <el-form-item label="项目描述" prop="description">
            <el-input
              v-model="projectForm.description"
              type="textarea"
              :rows="3"
              placeholder="请输入项目描述"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSubmit">创建</el-button>
            <el-button @click="handleCancel">取消</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script>
import { createProject } from '@/api/project'
import { createLog, LOG_TYPES } from '@/api/logs'

export default {
  name: 'ProjectCreate',
  data() {
    return {
      projectForm: {
        name: '',
        description: ''
      },
      rules: {
        name: [
          { required: true, message: '请输入项目名称', trigger: 'blur' },
          { min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur' }
        ]
      },
      loading: false
    }
  },
  methods: {
    async handleSubmit() {
      this.$refs.projectForm.validate(async(valid) => {
        if (valid) {
          this.loading = true
          try {
            // 调用后端API创建项目
            const response = await createProject({
              project_name: this.projectForm.name,
              description: this.projectForm.description
            })

            if (response && response.data) {
              const projectData = response.data

              this.$message.success('项目创建成功')
              // 创建成功后返回项目列表
              this.$router.push('/projects/index')
            }
          } catch (error) {
            console.error('创建项目失败:', error)
            this.$message.error('项目创建失败')
          } finally {
            this.loading = false
          }
        }
      })
    },
    handleCancel() {
      this.$router.push('/projects/index')
    }
  }
}
</script>

<style scoped>
.project-create-container {
  padding: 20px;
}

.project-create-header {
  margin-bottom: 20px;
}

.project-create-header h2 {
  margin: 0;
  color: #303133;
}
</style>
