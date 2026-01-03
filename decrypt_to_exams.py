#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
解密试卷到data/exams文件夹
将加密的试卷文件解密后保存到同一目录下
"""

import os
import sys
import json
from pathlib import Path

# 添加项目路径到系统路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from core.data_encryptor import encryptor


def decrypt_to_exams_folder():
    """
    解密所有试卷文件到data/exams文件夹
    """
    # 定义目录
    exams_dir = project_root / "data" / "exams"

    if not exams_dir.exists():
        print(f"错误：目录不存在 - {exams_dir}")
        return []

    # 查找所有加密文件
    encrypted_files = []
    for file in exams_dir.glob("*.enc"):
        encrypted_files.append(file)

    if not encrypted_files:
        print("未找到加密试卷文件 (.enc)")
        return []

    print(f"找到 {len(encrypted_files)} 个加密试卷文件")
    print("开始解密...")
    print("-" * 50)

    results = []

    for encrypted_file in encrypted_files:
        # 生成输出文件名（移除.enc后缀）
        output_filename = encrypted_file.stem  # 移除.enc，保留exam_001.json
        output_path = exams_dir / output_filename

        print(f"解密: {encrypted_file.name} -> {output_filename}")

        try:
            # 使用项目中的加密器解密文件
            decrypted_path = encryptor.decrypt_file(str(encrypted_file), str(output_path))

            # 验证解密文件
            if os.path.exists(decrypted_path):
                with open(decrypted_path, 'r', encoding='utf-8') as f:
                    decrypted_data = json.load(f)

                results.append({
                    'original': encrypted_file.name,
                    'decrypted': output_filename,
                    'path': decrypted_path,
                    'size': len(json.dumps(decrypted_data, ensure_ascii=False))
                })

                print(f"  ✓ 成功解密，大小: {results[-1]['size']} 字符")
            else:
                print(f"  ✗ 解密文件未创建")

        except Exception as e:
            print(f"  ✗ 解密失败: {str(e)}")

    print("-" * 50)

    if results:
        # 创建汇总文件
        summary_path = exams_dir / "decryption_summary.json"
        summary = {
            'total_decrypted': len(results),
            'files': [
                {
                    'original': r['original'],
                    'decrypted': r['decrypted'],
                    'path': str(Path(r['path']).relative_to(project_root)),
                    'size': r['size']
                }
                for r in results
            ]
        }

        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        print(f"解密完成！共解密 {len(results)} 个文件")
        print(f"汇总文件: {summary_path}")

        # 显示解密文件列表
        print("\n解密后的文件:")
        for r in results:
            print(f"  • {r['decrypted']} ({r['size']} 字符)")

    return results


def view_decrypted_file(filename=None):
    """
    查看解密后的文件内容

    Args:
        filename: 文件名（可选，如exam_001.json）
    """
    exams_dir = project_root / "data" / "exams"

    if not exams_dir.exists():
        print(f"错误：目录不存在 - {exams_dir}")
        return

    # 如果没有指定文件名，列出所有JSON文件
    if filename is None:
        json_files = []
        for file in exams_dir.glob("*.json"):
            if not file.name.endswith('.enc') and file.name != 'decryption_summary.json':
                json_files.append(file)

        if not json_files:
            print("未找到解密后的JSON文件")
            return

        print(f"找到 {len(json_files)} 个JSON文件:")
        for i, file in enumerate(json_files, 1):
            print(f"  {i}. {file.name}")

        try:
            choice = input("\n请输入文件编号查看内容 (或按Enter跳过): ").strip()
            if choice:
                file_idx = int(choice) - 1
                if 0 <= file_idx < len(json_files):
                    filename = json_files[file_idx].name
                else:
                    print("无效的文件编号")
                    return
            else:
                return
        except ValueError:
            print("请输入有效的数字")
            return

    # 查看指定文件
    file_path = exams_dir / filename

    if not file_path.exists():
        print(f"错误：文件不存在 - {file_path}")
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        print(f"\n文件: {filename}")
        print(f"大小: {len(json.dumps(data, ensure_ascii=False))} 字符")
        print("-" * 50)

        # 显示数据结构
        if isinstance(data, dict):
            print("数据结构（字典）:")
            for key, value in data.items():
                if isinstance(value, list):
                    print(f"  {key}: 列表 ({len(value)} 个元素)")
                elif isinstance(value, dict):
                    print(f"  {key}: 字典 ({len(value)} 个键)")
                else:
                    value_preview = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                    print(f"  {key}: {type(value).__name__} = {value_preview}")

        elif isinstance(data, list):
            print(f"数据结构: 列表 ({len(data)} 个元素)")
            if data:
                print("第一个元素:")
                first_elem = data[0]
                if isinstance(first_elem, dict):
                    for key, value in first_elem.items():
                        value_preview = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                        print(f"  {key}: {value_preview}")
                else:
                    print(f"  {first_elem}")

        # 显示完整JSON（前1000字符）
        print("\nJSON预览（前1000字符）:")
        full_json = json.dumps(data, ensure_ascii=False, indent=2)
        preview = full_json[:1000]
        print(preview + "..." if len(preview) == 1000 else preview)

        # 询问是否保存完整JSON到单独文件
        save_choice = input("\n是否保存完整JSON到单独文件？(y/n): ").strip().lower()
        if save_choice == 'y':
            output_file = exams_dir / f"{file_path.stem}_full.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(full_json)
            print(f"完整JSON已保存到: {output_file}")

    except Exception as e:
        print(f"读取文件失败: {str(e)}")


def main():
    """主函数"""
    print("=" * 60)
    print("试卷解密工具 - 保存到data/exams文件夹")
    print("=" * 60)

    exams_dir = project_root / "data" / "exams"

    if not exams_dir.exists():
        print(f"错误：目录不存在，请创建: {exams_dir}")
        return

    print(f"工作目录: {exams_dir}")
    print()

    # 检查现有文件
    encrypted_files = list(exams_dir.glob("*.enc"))
    json_files = [f for f in exams_dir.glob("*.json")
                  if not f.name.endswith('.enc') and f.name != 'decryption_summary.json']

    print(f"加密文件: {len(encrypted_files)} 个")
    print(f"JSON文件: {len(json_files)} 个")
    print()

    print("选择操作:")
    print("  1. 解密所有加密试卷到当前文件夹")
    print("  2. 查看解密后的文件内容")
    print("  3. 退出")

    choice = input("\n请输入选项 (1-3): ").strip()

    if choice == '1':
        # 解密所有文件
        results = decrypt_to_exams_folder()

        if results:
            print("\n操作完成！")
            print("解密后的文件已保存到data/exams文件夹")

            # 询问是否查看
            view_choice = input("\n是否查看解密后的文件？(y/n): ").strip().lower()
            if view_choice == 'y':
                view_decrypted_file()

    elif choice == '2':
        # 查看文件内容
        view_decrypted_file()

    elif choice == '3':
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