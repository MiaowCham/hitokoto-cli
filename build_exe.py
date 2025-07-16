#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
构建可执行文件脚本
使用 PyInstaller 构建项目，支持单文件模式(--onefile)和目录模式(--onedir)
默认使用单文件模式
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import tempfile


def create_version_file(script_dir, version):
    """创建Windows版本信息文件
    
    Args:
        script_dir: 脚本目录
        version: 版本号
    
    Returns:
        str: 版本文件路径
    """
    version_content = f'''# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    # filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
    # Set not needed items to zero 0.
    filevers=({version.replace('.', ', ')}, 0),
    prodvers=({version.replace('.', ', ')}, 0),
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
        [StringStruct(u'CompanyName', u'Hitokoto-Cli'),
        StringStruct(u'FileDescription', u'一个简单的命令行工具，用于获取和显示一言(Hitokoto)语句。支持从在线API获取或使用本地语句包。'),
        StringStruct(u'FileVersion', u'{version}'),
        StringStruct(u'InternalName', u'hitokoto'),
        StringStruct(u'LegalCopyright', u'MIT License'),
        StringStruct(u'OriginalFilename', u'hitokoto.exe'),
        StringStruct(u'ProductName', u'Hitokoto-Cli'),
        StringStruct(u'ProductVersion', u'{version}'),
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
        icon_option = ["--icon=icon.ico"]
    
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
    
    # 添加图标参数（如果图标文件存在）
    cmd.extend(icon_option)
    
    # 添加版本信息（仅在Windows下有效）
    if hasattr(args, 'version') and args.version and sys.platform.startswith("win"):
        version_info = [
            f"--version-file={create_version_file(script_dir, args.version)}"
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
        if hasattr(args, 'version') and args.version and sys.platform.startswith("win"):
            version_file = script_dir / "version_info.txt"
            if version_file.exists():
                try:
                    version_file.unlink()
                    print("已清理临时版本文件")
                except Exception as e:
                    print(f"清理版本文件失败: {e}")
        
        # 根据构建模式输出可执行文件路径
        if args.onefile:
            # 单文件模式
            if sys.platform.startswith("win"):
                exe_path = dist_dir / "hitokoto.exe"
            else:
                exe_path = dist_dir / "hitokoto"
        else:
            # 目录模式
            if sys.platform.startswith("win"):
                exe_path = dist_dir / "hitokoto" / "hitokoto.exe"
            else:
                exe_path = dist_dir / "hitokoto" / "hitokoto"
        
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
    print("=== 一言(Hitokoto)构建脚本 ===")
    
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
    
    args = parser.parse_args()
    
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
            if args.onefile:
                print(f"\n构建完成! 可以在dist目录中找到hitokoto.exe单文件可执行程序{version_info}。")
            else:
                print(f"\n构建完成! 可以在dist/hitokoto目录中找到可执行文件及其依赖{version_info}。")
            return 0
        else:
            print("\n构建失败! 请检查上述错误信息。")
            return 1
    else:
        print("\n由于PyInstaller问题，无法继续构建。")
        print("请手动安装PyInstaller后重试: pip install --user pyinstaller")
        return 1

if __name__ == "__main__":
    sys.exit(main())