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
    
    # 添加LICENSE文件（如果存在）
    cmd.extend(add_data_option)
    
    # 添加主程序文件
    cmd.append(str(main_script))
    
    print("开始构建可执行文件...")
    print(f"构建命令: {' '.join(cmd)}")
    
    try:
        subprocess.check_call(cmd)
        print("构建成功!")
        
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
            if args.onefile:
                print("\n构建完成! 可以在dist目录中找到hitokoto.exe单文件可执行程序。")
            else:
                print("\n构建完成! 可以在dist/hitokoto目录中找到可执行文件及其依赖。")
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