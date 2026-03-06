<template>
  <div class="audit-container">
    <div class="audit-header">
      <h2>系统日志审计</h2>
      <div class="filter-container">
        <el-form :inline="true" :model="filterForm" class="demo-form-inline">
          <el-form-item label="操作类型">
            <el-select v-model="filterForm.operation_type" placeholder="请选择操作类型" clearable>
              <el-option label="用户登入" value="USER_LOGIN" />
              <el-option label="用户登出" value="USER_LOGOUT" />
              <el-option label="创建项目" value="PROJECT_CREATE" />
              <el-option label="删除项目" value="PROJECT_DELETE" />
            </el-select>
          </el-form-item>
          <el-form-item label="用户名">
            <el-input v-model="filterForm.username" placeholder="请输入用户名" clearable />
          </el-form-item>
          <el-form-item label="开始日期">
            <el-date-picker
              v-model="filterForm.start_date"
              type="date"
              placeholder="选择开始日期"
              value-format="yyyy-MM-dd"
              clearable
            />
          </el-form-item>
          <el-form-item label="结束日期">
            <el-date-picker
              v-model="filterForm.end_date"
              type="date"
              placeholder="选择结束日期"
              value-format="yyyy-MM-dd"
              clearable
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">查询</el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>
    <div class="audit-content">
      <el-card>
        <el-table v-loading="loading" :data="auditLogs" style="width: 100%">
          <el-table-column prop="username" label="用户名" width="120" />
          <el-table-column prop="project_name" label="项目名" width="150">
            <template slot-scope="scope">
              {{ scope.row.project_name || '无' }}
            </template>
          </el-table-column>
          <el-table-column prop="operation_type" label="操作" width="150">
            <template slot-scope="scope">
              <el-tag :type="getActionType(scope.row.operation_type)">{{ getOperationName(scope.row.operation_type) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="operation_time" label="操作时间" width="180">
            <template slot-scope="scope">
              {{ formatLocalTime(scope.row.operation_time) }}
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="80">
            <template slot-scope="scope">
              <el-tag :type="scope.row.status === 'success' ? 'success' : 'danger'">
                {{ scope.row.status === 'success' ? '成功' : '失败' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination-container">
          <el-pagination
            :current-page="pagination.currentPage"
            :page-sizes="[10, 20, 50, 100]"
            :page-size="pagination.pageSize"
            layout="total, sizes, prev, pager, next, jumper"
            :total="pagination.total"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </el-card>
    </div>
  </div>
</template>

<script>
import { getLogs } from '@/api/logs'

export default {
  name: 'AuditLog',
  data() {
    return {
      auditLogs: [],
      loading: false,
      filterForm: {
        operation_type: '',
        username: '',
        start_date: '',
        end_date: ''
      },
      pagination: {
        currentPage: 1,
        pageSize: 10,
        total: 0
      }
    }
  },
  mounted() {
    this.fetchLogs()
  },
  methods: {
    async fetchLogs() {
      this.loading = true
      try {
        const params = {
          page: this.pagination.currentPage,
          per_page: this.pagination.pageSize,
          ...this.filterForm
        }

        // 移除空值参数
        Object.keys(params).forEach(key => {
          if (params[key] === '' || params[key] === null || params[key] === undefined) {
            delete params[key]
          }
        })

        const response = await getLogs(params)
        if (response && response.data) {
          this.auditLogs = response.data.logs || []
          this.pagination.total = response.data.total || 0
        }
      } catch (error) {
        console.error('获取日志列表失败:', error)
        this.$message.error('获取日志列表失败')
      } finally {
        this.loading = false
      }
    },

    handleSearch() {
      this.pagination.currentPage = 1
      this.fetchLogs()
    },

    handleReset() {
      this.filterForm = {
        operation_type: '',
        username: '',
        start_date: '',
        end_date: ''
      }
      this.pagination.currentPage = 1
      this.fetchLogs()
    },

    handleSizeChange(pageSize) {
      this.pagination.pageSize = pageSize
      this.pagination.currentPage = 1
      this.fetchLogs()
    },

    handleCurrentChange(currentPage) {
      this.pagination.currentPage = currentPage
      this.fetchLogs()
    },

    getActionType(action) {
      const typeMap = {
        // 登入登出操作 - 统一为蓝色系
        'USER_LOGIN': 'info',
        'USER_LOGOUT': 'info',

        // 项目操作 - 统一为绿色系
        'PROJECT_CREATE': 'success',
        'PROJECT_DELETE': 'success'

        // 预留其他核心流程操作 - 橙色系
        // 'DATA_ANALYSIS': 'warning',
        // 'REPORT_GENERATE': 'warning',
        // 'SYSTEM_CONFIG': 'warning'
      }
      return typeMap[action] || 'default'
    },

    getOperationName(operationType) {
      const operationMap = {
        'USER_LOGIN': '用户登入',
        'USER_LOGOUT': '用户登出',
        'PROJECT_CREATE': '创建项目',
        'PROJECT_DELETE': '删除项目'
      }
      return operationMap[operationType] || operationType
    },

    formatLocalTime(localTimeString) {
      if (!localTimeString) return ''

      // 后端返回的是已经格式化的本地时间字符串，直接返回即可
      return localTimeString
    }
  }
}
</script>

<style scoped>
.audit-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 84px);
}

.audit-header {
  margin-bottom: 20px;
  background: #fff;
  padding: 20px;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.audit-header h2 {
  margin: 0 0 20px 0;
  color: #303133;
  font-size: 20px;
  font-weight: 600;
}

.filter-container {
  margin-top: 20px;
}

.audit-content {
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.pagination-container {
  padding: 20px;
  text-align: right;
  border-top: 1px solid #ebeef5;
}

.demo-form-inline {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
}

.demo-form-inline .el-form-item {
  margin-right: 20px;
  margin-bottom: 10px;
}

.el-table {
  margin: 0;
}

.el-table .el-tag {
  margin: 2px 0;
}
</style>
