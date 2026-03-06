<template>
  <div class="navbar">
    <!-- 返回按钮 -->
    <div class="back-button" @click="goBack">
      <i class="el-icon-arrow-left" style="font-size: 20px;" />
    </div>
    <hamburger :is-active="sidebar.opened" class="hamburger-container" @toggleClick="toggleSideBar" />
    <breadcrumb class="breadcrumb-container" />

    <div class="right-menu">
      <el-dropdown class="avatar-container" trigger="click">
        <div class="avatar-wrapper">
          <img :src="getAvatarUrl(avatar)" class="user-avatar">
          <i class="el-icon-caret-bottom" />
        </div>
        <el-dropdown-menu slot="dropdown" class="user-dropdown">
          <el-dropdown-item divided @click.native="logout">
            <span style="display:block;">退出登录</span>
          </el-dropdown-item>
        </el-dropdown-menu>
      </el-dropdown>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import { resetRouter } from '@/router'
import Breadcrumb from '@/components/Breadcrumb'
import Hamburger from '@/components/Hamburger'

export default {
  components: {
    Breadcrumb,
    Hamburger
  },
  computed: {
    ...mapGetters([
      'sidebar',
      'avatar'
    ])
  },
  methods: {
    toggleSideBar() {
      this.$store.dispatch('app/toggleSideBar')
    },
    getAvatarUrl(avatar) {
      // 处理头像URL，避免错误的URL拼接
      if (!avatar) {
        // 返回默认头像
        return 'https://api.dicebear.com/7.x/initials/svg?seed=User'
      }
      // 如果已经是完整的URL，直接返回
      if (avatar.startsWith('http')) {
        return avatar
      }
      // 如果是相对路径，添加基础URL
      return avatar
    },
    async logout() {
      try {
        // 显示退出确认对话框
        await this.$confirm('确定要退出系统吗？退出后将需要重新登录。', '退出确认', {
          confirmButtonText: '确定退出',
          cancelButtonText: '取消',
          type: 'warning'
        })
        // 用户确认退出，执行登出操作
        await this.$store.dispatch('user/logout')
        // 登出成功后重定向到登录页面
        this.$router.push('/login')
      } catch (error) {
        // 如果用户取消退出，不执行任何操作
        if (error === 'cancel') {
          this.$message.info('已取消退出，继续使用系统')
          return
        }
        console.error('登出失败:', error)
        // 即使API调用失败，也要确保清除本地状态
        await this.$store.dispatch('user/resetToken')
        resetRouter()
        // API调用失败时也重定向到登录页面
        this.$router.push('/login')
      }
    },
    goBack() {
      // 实现返回功能
      this.$router.back()
    }
  }
}
</script>

<style lang="scss" scoped>
.navbar {
  height: 50px;
  overflow: hidden;
  position: relative;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0,21,41,.08);

  .back-button {
    line-height: 46px;
    height: 100%;
    float: left;
    padding: 0 10px;
    cursor: pointer;
    transition: background .3s;
    -webkit-tap-highlight-color:transparent;

    &:hover {
      background: rgba(0, 0, 0, .025)
    }
  }

  .hamburger-container {
    line-height: 46px;
    height: 100%;
    float: left;
    cursor: pointer;
    transition: background .3s;
    -webkit-tap-highlight-color:transparent;

    &:hover {
      background: rgba(0, 0, 0, .025)
    }
  }

  .breadcrumb-container {
    float: left;
  }

  .right-menu {
    float: right;
    height: 100%;
    line-height: 50px;

    &:focus {
      outline: none;
    }

    .right-menu-item {
      display: inline-block;
      padding: 0 8px;
      height: 100%;
      font-size: 18px;
      color: #5a5e66;
      vertical-align: text-bottom;

      &.hover-effect {
        cursor: pointer;
        transition: background .3s;

        &:hover {
          background: rgba(0, 0, 0, .025)
        }
      }
    }

    .avatar-container {
      margin-right: 30px;

      .avatar-wrapper {
        margin-top: 5px;
        position: relative;

        .user-avatar {
          cursor: pointer;
          width: 40px;
          height: 40px;
          border-radius: 10px;
        }

        .el-icon-caret-bottom {
          cursor: pointer;
          position: absolute;
          right: -20px;
          top: 25px;
          font-size: 12px;
        }
      }
    }
  }
}
</style>
