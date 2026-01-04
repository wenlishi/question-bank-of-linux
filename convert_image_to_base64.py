#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将图片文件转换为base64编码，并生成HTML代码
"""

import base64
import os

def image_to_base64(image_path):
    """将图片文件转换为base64字符串"""
    with open(image_path, 'rb') as image_file:
        # 读取图片数据
        image_data = image_file.read()

        # 转换为base64
        base64_str = base64.b64encode(image_data).decode('utf-8')

        # 根据文件类型确定MIME类型
        ext = os.path.splitext(image_path)[1].lower()
        mime_types = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.svg': 'image/svg+xml'
        }

        mime_type = mime_types.get(ext, 'image/png')
        return f"data:{mime_type};base64,{base64_str}"

def main():
    image_path = "data/pics/fruits.png"

    if not os.path.exists(image_path):
        print(f"错误：图片文件不存在: {image_path}")
        return

    print(f"正在转换图片: {image_path}")

    # 获取文件信息
    file_size = os.path.getsize(image_path)
    print(f"文件大小: {file_size} 字节")

    # 转换为base64
    base64_str = image_to_base64(image_path)

    # 输出结果
    print("\n" + "="*80)
    print("HTML代码（可直接复制到题目中）:")
    print("="*80)

    # 生成HTML代码
    html_code = f'<img src="{base64_str}" alt="进程列表" width="600" />'
    print(html_code)

    print("\n" + "="*80)
    print("用于JSON的转义代码:")
    print("="*80)

    # 生成用于JSON的转义代码
    # 需要转义双引号
    json_code = html_code.replace('"', '\\"')
    print(f'"{json_code}"')

    print("\n" + "="*80)
    print("Base64字符串信息:")
    print("="*80)
    print(f"Base64字符串长度: {len(base64_str)} 字符")

    # 计算压缩比
    compression_ratio = len(base64_str) / file_size
    print(f"Base64膨胀率: {compression_ratio:.2f}x (base64比原始文件大约{compression_ratio:.1f}倍)")

if __name__ == "__main__":
    main()