#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
加密现有试卷文件脚本
"""

import os
import sys
from core.data_encryptor import encryptor


def encrypt_all_exams():
    """加密所有试卷文件"""
    # 获取项目根目录
    project_root = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(project_root, "data")
    exams_dir = os.path.join(data_dir, "exams")

    if not os.path.exists(exams_dir):
        print(f"试卷目录不存在: {exams_dir}")
        return

    print(f"开始加密试卷目录: {exams_dir}")
    print("=" * 50)

    # 加密所有JSON文件
    encrypted_count = 0
    skipped_count = 0
    error_count = 0

    for filename in os.listdir(exams_dir):
        if filename.endswith('.json') and not filename.endswith('.enc'):
            input_file = os.path.join(exams_dir, filename)
            output_file = input_file + '.enc'

            # 检查是否已存在加密文件
            if os.path.exists(output_file):
                print(f"跳过 {filename}: 已存在加密文件")
                skipped_count += 1
                continue

            try:
                # 加密文件
                encryptor.encrypt_file(input_file, output_file)
                encrypted_count += 1

                # 验证加密文件可以正确解密
                with open(output_file, 'r', encoding='utf-8') as f:
                    encrypted_data = f.read().strip()

                # 尝试解密验证
                decrypted_data = encryptor.decrypt_data(encrypted_data)
                print(f"✓ 成功加密: {filename} -> {filename}.enc")
                print(f"  题目数量: {len(decrypted_data.get('questions', []))}")

                # 询问是否删除原始文件
                delete_original = input(f"  是否删除原始文件 {filename}? (y/N): ").strip().lower()
                if delete_original == 'y':
                    os.remove(input_file)
                    print(f"  已删除原始文件: {filename}")

            except Exception as e:
                print(f"✗ 加密失败 {filename}: {e}")
                error_count += 1

    print("=" * 50)
    print(f"加密完成!")
    print(f"成功加密: {encrypted_count} 个文件")
    print(f"跳过: {skipped_count} 个文件")
    print(f"失败: {error_count} 个文件")

    # 显示加密后的文件列表
    if encrypted_count > 0:
        print("\n加密后的文件列表:")
        for filename in os.listdir(exams_dir):
            if filename.endswith('.enc'):
                file_path = os.path.join(exams_dir, filename)
                file_size = os.path.getsize(file_path)
                print(f"  - {filename} ({file_size} bytes)")


def test_encryption():
    """测试加密解密功能"""
    print("测试加密解密功能...")
    print("=" * 50)

    # 测试数据
    test_data = {
        "exam_id": "test_exam",
        "exam_name": "测试试卷",
        "questions": [
            {
                "id": "q1",
                "question": "测试题目",
                "answer": ["A"]
            }
        ]
    }

    # 加密
    encrypted = encryptor.encrypt_data(test_data)
    print(f"原始数据: {test_data}")
    print(f"加密后长度: {len(encrypted)} 字符")
    print(f"加密数据预览: {encrypted[:50]}...")

    # 解密
    decrypted = encryptor.decrypt_data(encrypted)
    print(f"解密后数据: {decrypted}")

    # 验证
    if test_data == decrypted:
        print("✓ 加密解密测试通过!")
    else:
        print("✗ 加密解密测试失败!")

    print("=" * 50)


if __name__ == "__main__":
    print("试卷文件加密工具")
    print("=" * 50)

    # 测试加密功能
    test_encryption()

    # 询问是否加密现有文件
    choice = input("\n是否加密现有的试卷文件? (y/N): ").strip().lower()
    if choice == 'y':
        encrypt_all_exams()
    else:
        print("已取消加密操作")

    print("\n说明:")
    print("1. 加密后的文件扩展名为 .json.enc")
    print("2. 程序会自动识别并解密 .enc 文件")
    print("3. 原始JSON文件可以删除以增加安全性")
    print("4. 加密密钥保存在 core/data_encryptor.py 中")