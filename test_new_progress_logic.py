#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新的进度逻辑：进度全局累计，正确率基于上次
"""

import sys
import os
from datetime import datetime, timedelta

# 添加core模块到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.user_progress_manager import UserProgressManager


def simulate_exam_scenario():
    """模拟考试场景"""
    print("=== 模拟考试场景：进度全局累计，正确率基于上次 ===")

    # 使用临时文件测试
    import tempfile
    import shutil

    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    print(f"使用临时目录: {temp_dir}")

    try:
        # 初始化进度管理器（使用临时目录）
        progress_manager = UserProgressManager(data_dir=temp_dir)

        # 模拟试卷信息
        exam_id = "test_exam_001"
        total_questions = 10

        # 1. 初始状态
        print("\n1. 初始状态（未做任何题目）:")
        progress_manager.update_exam_total_questions(exam_id, total_questions)
        progress = progress_manager.get_exam_progress(exam_id)
        print(f"   进度: {progress['progress_percentage']:.1f}% (0/{total_questions})")
        print(f"   正确率: {progress['accuracy_percentage']:.1f}%")

        # 2. 第一次做题：做5题，正确3题
        print("\n2. 第一次做题（做5题，正确3题）:")
        for i in range(5):
            question_id = f"q_{i+1:03d}"
            is_correct = (i < 3)  # 前3题正确，后2题错误
            progress_manager.record_answer(
                exam_id=exam_id,
                question_id=question_id,
                is_correct=is_correct,
                user_answer=[f"answer_{i+1}"]
            )
            print(f"   题目 {question_id}: {'正确' if is_correct else '错误'}")

        progress = progress_manager.get_exam_progress(exam_id)
        print(f"   进度: {progress['progress_percentage']:.1f}% (5/{total_questions})")
        print(f"   正确率: {progress['accuracy_percentage']:.1f}% (3/5 = 60%)")

        # 3. 第二次做题：再做3题（其中2题是新的，1题是重做的）
        print("\n3. 第二次做题（再做3题，其中2题新的，1题重做）:")
        # 重做第1题（这次错了）
        progress_manager.record_answer(
            exam_id=exam_id,
            question_id="q_001",
            is_correct=False,  # 这次做错了
            user_answer=["wrong_answer"]
        )
        print(f"   重做题目 q_001: 错误")

        # 做2个新题
        for i in range(5, 7):  # 第6、7题
            question_id = f"q_{i+1:03d}"
            is_correct = True  # 都正确
            progress_manager.record_answer(
                exam_id=exam_id,
                question_id=question_id,
                is_correct=is_correct,
                user_answer=[f"answer_{i+1}"]
            )
            print(f"   新题目 {question_id}: {'正确' if is_correct else '错误'}")

        progress = progress_manager.get_exam_progress(exam_id)
        print(f"   进度: {progress['progress_percentage']:.1f}% (7/{total_questions})")
        print(f"   正确率: {progress['accuracy_percentage']:.1f}% (第二次做了3题，正确2题 = 66.7%)")

        # 4. 第三次做题：完成所有题目
        print("\n4. 第三次做题（完成剩余3题）:")
        for i in range(7, 10):  # 第8、9、10题
            question_id = f"q_{i+1:03d}"
            is_correct = (i < 9)  # 第8、9题正确，第10题错误
            progress_manager.record_answer(
                exam_id=exam_id,
                question_id=question_id,
                is_correct=is_correct,
                user_answer=[f"answer_{i+1}"]
            )
            print(f"   题目 {question_id}: {'正确' if is_correct else '错误'}")

        progress = progress_manager.get_exam_progress(exam_id)
        print(f"   进度: {progress['progress_percentage']:.1f}% (10/{total_questions} = 100%)")
        print(f"   正确率: {progress['accuracy_percentage']:.1f}% (第三次做了3题，正确2题 = 66.7%)")

        # 5. 第四次做题：重做所有题目（模拟复习）
        print("\n5. 第四次做题（重做所有题目复习）:")
        all_correct = True  # 这次全部做对
        for i in range(10):
            question_id = f"q_{i+1:03d}"
            progress_manager.record_answer(
                exam_id=exam_id,
                question_id=question_id,
                is_correct=all_correct,
                user_answer=[f"review_answer_{i+1}"]
            )

        progress = progress_manager.get_exam_progress(exam_id)
        print(f"   进度: {progress['progress_percentage']:.1f}% (仍然100%，进度不减少)")
        print(f"   正确率: {progress['accuracy_percentage']:.1f}% (第四次做了10题，全部正确 = 100%)")

        # 6. 查看题目历史
        print("\n6. 查看题目 q_001 的历史:")
        history = progress_manager.get_question_history(exam_id, "q_001")
        print(f"   共 {len(history)} 次答题记录:")
        for j, record in enumerate(history, 1):
            print(f"     第{j}次: {'正确' if record['correct'] else '错误'}, 时间: {record['timestamp']}")

        print("\n=== 测试完成 ===")

    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir)
        print(f"\n已清理临时目录: {temp_dir}")


def test_real_exam_progress():
    """测试真实试卷的进度"""
    print("\n=== 测试真实试卷进度 ===")

    progress_manager = UserProgressManager()
    question_manager = __import__('core.question_manager').question_manager.QuestionManager()

    # 获取真实试卷
    exams = question_manager.list_exams()
    if not exams:
        print("未找到试卷数据")
        return

    exam = exams[0]
    exam_id = exam['id']
    total_questions = exam['total_questions']

    print(f"试卷: {exam['name']} ({exam_id})")
    print(f"总题数: {total_questions}")

    # 获取当前进度
    progress = progress_manager.get_exam_progress(exam_id)

    print(f"\n当前进度:")
    print(f"  已做题目: {progress['attempted_questions']}/{total_questions}")
    print(f"  学习进度: {progress['progress_percentage']:.1f}%")
    print(f"  上次正确率: {progress['accuracy_percentage']:.1f}%")

    if progress['last_attempt']:
        print(f"  最后做题时间: {progress['last_attempt']}")

    # 如果有历史数据，显示一些统计
    if progress['attempted_questions'] > 0:
        print(f"\n历史统计:")
        # 获取所有题目历史
        total_attempts = 0
        total_correct = 0
        for q_id in progress_manager.progress_data["exams"].get(exam_id, {}).get("questions", {}):
            q_data = progress_manager.progress_data["exams"][exam_id]["questions"][q_id]
            total_attempts += q_data.get("attempts", 0)
            total_correct += q_data.get("correct", 0)

        if total_attempts > 0:
            overall_accuracy = (total_correct / total_attempts * 100)
            print(f"  总答题次数: {total_attempts}")
            print(f"  总正确次数: {total_correct}")
            print(f"  历史平均正确率: {overall_accuracy:.1f}%")
            print(f"  （注意：界面显示的是上次正确率: {progress['accuracy_percentage']:.1f}%）")


if __name__ == "__main__":
    # 运行模拟测试
    simulate_exam_scenario()

    # 运行真实数据测试
    test_real_exam_progress()