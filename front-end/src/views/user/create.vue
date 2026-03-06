<template>
  <div class="create-user-container">
    <div class="page-header">
      <el-button icon="el-icon-arrow-left" style="margin-right: 20px;" @click="goBack">返回</el-button>
      <h2>添加用户</h2>
    </div>

    <el-card>
      <el-form ref="userForm" :model="userForm" :rules="rules" label-width="120px" class="user-form">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" placeholder="请输入用户名" />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input v-model="userForm.password" type="password" placeholder="请输入密码" />
        </el-form-item>

        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="userForm.confirmPassword" type="password" placeholder="请再次输入密码" />
        </el-form-item>

        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" placeholder="请输入邮箱" />
        </el-form-item>

        <el-form-item label="角色" prop="role">
          <el-radio-group v-model="userForm.role">
            <el-radio label="user">普通用户</el-radio>
            <el-radio label="admin">管理员</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="状态">
          <el-switch v-model="userForm.status" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="submitForm('userForm')">添加用户</el-button>
          <el-button @click="resetForm('userForm')">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'CreateUser',
  data() {
    // 密码一致性验证
    const validatePassword = (rule, value, callback) => {
      if (value !== this.userForm.password) {
        callback(new Error('两次输入的密码不一致'))
      } else {
        callback()
      }
    }

    return {
      userForm: {
        username: '',
        password: '',
        confirmPassword: '',
        email: '',
        role: 'user',
        status: true
      },
      rules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' },
          { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, message: '密码长度不能少于 6 个字符', trigger: 'blur' }
        ],
        confirmPassword: [
          { required: true, message: '请确认密码', trigger: 'blur' },
          { validator: validatePassword, trigger: 'blur' }
        ],
        email: [
          { required: true, message: '请输入邮箱', trigger: 'blur' },
          { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
        ]
      }
    }
  },
  methods: {
    submitForm(formName) {
      this.$refs[formName].validate((valid) => {
        if (valid) {
          // 从localStorage获取现有用户数据
          const users = JSON.parse(localStorage.getItem('systemUsers') || '[]')

          // 创建新用户
          const newUser = {
            id: Date.now(), // 生成唯一ID
            ...this.userForm,
            createTime: new Date().toLocaleString('zh-CN'),
            // 移除确认密码字段
            confirmPassword: undefined
          }

          // 添加新用户到数组
          users.push(newUser)

          // 保存回localStorage
          localStorage.setItem('systemUsers', JSON.stringify(users))

          // 显示成功提示并跳转
          setTimeout(() => {
            this.$message.success('用户添加成功')
            // 跳回到用户列表页面
            this.$router.push('/admin')
          }, 300)
        } else {
          this.$message.error('表单验证失败，请检查输入')
          return false
        }
      })
    },

    resetForm(formName) {
      this.$refs[formName].resetFields()
    },

    goBack() {
      this.$router.push('/admin')
    }
  }
}
</script>

<style scoped>
.create-user-container {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
}

.page-header h2 {
  margin: 0;
  color: #303133;
}

.user-form {
  max-width: 600px;
}
</style>
