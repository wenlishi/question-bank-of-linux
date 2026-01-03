#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试激活码系统
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.activation import ActivationManager

def test_activation_system():
    """测试激活码系统"""
    print("=== 测试激活码系统 ===\n")

    # 创建激活码管理器
    activation_manager = ActivationManager()

    # 1. 生成激活码
    print("1. 生成激活码...")
    code1 = activation_manager.generate_activation_code(days=30, max_uses=1)
    code2 = activation_manager.generate_activation_code(days=365, max_uses=3)
    print(f"  生成激活码1: {code1} (30天, 单设备)")
    print(f"  生成激活码2: {code2} (1年, 3设备)\n")

    # 2. 验证激活码
    print("2. 验证激活码...")
    device_id1 = "test_device_001"
    device_id2 = "test_device_002"

    # 第一次激活
    result1 = activation_manager.verify_activation(code1, device_id1)
    print(f"  设备1激活码1: {'成功' if result1 else '失败'}")

    # 同一设备再次激活
    result2 = activation_manager.verify_activation(code1, device_id1)
    print(f"  设备1再次激活码1: {'成功' if result2 else '失败'}")

    # 不同设备激活（应该失败，因为max_uses=1）
    result3 = activation_manager.verify_activation(code1, device_id2)
    print(f"  设备2激活码1: {'成功' if result3 else '失败'}")

    # 激活码2可以激活多个设备
    result4 = activation_manager.verify_activation(code2, device_id1)
    result5 = activation_manager.verify_activation(code2, device_id2)
    print(f"  设备1激活码2: {'成功' if result4 else '失败'}")
    print(f"  设备2激活码2: {'成功' if result5 else '失败'}\n")

    # 3. 获取激活码信息
    print("3. 获取激活码信息...")
    info1 = activation_manager.get_activation_info(code1)
    info2 = activation_manager.get_activation_info(code2)

    if info1:
        print(f"  激活码1信息:")
        print(f"    状态: {info1.get('status')}")
        print(f"    使用次数: {info1.get('used_count')}/{info1.get('max_uses')}")
        print(f"    设备数: {len(info1.get('devices', []))}")

    if info2:
        print(f"  激活码2信息:")
        print(f"    状态: {info2.get('status')}")
        print(f"    使用次数: {info2.get('used_count')}/{info2.get('max_uses')}")
        print(f"    设备数: {len(info2.get('devices', []))}\n")

    # 4. 统计信息
    print("4. 统计信息...")
    stats = activation_manager.get_activation_stats()
    print(f"  总激活码数: {stats['total']}")
    print(f"  有效激活码: {stats['active']}")
    print(f"  总使用次数: {stats['used']}\n")

    # 5. 列出所有激活码
    print("5. 所有激活码:")
    activations = activation_manager.list_activations()
    for code, info in activations.items():
        print(f"  {code}: {info.get('status')}, 使用{info.get('used_count')}/{info.get('max_uses')}次")

    print("\n=== 测试完成 ===")

def test_question_bank():
    """测试题目库"""
    print("\n=== 测试题目库 ===\n")

    from core.question_bank import QuestionBank, QuestionType

    # 创建题目库
    question_bank = QuestionBank()

    # 1. 获取题目数量
    count = question_bank.get_question_count()
    print(f"1. 题目总数: {count}")

    # 2. 获取分类
    categories = question_bank.get_categories()
    print(f"2. 题目分类: {categories}")

    # 3. 随机获取题目
    print("3. 随机获取5道题目:")
    questions = question_bank.get_random_questions(count=5)
    for i, q in enumerate(questions, 1):
        print(f"   题目{i}: {q.get('question')[:50]}...")

    # 4. 测试答题
    print("\n4. 测试答题:")
    if questions:
        question = questions[0]
        question_id = question.get('id')
        correct_answer = question.get('answer', [])[0] if question.get('answer') else ""

        # 测试正确答案
        is_correct, explanation = question_bank.check_answer(question_id, [correct_answer])
        print(f"   正确答案测试: {'正确' if is_correct else '错误'}")

        # 测试错误答案
        wrong_answer = "错误答案"
        is_correct, explanation = question_bank.check_answer(question_id, [wrong_answer])
        print(f"   错误答案测试: {'正确' if is_correct else '错误'}")

    # 5. 获取统计信息
    print("\n5. 学习统计:")
    stats = question_bank.get_overall_stats()
    print(f"   总答题数: {stats['total_questions']}")
    print(f"   正确率: {stats['accuracy']}%")

    print("\n=== 题目库测试完成 ===")

if __name__ == "__main__":
    test_activation_system()
    test_question_bank()