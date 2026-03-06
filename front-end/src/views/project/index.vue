<template>
  <div class="project-container">
    <div class="project-header">
      <h2>项目管理</h2>
      <el-button type="primary" icon="el-icon-plus" @click="handleCreate">创建项目</el-button>
    </div>
    <div class="project-content">
      <el-card class="project-list">
        <div v-if="loading" class="loading-container">
          <el-skeleton :rows="5" animated />
        </div>
        <div v-else-if="projects.length === 0" class="empty-project">
          <el-empty description="暂无项目" />
        </div>
        <el-table v-else :data="projects" style="width: 100%">
          <el-table-column prop="project_name" label="项目名" width="200" />
          <el-table-column prop="created_time" label="创建时间" width="180" />
          <el-table-column label="操作" width="150" fixed="right">
            <template slot-scope="scope">
              <el-button type="primary" size="small" @click="handleEnter(scope.row.id)">进入项目</el-button>
              <el-button type="danger" size="small" @click="handleDelete(scope.row.id)">删除项目</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<script>
import { getProjects, deleteProject } from '@/api/project'
import { createLog, LOG_TYPES } from '@/api/logs'

export default {
  name: 'ProjectList',
  data() {
    return {
      projects: [],
      loading: false
    }
  },
  mounted() {
    // 加载项目数据
    this.loadProjects()
  },
  methods: {
    async loadProjects() {
      this.loading = true
      try {
        // 调用后端API获取项目列表
        const response = await getProjects()
        if (response && response.data) {
          this.projects = response.data.projects || []
        }
      } catch (error) {
        console.error('获取项目列表失败:', error)
        this.$message.error('获取项目列表失败')
        // 清空项目列表，避免显示错误数据
        this.projects = []
      } finally {
        this.loading = false
      }
    },
    handleCreate() {
      this.$router.push('/projects/create')
    },
    handleEnter(projectId) {
      this.$router.push(`/projects/detail/${projectId}`)
    },
    async handleDelete(projectId) {
      this.$confirm('确定要删除这个项目吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async() => {
        try {
          // 调用后端API删除项目
          await deleteProject(projectId)

          // 从列表中移除已删除的项目
          this.projects = this.projects.filter(item => item.id !== projectId)
          this.$message.success('项目删除成功')
        } catch (error) {
          console.error('删除项目失败:', error)
          this.$message.error('项目删除失败')
        }
      }).catch(() => {
        this.$message.info('已取消删除')
      })
    }
  }
}
</script>

<style scoped>
.project-container {
  padding: 20px;
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.project-header h2 {
  margin: 0;
  color: #303133;
}

.project-list {
  width: 100%;
}

.empty-project {
  padding: 50px 0;
  text-align: center;
}
</style>
