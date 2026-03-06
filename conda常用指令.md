# Conda常用命令参考手册
## 1. 环境管理命令
### 查看环境信息
```
# 查看当前激活的环境
conda info
conda env list

# 查看当前环境路径
conda info --base
conda info --envs
```
### 创建和管理环境
```
# 创建新环境
conda create -n 环境名 python=3.8
conda create -n 环境名 python=3.8 
numpy pandas

# 克隆环境
conda create -n 新环境名 --clone 原环
境名

# 删除环境
conda remove -n 环境名 --all
```
### 激活和退出环境
```
# 激活环境
conda activate 环境名

# 退出当前环境
conda deactivate
```
## 2. 包管理命令
### 安装包
```
# 安装单个包
conda install 包名
conda install 包名=版本号

# 从特定channel安装
conda install -c conda-forge 包名

# 安装多个包
conda install 包1 包2 包3
```
### 查看和管理包
```
# 查看已安装的包
conda list
conda list | findstr 包名  # Windows
搜索

# 查看包信息
conda search 包名
conda info 包名

# 更新包
conda update 包名
conda update --all  # 更新所有包

# 卸载包
conda remove 包名
```
## 3. 环境配置和清理
### 配置conda
```
# 查看配置
conda config --show

# 添加清华镜像源（国内推荐）
conda config --add channels https://
mirrors.tuna.tsinghua.edu.cn/
anaconda/pkgs/main/
conda config --add channels https://
mirrors.tuna.tsinghua.edu.cn/
anaconda/pkgs/free/
conda config --add channels https://
mirrors.tuna.tsinghua.edu.cn/
anaconda/cloud/conda-forge/
conda config --set 
show_channel_urls yes

# 恢复默认源
conda config --remove-key channels
```
### 清理缓存
```
# 清理包缓存
conda clean --all

# 清理tarballs
conda clean --tarballs

# 清理索引缓存
conda clean --index-cache
```
## 4. 实用命令
### 环境导出和导入
```
# 导出环境配置
conda env export > environment.yml

# 从文件创建环境
conda env create -f environment.yml

# 更新现有环境
conda env update -f environment.yml
```
### 检查环境状态
```
# 检查环境一致性
conda doctor

# 查看环境详细信息
conda info --envs --json

# 检查包依赖关系
conda list --show-channel-urls
```
## 5. 项目开发常用命令组合
### 创建项目环境
```
# 创建包含常用数据科学包的环境
conda create -n myproject python=3.
9 numpy pandas matplotlib jupyter

# 激活并安装额外包
conda activate myproject
conda install scikit-learn 
tensorflow
```
### 环境备份和恢复
```
# 备份当前环境
conda env export > myproject_backup.
yml

# 在新机器上恢复环境
conda env create -f 
myproject_backup.yml
conda activate myproject
```
## 6. 问题排查命令
### 环境问题排查
```
# 检查conda版本和状态
conda --version
conda info

# 检查环境冲突
conda list --revisions
conda install --revision 版本号  # 回
滚到指定版本

# 修复损坏的环境
conda clean --all
conda update conda
```
### 包冲突解决
```
# 强制解决依赖冲突
conda install 包名 --force-reinstall

# 使用pip安装（当conda无法解决依赖时）
pip install 包名

# 检查包依赖树
conda tree 包名
```
## 7. 快捷命令别名（可选配置）
您可以将以下别名添加到shell配置文件中：

```
# 查看当前环境
alias ce='conda info'

# 列出所有环境
alias cel='conda env list'

# 快速激活环境
alias ca='conda activate'

# 快速退出环境
alias cde='conda deactivate'
```
## 使用技巧
1. 优先使用conda安装包 ，特别是科学计算相关的包
2. 创建独立环境 用于不同项目，避免包冲突
3. 定期清理缓存 以节省磁盘空间
4. 使用环境配置文件 便于团队协作和部署
5. 遇到安装问题时 ，尝试使用 conda-forge channel