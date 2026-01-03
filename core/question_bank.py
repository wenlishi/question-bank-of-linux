#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
题目库管理系统
"""

import json
import os
import random
from datetime import datetime
from enum import Enum

class QuestionType(Enum):
    """题目类型枚举"""
    SINGLE_CHOICE = "single_choice"  # 单选题
    FILL_BLANK = "fill_blank"  # 填空题
    COMPREHENSIVE = "comprehensive"  # 综合题（大题包含多个填空题）

class QuestionBank:
    """题目库管理器"""

    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.questions_file = os.path.join(data_dir, "questions.json")
        self.stats_file = os.path.join(data_dir, "user_stats.json")

        # 确保数据目录存在
        os.makedirs(data_dir, exist_ok=True)

        # 加载题目数据
        self.questions = self._load_questions()

        # 加载用户统计
        self.user_stats = self._load_user_stats()

        # 题目分类
        self.categories = self._extract_categories()

    def _load_questions(self):
        """加载题目数据"""
        if os.path.exists(self.questions_file):
            try:
                with open(self.questions_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                # 如果文件损坏，创建示例题目
                return self._create_sample_questions()
        else:
            # 创建示例题目
            return self._create_sample_questions()

    def _load_user_stats(self):
        """加载用户统计"""
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_user_stats(self):
        """保存用户统计"""
        with open(self.stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.user_stats, f, ensure_ascii=False, indent=2)

    def _create_sample_questions(self):
        """创建示例题目"""
        sample_questions = {
            "questions": [
                {
                    "id": 1,
                    "type": QuestionType.SINGLE_CHOICE.value,
                    "category": "数学",
                    "question": "1 + 1 等于多少？",
                    "options": ["1", "2", "3", "4"],
                    "answer": ["2"],
                    "explanation": "基本的加法运算。"
                },
                {
                    "id": 2,
                    "type": QuestionType.SINGLE_CHOICE.value,
                    "category": "数学",
                    "question": "圆的周长公式是什么？",
                    "options": ["πr", "2πr", "πr²", "4πr²"],
                    "answer": ["2πr"],
                    "explanation": "圆的周长公式是 2πr，其中 r 是半径。"
                },
                {
                    "id": 3,
                    "type": QuestionType.MULTIPLE_CHOICE.value,
                    "category": "科学",
                    "question": "以下哪些是编程语言？",
                    "options": ["Python", "Java", "HTML", "CSS"],
                    "answer": ["Python", "Java"],
                    "explanation": "Python 和 Java 是编程语言，HTML 和 CSS 是标记语言和样式表语言。"
                },
                {
                    "id": 4,
                    "type": QuestionType.TRUE_FALSE.value,
                    "category": "常识",
                    "question": "太阳从西边升起。",
                    "options": ["正确", "错误"],
                    "answer": ["错误"],
                    "explanation": "太阳从东边升起，西边落下。"
                },
                {
                    "id": 5,
                    "type": QuestionType.FILL_BLANK.value,
                    "category": "常识",
                    "question": "中国的首都是______。",
                    "options": [],
                    "answer": ["北京"],
                    "explanation": "北京是中国的首都。"
                }
            ]
        }

        # 保存示例题目
        with open(self.questions_file, 'w', encoding='utf-8') as f:
            json.dump(sample_questions, f, ensure_ascii=False, indent=2)

        return sample_questions

    def _extract_categories(self):
        """提取题目分类"""
        categories = set()
        for q in self.questions.get("questions", []):
            categories.add(q.get("category", "未分类"))
        return sorted(list(categories))

    def get_question_count(self):
        """获取题目总数"""
        return len(self.questions.get("questions", []))

    def get_questions_by_category(self, category):
        """按分类获取题目"""
        return [q for q in self.questions.get("questions", [])
                if q.get("category") == category]

    def get_random_questions(self, count=10, category=None):
        """
        随机获取题目

        Args:
            count: 题目数量
            category: 分类筛选
        """
        all_questions = self.questions.get("questions", [])

        # 筛选题目
        filtered_questions = all_questions
        if category:
            filtered_questions = [q for q in filtered_questions
                                 if q.get("category") == category]

        # 如果题目数量不足，返回所有题目
        if len(filtered_questions) <= count:
            return filtered_questions.copy()

        # 随机选择题目
        return random.sample(filtered_questions, count)

    def get_question_by_id(self, question_id):
        """根据ID获取题目"""
        for q in self.questions.get("questions", []):
            if q.get("id") == question_id:
                return q.copy()
        return None

    def check_answer(self, question_id, user_answer):
        """
        检查答案

        Args:
            question_id: 题目ID
            user_answer: 用户答案（列表）
        """
        question = self.get_question_by_id(question_id)
        if not question:
            return False, "题目不存在"

        correct_answer = question.get("answer", [])
        question_type = question.get("type")

        # 根据题目类型检查答案
        if question_type == QuestionType.SINGLE_CHOICE.value:
            # 单选题：答案必须完全匹配
            is_correct = (len(user_answer) == 1 and
                         user_answer[0] in correct_answer)
        elif question_type == QuestionType.FILL_BLANK.value:
            # 填空题：答案必须完全匹配（不区分大小写）
            is_correct = (len(user_answer) == 1 and
                         user_answer[0].strip().lower() == correct_answer[0].lower())
        elif question_type == QuestionType.COMPREHENSIVE.value:
            # 综合题：检查所有子题目的答案
            sub_questions = question.get("sub_questions", [])
            if len(user_answer) != len(sub_questions):
                is_correct = False
            else:
                # 检查每个子题目的答案
                all_correct = True
                for i, sub_q in enumerate(sub_questions):
                    sub_correct_answer = sub_q.get("answer", [])
                    if not sub_correct_answer:
                        continue
                    user_sub_answer = user_answer[i] if i < len(user_answer) else ""
                    if user_sub_answer.strip().lower() != sub_correct_answer[0].lower():
                        all_correct = False
                        break
                is_correct = all_correct
        else:
            is_correct = False

        # 更新用户统计
        self._update_user_stats(question_id, is_correct)

        return is_correct, question.get("explanation", "")

    def _update_user_stats(self, question_id, is_correct):
        """更新用户统计"""
        today = datetime.now().strftime("%Y-%m-%d")

        # 初始化今日统计
        if today not in self.user_stats:
            self.user_stats[today] = {
                "total": 0,
                "correct": 0,
                "questions": []
            }

        # 更新统计
        self.user_stats[today]["total"] += 1
        if is_correct:
            self.user_stats[today]["correct"] += 1

        # 记录题目
        self.user_stats[today]["questions"].append({
            "id": question_id,
            "correct": is_correct,
            "time": datetime.now().isoformat()
        })

        # 保存统计
        self._save_user_stats()

    def get_user_stats(self, date=None):
        """获取用户统计"""
        if date:
            return self.user_stats.get(date, {})
        return self.user_stats

    def get_overall_stats(self):
        """获取总体统计"""
        total_questions = 0
        total_correct = 0
        category_stats = {}

        for date, stats in self.user_stats.items():
            total_questions += stats.get("total", 0)
            total_correct += stats.get("correct", 0)

        accuracy = (total_correct / total_questions * 100) if total_questions > 0 else 0

        return {
            "total_questions": total_questions,
            "total_correct": total_correct,
            "accuracy": round(accuracy, 2),
            "days_studied": len(self.user_stats)
        }

    def add_question(self, question_data):
        """添加题目"""
        questions = self.questions.get("questions", [])

        # 生成新ID
        new_id = max([q.get("id", 0) for q in questions], default=0) + 1
        question_data["id"] = new_id

        questions.append(question_data)
        self.questions["questions"] = questions

        # 保存到文件
        with open(self.questions_file, 'w', encoding='utf-8') as f:
            json.dump(self.questions, f, ensure_ascii=False, indent=2)

        # 更新分类
        self.categories = self._extract_categories()

        return new_id

    def import_questions(self, questions_list):
        """批量导入题目"""
        for q in questions_list:
            self.add_question(q)

    def export_questions(self, filepath):
        """导出题目"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.questions, f, ensure_ascii=False, indent=2)

    def get_categories(self):
        """获取所有分类"""
        return self.categories

