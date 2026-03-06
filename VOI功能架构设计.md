# VOI选取功能架构设计文档

## 1. 整体架构图

```
前端 (Vue.js + Three.js)          后端 (Flask + Python)
┌─────────────────────┐          ┌─────────────────────┐
│                     │          │                     │
│  Three.js 3D渲染    │◄──GLB───►│  PyVista数据转换    │
│                     │          │                     │
│  红框裁截交互       │◄─WebSocket─►│  TIFF序列处理      │
│                     │          │                     │
│  实时预览着色器     │◄──JSON───►│  裁截区域计算       │
│                     │          │                     │
└─────────────────────┘          └─────────────────────┘
```

## 2. 详细数据流

### 2.1 数据准备阶段
```
后端二值化TIFF目录
    ↓ (文件扫描)
后端加载所有TIFF文件
    ↓ (numpy + PyVista)
转换为3D体积数据
    ↓ (GLB转换)
生成GLB格式文件
    ↓ (API传输)
前端下载GLB文件
```

### 2.2 3D可视化阶段
```
前端加载GLB文件
    ↓ (Three.js GLTFLoader)
创建3D网格模型
    ↓ (材质和光照设置)
渲染可交互3D场景
    ↓ (轨道控制器)
用户可旋转缩放查看
```

### 2.3 实时裁截阶段
```
用户拖动红框边界
    ↓ (前端计算边界坐标)
前端GPU着色器实时渲染裁截效果
    ↓ (WebSocket发送边界数据)
后端接收边界参数
    ↓ (PyVista计算统计信息)
返回裁截区域统计
    ↓ (前端显示统计信息)
用户实时预览效果
```

### 2.4 确认保存阶段
```
用户点击确认裁截
    ↓ (发送确认请求)
后端接收最终裁截参数
    ↓ (PyVista执行裁截)
生成新的TIFF序列
    ↓ (保存到指定目录)
返回保存结果
    ↓ (前端显示成功信息)
流程完成
```

## 3. 文件结构设计

### 后端文件结构
```
back-end/
├── hole-analysis/
│   ├── 第1步 原始图像的二值化/
│   │   └── output/              # 输入：二值化TIFF序列
│   └── 第2步 选择自己感兴趣的区域/
│       └── selected_tiff_slices/ # 输出：裁截后的TIFF序列
├── voi_web_api.py               # VOI相关API接口
├── glb_converter.py             # GLB转换工具
└── voi_processor.py             # VOI处理逻辑
```

### 前端文件结构
```
front-end/src/
├── views/project/
│   ├── detail.vue               # 主页面组件
│   ├── components/
│   │   ├── VOI3DViewer.vue      # 3D可视化组件
│   │   └── VOIControlPanel.vue  # 控制面板组件
│   └── utils/
│       ├── threejs-utils.js     # Three.js工具函数
│       └── websocket-utils.js   # WebSocket工具函数
└── assets/
    └── shaders/                 # GLSL着色器文件
        ├── clipping.vert        # 顶点着色器
        └── clipping.frag        # 片段着色器
```

## 4. API接口设计

### 4.1 数据获取接口
- `GET /api/voi/load-volume` - 加载3D体积数据
- `GET /api/voi/get-glb` - 获取GLB格式文件

### 4.2 裁截处理接口
- `POST /api/voi/select-region` - 选择裁截区域
- `POST /api/voi/confirm-clipping` - 确认裁截并保存

### 4.3 WebSocket通信
- `ws://localhost:5000/voi-realtime` - 实时裁截通信

## 5. 关键技术实现

### 5.1 前端关键技术
- **Three.js GLTFLoader**: 加载GLB格式3D模型
- **自定义着色器**: 实现实时裁截效果
- **轨道控制器**: 提供3D交互体验
- **WebSocket**: 实时通信后端

### 5.2 后端关键技术
- **PyVista**: 3D数据处理和裁截
- **numpy**: 体积数据计算
- **tifffile**: TIFF文件读写
- **trimesh**: GLB格式转换

## 6. 性能优化策略

### 6.1 数据传输优化
- GLB文件压缩传输
- WebSocket二进制数据传输
- 增量更新裁截参数

### 6.2 渲染性能优化
- 前端GPU加速裁截
- 后端批量处理TIFF序列
- 内存优化和垃圾回收

## 7. 错误处理机制

### 7.1 前端错误处理
- 网络连接失败重试
- 3D渲染失败降级方案
- 用户操作异常提示

### 7.2 后端错误处理
- 文件读取失败处理
- 数据处理异常捕获
- 内存溢出防护

---
*文档版本: 1.0 | 创建时间: 2025-12-09*