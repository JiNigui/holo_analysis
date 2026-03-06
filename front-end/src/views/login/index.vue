<template>
  <div class="login-container">
    <div class="login-wrapper">
      <div class="login-form-card">
        <el-form ref="loginForm" :model="loginForm" :rules="loginRules" class="login-form" auto-complete="on" label-position="left">
          <!-- 错误提示 -->
          <div v-if="errorMsg" class="error-message">
            <svg-icon icon-class="error" />
            {{ errorMsg }}
          </div>

          <div class="title-container">
            <h3 class="title">孔洞分析系统</h3>
            <p class="subtitle">欢迎回来，请登录</p>
          </div>

          <el-form-item prop="username">
            <span class="svg-container">
              <svg-icon icon-class="user" />
            </span>
            <el-input
              ref="username"
              v-model="loginForm.username"
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
              v-model="loginForm.password"
              :type="passwordType"
              placeholder="密码"
              name="password"
              tabindex="2"
              auto-complete="on"
              @keyup.enter.native="handleLogin"
            />
            <span class="show-pwd" @click="showPwd">
              <svg-icon :icon-class="passwordType === 'password' ? 'eye' : 'eye-open'" />
            </span>
          </el-form-item>

          <div class="form-actions">
            <el-button :loading="loading" type="primary" class="login-button" @click.native.prevent="handleLogin">登录</el-button>
          </div>

        </el-form>
      </div>
    </div>
  </div>
</template>

<script>
import { validUsername } from '@/utils/validate'

export default {
  name: 'Login',
  data() {
    const validateUsername = (rule, value, callback) => {
      if (!value) {
        callback(new Error('请输入用户名'))
      } else if (!validUsername(value)) {
        // 使用导入的validUsername函数进行格式验证
        callback(new Error('用户名格式不正确（3-20个字符）'))
      } else {
        callback()
      }
    }
    const validatePassword = (rule, value, callback) => {
      if (!value) {
        callback(new Error('请输入密码'))
      } else if (value.length < 6) {
        callback(new Error('密码不能少于6位'))
      } else {
        callback()
      }
    }
    return {
      loginForm: {
        username: '',
        password: ''
      },
      loginRules: {
        username: [{ required: true, trigger: 'blur', validator: validateUsername }],
        password: [{ required: true, trigger: 'blur', validator: validatePassword }]
      },
      loading: false,
      passwordType: 'password',
      redirect: undefined,
      errorMsg: '' // 新增错误提示信息
    }
  },
  watch: {
    $route: {
      handler: function(route) {
        this.redirect = route.query && route.query.redirect
      },
      immediate: true
    }
  },
  mounted() {
    // 清除可能存在的无效token，避免请求中断
    if (this.$store.getters.token) {
      console.log('清除可能无效的token')
      this.$store.dispatch('user/resetToken')
    }
  },
  methods: {
    showPwd() {
      if (this.passwordType === 'password') {
        this.passwordType = ''
      } else {
        this.passwordType = 'password'
      }
      this.$nextTick(() => {
        this.$refs.password.focus()
      })
    },
    handleLogin() {
      // 清除之前的错误信息
      this.errorMsg = ''

      this.$refs.loginForm.validate(valid => {
        if (valid) {
          this.loading = true
          this.$store.dispatch('user/login', this.loginForm).then(() => {
            // 登录成功后，获取用户信息并生成路由
            return this.$store.dispatch('user/getInfo')
          }).then(() => {
            // 生成权限路由并动态添加
            const { roles } = this.$store.getters
            return this.$store.dispatch('permission/generateRoutes', roles)
          }).then((accessRoutes) => {
            // 动态添加路由到router实例
            this.$router.addRoutes(accessRoutes)
            // 路由添加完成后，主动跳转到dashboard页面
            this.loading = false

            // 先跳转到dashboard页面，然后在路由守卫中执行历史记录替换
            this.$router.push('/dashboard')

            // 延迟调用历史记录替换，确保页面跳转完成
            setTimeout(() => {
              if (window.navigationGuard) {
                console.log('登录成功后执行历史记录替换')
                window.navigationGuard.replaceHistoryAfterLogin()
              }
            }, 100)
          }).catch((error) => {
            // 完善错误提示
            const errorCode = error.response?.status

            if (errorCode === 409) {
              // 单点登录冲突：账号已在其他地方登录
              this.errorMsg = error.response?.data?.message || '账号已在其他地方登录，请先退出其他设备'
              this.$message.warning(this.errorMsg)
            } else {
              // 其他错误
              this.errorMsg = error.response?.data?.message || '登录失败，请检查用户名和密码'
              this.$message.error(this.errorMsg)
            }

            this.loading = false
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

<style lang="scss">
/* 修复input 背景不协调 和光标变色 */
/* Detail see https://github.com/PanJiaChen/vue-element-admin/pull/927 */

$bg:#283443;
$light_gray:#fff;
$cursor: #fff;
$primary-color: #409eff;
$error-color: #f56c6c;

@supports (-webkit-mask: none) and (not (cater-color: $cursor)) {
  .login-container .el-input input {
    color: $cursor;
  }
}

/* reset element-ui css */
.login-container {
  .el-input {
    display: inline-block;
    height: 47px;
    width: 85%;

    input {
      background: transparent;
      border: 0px;
      -webkit-appearance: none;
      border-radius: 0px;
      padding: 12px 5px 12px 15px;
      color: $light_gray;
      height: 47px;
      caret-color: $cursor;

      &:-webkit-autofill {
        box-shadow: 0 0 0px 1000px $bg inset !important;
        -webkit-text-fill-color: $cursor !important;
      }
    }
  }

  .el-form-item {
    border: 1px solid rgba(255, 255, 255, 0.1);
    background: rgba(0, 0, 0, 0.1);
    border-radius: 5px;
    color: #454545;
    transition: all 0.3s ease;

    &:hover {
      border-color: rgba(255, 255, 255, 0.2);
      background: rgba(0, 0, 0, 0.15);
    }
  }

  .el-button--primary {
    background: $primary-color;
    border-color: $primary-color;
    transition: all 0.3s ease;

    &:hover {
      background: darken($primary-color, 10%);
      border-color: darken($primary-color, 10%);
    }
  }
}
</style>

<style lang="scss" scoped>
$bg:#2d3a4b;
$dark_gray:#889aa4;
$light_gray:#eee;
$primary-color: #409eff;
$error-color: #f56c6c;
$form-bg: rgba(45, 58, 75, 0.8);

.login-container {
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

.login-wrapper {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 520px;
  animation: fadeIn 0.5s ease-in-out;
}

.login-form-card {
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

.login-form {
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

.tips {
  font-size: 13px;
  color: rgba($light_gray, 0.7);
  margin-top: 20px;
  text-align: center;

  span {
    &:first-of-type {
      margin-right: 16px;
    }
  }
}

// 表单操作区域
.form-actions {
  margin-top: 30px;
}

.login-button {
  width: 100%;
  height: 45px;
  font-size: 16px;
  font-weight: 500;
  border-radius: 5px;
}

// 注册入口链接样式
.register-link {
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
  .login-form {
    padding: 30px 20px;
  }

  .title-container .title {
    font-size: 24px;
  }
}
</style>
