<template>
  <div class="register-container">
    <div class="register-wrapper">
      <div class="register-form-card">
        <el-form ref="registerForm" :model="registerForm" :rules="registerRules" class="register-form" auto-complete="on" label-position="left">
          <!-- 错误提示 -->
          <div v-if="errorMsg" class="error-message">
            <svg-icon icon-class="error" />
            {{ errorMsg }}
          </div>

          <div class="title-container">
            <h3 class="title">创建账号</h3>
            <p class="subtitle">填写以下信息完成注册</p>
          </div>

          <el-form-item prop="username">
            <span class="svg-container">
              <svg-icon icon-class="user" />
            </span>
            <el-input
              ref="username"
              v-model="registerForm.username"
              placeholder="用户名"
              name="username"
              type="text"
              tabindex="1"
              auto-complete="on"
            />
          </el-form-item>

          <el-form-item prop="password">
            <span class="svg-container">
              <svg-icon icon-class="password" />
            </span>
            <el-input
              :key="passwordType"
              ref="password"
              v-model="registerForm.password"
              :type="passwordType"
              placeholder="密码（至少6位）"
              name="password"
              tabindex="2"
              auto-complete="on"
            />
            <span class="show-pwd" @click="showPwd">
              <svg-icon :icon-class="passwordType === 'password' ? 'eye' : 'eye-open'" />
            </span>
          </el-form-item>

          <el-form-item prop="confirmPassword">
            <span class="svg-container">
              <svg-icon icon-class="password" />
            </span>
            <el-input
              :key="confirmPasswordType"
              ref="confirmPassword"
              v-model="registerForm.confirmPassword"
              :type="confirmPasswordType"
              placeholder="确认密码"
              name="confirmPassword"
              tabindex="3"
              auto-complete="on"
              @keyup.enter.native="handleRegister"
            />
            <span class="show-pwd" @click="showConfirmPwd">
              <svg-icon :icon-class="confirmPasswordType === 'password' ? 'eye' : 'eye-open'" />
            </span>
          </el-form-item>

          <div class="form-actions">
            <el-button :loading="loading" type="primary" class="register-button" @click.native.prevent="handleRegister">注册</el-button>

            <!-- 登录入口链接 -->
            <div class="login-link">
              已有账号？ <router-link to="/login">返回登录</router-link>
            </div>
          </div>

        </el-form>
      </div>
    </div>
  </div>
</template>

<script>
// 导入注册API
import { register } from '@/api/user'

export default {
  name: 'Register',
  data() {
    const validateUsername = (rule, value, callback) => {
      if (!value) {
        callback(new Error('请输入用户名'))
      } else if (value.length < 3) {
        callback(new Error('用户名长度不能少于3位'))
      } else if (value.length > 20) {
        callback(new Error('用户名长度不能超过20位'))
      } else {
        callback()
      }
    }

    const validatePassword = (rule, value, callback) => {
      if (!value) {
        callback(new Error('请输入密码'))
      } else if (value.length < 6) {
        callback(new Error('密码长度不能少于6位'))
      } else {
        // 密码强度验证
        if (!/^(?=.*[a-zA-Z])(?=.*\d).{6,}$/.test(value)) {
          callback(new Error('密码必须包含字母和数字'))
        } else {
          callback()
        }
      }
    }

    const validateConfirmPassword = (rule, value, callback) => {
      if (!value) {
        callback(new Error('请确认密码'))
      } else if (value !== this.registerForm.password) {
        callback(new Error('两次输入的密码不一致'))
      } else {
        callback()
      }
    }

    return {
      registerForm: {
        username: '',
        password: '',
        confirmPassword: ''
      },
      registerRules: {
        username: [{ required: true, trigger: 'blur', validator: validateUsername }],
        password: [{ required: true, trigger: 'blur', validator: validatePassword }],
        confirmPassword: [{ required: true, trigger: 'blur', validator: validateConfirmPassword }]
      },
      loading: false,
      passwordType: 'password',
      confirmPasswordType: 'password',
      errorMsg: ''
    }
  },
  methods: {
    showPwd() {
      this.passwordType = this.passwordType === 'password' ? '' : 'password'
      this.$nextTick(() => {
        this.$refs.password.focus()
      })
    },

    showConfirmPwd() {
      this.confirmPasswordType = this.confirmPasswordType === 'password' ? '' : 'password'
      this.$nextTick(() => {
        this.$refs.confirmPassword.focus()
      })
    },

    handleRegister() {
      // 清除之前的错误信息
      this.errorMsg = ''

      this.$refs.registerForm.validate(valid => {
        if (valid) {
          this.loading = true

          // 准备注册数据（只需要用户名和密码）
          const registerData = {
            username: this.registerForm.username,
            password: this.registerForm.password
          }

          // 调用注册API
          register(registerData).then(() => {
            this.$message.success('注册成功，请登录')
            // 使用replace而不是push，避免用户从登录页返回注册页（因为注册已完成）
            this.$router.replace('/login')
            this.loading = false
          }).catch((error) => {
            // 显示后端返回的错误信息
            this.errorMsg = error.response?.data?.message || '注册失败，请稍后重试'
            this.loading = false
            this.$message.error(this.errorMsg)
          })
        } else {
          console.log('表单验证失败')
          return false
        }
      })
    }
  }
}
</script>

