# 一言(Hitokoto)命令行工具

一个简单的命令行工具，用于获取和显示一言(Hitokoto)语句。支持从在线API获取或使用本地语句包。

## 功能特点

- 支持从一言API在线获取语句
- 支持使用本地语句包（无需联网）
- 支持按类型、长度筛选语句
- 支持显示语句来源信息
- 支持JSON格式输出
- 支持导出多条语句到文件
- 完整的日志记录功能

### 项目依赖

运行依赖
- Python>=3.6
- requests>=2.25.0
- click>=8.0.0
- jsonlines>=3.0.0
- PyYAML>=6.0.0
- loguru>=0.7.0

开发依赖
- pyinstaller>=5.6.2 （用于构建可执行文件）

## 自行构建

<details>
<summary>点击展开自行构建说明</summary>

首先请下载或克隆本仓库
```bash
git clone URL_ADDRESS.com/your_username/hitokoto-cli.git
cd hitokoto-cli
```

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行
```bash
python hitokoto_cli.py
```

### 构建可执行文件

如果您想将此工具打包为可执行文件，可以使用提供的构建脚本：

```bash
python build_exe.py
```

默认情况下，这将在 `dist` 目录下生成 `hitokoto.exe` 单文件可执行程序。

构建脚本支持以下参数：

```
--force       强制重新安装PyInstaller
--skip-check  跳过PyInstaller检查
--onefile     使用单文件模式构建（默认）
--onedir      使用目录模式构建
```

如果使用 `--onedir` 参数，将在 `dist/hitokoto` 目录下生成可执行文件及其依赖文件。
</details>

## 使用方法

> [!note]  
> 前往 [Release](URL_ADDRESS.com/your_username/hitokoto-cli/releases) 可以下载构建好的可执行文件。  
> 构建版本请将 `hitokoto_cli.py` 替换为 `.\hitokoto.exe`。  
> 将构建版本所处目录添加至环境变量 `PATH` 中，即可在任意目录使用 `hitokoto` 命令。

### 基本用法

```bash
python hitokoto_cli.py
```

这将随机显示一条一言语句。

### 参数说明

```
选项:
  -a, --api [in|cn]        强制调用指定API (in=国际, cn=中国)
  -g, --get-bundle         获取语句包
  -b, --bundle             强制使用语句包
  -t, --type TEXT          语句类型 (a-l)
  --min INTEGER            最小字符数
  --max INTEGER            最大字符数
  -f, --from               在输出中包含来源
  -i, --id TEXT            精确查找指定语句ID/UUID (仅支持本地)
  --encode [text|json]     输出格式
  -c, --check-bundle       检查语句包状态
  --debug                  启用调试模式
  --help                   显示帮助信息
```

### 获取语句包（可选）

如果您想使用本地语句包（推荐，可离线使用），请运行：

```bash
python bundle_get.py
# 或
python hitokoto_cli.py -g
```

这将从一言官方源下载语句包到本地。

### 示例

1. 获取一条动画类型的语句，并显示来源：

```bash
python hitokoto_cli.py -t a -f
```

2. 获取一条长度在10-20字之间的语句：

```bash
python hitokoto_cli.py --min 10 --max 20
```

3. 以JSON格式输出：

```bash
python hitokoto_cli.py --encode json
```

4. 强制使用在线API：

```bash
python hitokoto_cli.py -a in
```

## 语句类型说明

- a: 动画
- b: 漫画
- c: 游戏
- d: 文学
- e: 原创
- f: 来自网络
- g: 其他
- h: 影视
- i: 诗词
- j: 网易云
- k: 哲学
- l: 抖机灵

## 许可证

本项目采用 MIT 许可证。

## 致谢

感谢 [一言开发者](https://hitokoto.cn/) 提供的API和语句数据。