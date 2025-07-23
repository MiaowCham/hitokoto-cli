<div align="center">

<img src="icon.ico" width="30%" alt="icon" />

# 一言(Hitokoto)命令行工具

</div>

> [!note]
> 这不是一言官方提供的命令行工具！本项目和一言官方无关。

一个简单的命令行工具，用于获取和显示一言(Hitokoto)语句。支持从在线API获取或使用本地语句包。

## 功能特点

- 支持从一言API在线获取语句
- 支持使用本地语句包（无需联网）
- 支持按类型、长度筛选语句
- 支持显示语句来源信息
- 支持JSON格式输出
- 支持导出多条语句到文件
- 完整的日志记录功能

## 项目使用

### 项目依赖

运行依赖
- Python>=3.6
- requests>=2.25.0
- jsonlines>=3.0.0
- loguru>=0.7.0

开发依赖
- pyinstaller>=5.6.2 （用于构建可执行文件）

### 克隆项目
首先请下载或克隆本仓库
```bash
git clone https://github.com/MiaowCham/hitokoto-cli.git
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

## 构建可执行文件

> [!note]  
> 除 Windows x64 平台外，其他平台均未经测试。Github Actions 已经成功在 macOS 14 (arm64) 和 Ubuntu 22.04 上成功构建，但不保证构建产物的可用性。
>
> 有关构建详的细描述请见 [BUILD.md](BUILD.md)

使用 `build_exe.py` 脚本可以快捷对项目进行构建。

```bash
python build_exe.py
```
构建完成后，在 `dist` 目录下会生成可执行文件。

## 使用方法

> [!note]  
> 前往 [Release](https://github.com/MiaowCham/hitokoto-cli/releases) 可以下载构建好的 Windows x64 可执行文件。  
> 或者前往 [Github Actions](https://github.com/MiaowCham/hitokoto-cli/actions/workflows/build.yml) 获取最新的多平台构建。
> 构建版本请将 `hitokoto_cli.py` 替换为 `.\hitokoto.exe`。  
> 将构建版本所处目录添加至环境变量中，即可在任意目录使用 `hitokoto` 命令。[^1]

[^1]: 当然如果你就是想直接使用 Python 源码的话，我记得各个系统都有自定义命令的方法（具体办法自己百度！），把 `python 完整路径/hitokoyo_cli.py` 设置一个你喜欢的命令名称，也是可以实现在任意目录使用 `hitokoto` 。

### 基本用法

```bash
python hitokoto_cli.py
```

这将随机显示一条一言语句。

### 参数说明

<details>
<summary>点击展开参数说明</summary>

```
选项:
  -h, --help                     显示帮助信息
  -a, --api [{in,cn}]            强制调用指定API (默认:in=国际, cn=中国)
  -b, --bundle                   强制使用语句包
  -t, --type [TYPE]              语句类型 (默认:none=随机, a-l, 或输入 help 查看详细说明)
  --min MIN_LENGTH               指定最小字符数
  --max MAX_LENGTH               指定最大字符数
  -f, --from                     在输出中包含来源
  -i, --id SENTENCE_ID           精确查找指定语句ID/UUID (仅支持本地)
  --encode {text,json}           输出格式
  -c, --check-bundle             检查语句包状态
  -d, --delete-bundle            删除本地语句包
  -u, --update-index             更新索引文件
  -g, --get-bundle [{of,gh,jsd}] 获取语句包 (默认:of, 可选:gh, jsd)
  -e, --echo [ECHO_COUNT]        输出至文件的语句数量，默认10条
  -p, --path ECHO_PATH           输出文件路径
  --debug                        启用调试模式，显示详细日志信息
  -v, --version                  显示版本信息
```

### 语句类型说明

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

### 获取语句包（可选）

如果您想使用本地语句包（推荐，可离线使用），请运行：

```bash
python bundle_get.py
# 或
python hitokoto_cli.py -g
```

这将从一言官方源下载语句包到本地。

</details>

### 示例
<details>
<summary>点击展开示例</summary>
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

</details>

## 许可证与声明

> [!note]
本项目大部分代码来自 [Trae Pro](https://www.trae.ai/) 的 Claude-4 及 Claude-3.7，请注意辨别

本项目采用 CC0-1.0 许可证。  
由于本项目主要使用 AI 实现代码，故将此项目开放至公共领域。  

`icon.ico` 是 [一言](hitokoto.cn) 的logo，根据其开发者中心使用的 MIT 协议共享，用于 hitokoto-cli 项目的图标  
hitokoto-cli 是开源项目，不包含商业用途，且基于 CC0 1.0 协议完全共享至公共领域

hitokoto 开发者中心版权声明：
```
本文档遵循 MIT 协议
© 2024 MoeTeam All Rights Reserved.
```

## 致谢

感谢 [Trae 编辑器](https://www.trae.ai/)，花了 3$ 就能看各种大模型自己完成项目，~~我都不用动手（bush~~

### 特别感谢: [一言官方](https://hitokoto.cn/)
  - 提供了 [API 服务](https://developer.hitokoto.cn/sentence/)
  - 提供了[语句包下载服务](https://sentences-bundle.hitokoto.cn/)
