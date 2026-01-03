#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片映射管理工具
用于管理题目ID到图片文件的映射关系
"""

import os
import json
import sys

def load_image_mapping():
    """加载图片映射配置"""
    config_path = os.path.join("data", "image_mapping.json")

    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # 创建默认配置
        default_config = {
            "image_mapping": {},
            "image_config": {
                "default_max_width": 800,
                "image_dir": "data/pics",
                "supported_formats": [".txt", ".png", ".jpg", ".jpeg", ".gif", ".bmp"]
            }
        }
        return default_config

def save_image_mapping(config):
    """保存图片映射配置"""
    config_path = os.path.join("data", "image_mapping.json")

    # 确保目录存在
    os.makedirs(os.path.dirname(config_path), exist_ok=True)

    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print(f"配置已保存到: {config_path}")

def add_image_mapping(question_id, image_filename):
    """添加图片映射

    Args:
        question_id: 题目ID
        image_filename: 图片文件名
    """
    config = load_image_mapping()

    # 检查图片文件是否存在
    image_dir = config.get('image_config', {}).get('image_dir', 'data/pics')
    image_path = os.path.join(image_dir, image_filename)

    if not os.path.exists(image_path):
        # 尝试添加常见后缀
        found = False
        for ext in ['.txt', '.png', '.jpg', '.jpeg']:
            test_path = os.path.join(image_dir, f"{image_filename}{ext}")
            if os.path.exists(test_path):
                image_filename = f"{image_filename}{ext}"
                image_path = test_path
                found = True
                break

        if not found:
            print(f"警告: 图片文件不存在: {image_path}")
            print("请确保图片文件已放置在 data/pics 目录下")
            return False

    # 添加映射
    config['image_mapping'][question_id] = image_filename
    save_image_mapping(config)

    print(f"已添加映射: {question_id} -> {image_filename}")
    return True

def remove_image_mapping(question_id):
    """删除图片映射

    Args:
        question_id: 题目ID
    """
    config = load_image_mapping()

    if question_id in config['image_mapping']:
        removed = config['image_mapping'].pop(question_id)
        save_image_mapping(config)
        print(f"已删除映射: {question_id} -> {removed}")
        return True
    else:
        print(f"错误: 未找到题目ID: {question_id}")
        return False

def list_image_mapping():
    """列出所有图片映射"""
    config = load_image_mapping()

    print("当前图片映射:")
    print("-" * 80)

    if not config['image_mapping']:
        print("暂无图片映射")
    else:
        for question_id, image_filename in config['image_mapping'].items():
            print(f"  {question_id}: {image_filename}")

    print("-" * 80)
    print(f"图片目录: {config['image_config'].get('image_dir', 'data/pics')}")
    print(f"默认最大宽度: {config['image_config'].get('default_max_width', 800)}")

def list_images():
    """列出data/pics目录下的所有图片文件"""
    image_dir = "data/pics"

    if not os.path.exists(image_dir):
        print(f"错误: 图片目录不存在: {image_dir}")
        return

    print(f"{image_dir} 目录下的图片文件:")
    print("-" * 80)

    files = os.listdir(image_dir)
    image_files = [f for f in files if f.lower().endswith(('.txt', '.png', '.jpg', '.jpeg', '.gif', '.bmp'))]

    if not image_files:
        print("暂无图片文件")
    else:
        for i, filename in enumerate(image_files, 1):
            file_path = os.path.join(image_dir, filename)
            file_size = os.path.getsize(file_path)
            print(f"  {i:2d}. {filename} ({file_size:,} 字节)")

    print("-" * 80)
    print(f"共 {len(image_files)} 个图片文件")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法:")
        print("  python manage_image_mapping.py list          # 列出所有映射")
        print("  python manage_image_mapping.py images        # 列出所有图片文件")
        print("  python manage_image_mapping.py add <题目ID> <图片文件名>")
        print("  python manage_image_mapping.py remove <题目ID>")
        return

    command = sys.argv[1]

    if command == "list":
        list_image_mapping()
    elif command == "images":
        list_images()
    elif command == "add":
        if len(sys.argv) != 4:
            print("用法: python manage_image_mapping.py add <题目ID> <图片文件名>")
            return
        question_id = sys.argv[2]
        image_filename = sys.argv[3]
        add_image_mapping(question_id, image_filename)
    elif command == "remove":
        if len(sys.argv) != 3:
            print("用法: python manage_image_mapping.py remove <题目ID>")
            return
        question_id = sys.argv[2]
        remove_image_mapping(question_id)
    else:
        print(f"未知命令: {command}")
        print("可用命令: list, images, add, remove")

if __name__ == "__main__":
    main()