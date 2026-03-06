<template>
  <div class="dashboard-container">
    <div class="dashboard-card">
      <h2>欢迎使用孔洞分析软件</h2>
      <p>这是孔洞分析软件的首页，您可以在这里查看系统状态和快速访问主要功能。</p>
      <div class="dashboard-actions">
        <el-button type="primary" size="medium">开始新分析</el-button>
        <el-button size="medium">查看历史记录</el-button>
      </div>
    </div>

    <div class="dashboard-stats">
      <el-row :gutter="20">
        <el-col :xs="12" :sm="12" :md="6" :lg="6" :xl="6">
          <div class="stat-card">
            <div class="stat-icon primary">
              <svg-icon icon-class="documentation" />
            </div>
            <div class="stat-content">
              <div class="stat-number">0</div>
              <div class="stat-desc">今日分析</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="12" :md="6" :lg="6" :xl="6">
          <div class="stat-card">
            <div class="stat-icon success">
              <svg-icon icon-class="list" />
            </div>
            <div class="stat-content">
              <div class="stat-number">0</div>
              <div class="stat-desc">历史记录</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="12" :md="6" :lg="6" :xl="6">
          <div class="stat-card">
            <div class="stat-icon warning">
              <svg-icon icon-class="eye" />
            </div>
            <div class="stat-content">
              <div class="stat-number">0</div>
              <div class="stat-desc">分析图表</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="12" :md="6" :lg="6" :xl="6">
          <div class="stat-card">
            <div class="stat-icon info">
              <svg-icon icon-class="setting" />
            </div>
            <div class="stat-content">
              <div class="stat-number">v1.0.0</div>
              <div class="stat-desc">系统版本</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Dashboard',
  data() {
    return {
      // 后续可以在这里添加数据
    }
  },
  created() {
    // 可以在这里获取初始数据
  },
  methods: {
    // 后续添加方法
  }
}
</script>

<style lang="scss" scoped>
.dashboard-container {
  padding: 20px;
}

.dashboard-card {
  background: #fff;
  border-radius: 6px;
  padding: 30px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  h2 {
    color: #262626;
    margin-bottom: 10px;
  }
  p {
    color: #8c8c8c;
    margin-bottom: 20px;
  }
  .dashboard-actions {
    display: flex;
    gap: 10px;
  }
}

.dashboard-stats {
  .stat-card {
    background: #fff;
    border-radius: 6px;
    padding: 20px;
    display: flex;
    align-items: center;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    .stat-icon {
      width: 50px;
      height: 50px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-right: 15px;
      &.primary {
        background: #e6f7ff;
        color: #1890ff;
      }
      &.success {
        background: #f6ffed;
        color: #52c41a;
      }
      &.warning {
        background: #fff7e6;
        color: #fa8c16;
      }
      &.info {
        background: #f0f5ff;
        color: #722ed1;
      }
    }
    .stat-content {
      .stat-number {
        font-size: 24px;
        font-weight: bold;
        color: #262626;
      }
      .stat-desc {
        color: #8c8c8c;
        font-size: 14px;
      }
    }
  }
}
</style>
