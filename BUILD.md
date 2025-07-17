# 构建说明

> [!note]
> AI声明：本文使用AI生成，可能存在错误，仅供参考。

本项目支持全平台构建，包括 Windows、macOS 和 Linux。

## 本地构建

### 系统要求

- Python 3.8+
- PyInstaller (会自动安装)

### 支持的平台

- **Windows**: x86/x64
- **macOS**: Intel 和 Apple Silicon (支持 Universal2)
- **Linux**: x64 (优先适配 Debian/Ubuntu)

### 构建命令

```bash
# 基本构建（单文件模式）
python build_exe.py

# 目录模式构建
python build_exe.py --onedir

# 指定版本号
python build_exe.py --version 1.0.0

# macOS Universal2 构建（仅在 macOS 上可用）
python build_exe.py --universal2

# 强制重新安装 PyInstaller
python build_exe.py --force

# 跳过 PyInstaller 检查
python build_exe.py --skip-check
```

### 平台特定说明

#### Windows
- 支持 x86 和 x64 架构
- 自动生成版本信息文件
- 输出 `.exe` 可执行文件

#### macOS
- 支持 Intel 和 Apple Silicon
- 使用 `--universal2` 参数可构建通用二进制文件
- 需要 `icon.icns` 文件作为应用图标（可选）
- 自动设置 Bundle Identifier

#### Linux
- 自动启用文件压缩优化
- 输出标准可执行文件
- 在 Debian/Ubuntu 系统上测试

## GitHub Actions 自动构建

### 触发构建

1. 进入项目的 GitHub 页面
2. 点击 "Actions" 标签
3. 选择 "Build Executables" 工作流
4. 点击 "Run workflow" 按钮
5. 选择构建选项：
   - **构建模式**: `onefile`（单文件）或 `onedir`（目录）
   - **创建 Release**: 是否自动创建 GitHub Release

### 构建矩阵

工作流会在以下环境中并行构建：

| 平台 | 操作系统 | 架构 | Python版本 | 状态 |
|------|----------|------|------------|------|
| Windows x86 | Windows Server 2022 | x86 | 3.9 | ✅ 启用 |
| Windows x64 | Windows Server 2022 | x64 | 3.9 | ✅ 启用 |
| macOS x64 | macOS Latest | x86_64 | 3.9 | 💤 已注释（可选启用） |
| macOS ARM64 | macOS Latest | aarch64 | 3.9 | 💤 已注释（可选启用） |
| macOS Universal2 | macOS Latest | Universal2 | 3.9 | ✅ 启用 |
| Linux x64 | Ubuntu 22.04 | x64 | 3.9 | ✅ 启用 |

### 构建产物

构建完成后，会生成以下文件：

**启用的构建目标：**
- `hitokoto-windows-x86-{commit}.exe` - Windows 32位可执行文件
- `hitokoto-windows-x64-{commit}.exe` - Windows 64位可执行文件
- `hitokoto-macOS-universal2-{commit}` - macOS Universal2可执行文件（支持Intel和Apple Silicon）
- `hitokoto-linux-x64-{commit}` - Linux 64位可执行文件

**可选构建目标（已注释）：**
- `hitokoto-macOS-x64-{commit}` - macOS Intel专用可执行文件
- `hitokoto-macOS-arm64-{commit}` - macOS Apple Silicon专用可执行文件

> 💡 **提示**: 要启用可选的macOS架构构建，请在 `.github/workflows/build.yml` 中取消相应行的注释。

### 版本信息

- GitHub 构建会自动使用提交的短哈希作为版本号
- 格式：`git-{7位提交哈希}`
- 在 Windows 版本信息中会标注为 "Github构建版本，未经测试，可能不稳定或不可用"

## 故障排除

### 常见问题

1. **PyInstaller 安装失败**
   ```bash
   pip install --user pyinstaller
   ```

2. **权限错误（Windows）**
   - 以管理员身份运行命令提示符
   - 或使用 `--user` 参数安装依赖

3. **macOS 代码签名问题**
   - 构建的应用可能需要在"系统偏好设置 > 安全性与隐私"中允许运行
   - 或使用 `xattr -d com.apple.quarantine hitokoto` 命令

4. **Linux 依赖问题**
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install python3-dev
   
   # CentOS/RHEL
   sudo yum install python3-devel
   ```

### 清理构建文件

```bash
# 删除构建目录
rm -rf build dist

# Windows
rmdir /s build dist
```

## 开发说明

### 添加新平台支持

1. 在 `detect_platform()` 函数中添加平台检测逻辑
2. 在 `build_executable()` 函数中添加平台特定的构建选项
3. 更新 GitHub Actions 工作流矩阵

### 自定义构建选项

可以通过修改 `build_exe.py` 中的 PyInstaller 参数来自定义构建：

- `--exclude-module`: 排除不需要的模块
- `--add-data`: 添加额外的数据文件
- `--hidden-import`: 添加隐式导入
- `--optimize`: 优化级别

### 图标文件

- **Windows**: `icon.ico`
- **macOS**: `icon.icns`
- **Linux**: 通常不需要

图标文件应放在项目根目录中。