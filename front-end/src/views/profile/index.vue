<template>
  <div class="profile-container">
    <div class="profile-header">
      <h2>个人信息</h2>
      <el-button v-if="!isEditing" type="primary" @click="startEdit">编辑信息</el-button>
    </div>
    <div class="profile-content">
      <el-card class="profile-card">
        <div class="user-avatar">
          <img :src="userInfo.avatar" alt="用户头像" class="avatar-img">
        </div>
        <!-- 查看模式 -->
        <div v-if="!isEditing" class="user-info">
          <div class="info-item">
            <span class="label">用户名：</span>
            <span class="value">{{ userInfo.name }}</span>
          </div>
          <div class="info-item">
            <span class="label">用户ID：</span>
            <span class="value">{{ userInfo.userId }}</span>
          </div>
          <div class="info-item">
            <span class="label">角色：</span>
            <span class="value">{{ userInfo.roles.join(', ') }}</span>
          </div>
          <div class="info-item">
            <span class="label">登录时间：</span>
            <span class="value">{{ loginTime }}</span>
          </div>
        </div>
        <!-- 编辑模式 -->
        <el-form v-if="isEditing" ref="editForm" :model="editForm" :rules="rules" label-width="100px">
          <el-divider>修改密码</el-divider>
          <el-form-item label="旧密码" prop="oldPassword">
            <el-input v-model="editForm.oldPassword" type="password" placeholder="请输入旧密码" show-password />
          </el-form-item>
          <el-form-item label="新密码" prop="newPassword">
            <el-input v-model="editForm.newPassword" type="password" placeholder="请输入新密码" show-password />
          </el-form-item>
          <el-form-item label="确认新密码" prop="confirmPassword">
            <el-input v-model="editForm.confirmPassword" type="password" placeholder="请再次输入新密码" show-password />
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="handleSave">保存</el-button>
            <el-button @click="cancelEdit">取消</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import { updateProfile } from '@/api/user'
export default {
  name: 'Profile',
  data() {
    return {
      userInfo: {
        name: '',
        avatar: '',
        userId: '',
        roles: [],
        email: ''
      },
      editForm: {
        oldPassword: '',
        newPassword: '',
        confirmPassword: ''
      },
      loginTime: '',
      isEditing: false,
      rules: {
        oldPassword: [
          { required: false, message: '请输入旧密码', trigger: 'blur' }
        ],
        newPassword: [
          { required: false, message: '请输入新密码', trigger: 'blur' },
          { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' }
        ],
        confirmPassword: [
          { required: false, message: '请再次输入新密码', trigger: 'blur' },
          { validator: (rule, value, callback) => this.validateConfirmPassword(rule, value, callback), trigger: 'blur' }
        ]
      }
    }
  },
  computed: {
    // 从store中获取用户信息
    ...mapGetters(['name', 'avatar', 'userId', 'roles'])
  },
  created() {
    this.loadUserData()
    this.loginTime = new Date().toLocaleString()
  },
  methods: {
    loadUserData() {
      // 获取用户信息
      // 优先从localStorage获取数据，确保保存的数据能够被读取
      const userData = JSON.parse(localStorage.getItem('currentUser') || '{}')
      this.userInfo = {
        name: userData.name || this.name || '用户',
        avatar: userData.avatar || this.avatar || 'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif',
        userId: this.userId || 'N/A',
        roles: this.roles || ['普通用户'],
        email: userData.email || ''
      }
    },
    // 开始编辑
    startEdit() {
      // 复制用户信息到编辑表单
      this.editForm = {
        oldPassword: '',
        newPassword: '',
        confirmPassword: ''
      }
      this.isEditing = true
    },
    // 取消编辑
    cancelEdit() {
      this.isEditing = false
      // 重置编辑表单
      this.editForm = {
        oldPassword: '',
        newPassword: '',
        confirmPassword: ''
      }
    },
    // 验证确认密码
    validateConfirmPassword(rule, value, callback) {
      if (value !== this.editForm.newPassword) {
        callback(new Error('两次输入的密码不一致'))
      } else {
        callback()
      }
    },
    // 检查是否需要修改密码
    needChangePassword() {
      return this.editForm.oldPassword || this.editForm.newPassword || this.editForm.confirmPassword
    },
    // 验证密码修改逻辑
    validatePasswordChange() {
      if (this.needChangePassword()) {
        if (!this.editForm.oldPassword) {
          this.$message.error('修改密码必须输入旧密码')
          return false
        }
        if (!this.editForm.newPassword) {
          this.$message.error('请输入新密码')
          return false
        }
        if (!this.editForm.confirmPassword) {
          this.$message.error('请确认新密码')
          return false
        }
        if (this.editForm.newPassword !== this.editForm.confirmPassword) {
          this.$message.error('两次输入的新密码不一致')
          return false
        }
      }
      return true
    },
    // 保存编辑
    handleSave() {
      this.$refs.editForm.validate((valid) => {
        if (valid) {
          // 验证密码修改逻辑
          if (!this.validatePasswordChange()) {
            return
          }

          // 检查是否有实际修改
          const hasChanges = this.needChangePassword()

          if (!hasChanges) {
            this.$message.warning('没有检测到任何修改')
            return
          }

          this.updateUserInfo()
        } else {
          this.$message.error('请正确填写表单')
        }
      })
    },
    // 调用API更新用户信息
    async updateUserInfo() {
      try {
        // 准备更新数据
        const updateData = {}

        // 如果修改了密码
        if (this.needChangePassword()) {
          updateData.old_password = this.editForm.oldPassword
          updateData.new_password = this.editForm.newPassword
        }

        const response = await updateProfile(updateData)

        if (response.code === 200) {
          // 如果修改了密码，给出成功提示并保持在个人信息界面
          if (this.needChangePassword()) {
            this.$message.success('密码已更改')
            this.$message.info('密码修改成功，您可以继续使用系统')
          } else {
            this.$message.success('个人信息更新成功')
          }

          // 取消编辑模式，返回查看模式
          this.cancelEdit()

          // 刷新用户信息，确保显示最新数据
          this.loadUserData()
        } else {
          this.$message.error(response.msg || '密码修改失败')
        }
      } catch (error) {
        console.error('修改密码失败:', error)
        this.$message.error('密码修改失败，请稍后重试')
      }
    }
  }
}
</script>

<style scoped>
.profile-container {
  padding: 20px;
}

.profile-header {
  margin-bottom: 20px;
}

.profile-header h2 {
  margin: 0;
  color: #303133;
}

.profile-card {
  width: 100%;
}

.user-avatar {
  text-align: center;
  margin-bottom: 20px;
}

.avatar-img {
  width: 100px;
  height: 100px;
  border-radius: 50%;
}

.user-info {
  padding: 20px;
}

.info-item {
  margin-bottom: 15px;
  display: flex;
  align-items: center;
}

.label {
  font-weight: bold;
  color: #606266;
  width: 100px;
}

.value {
  color: #303133;
}
</style>

