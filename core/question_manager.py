#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
试题管理器 - 读取和管理真实的试题数据
"""

import json
import os
from typing import Dict, List, Any, Optional
from .data_encryptor import encryptor


class QuestionManager:
    """试题管理器"""

    def __init__(self, data_dir: str = "data/exams"):
        """
        初始化试题管理器

        Args:
            data_dir: 试题数据目录路径
        """
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), data_dir)

        # 确保数据目录存在
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            print(f"创建数据目录: {self.data_dir}")

    def list_exams(self) -> List[Dict[str, Any]]:
        """
        列出所有试卷（支持加密文件）

        Returns:
            试卷列表，每个试卷包含基本信息
        """
        exams = []

        if not os.path.exists(self.data_dir):
            return exams

        for filename in os.listdir(self.data_dir):
            # 支持.json和.json.enc文件
            if filename.endswith('.json') or filename.endswith('.json.enc'):
                exam_path = os.path.join(self.data_dir, filename)
                try:
                    # 检查是否是加密文件
                    if filename.endswith('.enc') or encryptor.is_encrypted_file(exam_path):
                        # 解密文件获取基本信息
                        with open(exam_path, 'r', encoding='utf-8') as f:
                            encrypted_data = f.read().strip()
                        exam_data = encryptor.decrypt_data(encrypted_data)
                    else:
                        # 普通JSON文件
                        with open(exam_path, 'r', encoding='utf-8') as f:
                            exam_data = json.load(f)

                    # 提取试卷基本信息
                    exam_id = filename.replace('.json', '').replace('.enc', '')
                    exam_info = {
                        'id': exam_data.get('exam_id', exam_id),
                        'name': exam_data.get('exam_name', '未命名试卷'),
                        'description': exam_data.get('description', ''),
                        'time_limit': exam_data.get('time_limit', 120),
                        'total_questions': len(exam_data.get('questions', [])),
                        'total_score': exam_data.get('total_score', 0),
                        'file_path': exam_path
                    }
                    exams.append(exam_info)
                except Exception as e:
                    print(f"读取试卷文件 {filename} 失败: {e}")

        return exams

    def load_exam(self, exam_id: str) -> Optional[Dict[str, Any]]:
        """
        加载指定试卷（支持加密文件）

        Args:
            exam_id: 试卷ID

        Returns:
            试卷数据字典，包含所有题目
        """
        # 尝试多种可能的文件名（包括加密文件）
        possible_filenames = [
            f"{exam_id}.json",
            f"{exam_id}.json.enc",  # 加密文件
            f"exam_{exam_id}.json" if not exam_id.startswith('exam_') else f"{exam_id}.json",
            f"exam_{exam_id}.json.enc" if not exam_id.startswith('exam_') else f"{exam_id}.json.enc",
        ]

        for filename in possible_filenames:
            exam_path = os.path.join(self.data_dir, filename)
            if os.path.exists(exam_path):
                try:
                    # 检查是否是加密文件
                    if filename.endswith('.enc') or encryptor.is_encrypted_file(exam_path):
                        # 解密文件
                        with open(exam_path, 'r', encoding='utf-8') as f:
                            encrypted_data = f.read().strip()
                        exam_data = encryptor.decrypt_data(encrypted_data)
                    else:
                        # 普通JSON文件
                        with open(exam_path, 'r', encoding='utf-8') as f:
                            exam_data = json.load(f)

                    # 确保试卷ID正确
                    exam_data['exam_id'] = exam_id

                    # 验证题目数据格式
                    self._validate_exam_data(exam_data)

                    return exam_data
                except Exception as e:
                    print(f"加载试卷 {exam_id} 失败: {e}")
                    import traceback
                    traceback.print_exc()
                    return None

        print(f"未找到试卷文件: {exam_id}")
        return None

    def _validate_exam_data(self, exam_data: Dict[str, Any]) -> None:
        """
        验证试卷数据格式

        Args:
            exam_data: 试卷数据

        Raises:
            ValueError: 数据格式错误
        """
        required_fields = ['exam_id', 'exam_name', 'questions']
        for field in required_fields:
            if field not in exam_data:
                raise ValueError(f"试卷数据缺少必要字段: {field}")

        # 验证题目数据
        questions = exam_data.get('questions', [])
        if not isinstance(questions, list):
            raise ValueError("questions字段必须是列表")

        for i, question in enumerate(questions):
            if not isinstance(question, dict):
                raise ValueError(f"第{i+1}题必须是字典格式")

            # 检查必要字段
            if 'id' not in question:
                raise ValueError(f"第{i+1}题缺少id字段")
            if 'type' not in question:
                raise ValueError(f"第{i+1}题缺少type字段")
            if 'question' not in question:
                raise ValueError(f"第{i+1}题缺少question字段")

            # 综合题和完形填空组不需要顶层的answer字段
            question_type = question.get('type')
            if question_type not in ['comprehensive', 'cloze_group'] and 'answer' not in question:
                raise ValueError(f"第{i+1}题缺少answer字段")

            # 验证题型
            question_type = question.get('type')
            if question_type not in ['single_choice', 'fill_blank', 'comprehensive', 'cloze_group']:
                raise ValueError(f"第{i+1}题题型无效: {question_type}")

            # 根据题型验证字段
            if question_type == 'single_choice':
                # 单选题需要answer字段
                if 'answer' not in question:
                    raise ValueError(f"第{i+1}题(单选题)缺少answer字段")
                answer = question.get('answer')
                if not isinstance(answer, list):
                    raise ValueError(f"第{i+1}题(单选题)answer字段必须是列表")
                if 'options' not in question:
                    raise ValueError(f"第{i+1}题(单选题)缺少options字段")
                if not isinstance(question['options'], list):
                    raise ValueError(f"第{i+1}题(单选题)options字段必须是列表")
                if len(question['options']) < 2:
                    raise ValueError(f"第{i+1}题(单选题)至少需要2个选项")

            elif question_type == 'fill_blank':
                # 填空题需要answer字段
                if 'answer' not in question:
                    raise ValueError(f"第{i+1}题(填空题)缺少answer字段")
                answer = question.get('answer')
                if not isinstance(answer, list):
                    raise ValueError(f"第{i+1}题(填空题)answer字段必须是列表")

            elif question_type == 'comprehensive':
                # 综合题使用items字段（类似cloze_group）
                if 'items' not in question:
                    raise ValueError(f"第{i+1}题(综合题)缺少items字段")
                if not isinstance(question['items'], list):
                    raise ValueError(f"第{i+1}题(综合题)items字段必须是列表")
                if len(question['items']) == 0:
                    raise ValueError(f"第{i+1}题(综合题)至少需要1个item")

                # 验证items
                for j, item in enumerate(question['items']):
                    if not isinstance(item, dict):
                        raise ValueError(f"第{i+1}题第{j+1}个item必须是字典格式")
                    if 'id' not in item:
                        raise ValueError(f"第{i+1}题第{j+1}个item缺少id字段")
                    if 'answer' not in item:
                        raise ValueError(f"第{i+1}题第{j+1}个item缺少answer字段")
                    item_answer = item.get('answer')
                    if not isinstance(item_answer, str):
                        raise ValueError(f"第{i+1}题第{j+1}个item的answer字段必须是字符串")
                    if 'score' not in item:
                        raise ValueError(f"第{i+1}题第{j+1}个item缺少score字段")
                    if not isinstance(item.get('score'), (int, float)):
                        raise ValueError(f"第{i+1}题第{j+1}个item的score字段必须是数字")

            elif question_type == 'cloze_group':
                # 完形填空组不需要顶层的answer字段，但需要items
                if 'items' not in question:
                    raise ValueError(f"第{i+1}题(完形填空组)缺少items字段")
                if not isinstance(question['items'], list):
                    raise ValueError(f"第{i+1}题(完形填空组)items字段必须是列表")
                if len(question['items']) == 0:
                    raise ValueError(f"第{i+1}题(完形填空组)至少需要1个空位")

                # 验证每个空位
                for j, item in enumerate(question['items']):
                    if not isinstance(item, dict):
                        raise ValueError(f"第{i+1}题第{j+1}个空位必须是字典格式")
                    if 'id' not in item:
                        raise ValueError(f"第{i+1}题第{j+1}个空位缺少id字段")
                    if 'index' not in item:
                        raise ValueError(f"第{i+1}题第{j+1}个空位缺少index字段")
                    if 'answer' not in item:
                        raise ValueError(f"第{i+1}题第{j+1}个空位缺少answer字段")
                    if 'score' not in item:
                        raise ValueError(f"第{i+1}题第{j+1}个空位缺少score字段")
                    item_answer = item.get('answer')
                    if not isinstance(item_answer, str):
                        raise ValueError(f"第{i+1}题第{j+1}个空位answer字段必须是字符串")

    def check_answer(self, question: Dict[str, Any], user_answer: List[str]) -> tuple[bool, str, List[bool], List[int]]:
        """
        检查用户答案是否正确

        Args:
            question: 题目数据
            user_answer: 用户答案列表

        Returns:
            (整体是否正确, 解析说明, 每个空的正确性列表, 每个空的得分列表)
        """
        question_type = question.get('type', 'single_choice')
        correct_answer = []
        item_scores = []
        item_correctness = []

        # 根据题型获取正确答案
        if question_type == "comprehensive":
            # 综合题：从items中提取答案和分值（类似cloze_group）
            items = question.get('items', [])
            for item in items:
                item_answer = item.get('answer', '')
                item_score = item.get('score', 1)
                if isinstance(item_answer, list):
                    correct_answer.extend(item_answer)
                    item_scores.extend([item_score] * len(item_answer))
                else:
                    correct_answer.append(str(item_answer))
                    item_scores.append(item_score)
        elif question_type == "cloze_group":
            # 完形填空组：从items中提取答案和分值
            items = question.get('items', [])
            for item in items:
                item_answer = item.get('answer', '')
                item_score = item.get('score', 1)
                if isinstance(item_answer, list):
                    correct_answer.extend(item_answer)
                    item_scores.extend([item_score] * len(item_answer))
                else:
                    correct_answer.append(str(item_answer))
                    item_scores.append(item_score)
        else:
            # 单选题和填空题：直接从answer字段获取
            correct_answer = question.get('answer', [])

        # 清理答案（去除首尾空格，转为小写）
        # 注意：这里不能过滤空字符串，因为需要保持索引对应关系
        cleaned_user_answer = [str(ans).strip().lower() for ans in user_answer]
        cleaned_correct_answer = [str(ans).strip().lower() for ans in correct_answer]

        # 对于cloze_group和comprehensive类型，计算每个空的正确性和得分
        if question_type == "cloze_group" or question_type == "comprehensive":
            item_correctness = []
            item_earned_scores = []
            for i in range(len(cleaned_correct_answer)):
                if i < len(cleaned_user_answer) and cleaned_user_answer[i]:  # 用户填写了该空
                    is_item_correct = cleaned_user_answer[i] == cleaned_correct_answer[i]
                    item_correctness.append(is_item_correct)
                    # 如果正确，获得该空的全部分值；否则得0分
                    item_score = item_scores[i] if i < len(item_scores) else 1
                    item_earned_scores.append(item_score if is_item_correct else 0)
                else:
                    # 用户没填写该空，不算对也不算错
                    item_correctness.append(False)  # 暂时标记为False，但实际应该不参与判题
                    item_earned_scores.append(0)

            # 对于cloze_group类型，is_correct应该基于实际得分
            # 如果有任何一个item得分>0，就认为题目有部分正确
            total_possible_score = sum(item_scores) if item_scores else len(cleaned_correct_answer)
            earned_score = sum(item_earned_scores)
            is_correct = earned_score > 0  # 只要得了分就算部分正确
        else:
            # 对于其他题型，使用整体答案匹配
            is_correct = cleaned_user_answer == cleaned_correct_answer
            # 对于其他题型，返回空列表
            item_correctness = []
            item_earned_scores = []

        # 获取解析
        analysis = question.get('analysis', '暂无解析')

        return is_correct, analysis, item_correctness, item_earned_scores

    def create_exam_template(self, exam_id: str, exam_name: str, description: str = "") -> Dict[str, Any]:
        """
        创建试卷模板

        Args:
            exam_id: 试卷ID
            exam_name: 试卷名称
            description: 试卷描述

        Returns:
            试卷模板字典
        """
        return {
            "exam_id": exam_id,
            "exam_name": exam_name,
            "description": description,
            "time_limit": 120,  # 默认120分钟
            "total_score": 100,  # 默认100分
            "questions": []
        }

    def save_exam(self, exam_data: Dict[str, Any]) -> bool:
        """
        保存试卷到文件

        Args:
            exam_data: 试卷数据

        Returns:
            是否保存成功
        """
        try:
            exam_id = exam_data.get('exam_id')
            if not exam_id:
                return False

            filename = f"{exam_id}.json"
            filepath = os.path.join(self.data_dir, filename)

            # 验证数据格式
            self._validate_exam_data(exam_data)

            # 保存到文件
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(exam_data, f, ensure_ascii=False, indent=2)

            print(f"试卷已保存: {filepath}")
            return True

        except Exception as e:
            print(f"保存试卷失败: {e}")
            return False