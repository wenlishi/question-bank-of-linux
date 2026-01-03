#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
试卷解密工具
用于解密data/exams目录下的加密试卷文件，获取原始JSON数据
"""

import os
import sys
import json
from pathlib import Path

# 添加项目路径到系统路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from core.data_encryptor import encryptor


def decrypt_exam_file(encrypted_file_path, output_dir=None):
    """
    解密单个试卷文件

    Args:
        encrypted_file_path: 加密文件路径
        output_dir: 输出目录（可选，默认为当前目录下的decrypted_exams目录）

    Returns:
        解密后的文件路径
    """
    # 检查文件是否存在
    if not os.path.exists(encrypted_file_path):
        print(f"错误：文件不存在 - {encrypted_file_path}")
        return None

    # 设置输出目录
    if output_dir is None:
        output_dir = project_root / "decrypted_exams"

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 生成输出文件名
    filename = os.path.basename(encrypted_file_path)
    if filename.endswith('.enc'):
        output_filename = filename[:-4]  # 移除.enc后缀
    else:
        output_filename = filename + '.decrypted.json'

    output_path = os.path.join(output_dir, output_filename)

    try:
        # 使用项目中的加密器解密文件
        decrypted_path = encryptor.decrypt_file(encrypted_file_path, output_path)

        # 读取解密后的JSON数据
        with open(decrypted_path, 'r', encoding='utf-8') as f:
            decrypted_data = json.load(f)

        print(f"✓ 成功解密: {filename}")
        print(f"  保存到: {decrypted_path}")
        print(f"  数据大小: {len(json.dumps(decrypted_data, ensure_ascii=False))} 字符")

        return decrypted_path, decrypted_data

    except Exception as e:
        print(f"✗ 解密失败: {filename}")
        print(f"  错误: {str(e)}")
        return None, None


def decrypt_all_exams(exams_dir=None, output_dir=None):
    """
    解密所有试卷文件

    Args:
        exams_dir: 加密试卷目录（可选，默认为data/exams）
        output_dir: 输出目录（可选）

    Returns:
        解密结果列表
    """
    # 设置默认目录
    if exams_dir is None:
        exams_dir = project_root / "data" / "exams"

    if output_dir is None:
        output_dir = project_root / "decrypted_exams"

    # 检查目录是否存在
    if not os.path.exists(exams_dir):
        print(f"错误：试卷目录不存在 - {exams_dir}")
        return []

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    print(f"开始解密试卷文件...")
    print(f"加密试卷目录: {exams_dir}")
    print(f"解密输出目录: {output_dir}")
    print("-" * 50)

    results = []

    # 遍历所有加密文件
    for filename in os.listdir(exams_dir):
        if filename.endswith('.enc'):
            encrypted_file_path = os.path.join(exams_dir, filename)

            # 解密文件
            decrypted_path, decrypted_data = decrypt_exam_file(
                encrypted_file_path, output_dir
            )

            if decrypted_path:
                results.append({
                    'original_file': filename,
                    'decrypted_file': os.path.basename(decrypted_path),
                    'decrypted_path': decrypted_path,
                    'data': decrypted_data
                })

    print("-" * 50)
    print(f"解密完成！共解密 {len(results)} 个文件")

    # 创建汇总文件
    if results:
        summary_path = os.path.join(output_dir, "decryption_summary.json")
        summary = {
            'total_decrypted': len(results),
            'files': [
                {
                    'original': r['original_file'],
                    'decrypted': r['decrypted_file'],
                    'path': r['decrypted_path']
                }
                for r in results
            ]
        }

        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        print(f"汇总文件: {summary_path}")

    return results


def view_decrypted_data(decrypted_file_path):
    """
    查看解密后的数据

    Args:
        decrypted_file_path: 解密后的文件路径
    """
    if not os.path.exists(decrypted_file_path):
        print(f"错误：文件不存在 - {decrypted_file_path}")
        return

    try:
        with open(decrypted_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        print(f"文件: {decrypted_file_path}")
        print(f"数据大小: {len(json.dumps(data, ensure_ascii=False))} 字符")
        print("-" * 50)

        # 显示数据结构
        if isinstance(data, dict):
            print("数据结构（字典）:")
            for key, value in data.items():
                if isinstance(value, list):
                    print(f"  {key}: 列表，包含 {len(value)} 个元素")
                elif isinstance(value, dict):
                    print(f"  {key}: 字典，包含 {len(value)} 个键")
                else:
                    print(f"  {key}: {type(value).__name__}")

        elif isinstance(data, list):
            print(f"数据结构: 列表，包含 {len(data)} 个元素")
            if data:
                print("第一个元素:")
                print(json.dumps(data[0], ensure_ascii=False, indent=2))

        # 显示前几行数据
        print("\n数据预览（前500字符）:")
        preview = json.dumps(data, ensure_ascii=False, indent=2)[:500]
        print(preview + "..." if len(preview) == 500 else preview)

    except Exception as e:
        print(f"读取文件失败: {str(e)}")


def main():
    """主函数"""
    print("=" * 60)
    print("试卷解密工具")
    print("=" * 60)

    # 定义目录
    exams_dir = project_root / "data" / "exams"
    output_dir = project_root / "decrypted_exams"

    # 检查是否有加密文件
    if not os.path.exists(exams_dir):
        print(f"错误：试卷目录不存在 - {exams_dir}")
        return

    encrypted_files = [f for f in os.listdir(exams_dir) if f.endswith('.enc')]

    if not encrypted_files:
        print("未找到加密试卷文件 (.enc)")
        return

    print(f"找到 {len(encrypted_files)} 个加密试卷文件:")
    for i, filename in enumerate(encrypted_files, 1):
        print(f"  {i}. {filename}")

    print("\n选择操作:")
    print("  1. 解密所有试卷文件")
    print("  2. 解密指定试卷文件")
    print("  3. 查看已解密的文件")
    print("  4. 退出")

    choice = input("\n请输入选项 (1-4): ").strip()

    if choice == '1':
        # 解密所有文件
        results = decrypt_all_exams(exams_dir, output_dir)

        if results:
            print("\n解密完成！文件保存在:")
            print(f"  {output_dir}")

            # 询问是否查看数据
            view_choice = input("\n是否查看解密后的数据？(y/n): ").strip().lower()
            if view_choice == 'y':
                for result in results:
                    print(f"\n查看文件: {result['decrypted_file']}")
                    view_decrypted_data(result['decrypted_path'])
                    print("-" * 50)

    elif choice == '2':
        # 解密指定文件
        print("\n选择要解密的文件:")
        for i, filename in enumerate(encrypted_files, 1):
            print(f"  {i}. {filename}")

        try:
            file_choice = int(input("\n请输入文件编号: ").strip())
            if 1 <= file_choice <= len(encrypted_files):
                filename = encrypted_files[file_choice - 1]
                encrypted_path = os.path.join(exams_dir, filename)

                decrypted_path, decrypted_data = decrypt_exam_file(
                    encrypted_path, output_dir
                )

                if decrypted_path:
                    print(f"\n解密成功！")
                    print(f"文件: {decrypted_path}")

                    # 询问是否查看数据
                    view_choice = input("\n是否查看解密后的数据？(y/n): ").strip().lower()
                    if view_choice == 'y':
                        view_decrypted_data(decrypted_path)
            else:
                print("无效的文件编号")
        except ValueError:
            print("请输入有效的数字")

    elif choice == '3':
        # 查看已解密的文件
        if os.path.exists(output_dir):
            decrypted_files = [f for f in os.listdir(output_dir)
                             if f.endswith('.json') and not f.endswith('_summary.json')]

            if decrypted_files:
                print(f"\n找到 {len(decrypted_files)} 个已解密的文件:")
                for i, filename in enumerate(decrypted_files, 1):
                    print(f"  {i}. {filename}")

                try:
                    file_choice = int(input("\n请输入文件编号查看数据: ").strip())
                    if 1 <= file_choice <= len(decrypted_files):
                        filename = decrypted_files[file_choice - 1]
                        file_path = os.path.join(output_dir, filename)
                        view_decrypted_data(file_path)
                    else:
                        print("无效的文件编号")
                except ValueError:
                    print("请输入有效的数字")
            else:
                print("未找到已解密的文件")
        else:
            print("解密目录不存在，请先解密文件")

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