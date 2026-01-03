#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单解密脚本
直接解密试卷文件并显示JSON数据
"""

import os
import sys
import json
from pathlib import Path

# 添加项目路径到系统路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from core.data_encryptor import encryptor


def decrypt_and_show(exam_number=1):
    """
    解密并显示指定试卷的JSON数据

    Args:
        exam_number: 试卷编号（1或2）
    """
    # 构建文件路径
    encrypted_file = project_root / "data" / "exams" / f"exam_{exam_number:03d}.json.enc"

    if not encrypted_file.exists():
        print(f"错误：文件不存在 - {encrypted_file}")
        return None

    print(f"正在解密: {encrypted_file.name}")
    print("-" * 50)

    try:
        # 读取加密文件内容
        with open(encrypted_file, 'r', encoding='utf-8') as f:
            encrypted_b64 = f.read().strip()

        # 直接解密数据（不保存文件）
        decrypted_data = encryptor.decrypt_data(encrypted_b64)

        # 显示解密后的数据
        print("解密成功！")
        print(f"数据类型: {type(decrypted_data).__name__}")

        if isinstance(decrypted_data, dict):
            print(f"字典键数量: {len(decrypted_data)}")
            print("\n数据结构:")
            for key, value in decrypted_data.items():
                if isinstance(value, list):
                    print(f"  {key}: 列表 ({len(value)} 个元素)")
                elif isinstance(value, dict):
                    print(f"  {key}: 字典 ({len(value)} 个键)")
                else:
                    print(f"  {key}: {type(value).__name__}")

        elif isinstance(decrypted_data, list):
            print(f"列表元素数量: {len(decrypted_data)}")

        # 格式化输出JSON
        formatted_json = json.dumps(decrypted_data, ensure_ascii=False, indent=2)

        print(f"\nJSON数据大小: {len(formatted_json)} 字符")
        print("\n完整JSON数据:")
        print("=" * 80)
        print(formatted_json)
        print("=" * 80)

        # 保存到文件（可选）
        save_choice = input("\n是否保存到文件？(y/n): ").strip().lower()
        if save_choice == 'y':
            output_file = project_root / f"exam_{exam_number:03d}_decrypted.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(formatted_json)
            print(f"已保存到: {output_file}")

        return decrypted_data

    except Exception as e:
        print(f"解密失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def list_encrypted_files():
    """列出所有加密文件"""
    exams_dir = project_root / "data" / "exams"

    if not exams_dir.exists():
        print(f"错误：目录不存在 - {exams_dir}")
        return []

    encrypted_files = []
    for file in exams_dir.glob("*.enc"):
        encrypted_files.append(file)

    return encrypted_files


def main():
    """主函数"""
    print("=" * 60)
    print("简单试卷解密工具")
    print("=" * 60)

    # 列出所有加密文件
    encrypted_files = list_encrypted_files()

    if not encrypted_files:
        print("未找到加密试卷文件 (.enc)")
        return

    print(f"找到 {len(encrypted_files)} 个加密试卷文件:")
    for i, file in enumerate(encrypted_files, 1):
        print(f"  {i}. {file.name}")

    print("\n选择要解密的试卷:")
    print("  1. exam_001.json.enc")
    print("  2. exam_002.json.enc")
    print("  3. 解密所有试卷")
    print("  4. 退出")

    choice = input("\n请输入选项 (1-4): ").strip()

    if choice == '1':
        decrypt_and_show(1)
    elif choice == '2':
        decrypt_and_show(2)
    elif choice == '3':
        for i in range(1, len(encrypted_files) + 1):
            print(f"\n{'='*60}")
            print(f"解密试卷 {i}")
            print('='*60)
            decrypt_and_show(i)
            input("\n按Enter键继续下一个...")
    elif choice == '4':
        print("退出程序")
        return
    else:
        print("无效的选项")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    except Exception as e:
        print(f"\n程序运行出错: {str(e)}")
        import traceback
        traceback.print_exc()