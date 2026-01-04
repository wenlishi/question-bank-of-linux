#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清除第一套试卷的进度
"""

import sys
import os

# 添加core模块到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.user_progress_manager import UserProgressManager


def clear_exam_001_progress():
    """清除第一套试卷（exam_001）的进度"""
    print("=== 清除第一套试卷进度 ===")

    # 初始化进度管理器
    progress_manager = UserProgressManager()

    # 检查当前进度
    print("\n当前进度:")
    progress_data = progress_manager.get_exam_progress("exam_002")
    print(f"  试卷ID: {progress_data['exam_id']}")
    print(f"  总题数: {progress_data['total_questions']}")
    print(f"  已做题数: {progress_data['attempted_questions']}")
    print(f"  学习进度: {progress_data['progress_percentage']:.1f}%")
    print(f"  正确率: {progress_data['accuracy_percentage']:.1f}%")

    # 直接清除（不需要确认）
    print("\n正在清除第一套试卷进度...")

    # 清除进度
    print("\n正在清除进度...")
    success = progress_manager.clear_exam_progress("exam_002")

    if success:
        print("[成功] 进度清除成功！")

        # 验证清除结果
        print("\n清除后的进度:")
        progress_data = progress_manager.get_exam_progress("exam_002")
        print(f"  试卷ID: {progress_data['exam_id']}")
        print(f"  总题数: {progress_data['total_questions']}")
        print(f"  已做题数: {progress_data['attempted_questions']}")
        print(f"  学习进度: {progress_data['progress_percentage']:.1f}%")
        print(f"  正确率: {progress_data['accuracy_percentage']:.1f}%")

        # 检查文件是否更新
        print("\n[成功] 第一套试卷进度已重置为0%")
    else:
        print("[失败] 进度清除失败")


def check_all_exams_progress():
    """检查所有试卷进度"""
    print("\n=== 所有试卷进度 ===")

    progress_manager = UserProgressManager()
    all_progress = progress_manager.get_all_exams_progress()

    if not all_progress:
        print("没有找到进度数据")
        return

    for exam_id, progress in all_progress.items():
        print(f"\n试卷: {exam_id}")
        print(f"  总题数: {progress['total_questions']}")
        print(f"  已做题数: {progress['attempted_questions']}")
        print(f"  学习进度: {progress['progress_percentage']:.1f}%")
        print(f"  正确率: {progress['accuracy_percentage']:.1f}%")


if __name__ == "__main__":
    # 显示所有试卷进度
    check_all_exams_progress()

    # 清除第一套试卷进度
    clear_exam_001_progress()

    # 再次显示所有试卷进度
    check_all_exams_progress()