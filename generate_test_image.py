#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成测试图片并转换为base64
"""

import base64
from PIL import Image, ImageDraw, ImageFont
import io

def create_test_image():
    """创建一个简单的测试图片"""
    # 创建一个400x200的白色图片
    img = Image.new('RGB', (400, 200), color='white')
    draw = ImageDraw.Draw(img)

    # 添加一些文本
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()

    draw.text((50, 50), "进程列表测试图", fill='black', font=font)
    draw.text((50, 80), "PID: 1234  CMD: python", fill='blue', font=font)
    draw.text((50, 110), "PID: 5678  CMD: bash", fill='green', font=font)
    draw.text((50, 140), "PID: 9012  CMD: sshd", fill='red', font=font)

    # 画一个简单的表格
    draw.rectangle([40, 40, 360, 160], outline='black', width=2)
    draw.line([40, 70, 360, 70], fill='gray', width=1)
    draw.line([40, 100, 360, 100], fill='gray', width=1)
    draw.line([40, 130, 360, 130], fill='gray', width=1)

    return img

def image_to_base64(img):
    """将PIL图片转换为base64字符串"""
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{img_str}"

def main():
    print("生成测试图片...")

    # 创建图片
    img = create_test_image()

    # 转换为base64
    base64_str = image_to_base64(img)

    # 输出HTML代码
    print("\nHTML代码:")
    print("-" * 80)
    html_code = f'<img src="{base64_str}" alt="进程列表" width="400" />'
    print(html_code)

    # 输出用于JSON的代码
    print("\n用于JSON的代码:")
    print("-" * 80)
    # 只取base64部分（去掉data:image/png;base64,前缀）
    pure_base64 = base64_str.replace('data:image/png;base64,', '')
    print(f'"<img src=\\"data:image/png;base64,{pure_base64}\\" alt=\\"进程列表\\" width=\\"400\\" />"')

    # 保存图片供查看
    img.save("test_process_list.png")
    print(f"\n图片已保存为: test_process_list.png")

    # 显示图片信息
    print(f"\n图片大小: {img.size}")
    print(f"Base64字符串长度: {len(base64_str)} 字符")

if __name__ == "__main__":
    main()