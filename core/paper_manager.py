#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
试卷管理系统
支持导入和管理多套试卷
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

class PaperManager:
    """试卷管理器"""

    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.papers_file = os.path.join(data_dir, "papers.json")
        self.questions_file = os.path.join(data_dir, "questions.json")

        # 确保数据目录存在
        os.makedirs(data_dir, exist_ok=True)

        # 加载试卷数据
        self.papers = self._load_papers()

        # 加载题目数据
        self.questions = self._load_questions()

    def _load_papers(self):
        """加载试卷数据"""
        if os.path.exists(self.papers_file):
            try:
                with open(self.papers_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"papers": [], "next_paper_id": 1}
        return {"papers": [], "next_paper_id": 1}

    def _load_questions(self):
        """加载题目数据"""
        if os.path.exists(self.questions_file):
            try:
                with open(self.questions_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"questions": [], "next_question_id": 1}
        return {"questions": [], "next_question_id": 1}

    def _save_papers(self):
        """保存试卷数据"""
        with open(self.papers_file, 'w', encoding='utf-8') as f:
            json.dump(self.papers, f, ensure_ascii=False, indent=2)

    def _save_questions(self):
        """保存题目数据"""
        with open(self.questions_file, 'w', encoding='utf-8') as f:
            json.dump(self.questions, f, ensure_ascii=False, indent=2)

    def create_paper(self, title, description="", time_limit=120, total_score=100):
        """
        创建新试卷

        Args:
            title: 试卷标题
            description: 试卷描述
            time_limit: 时间限制（分钟）
            total_score: 总分
        """
        paper_id = self.papers["next_paper_id"]
        self.papers["next_paper_id"] += 1

        paper = {
            "id": paper_id,
            "title": title,
            "description": description,
            "time_limit": time_limit,
            "total_score": total_score,
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat(),
            "question_ids": [],  # 试卷包含的题目ID列表
            "status": "active"  # active, draft, archived
        }

        self.papers["papers"].append(paper)
        self._save_papers()

        return paper_id

    def add_question_to_paper(self, paper_id, question_id):
        """添加题目到试卷"""
        for paper in self.papers["papers"]:
            if paper["id"] == paper_id:
                if question_id not in paper["question_ids"]:
                    paper["question_ids"].append(question_id)
                    paper["updated"] = datetime.now().isoformat()
                    self._save_papers()
                    return True
        return False

    def remove_question_from_paper(self, paper_id, question_id):
        """从试卷中移除题目"""
        for paper in self.papers["papers"]:
            if paper["id"] == paper_id:
                if question_id in paper["question_ids"]:
                    paper["question_ids"].remove(question_id)
                    paper["updated"] = datetime.now().isoformat()
                    self._save_papers()
                    return True
        return False

    def get_paper(self, paper_id):
        """获取试卷信息"""
        for paper in self.papers["papers"]:
            if paper["id"] == paper_id:
                return paper.copy()
        return None

    def get_paper_questions(self, paper_id):
        """获取试卷的所有题目"""
        paper = self.get_paper(paper_id)
        if not paper:
            return []

        questions = []
        for q in self.questions["questions"]:
            if q["id"] in paper["question_ids"]:
                questions.append(q.copy())

        return questions

    def list_papers(self, status=None):
        """列出所有试卷"""
        if status:
            return [p.copy() for p in self.papers["papers"] if p.get("status") == status]
        return [p.copy() for p in self.papers["papers"]]

    def update_paper(self, paper_id, **kwargs):
        """更新试卷信息"""
        for paper in self.papers["papers"]:
            if paper["id"] == paper_id:
                for key, value in kwargs.items():
                    if key in paper:
                        paper[key] = value
                paper["updated"] = datetime.now().isoformat()
                self._save_papers()
                return True
        return False

    def delete_paper(self, paper_id):
        """删除试卷"""
        for i, paper in enumerate(self.papers["papers"]):
            if paper["id"] == paper_id:
                self.papers["papers"].pop(i)
                self._save_papers()
                return True
        return False

    # 题目管理方法
    def add_question(self, question_data):
        """添加题目"""
        question_id = self.questions["next_question_id"]
        self.questions["next_question_id"] += 1

        question_data["id"] = question_id
        question_data["created"] = datetime.now().isoformat()
        question_data.setdefault("score", 5)  # 默认每题5分

        # 移除难度字段（不需要）
        if "difficulty" in question_data:
            del question_data["difficulty"]

        # 验证题目类型
        question_type = question_data.get("type")
        if question_type == QuestionType.COMPREHENSIVE.value:
            # 综合题需要包含子题目
            if "sub_questions" not in question_data:
                question_data["sub_questions"] = []

        self.questions["questions"].append(question_data)
        self._save_questions()

        return question_id

    def batch_add_questions(self, questions_list):
        """批量添加题目"""
        question_ids = []
        for q in questions_list:
            question_id = self.add_question(q)
            question_ids.append(question_id)
        return question_ids

    def get_question(self, question_id):
        """获取题目信息"""
        for q in self.questions["questions"]:
            if q["id"] == question_id:
                return q.copy()
        return None

    def update_question(self, question_id, **kwargs):
        """更新题目信息"""
        for q in self.questions["questions"]:
            if q["id"] == question_id:
                for key, value in kwargs.items():
                    if key in q:
                        q[key] = value
                self._save_questions()
                return True
        return False

    def delete_question(self, question_id):
        """删除题目"""
        for i, q in enumerate(self.questions["questions"]):
            if q["id"] == question_id:
                self.questions["questions"].pop(i)
                self._save_questions()
                return True
        return False

    def search_questions(self, keyword=None, question_type=None):
        """搜索题目"""
        results = []
        for q in self.questions["questions"]:
            match = True

            if keyword:
                keyword_lower = keyword.lower()
                question_text = q.get("question", "").lower()
                explanation = q.get("explanation", "").lower()
                if keyword_lower not in question_text and keyword_lower not in explanation:
                    match = False

            if question_type and q.get("type") != question_type:
                match = False

            if match:
                results.append(q.copy())

        return results

    def get_question_count(self):
        """获取题目总数"""
        return len(self.questions["questions"])

    def get_paper_count(self):
        """获取试卷总数"""
        return len(self.papers["papers"])

    # 导入导出功能
    def import_from_json(self, json_file):
        """从JSON文件导入题目"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            imported_count = 0

            # 导入题目
            if "questions" in data:
                for q in data["questions"]:
                    self.add_question(q)
                    imported_count += 1

            # 导入试卷
            if "papers" in data:
                for paper_data in data["papers"]:
                    paper_id = self.create_paper(
                        title=paper_data.get("title", "未命名试卷"),
                        description=paper_data.get("description", ""),
                        time_limit=paper_data.get("time_limit", 120),
                        total_score=paper_data.get("total_score", 100)
                    )

                    # 添加题目到试卷
                    for question_id in paper_data.get("question_ids", []):
                        self.add_question_to_paper(paper_id, question_id)

            return imported_count

        except Exception as e:
            print(f"导入失败: {e}")
            return 0

    def export_to_json(self, json_file, include_questions=True, include_papers=True):
        """导出到JSON文件"""
        data = {}

        if include_questions:
            data["questions"] = self.questions["questions"]

        if include_papers:
            data["papers"] = self.papers["papers"]

        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return len(data.get("questions", [])) + len(data.get("papers", []))

    # 试卷生成功能
    def generate_random_paper(self, title, question_count=50, question_types=None):
        """
        随机生成试卷

        Args:
            title: 试卷标题
            question_count: 题目数量
            question_types: 题目类型列表，如 ["single_choice", "fill_blank"]
        """
        # 筛选题目
        all_questions = self.questions["questions"]
        if question_types:
            filtered_questions = [q for q in all_questions if q.get("type") in question_types]
        else:
            filtered_questions = all_questions

        # 随机选择题目
        if len(filtered_questions) < question_count:
            selected_questions = filtered_questions
        else:
            selected_questions = random.sample(filtered_questions, question_count)

        # 创建试卷
        paper_id = self.create_paper(title, f"随机生成的试卷，共{len(selected_questions)}题")

        # 添加题目到试卷
        for q in selected_questions:
            self.add_question_to_paper(paper_id, q["id"])

        return paper_id

    # 统计功能
    def get_statistics(self):
        """获取统计信息"""
        total_questions = len(self.questions["questions"])
        total_papers = len(self.papers["papers"])

        # 按类型统计题目
        type_stats = {}
        for q in self.questions["questions"]:
            q_type = q.get("type", "unknown")
            type_stats[q_type] = type_stats.get(q_type, 0) + 1

        return {
            "total_questions": total_questions,
            "total_papers": total_papers,
            "question_types": type_stats
        }