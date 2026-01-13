#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
极智考典 - 用户版本打包脚本
简化版打包工具
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_header(title):
    """打印标题"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def check_dependencies():
    """检查依赖是否安装"""
    print_header("检查依赖")

    dependencies = [
        ("PyQt5", "PyQt5>=5.15.0"),
        ("pycryptodome", "pycryptodome>=3.15.0"),
        ("pyinstaller", "pyinstaller")
    ]

    for dep_name, dep_spec in dependencies:
        try:
            if dep_name == "PyQt5":
                import PyQt5
            elif dep_name == "pycryptodome":
                from Crypto.Cipher import AES
            elif dep_name == "pyinstaller":
                import PyInstaller
            print(f"✓ {dep_name} 已安装")
        except ImportError:
            print(f"✗ {dep_name} 未安装，正在安装...")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", dep_spec],
                             check=True, capture_output=True, text=True)
                print(f"✓ {dep_name} 安装成功")
            except subprocess.CalledProcessError as e:
                print(f"✗ {dep_name} 安装失败: {e.stderr}")
                return False

    return True

def clean_old_files():
    """清理旧的打包文件"""
    print_header("清理旧文件")

    files_to_clean = [
        "build",
        "dist",
        "__pycache__",
        "极智考典.spec"
    ]

    for item in files_to_clean:
        if Path(item).exists():
            try:
                if Path(item).is_dir():
                    shutil.rmtree(item, ignore_errors=True)
                    print(f"删除目录: {item}")
                else:
                    os.remove(item)
                    print(f"删除文件: {item}")
            except Exception as e:
                print(f"警告: 清理 {item} 失败: {e}")

def build_exe():
    """使用PyInstaller打包exe"""
    print_header("开始打包")

    # PyInstaller命令参数
    cmd = [
        "pyinstaller",
        "--onefile",           # 打包成单个exe文件
        "--windowed",          # 窗口程序（不显示控制台）
        "--name=极智考典",  # 输出文件名
        "--clean",             # 清理临时文件
        "--noconfirm",         # 不确认覆盖
        # 添加数据文件
        "--add-data=data;data",
        "--add-data=ui;ui",
        "--add-data=core;core",
        # 排除不必要的模块
        "--exclude-module=admin",
        "--exclude-module=generate_codes",
        "--exclude-module=encrypt_exams",
        "--exclude-module=decrypt_exams",
        "--exclude-module=import_papers",
        "--exclude-module=fix_activation_data",
        "--exclude-module=manage_image_mapping",
        # 隐藏导入（减少exe大小）
        "--hidden-import=PyQt5.QtWidgets",
        "--hidden-import=PyQt5.QtCore",
        "--hidden-import=PyQt5.QtGui",
        "--hidden-import=crypto",
        "--hidden-import=crypto.Cipher",
        "--hidden-import=crypto.Cipher.AES",
        "main.py"
    ]

    print("执行命令:", " ".join(cmd))

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')

        if result.returncode == 0:
            print("✓ 打包成功！")

            # 显示输出信息
            if result.stdout:
                print("输出信息:", result.stdout[:500])

            return True
        else:
            print("✗ 打包失败")
            print("错误信息:", result.stderr)
            return False

    except Exception as e:
        print(f"✗ 打包过程中发生错误: {e}")
        return False

def show_result():
    """显示打包结果"""
    print_header("打包完成")

    exe_path = Path("dist") / "极智考典.exe"
    if exe_path.exists():
        exe_size = exe_path.stat().st_size / (1024*1024)  # MB
        print(f"✓ EXE文件: {exe_path}")
        print(f"✓ 文件大小: {exe_size:.2f} MB")

        print("\n下一步操作:")
        print("1. 测试 dist/极智考典.exe 是否正常运行")
        print("2. 将exe文件分发给用户")
        print("3. 使用 admin/activation_admin.py 生成激活码")
        print("4. 将激活码提供给用户")
    else:
        print("✗ EXE文件未生成")

def main():
    """主函数"""
    print_header("极智考典 - 用户版本打包工具")

    # 检查是否在 user_version 目录
    current_dir = Path.cwd()
    if current_dir.name != "user_version":
        print("错误: 请在 user_version 目录中运行此脚本")
        print(f"当前目录: {current_dir}")
        print("请执行: cd user_version && python ../build_user_version.py")
        return 1

    # 检查依赖
    if not check_dependencies():
        return 1

    # 清理旧文件
    clean_old_files()

    # 打包exe
    if build_exe():
        show_result()
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())