<style lang="scss" scoped>
// 复用登录页面的样式变量
$bg:#2d3a4b;
$dark_gray:#889aa4;
$light_gray:#eee;
$primary-color: #409eff;
$error-color: #f56c6c;
$form-bg: rgba(45, 58, 75, 0.8);

// 复用登录页面的布局和样式结构
.register-container {
  min-height: 100vh;
  width: 100%;
  background: linear-gradient(135deg, $bg 0%, #1a202c 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;

  // 添加背景装饰
  &::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url('~@/assets/images/login-bg.svg') center no-repeat;
    background-size: cover;
    opacity: 0.1;
    z-index: 0;
  }
}

.register-wrapper {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 520px;
  animation: fadeIn 0.5s ease-in-out;
}

.register-form-card {
  background: $form-bg;
  border-radius: 12px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
  overflow: hidden;
  transition: transform 0.3s ease;

  &:hover {
    transform: translateY(-5px);
  }
}

.register-form {
  padding: 40px;
  width: 100%;
}

// 错误提示样式
.error-message {
  background: rgba($error-color, 0.1);
  border: 1px solid rgba($error-color, 0.3);
  color: lighten($error-color, 10%);
  padding: 10px 15px;
  border-radius: 5px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  animation: shake 0.5s ease-in-out;

  svg {
    margin-right: 8px;
  }
}

.title-container {
  text-align: center;
  margin-bottom: 30px;

  .title {
    font-size: 28px;
    color: $light_gray;
    margin: 0 0 10px 0;
    font-weight: 600;
    letter-spacing: 1px;
  }

  .subtitle {
    font-size: 14px;
    color: $dark_gray;
    margin: 0;
  }
}

.svg-container {
  padding: 6px 10px 6px 15px;
  color: $dark_gray;
  vertical-align: middle;
  width: 40px;
  display: inline-block;
}

.show-pwd {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 18px;
  color: $dark_gray;
  cursor: pointer;
  user-select: none;
  transition: color 0.3s ease;

  &:hover {
    color: $primary-color;
  }
}

// 表单操作区域
.form-actions {
  margin-top: 30px;
}

.register-button {
  width: 100%;
  height: 45px;
  font-size: 16px;
  font-weight: 500;
  border-radius: 5px;
}

// 登录入口链接样式
.login-link {
  text-align: center;
  margin-top: 20px;
  font-size: 14px;
  color: $dark_gray;

  a {
    color: $primary-color;
    text-decoration: none;
    transition: color 0.3s ease;

    &:hover {
      color: lighten($primary-color, 10%);
      text-decoration: underline;
    }
  }
}

// 动画效果
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
  20%, 40%, 60%, 80% { transform: translateX(5px); }
}

// 响应式设计
@media (max-width: 576px) {
  .register-form {
    padding: 30px 20px;
  }

  .title-container .title {
    font-size: 24px;
  }
}
</style>
