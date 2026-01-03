#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新试卷数据脚本
1. 移除category字段
2. 设置选择题分值为1分，填空题分值为2分
"""

import json
import os
import glob

def update_exam_file(file_path):
    """更新单个试卷文件"""
    print(f"处理文件: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    total_score = 0
    questions_updated = 0

    # 更新每个题目
    for question in data['questions']:
        # 移除category字段
        if 'category' in question:
            del question['category']
            questions_updated += 1

        # 更新分值
        if question['type'] == 'single_choice':
            question['score'] = 1
            total_score += 1
        elif question['type'] == 'fill_blank':
            question['score'] = 2
            total_score += 2
        elif question['type'] == 'comprehensive':
            # 综合题保持原分值，但需要重新计算总分
            total_score += question['score']

    # 更新总分
    data['total_score'] = total_score

    # 保存更新后的文件
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"  更新完成: 移除了{questions_updated}个题目的category字段，总分更新为{total_score}")
    return total_score

def main():
    """主函数"""
    exam_dir = os.path.join('data', 'exams')

    if not os.path.exists(exam_dir):
        print(f"错误: 目录不存在: {exam_dir}")
        return

    # 查找所有JSON试卷文件
    exam_files = glob.glob(os.path.join(exam_dir, '*.json'))

    if not exam_files:
        print(f"警告: 在 {exam_dir} 中没有找到试卷文件")
        return

    print(f"找到 {len(exam_files)} 个试卷文件")
    print("=" * 50)

    total_exams = 0
    total_questions_updated = 0

    for exam_file in exam_files:
        try:
            update_exam_file(exam_file)
            total_exams += 1
        except Exception as e:
            print(f"  处理文件时出错: {exam_file}")
            print(f"  错误信息: {e}")

    print("=" * 50)
    print(f"处理完成: 成功更新了 {total_exams} 个试卷文件")

if __name__ == '__main__':
    main()