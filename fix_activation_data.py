#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复激活码数据文件
"""

import os
import json
import sys

def fix_activation_data():
    """修复激活码数据文件"""
    data_dir = "data"
    activation_file = os.path.join(data_dir, "activations.json")

    print("=== 修复激活码数据 ===\n")

    if not os.path.exists(activation_file):
        print("❌ 激活码数据文件不存在")
        print("✅ 无需修复，可以正常使用")
        return

    # 读取原始文件
    try:
        with open(activation_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return

    print(f"找到 {len(data)} 个激活码记录")

    # 备份原始文件
    backup_file = activation_file + ".backup"
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ 已备份原始文件到: {backup_file}")

    # 分析数据
    string_count = 0
    dict_count = 0

    for code, info in data.items():
        if isinstance(info, str):
            string_count += 1
            print(f"  {code}: 字符串数据 (需要修复)")
        elif isinstance(info, dict):
            dict_count += 1
            print(f"  {code}: 字典数据 (正常)")
        else:
            print(f"  {code}: 未知类型 {type(info)}")

    print(f"\n统计: {string_count} 个字符串, {dict_count} 个字典")

    if string_count == 0:
        print("✅ 数据正常，无需修复")
        return

    # 询问是否修复
    choice = input("\n是否修复数据？(y/n): ").strip().lower()
    if choice != 'y':
        print("❌ 取消修复")
        return

    # 创建新的数据文件
    new_data = {}
    for code, info in data.items():
        if isinstance(info, dict):
            # 字典数据直接复制
            new_data[code] = info
        elif isinstance(info, str):
            # 字符串数据，创建新的激活码信息
            print(f"⚠️  删除无效的字符串数据: {code}")
            # 这里可以选择重新生成激活码，或者跳过

    # 保存新数据
    with open(activation_file, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 修复完成!")
    print(f"原始记录: {len(data)} 个")
    print(f"修复后记录: {len(new_data)} 个")
    print(f"删除了 {len(data) - len(new_data)} 个无效记录")

    # 生成新的激活码示例
    print("\n=== 生成新的激活码示例 ===")
    print("请使用以下命令生成新的激活码:")
    print("1. 启动管理后台: python admin/activation_admin.py")
    print("2. 或使用命令行: python -c \"from core.activation import ActivationManager; m=ActivationManager(); print(m.generate_activation_code(365, 1))\"")

    # 创建测试激活码
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from core.activation import ActivationManager

        manager = ActivationManager()
        test_code = manager.generate_activation_code(days=7, max_uses=1)
        print(f"\n✅ 已生成测试激活码: {test_code}")
        print("   有效期: 7天")
        print("   使用次数: 1次")

    except ImportError as e:
        print(f"\n⚠️  无法导入模块: {e}")
        print("请先安装依赖: pip install PyQt5 pycryptodome")

if __name__ == "__main__":
    try:
        fix_activation_data()
    except KeyboardInterrupt:
        print("\n\n程序已退出")
    except Exception as e:
        print(f"\n❌ 错误: {e}")