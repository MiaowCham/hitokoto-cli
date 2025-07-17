#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
构建可执行文件脚本
使用 PyInstaller 构建项目，支持单文件模式(--onefile)和目录模式(--onedir)
默认使用单文件模式
支持全平台构建：Windows (x86/x64)、macOS (Intel/Apple Silicon)、Linux
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path
import tempfile


def detect_platform():
    """检测当前平台信息
    
    Returns:
        dict: 包含平台信息的字典
    """
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    platform_info = {
        'system': system,
        'machine': machine,
        'is_windows': system == 'windows',
        'is_macos': system == 'darwin',
        'is_linux': system == 'linux',
        'is_64bit': machine in ['x86_64', 'amd64', 'arm64', 'aarch64'],
        'is_arm': machine in ['arm64', 'aarch64', 'arm'],
        'is_github': os.getenv('GITHUB_ACTIONS') == 'true'
    }
    
    return platform_info


def get_github_info():
    """获取GitHub环境信息
    
    Returns:
        dict: GitHub环境信息
    """
    return {
        'sha': os.getenv('GITHUB_SHA', ''),
        'short_sha': os.getenv('GITHUB_SHA', '')[:7] if os.getenv('GITHUB_SHA') else '',
        'ref': os.getenv('GITHUB_REF', ''),
        'repository': os.getenv('GITHUB_REPOSITORY', ''),
        'workflow': os.getenv('GITHUB_WORKFLOW', ''),
        'run_id': os.getenv('GITHUB_RUN_ID', ''),
        'run_number': os.getenv('GITHUB_RUN_NUMBER', '')
    }


def create_version_file(script_dir, version, platform_info=None, github_info=None):
    """创建Windows版本信息文件
    
    Args:
        script_dir: 脚本目录
        version: 版本号
        platform_info: 平台信息
        github_info: GitHub环境信息
    
    Returns:
        str: 版本文件路径
    """
    # 构建文件描述
    base_description = "一个简单的命令行工具，用于获取和显示一言(Hitokoto)语句。支持从在线API获取或使用本地语句包。"
    
    if platform_info and platform_info.get('is_github'):
        file_description = base_description + " Github构建版本，未经测试，可能不稳定或不可用。"
    else:
        file_description = base_description
    # 处理版本号格式，确保是数字格式
    if version.startswith('git-'):
        # GitHub版本使用1.0.0.0格式
        version_tuple = "1, 0, 0, 0"
        display_version = version
    else:
        # 标准版本号处理
        version_parts = version.split('.')
        # 确保有4个部分
        while len(version_parts) < 4:
            version_parts.append('0')
        # 只取前4个部分，并确保都是数字
        version_nums = []
        for part in version_parts[:4]:
            try:
                version_nums.append(str(int(part)))
            except ValueError:
                version_nums.append('0')
        version_tuple = ', '.join(version_nums)
        display_version = version
    
    version_content = f'''# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    # filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
    # Set not needed items to zero 0.
    filevers=({version_tuple}),
    prodvers=({version_tuple}),
    # Contains a bitmask that specifies the valid bits 'flags'r
    mask=0x3f,
    # Contains a bitmask that specifies the Boolean attributes of the file.
    flags=0x0,
    # The operating system for which this file was designed.
    # 0x4 - NT and there is no need to change it.
    OS=0x4,
    # The general type of file.
    # 0x1 - the file is an application.
    fileType=0x1,
    # The function of the file.
    # 0x0 - the function is not defined for this fileType
    subtype=0x0,
    # Creation date and time stamp.
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'080404B0',
        [StringStruct(u'CompanyName', u'MiaowCham'),
        StringStruct(u'FileDescription', u'{file_description}'),
        StringStruct(u'FileVersion', u'{display_version}'),
        StringStruct(u'InternalName', u'hitokoto'),
        StringStruct(u'LegalCopyright', u'MIT License'),
        StringStruct(u'OriginalFilename', u'hitokoto.exe'),
        StringStruct(u'ProductName', u'Hitokoto-Cli'),
        StringStruct(u'ProductVersion', u'{display_version}'),
        StringStruct(u'Language', u'中文')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [2052, 1200])])
  ]
)'''
    
    # 创建临时版本文件
    version_file = script_dir / "version_info.txt"
    with open(version_file, 'w', encoding='utf-8') as f:
        f.write(version_content)
    
    return str(version_file)


