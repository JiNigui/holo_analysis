<template>
  <div class="user-container">
    <div class="user-header">
      <h2>用户管理</h2>
      <el-button type="primary" @click="showAddDialog = true">添加用户</el-button>
    </div>
    <div class="user-content">
      <el-card>
        <el-table v-loading="loading" :data="users" style="width: 100%">
          <el-table-column prop="id" label="用户ID" width="80" />
          <el-table-column prop="username" label="用户名" width="150" />
          <el-table-column prop="role" label="角色" width="100">
            <template slot-scope="scope">
              <el-tag v-if="scope.row.role === 'admin'" type="danger">管理员</el-tag>
              <el-tag v-else>普通用户</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="180" />
          <el-table-column prop="last_login" label="最后登录时间" width="180" />
          <el-table-column prop="session_created_at" label="会话创建时间" width="180" />
          <el-table-column label="操作" width="200" fixed="right">
            <template slot-scope="scope">
              <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
              <el-button size="small" type="danger" @click="handleDelete(scope.row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- 添加用户对话框 -->
    <el-dialog title="添加用户" :visible.sync="showAddDialog" width="500px">
      <el-form ref="addForm" :model="addForm" :rules="addRules" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="addForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="addForm.password" type="password" placeholder="请输入密码" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="addForm.role" placeholder="请选择角色">
            <el-option label="管理员" value="admin" />
            <el-option label="普通用户" value="user" />
          </el-select>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" :loading="adding" @click="handleAddUser">确定</el-button>
      </div>
    </el-dialog>

    <!-- 编辑用户对话框 -->
    <el-dialog title="编辑用户" :visible.sync="showEditDialog" width="500px">
      <el-form ref="editForm" :model="editForm" :rules="editRules" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="editForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="editForm.password" type="password" placeholder="请输入新密码（留空则不修改）" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="editForm.role" placeholder="请选择角色">
            <el-option label="管理员" value="admin" />
            <el-option label="普通用户" value="user" />
          </el-select>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" :loading="editing" @click="handleUpdateUser">确定</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { getUsers, register, deleteUser, updateUser } from '@/api/user'

export default {
  name: 'UserList',
  data() {
    return {
      users: [],
      loading: false,
      showAddDialog: false,
      showEditDialog: false,
      adding: false,
      editing: false,
      addForm: {
        username: '',
        password: '',
        role: 'user'
      },
      editForm: {
        id: null,
        username: '',
        password: '',
        role: 'user'
      },
      addRules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' },
          { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, message: '密码长度不能少于 6 个字符', trigger: 'blur' }
        ],
        role: [
          { required: true, message: '请选择角色', trigger: 'change' }
        ]
      },
      editRules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' },
          { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
        ],
        password: [
          { min: 6, message: '密码长度不能少于 6 个字符', trigger: 'blur' }
        ],
        role: [
          { required: true, message: '请选择角色', trigger: 'change' }
        ]
      }
    }
  },
  mounted() {
    this.loadUsers()
  },
  methods: {
    async loadUsers() {
      this.loading = true
      try {
        const response = await getUsers()
        if (response.code === 200) {
          this.users = response.data
        } else {
          this.$message.error('获取用户列表失败：' + response.message)
          console.error('用户管理API错误：', response)
        }
      } catch (error) {
        this.$message.error('获取用户列表失败：' + error.message)
        console.error('用户管理API异常：', error)
      } finally {
        this.loading = false
      }
    },
    handleEdit(user) {
      // 填充编辑表单
      this.editForm = {
        id: user.id,
        username: user.username,
        password: '',
        role: user.role
      }
      this.showEditDialog = true
    },
    async handleDelete(userId) {
      this.$confirm('确定要删除这个用户吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async() => {
        try {
          const response = await deleteUser(userId)
          if (response.code === 200) {
            this.$message.success('用户删除成功')
            // 重新加载用户列表
            await this.loadUsers()
          } else {
            this.$message.error('删除用户失败：' + response.message)
          }
        } catch (error) {
          this.$message.error('删除用户失败：' + error.message)
        }
      }).catch(() => {
        this.$message.info('已取消删除')
      })
    },
    async handleUpdateUser() {
      this.$refs.editForm.validate(async(valid) => {
        if (!valid) return
        this.editing = true
        try {
          // 准备更新数据（如果密码为空则不更新密码）
          const updateData = {
            username: this.editForm.username,
            role: this.editForm.role
          }
          // 如果密码不为空，则包含密码字段
          if (this.editForm.password) {
            updateData.password = this.editForm.password
          }
          const response = await updateUser(this.editForm.id, updateData)
          if (response.code === 200) {
            this.$message.success('用户信息更新成功')
            this.showEditDialog = false
            this.resetEditForm()
            // 重新加载用户列表
            await this.loadUsers()
          } else {
            this.$message.error('更新用户信息失败：' + response.message)
          }
        } catch (error) {
          this.$message.error('更新用户信息失败：' + error.message)
        } finally {
          this.editing = false
        }
      })
    },
    async handleAddUser() {
      this.$refs.addForm.validate(async(valid) => {
        if (!valid) return

        this.adding = true
        try {
          const response = await register(this.addForm)
          if (response.code === 200) {
            this.$message.success('用户添加成功')
            this.showAddDialog = false
            this.resetAddForm()
            // 重新加载用户列表
            await this.loadUsers()
          } else {
            this.$message.error('添加用户失败：' + response.message)
          }
        } catch (error) {
          this.$message.error('添加用户失败：' + error.message)
        } finally {
          this.adding = false
        }
      })
    },
    resetAddForm() {
      this.addForm = {
        username: '',
        password: '',
        role: 'user'
      }
      this.$refs.addForm.clearValidate()
    },
    resetEditForm() {
      this.editForm = {
        id: null,
        username: '',
        password: '',
        role: 'user'
      }
      if (this.$refs.editForm) {
        this.$refs.editForm.clearValidate()
      }
    }
  }
}
</script>

<style scoped>
.user-container {
  padding: 20px;
}

.user-header {
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-header h2 {
  margin: 0;
  color: #303133;
}
</style>
