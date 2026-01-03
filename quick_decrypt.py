#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速解密脚本
直接输出解密后的JSON数据
用法: python quick_decrypt.py [试卷编号]
"""

import os
import sys
import json
from pathlib import Path

# 添加项目路径到系统路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from core.data_encryptor import encryptor


def quick_decrypt(exam_number=1, output_file=None):
    """
    快速解密试卷并输出JSON

    Args:
        exam_number: 试卷编号（1或2）
        output_file: 输出文件路径（可选）
    """
    # 构建文件路径
    encrypted_file = project_root / "data" / "exams" / f"exam_{exam_number:03d}.json.enc"

    if not encrypted_file.exists():
        print(f"错误：文件不存在 - {encrypted_file}", file=sys.stderr)
        return False

    try:
        # 读取加密文件
        with open(encrypted_file, 'r', encoding='utf-8') as f:
            encrypted_b64 = f.read().strip()

        # 解密数据
        decrypted_data = encryptor.decrypt_data(encrypted_b64)

        # 格式化JSON
        formatted_json = json.dumps(decrypted_data, ensure_ascii=False, indent=2)

        # 输出或保存
        if output_file:
            output_path = Path(output_file)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(formatted_json)
            print(f"解密成功！已保存到: {output_path}")
        else:
            # 直接输出到控制台
            print(formatted_json)

        return True

    except Exception as e:
        print(f"解密失败: {str(e)}", file=sys.stderr)
        return False


def list_exams():
    """列出所有可解密的试卷"""
    exams_dir = project_root / "data" / "exams"

    if not exams_dir.exists():
        return []

    exams = []
    for file in exams_dir.glob("exam_*.json.enc"):
        # 提取试卷编号
        name = file.stem  # exam_001.json
        if name.startswith("exam_"):
            try:
                num = int(name[5:8])  # 提取001中的数字
                exams.append((num, file))
            except ValueError:
                continue

    return sorted(exams, key=lambda x: x[0])


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description='解密试卷文件')
    parser.add_argument('exam_number', type=int, nargs='?', default=1,
                       help='试卷编号（默认: 1）')
    parser.add_argument('-o', '--output', type=str,
                       help='输出文件路径（可选）')
    parser.add_argument('-l', '--list', action='store_true',
                       help='列出所有可解密的试卷')
    parser.add_argument('-a', '--all', action='store_true',
                       help='解密所有试卷')

    args = parser.parse_args()

    if args.list:
        exams = list_exams()
        if exams:
            print("可解密的试卷:")
            for num, file in exams:
                print(f"  试卷 {num}: {file.name}")
        else:
            print("未找到加密试卷文件")
        return

    if args.all:
        exams = list_exams()
        if not exams:
            print("未找到加密试卷文件", file=sys.stderr)
            sys.exit(1)

        success_count = 0
        for num, file in exams:
            output_file = args.output.format(num=num) if args.output else f"exam_{num:03d}_decrypted.json"
            print(f"解密试卷 {num}...", end=' ')
            if quick_decrypt(num, output_file):
                success_count += 1
                print("✓")
            else:
                print("✗")

        print(f"\n解密完成：{success_count}/{len(exams)} 个文件成功")
        return

    # 解密单个试卷
    success = quick_decrypt(args.exam_number, args.output)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()