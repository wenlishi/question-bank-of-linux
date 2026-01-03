#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成示例激活码
"""

import sys
import os
import json
from datetime import datetime

# 添加core模块到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from core.activation import ActivationManager

    print("=== 生成示例激活码 ===\n")

    # 创建激活码管理器
    manager = ActivationManager()

    # 生成不同类型的激活码
    print("1. 体验版激活码 (7天有效期):")
    trial_code = manager.generate_activation_code(days=7, max_uses=1)
    print(f"   {trial_code}\n")

    print("2. 月卡激活码 (30天有效期):")
    monthly_code = manager.generate_activation_code(days=30, max_uses=1)
    print(f"   {monthly_code}\n")

    print("3. 年卡激活码 (365天有效期):")
    yearly_code = manager.generate_activation_code(days=365, max_uses=1)
    print(f"   {yearly_code}\n")

    print("4. 多设备版激活码 (365天，3次使用):")
    multi_code = manager.generate_activation_code(days=365, max_uses=3)
    print(f"   {multi_code}\n")

    print("=== 激活码信息 ===")
    print(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"保存位置: data/activations.json")
    print("\n提示: 可以使用管理后台查看和管理这些激活码。")

except ImportError as e:
    print(f"导入错误: {e}")
    print("\n请先安装依赖:")
    print("pip install PyQt5 pycryptodome")

except Exception as e:
    print(f"错误: {e}")