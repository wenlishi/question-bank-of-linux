#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户进度管理器 - 管理用户做题进度和正确率
"""
import sys
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

class UserProgressManager:
    """用户进度管理器"""

    def __init__(self, data_dir: str = "data"):
        """
        初始化用户进度管理器
        """
        # === 【核心修改开始】 ===
        # 判断是打包后的环境(frozen)还是开发环境
        if getattr(sys, 'frozen', False):
            #如果是打包后的 EXE，基准路径是 EXE 文件所在的目录
            base_path = os.path.dirname(sys.executable)
        else:
            # 如果是 Python 源码运行，基准路径是项目根目录
            # core/ -> 上一级 -> 项目根目录
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
        self.data_dir = os.path.join(base_path, data_dir)
        # === 【核心修改结束】 ===
        
        self.progress_file = os.path.join(self.data_dir, "user_progress.json")

        # 确保数据目录存在
        # 这里非常重要：因为打包时我们排除了data目录里的动态文件
        # 所以第一次运行时，如果EXE旁边没有data文件夹，这里会自动创建它
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

        # 加载或初始化进度数据
        self.progress_data = self._load_progress_data()

    def _load_progress_data(self) -> Dict[str, Any]:
        """
        加载用户进度数据

        Returns:
            用户进度数据字典
        """
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载用户进度数据失败: {e}")

        # 初始化数据结构
        return {
            "version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "exams": {},  # 按试卷ID存储进度
            "daily_stats": {}  # 按日期存储统计（向后兼容）
        }

    def _save_progress_data(self) -> bool:
        """
        保存用户进度数据

        Returns:
            是否保存成功
        """
        try:
            self.progress_data["last_updated"] = datetime.now().isoformat()
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(self.progress_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存用户进度数据失败: {e}")
            return False

    def record_answer(self, exam_id: str, question_id: str, is_correct: bool,
                      user_answer: List[str] = None, session_id: str = None) -> bool:
        """
        记录用户答题结果

        Args:
            exam_id: 试卷ID
            question_id: 题目ID
            is_correct: 是否正确
            user_answer: 用户答案（可选）
            session_id: 会话ID（用于关联同一次交卷的题目）

        Returns:
            是否记录成功
        """
        try:
            # 确保试卷记录存在
            if exam_id not in self.progress_data["exams"]:
                self.progress_data["exams"][exam_id] = {
                    "total_attempts": 0,
                    "correct_attempts": 0,
                    "questions": {},
                    "last_attempt": None,
                    "best_score": 0,
                    "total_questions": 0  # 将在首次加载试卷时更新
                }

            exam_data = self.progress_data["exams"][exam_id]

            # 确保题目记录存在
            if question_id not in exam_data["questions"]:
                exam_data["questions"][question_id] = {
                    "attempts": 0,
                    "correct": 0,
                    "last_attempt": None,
                    "last_correct": False,  # 最后一次是否正确
                    "history": []
                }

            question_data = exam_data["questions"][question_id]

            # 记录本次答题
            attempt_record = {
                "timestamp": datetime.now().isoformat(),
                "correct": is_correct,
                "user_answer": user_answer if user_answer else [],
                "session_id": session_id  # 记录会话ID
            }

            question_data["history"].append(attempt_record)
            question_data["attempts"] += 1
            if is_correct:
                question_data["correct"] += 1
            question_data["last_attempt"] = datetime.now().isoformat()
            question_data["last_correct"] = is_correct  # 记录最后一次是否正确

            # 更新试卷统计
            exam_data["total_attempts"] += 1
            if is_correct:
                exam_data["correct_attempts"] += 1
            exam_data["last_attempt"] = datetime.now().isoformat()

            # 保存数据
            return self._save_progress_data()

        except Exception as e:
            print(f"记录答题结果失败: {e}")
            return False

    def get_exam_progress(self, exam_id: str) -> Dict[str, Any]:
        """
        获取指定试卷的学习进度

        Args:
            exam_id: 试卷ID

        Returns:
            试卷进度信息
        """
        if exam_id not in self.progress_data["exams"]:
            return {
                "exam_id": exam_id,
                "total_questions": 0,
                "attempted_questions": 0,
                "correct_questions": 0,
                "progress_percentage": 0,
                "accuracy_percentage": 0,
                "last_attempt": None,
                "best_score": 0,
                "last_accuracy": 0  # 上次正确率
            }

        exam_data = self.progress_data["exams"][exam_id]
        questions = exam_data["questions"]

        # 计算进度：已做过的题目数 / 总题目数（全局累计）
        attempted_questions = len(questions)

        # 获取上次交卷的正确率
        last_accuracy = self.get_last_session_accuracy(exam_id)

        # 注意：如果上次交卷正确率是0%，就显示0%，不要使用历史计算
        # 只有完全没有交卷记录时（last_accuracy为0且没有sessions记录），才使用历史计算
        if last_accuracy == 0.0:
            # 检查是否有交卷记录
            exam_data = self.progress_data["exams"].get(exam_id, {})
            sessions = exam_data.get("sessions", [])

            # 如果有交卷记录，即使正确率是0%，也显示0%
            # 只有完全没有交卷记录时，才使用历史计算
            if not sessions:
                last_accuracy = self._calculate_last_attempt_accuracy(exam_id, questions)

        return {
            "exam_id": exam_id,
            "total_questions": exam_data.get("total_questions", 0),
            "attempted_questions": attempted_questions,
            "correct_questions": sum(1 for q in questions.values() if q.get("last_correct", False)),
            "progress_percentage": (attempted_questions / exam_data.get("total_questions", 1) * 100) if exam_data.get("total_questions", 0) > 0 else 0,
            "accuracy_percentage": last_accuracy,  # 使用上次正确率
            "last_attempt": exam_data.get("last_attempt"),
            "best_score": exam_data.get("best_score", 0),
            "last_accuracy": last_accuracy
        }

    def _calculate_last_attempt_accuracy(self, exam_id: str, questions: Dict[str, Any]) -> float:
        """
        计算上次做题的正确率

        Args:
            exam_id: 试卷ID
            questions: 题目数据字典

        Returns:
            上次正确率（百分比）
        """
        if not questions:
            return 0.0

        # 找出所有题目最近一次答题的时间
        recent_attempts = []
        for q_id, q_data in questions.items():
            if q_data.get("history"):
                # 获取最近一次答题记录
                last_record = q_data["history"][-1]
                recent_attempts.append({
                    "question_id": q_id,
                    "timestamp": last_record.get("timestamp"),
                    "correct": last_record.get("correct", False)
                })

        if not recent_attempts:
            return 0.0

        # 按时间排序，找到最近的时间
        recent_attempts.sort(key=lambda x: x["timestamp"] or "", reverse=True)
        most_recent_time = recent_attempts[0]["timestamp"]

        if not most_recent_time:
            return 0.0

        # 找出在最近时间窗口内（比如30分钟内）做的题目
        # 首先解析时间字符串
        from datetime import datetime
        try:
            most_recent_dt = datetime.fromisoformat(most_recent_time.replace('Z', '+00:00'))
        except:
            # 如果时间格式解析失败，使用简单方法
            most_recent_dt = None

        last_session_questions = []
        for attempt in recent_attempts:
            timestamp = attempt["timestamp"]
            if not timestamp:
                continue

            if most_recent_dt:
                # 使用时间窗口（30分钟）
                try:
                    attempt_dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    time_diff = abs((attempt_dt - most_recent_dt).total_seconds())
                    if time_diff <= 1800:  # 30分钟内的题目视为同一次会话
                        last_session_questions.append(attempt)
                except:
                    # 时间解析失败，直接比较字符串
                    if timestamp == most_recent_time:
                        last_session_questions.append(attempt)
            else:
                # 没有时间解析，直接比较字符串
                if timestamp == most_recent_time:
                    last_session_questions.append(attempt)

        # 如果没有找到时间窗口内的题目，至少使用最近的一道题
        if not last_session_questions and recent_attempts:
            last_session_questions = [recent_attempts[0]]

        # 计算正确率：上次做对的题数 / 上次做的题数
        correct_count = sum(1 for q in last_session_questions if q["correct"])
        total_count = len(last_session_questions)

        return (correct_count / total_count * 100) if total_count > 0 else 0.0

    def record_exam_session(self, exam_id: str, accuracy: float, session_id: str = None) -> bool:
        """
        记录交卷会话的正确率

        Args:
            exam_id: 试卷ID
            accuracy: 这次交卷的正确率
            session_id: 会话ID（如果为None则自动生成）

        Returns:
            是否记录成功
        """
        try:
            if exam_id not in self.progress_data["exams"]:
                self.progress_data["exams"][exam_id] = {
                    "total_attempts": 0,
                    "correct_attempts": 0,
                    "questions": {},
                    "last_attempt": None,
                    "best_score": 0,
                    "total_questions": 0,
                    "last_session_accuracy": 0,  # 上次交卷正确率
                    "sessions": []  # 交卷会话历史
                }

            exam_data = self.progress_data["exams"][exam_id]

            # 生成会话ID（如果未提供）
            if not session_id:
                session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

            # 记录会话
            session_record = {
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "accuracy": accuracy
            }

            if "sessions" not in exam_data:
                exam_data["sessions"] = []

            exam_data["sessions"].append(session_record)
            exam_data["last_session_accuracy"] = accuracy
            exam_data["last_attempt"] = datetime.now().isoformat()

            # 保存数据
            return self._save_progress_data()

        except Exception as e:
            print(f"记录交卷会话失败: {e}")
            return False

    def get_last_session_accuracy(self, exam_id: str) -> float:
        """
        获取上次交卷的正确率

        Args:
            exam_id: 试卷ID

        Returns:
            上次交卷正确率（百分比），如果没有记录则返回0
        """
        if exam_id not in self.progress_data["exams"]:
            return 0.0

        exam_data = self.progress_data["exams"][exam_id]
        return exam_data.get("last_session_accuracy", 0.0)

    def update_exam_total_questions(self, exam_id: str, total_questions: int) -> bool:
        """
        更新试卷总题数

        Args:
            exam_id: 试卷ID
            total_questions: 总题数

        Returns:
            是否更新成功
        """
        if exam_id not in self.progress_data["exams"]:
            self.progress_data["exams"][exam_id] = {
                "total_attempts": 0,
                "correct_attempts": 0,
                "questions": {},
                "last_attempt": None,
                "best_score": 0,
                "total_questions": total_questions
            }
        else:
            self.progress_data["exams"][exam_id]["total_questions"] = total_questions

        return self._save_progress_data()

    def get_all_exams_progress(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有试卷的进度

        Returns:
            所有试卷进度字典
        """
        result = {}
        for exam_id in self.progress_data["exams"]:
            result[exam_id] = self.get_exam_progress(exam_id)
        return result

    def migrate_from_old_stats(self, old_stats_file: str = "user_stats.json") -> bool:
        """
        从旧的用户统计数据迁移

        Args:
            old_stats_file: 旧统计数据文件名

        Returns:
            是否迁移成功
        """
        old_file_path = os.path.join(self.data_dir, old_stats_file)
        if not os.path.exists(old_file_path):
            return False

        try:
            with open(old_file_path, 'r', encoding='utf-8') as f:
                old_data = json.load(f)

            # 这里需要根据旧数据结构进行迁移
            # 由于旧数据没有试卷信息，我们假设所有题目都属于一个默认试卷
            default_exam_id = "default_exam"

            for date_str, date_data in old_data.items():
                if "questions" in date_data:
                    for question in date_data["questions"]:
                        question_id = str(question.get("id", "unknown"))
                        is_correct = question.get("correct", False)

                        # 记录到默认试卷
                        self.record_answer(default_exam_id, question_id, is_correct)

            print(f"从旧数据迁移了 {len(old_data)} 天的记录")
            return self._save_progress_data()

        except Exception as e:
            print(f"迁移旧数据失败: {e}")
            return False

    def clear_exam_progress(self, exam_id: str) -> bool:
        """
        清除指定试卷的进度

        Args:
            exam_id: 试卷ID

        Returns:
            是否清除成功
        """
        if exam_id in self.progress_data["exams"]:
            del self.progress_data["exams"][exam_id]
            return self._save_progress_data()
        return True

    def get_question_history(self, exam_id: str, question_id: str) -> List[Dict[str, Any]]:
        """
        获取指定题目的答题历史

        Args:
            exam_id: 试卷ID
            question_id: 题目ID

        Returns:
            答题历史列表
        """
        if (exam_id not in self.progress_data["exams"] or
            question_id not in self.progress_data["exams"][exam_id]["questions"]):
            return []

        return self.progress_data["exams"][exam_id]["questions"][question_id].get("history", [])

    def get_daily_stats(self, date_str: str = None) -> Dict[str, Any]:
        """
        获取每日统计（向后兼容）

        Args:
            date_str: 日期字符串（YYYY-MM-DD），如果为None则返回今天

        Returns:
            每日统计数据
        """
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")

        if date_str not in self.progress_data["daily_stats"]:
            return {
                "date": date_str,
                "total": 0,
                "correct": 0,
                "questions": []
            }

        return self.progress_data["daily_stats"][date_str]

    def reload_data(self) -> bool:
        """
        重新从文件加载进度数据

        Returns:
            是否加载成功
        """
        try:
            self.progress_data = self._load_progress_data()
            return True
        except Exception as e:
            print(f"重新加载进度数据失败: {e}")
            return False