def check_pyinstaller():
    """检查是否安装了 PyInstaller"""
    try:
        import PyInstaller
        print("PyInstaller 已安装，版本:", PyInstaller.__version__)
        return True
    except ImportError:
        print("未安装 PyInstaller，正在尝试安装...")
        print("提示: 如果自动安装失败，请手动运行: pip install pyinstaller")
        try:
            # 尝试使用pip安装
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "pyinstaller"])
            print("PyInstaller 安装成功")
            
            # 重新导入以验证安装
            try:
                import PyInstaller
                print("验证安装成功，版本:", PyInstaller.__version__)
                return True
            except ImportError:
                print("PyInstaller 安装后无法导入，请重启脚本再试")
                return False
                
        except Exception as e:
            print(f"安装 PyInstaller 失败: {e}")
            print("请手动安装: pip install --user pyinstaller")
            print("安装后重新运行此脚本")
            return False


def build_executable(args):
    """构建可执行文件
    
    Args:
        args: 命令行参数
    """
    # 获取平台和GitHub信息
    platform_info = detect_platform()
    github_info = get_github_info()
    
    print(f"检测到平台: {platform_info['system']} {platform_info['machine']}")
    if platform_info['is_github']:
        print(f"GitHub Actions环境，提交SHA: {github_info['short_sha']}")
    
    # 获取脚本所在目录
    script_dir = Path(__file__).parent.absolute()
    
    # 设置构建目录
    build_dir = script_dir / "build"
    dist_dir = script_dir / "dist"
    
    # 清理旧的构建文件
    try:
        if build_dir.exists():
            print(f"清理旧的构建目录: {build_dir}")
            shutil.rmtree(build_dir)
        
        if dist_dir.exists():
            print(f"清理旧的分发目录: {dist_dir}")
            shutil.rmtree(dist_dir)
    except PermissionError as e:
        print(f"无法清理目录，权限不足: {e}")
        print("请尝试手动删除 build 和 dist 目录后重试")
        return False
    except Exception as e:
        print(f"清理目录时出错: {e}")
        print("继续构建过程...")
    
    # 主程序文件
    main_script = script_dir / "hitokoto_cli.py"
    
    # 确保主程序文件存在
    if not main_script.exists():
        print(f"错误: 主程序文件不存在: {main_script}")
        return False
    
    # 检查LICENSE文件
    license_file = script_dir / "LICENSE"
    if not license_file.exists():
        print("警告: LICENSE文件不存在，将不会包含在构建中")
        add_data_option = []
    else:
        # 根据操作系统设置不同的分隔符
        separator = ";" if sys.platform.startswith("win") else ":"
        add_data_option = [f"--add-data=LICENSE{separator}."]
    
    # 检查图标文件
    icon_file = script_dir / "icon.ico"
    if not icon_file.exists():
        print("警告: 图标文件icon.ico不存在，将不会设置应用程序图标")
        icon_option = []
    else:
        if platform_info['is_windows']:
            icon_option = ["--icon=icon.ico"]
        elif platform_info['is_macos']:
            # macOS使用icns格式，如果没有则跳过
            icns_file = script_dir / "icon.icns"
            if icns_file.exists():
                icon_option = [f"--icon={icns_file}"]
            else:
                print("警告: macOS需要icon.icns文件，将不会设置应用程序图标")
                icon_option = []
        else:
            icon_option = []  # Linux通常不需要图标文件
    
    # 根据参数决定构建模式
    build_mode = "--onefile" if args.onefile else "--onedir"
    
    # 构建命令
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=hitokoto",
        build_mode,  # 根据参数选择构建模式
        "--clean",
        "--noconfirm",
    ]
    
    # 添加平台特定的优化选项
    if platform_info['is_macos']:
        # macOS特定选项
        if hasattr(args, 'universal2') and args.universal2:
            # 检查是否支持Universal2构建
            try:
                # 尝试检查Python是否为Universal2版本
                result = subprocess.run(['file', sys.executable], capture_output=True, text=True)
                if 'universal' in result.stdout.lower() or 'fat' in result.stdout.lower():
                    cmd.extend(["--target-arch=universal2"])
                    print("启用macOS Universal2构建（Intel + Apple Silicon）")
                else:
                    print("警告: 当前Python不支持Universal2，将使用当前架构构建")
                    print(f"Python架构信息: {result.stdout.strip()}")
            except Exception as e:
                print(f"警告: 无法检测Python架构，跳过Universal2构建: {e}")
        cmd.extend(["--osx-bundle-identifier=com.miaowcham.hitokoto"])
    elif platform_info['is_linux']:
        # Linux特定选项
        cmd.extend(["--strip"])  # 减小文件大小
    elif platform_info['is_windows']:
        # Windows特定选项
        cmd.extend(["--console"])  # 确保控制台应用
    
    # 添加图标参数（如果图标文件存在）
    cmd.extend(icon_option)
    
    # 添加版本信息（仅在Windows下有效）
    if hasattr(args, 'version') and args.version and platform_info['is_windows']:
        version_info = [
            f"--version-file={create_version_file(script_dir, args.version, platform_info, github_info)}"
        ]
        cmd.extend(version_info)
    
    # 添加LICENSE文件（如果存在）
    cmd.extend(add_data_option)
    
    # 添加主程序文件
    cmd.append(str(main_script))
    
    print("开始构建可执行文件...")
    print(f"构建命令: {' '.join(cmd)}")
    
    try:
        subprocess.check_call(cmd)
        print("构建成功!")
        
        # 清理临时版本文件
        if hasattr(args, 'version') and args.version and platform_info['is_windows']:
            version_file = script_dir / "version_info.txt"
            if version_file.exists():
                try:
                    version_file.unlink()
                    print("已清理临时版本文件")
                except Exception as e:
                    print(f"清理版本文件失败: {e}")
        
        # 根据构建模式和平台输出可执行文件路径
        exe_name = "hitokoto.exe" if platform_info['is_windows'] else "hitokoto"
        
        if args.onefile:
            # 单文件模式
            exe_path = dist_dir / exe_name
        else:
            # 目录模式
            exe_path = dist_dir / "hitokoto" / exe_name
        
        print(f"可执行文件位于: {exe_path}")
        if hasattr(args, 'version') and args.version:
            print(f"版本信息: {args.version}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"构建失败: {e}")
        return False
    except Exception as e:
        print(f"构建过程中发生未知错误: {e}")
        return False


def main():
    """主函数"""
    # 设置UTF-8编码输出，避免Windows下的编码问题
    import sys
    import io
    if sys.platform.startswith('win'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    print("=== Hitokoto Multi-Platform Build Script ===")
    
    # 获取平台和GitHub信息
    platform_info = detect_platform()
    github_info = get_github_info()
    
    # 解析命令行参数
    import argparse
    parser = argparse.ArgumentParser(description="构建一言(Hitokoto)命令行工具的可执行文件")
    parser.add_argument("--force", action="store_true", help="强制重新安装PyInstaller")
    parser.add_argument("--skip-check", action="store_true", help="跳过PyInstaller检查")
    parser.add_argument("-v", "--version", type=str, help="设置可执行文件的版本号（例如：1.0.0）")
    
    # 添加构建模式选项
    build_mode_group = parser.add_mutually_exclusive_group()
    build_mode_group.add_argument("--onefile", action="store_true", help="使用单文件模式构建（默认）")
    build_mode_group.add_argument("--onedir", action="store_true", dest="onedir", help="使用目录模式构建")
    
    # 添加平台特定选项
    if platform_info['is_macos']:
        parser.add_argument("--universal2", action="store_true", help="构建macOS Universal2二进制文件（Intel + Apple Silicon）")
    
    args = parser.parse_args()
    
    # 在GitHub环境中自动设置版本
    if platform_info['is_github'] and not args.version and github_info['short_sha']:
        args.version = f"git-{github_info['short_sha']}"
        print(f"GitHub环境检测到，自动设置版本为: {args.version}")
    
    # 如果两个模式都没有指定，默认使用单文件模式
    if not args.onedir:
        args.onefile = True
    
    # 检查PyInstaller
    if args.skip_check:
        print("跳过PyInstaller检查")
        pyinstaller_ok = True
    elif args.force:
        print("强制重新安装PyInstaller")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "--force-reinstall", "pyinstaller"])
            pyinstaller_ok = True
        except Exception as e:
            print(f"强制重新安装PyInstaller失败: {e}")
            pyinstaller_ok = False
    else:
        pyinstaller_ok = check_pyinstaller()
    
    # 构建可执行文件
    if pyinstaller_ok:
        success = build_executable(args)
        if success:
            version_info = f" (版本: {args.version})" if hasattr(args, 'version') and args.version else ""
            platform_name = f"{platform_info['system'].title()} {platform_info['machine']}"
            
            if args.onefile:
                exe_name = "hitokoto.exe" if platform_info['is_windows'] else "hitokoto"
                print(f"\n🎉 构建完成! 可以在dist目录中找到{exe_name}单文件可执行程序{version_info}。")
            else:
                print(f"\n🎉 构建完成! 可以在dist/hitokoto目录中找到可执行文件及其依赖{version_info}。")
            
            print(f"📋 平台信息: {platform_name}")
            if platform_info['is_github']:
                print(f"🔧 GitHub Actions构建，提交: {github_info['short_sha']}")
            if platform_info['is_macos'] and hasattr(args, 'universal2') and args.universal2:
                print(f"🍎 macOS Universal2构建（支持Intel和Apple Silicon）")
            
            return 0
        else:
            print("\n❌ 构建失败! 请检查上述错误信息。")
            return 1
    else:
        print("\n❌ 由于PyInstaller问题，无法继续构建。")
        print("请手动安装PyInstaller后重试: pip install --user pyinstaller")
        return 1

if __name__ == "__main__":
    sys.exit(main())