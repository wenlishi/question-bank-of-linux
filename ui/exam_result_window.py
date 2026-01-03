#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交卷结果窗口 - ExamResultWindow
三段式垂直布局：顶部信息头 + 中间滚动区域 + 底部操作面板
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QFrame, QScrollArea, QPushButton, QGridLayout,
                             QGroupBox, QSizePolicy, QSpacerItem)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette, QPainter, QBrush
import math


class CircularButton(QPushButton):
    """圆形题目序号按钮"""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedSize(40, 40)
        self.setStyleSheet("""
            QPushButton {
                border-radius: 20px;
                border: 2px solid #dee2e6;
                background-color: white;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #f8f9fa;
            }
        """)

    def set_status(self, status):
        """设置按钮状态：correct, wrong, unanswered"""
        if status == "correct":
            self.setStyleSheet("""
                QPushButton {
                    border-radius: 20px;
                    border: 2px solid #28a745;
                    background-color: #d4edda;
                    color: #155724;
                    font-weight: bold;
                    font-size: 14px;
                }
            """)
        elif status == "wrong":
            self.setStyleSheet("""
                QPushButton {
                    border-radius: 20px;
                    border: 2px solid #dc3545;
                    background-color: #f8d7da;
                    color: #721c24;
                    font-weight: bold;
                    font-size: 14px;
                }
            """)
        elif status == "unanswered":
            self.setStyleSheet("""
                QPushButton {
                    border-radius: 20px;
                    border: 2px solid #6c757d;
                    background-color: #e9ecef;
                    color: #495057;
                    font-weight: bold;
                    font-size: 14px;
                }
            """)


class StatBar(QFrame):
    """统计条 - 横向排列的圆角统计条"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(80)
        self.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 10px;
                border: 1px solid #dee2e6;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(30)

        # 总题数统计
        self.total_stat = self.create_stat_item("总题数", "0", "#007bff")
        layout.addWidget(self.total_stat)

        # 正确题数统计
        self.correct_stat = self.create_stat_item("正确", "0", "#28a745")
        layout.addWidget(self.correct_stat)

        # 错误题数统计
        self.wrong_stat = self.create_stat_item("错误", "0", "#dc3545")
        layout.addWidget(self.wrong_stat)

        # 未答题数统计
        self.unanswered_stat = self.create_stat_item("未答", "0", "#6c757d")
        layout.addWidget(self.unanswered_stat)

        # 正确率统计
        self.accuracy_stat = self.create_stat_item("正确率", "0%", "#17a2b8")
        layout.addWidget(self.accuracy_stat)

        layout.addStretch()

    def create_stat_item(self, title, value, color):
        """创建统计项"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 8px;
                border: 2px solid {color};
                padding: 8px;
            }}
        """)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(5)

        # 标题
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 12px;
                font-weight: bold;
            }}
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # 数值
        value_label = QLabel(value)
        value_label.setStyleSheet("""
            QLabel {
                color: #212529;
                font-size: 18px;
                font-weight: bold;
            }
        """)
        value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(value_label)

        return frame

    def update_stats(self, total, correct, wrong, unanswered, accuracy):
        """更新统计信息"""
        self.total_stat.layout().itemAt(1).widget().setText(str(total))
        self.correct_stat.layout().itemAt(1).widget().setText(str(correct))
        self.wrong_stat.layout().itemAt(1).widget().setText(str(wrong))
        self.unanswered_stat.layout().itemAt(1).widget().setText(str(unanswered))
        self.accuracy_stat.layout().itemAt(1).widget().setText(f"{accuracy:.1f}%")


class ExamResultWindow(QWidget):
    """交卷结果窗口"""

    # 定义信号：确定和取消
    confirmed = pyqtSignal()
    cancelled = pyqtSignal()

    def __init__(self, exam_name="试卷结果", parent=None):
        super().__init__(parent)
        self.exam_name = exam_name
        self.question_groups = {}  # 存储题目分组

        self.setWindowTitle("试卷完成")
        self.setGeometry(200, 100, 900, 700)

        # 初始化UI
        self.init_ui()

    def init_ui(self):
        """初始化界面 - 三段式垂直布局"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. 顶部信息头
        self.create_top_header(main_layout)

        # 2. 中间滚动区域
        self.create_middle_scroll_area(main_layout)

        # 3. 底部操作面板
        self.create_bottom_panel(main_layout)

    def create_top_header(self, parent_layout):
        """创建顶部信息头"""
        header_frame = QFrame()
        header_frame.setFixedHeight(180)
        header_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-bottom: 2px solid #dee2e6;
            }
        """)

        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 15, 20, 15)
        header_layout.setSpacing(15)

        # 标题栏
        title_label = QLabel(self.exam_name)
        title_label.setStyleSheet("""
            QLabel {
                color: #007bff;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label)

        # 副标题
        subtitle_label = QLabel("答题结果分析")
        subtitle_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-size: 14px;
            }
        """)
        subtitle_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(subtitle_label)

        # 统计条
        self.stat_bar = StatBar()
        header_layout.addWidget(self.stat_bar)

        parent_layout.addWidget(header_frame)

    def create_middle_scroll_area(self, parent_layout):
        """创建中间滚动区域"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
            }
            QScrollArea > QWidget > QWidget {
                background-color: white;
            }
        """)

        # 滚动区域的内容容器
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: white;")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(20, 20, 20, 20)
        scroll_layout.setSpacing(20)

        # 这里的内容会在set_result_data中动态添加
        self.scroll_content = scroll_content
        self.scroll_layout = scroll_layout

        scroll_area.setWidget(scroll_content)
        parent_layout.addWidget(scroll_area)

    def create_bottom_panel(self, parent_layout):
        """创建底部操作面板"""
        bottom_frame = QFrame()
        bottom_frame.setFixedHeight(120)
        bottom_frame.setStyleSheet("""
            QFrame {
                background-color: #fff3cd;
                border-top: 2px solid #ffeaa7;
            }
        """)

        bottom_layout = QVBoxLayout(bottom_frame)
        bottom_layout.setContentsMargins(20, 15, 20, 15)
        bottom_layout.setSpacing(10)

        # 警告文本
        warning_label = QLabel("请仔细检查答题结果，确认无误后点击确定提交")
        warning_label.setStyleSheet("""
            QLabel {
                color: #856404;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        warning_label.setAlignment(Qt.AlignCenter)
        bottom_layout.addWidget(warning_label)

        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # 取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.setFixedSize(100, 40)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
            QPushButton:pressed {
                background-color: #545b62;
            }
        """)
        cancel_btn.clicked.connect(self.on_cancel_clicked)
        button_layout.addWidget(cancel_btn)

        button_layout.addSpacing(20)

        # 确定按钮
        confirm_btn = QPushButton("确定")
        confirm_btn.setFixedSize(100, 40)
        confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        confirm_btn.clicked.connect(self.on_confirm_clicked)
        button_layout.addWidget(confirm_btn)

        button_layout.addStretch()
        bottom_layout.addLayout(button_layout)

        parent_layout.addWidget(bottom_frame)

    def set_result_data(self, exam_data, user_answers, question_results):
        """
        设置结果数据

        Args:
            exam_data: 试卷数据
            user_answers: 用户答案字典 {question_id: answer_list}
            question_results: 题目结果字典 {question_id: {"correct": bool, "score": int}}
        """
        # 清空现有内容
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # 按题型分组题目
        self.group_questions_by_type(exam_data, user_answers, question_results)

        # 添加各个题型分组
        for question_type, questions in self.question_groups.items():
            group_widget = self.create_question_group(question_type, questions)
            self.scroll_layout.addWidget(group_widget)

        # 添加弹性空间
        self.scroll_layout.addStretch()

        # 更新统计信息
        self.update_statistics(question_results, user_answers, exam_data)

    def group_questions_by_type(self, exam_data, user_answers, question_results):
        """按题型分组题目"""
        self.question_groups = {
            "single_choice": [],
            "fill_blank": [],
            "comprehensive": []
        }

        questions = exam_data.get('questions', [])
        for i, question in enumerate(questions):
            question_id = question.get('id', f'q_{i+1}')
            question_type = question.get('type', 'single_choice')

            # 获取题目结果
            result = question_results.get(question_id, {"correct": False, "score": 0})

            # 判断是否作答
            has_answer = question_id in user_answers and user_answers[question_id]

            self.question_groups[question_type].append({
                "index": i + 1,
                "id": question_id,
                "question": question.get('question', ''),
                "type": question_type,
                "correct": result.get("correct", False),
                "score": result.get("score", 0),
                "has_answer": has_answer,
                "user_answer": user_answers.get(question_id, []),
                "correct_answer": question.get('answer', [])
            })

    def create_question_group(self, question_type, questions):
        """创建题型分组"""
        if not questions:
            return None

        # 题型名称映射
        type_names = {
            "single_choice": "选择题",
            "fill_blank": "填空题",
            "comprehensive": "综合题"
        }

        group_frame = QFrame()
        group_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
            }
        """)

        group_layout = QVBoxLayout(group_frame)
        group_layout.setContentsMargins(0, 0, 0, 15)
        group_layout.setSpacing(0)

        # 分组标题行（灰色背景）
        title_frame = QFrame()
        title_frame.setFixedHeight(50)
        title_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-bottom: 1px solid #dee2e6;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
        """)

        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(15, 0, 15, 0)

        title_label = QLabel(type_names.get(question_type, question_type))
        title_label.setStyleSheet("""
            QLabel {
                color: #495057;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        title_layout.addWidget(title_label)

        # 统计信息
        total_count = len(questions)
        correct_count = sum(1 for q in questions if q["correct"])
        stat_text = f"共{total_count}题，正确{correct_count}题"

        stat_label = QLabel(stat_text)
        stat_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-size: 14px;
            }
        """)
        title_layout.addWidget(stat_label)

        title_layout.addStretch()
        group_layout.addWidget(title_frame)

        # 题目按钮区域
        buttons_frame = QFrame()
        buttons_layout = QGridLayout(buttons_frame)
        buttons_layout.setContentsMargins(15, 15, 15, 15)
        buttons_layout.setHorizontalSpacing(15)
        buttons_layout.setVerticalSpacing(15)

        # 计算每行最多显示多少个按钮
        max_buttons_per_row = 10

        for idx, question in enumerate(questions):
            row = idx // max_buttons_per_row
            col = idx % max_buttons_per_row

            # 确定按钮状态
            if not question["has_answer"]:
                status = "unanswered"
            elif question["correct"]:
                status = "correct"
            else:
                status = "wrong"

            # 创建圆形按钮
            btn = CircularButton(str(question["index"]))
            btn.set_status(status)

            # 添加提示信息
            tooltip = f"第{question['index']}题: "
            if not question["has_answer"]:
                tooltip += "未作答"
            elif question["correct"]:
                tooltip += "正确"
            else:
                tooltip += "错误"

            btn.setToolTip(tooltip)
            buttons_layout.addWidget(btn, row, col)

        group_layout.addWidget(buttons_frame)

        return group_frame

    def update_statistics(self, question_results, user_answers, exam_data):
        """更新统计信息"""
        total_questions = len(exam_data.get('questions', []))

        # 计算各种统计
        correct_count = 0
        wrong_count = 0
        unanswered_count = 0

        for question_id, result in question_results.items():
            if question_id in user_answers and user_answers[question_id]:
                if result.get("correct", False):
                    correct_count += 1
                else:
                    wrong_count += 1
            else:
                unanswered_count += 1

        # 计算正确率
        answered_count = correct_count + wrong_count
        accuracy = (correct_count / answered_count * 100) if answered_count > 0 else 0

        # 更新统计条
        self.stat_bar.update_stats(
            total=total_questions,
            correct=correct_count,
            wrong=wrong_count,
            unanswered=unanswered_count,
            accuracy=accuracy
        )

    def on_confirm_clicked(self):
        """确定按钮点击事件"""
        print("确定提交结果")
        self.confirmed.emit()
        self.close()

    def on_cancel_clicked(self):
        """取消按钮点击事件"""
        print("取消提交")
        self.cancelled.emit()
        self.close()

    def closeEvent(self, event):
        """窗口关闭事件"""
        # 确保窗口关闭时发出信号（如果用户直接点击窗口关闭按钮）
        if not self.signalsBlocked():
            self.cancelled.emit()
        super().closeEvent(event)


if __name__ == "__main__":
    # 测试代码
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # 创建测试数据
    exam_data = {
        "exam_name": "Linux操作系统测试",
        "questions": [
            {"id": "q1", "type": "single_choice", "question": "题目1", "answer": ["A"]},
            {"id": "q2", "type": "single_choice", "question": "题目2", "answer": ["B"]},
            {"id": "q3", "type": "fill_blank", "question": "题目3", "answer": ["答案"]},
            {"id": "q4", "type": "fill_blank", "question": "题目4", "answer": ["答案"]},
            {"id": "q5", "type": "comprehensive", "question": "题目5", "answer": ["答案1", "答案2"]},
        ]
    }

    user_answers = {
        "q1": ["A"],  # 正确
        "q2": ["C"],  # 错误
        "q3": ["答案"],  # 正确
        # q4 未作答
        "q5": ["答案1", "错误答案"]  # 部分错误
    }

    question_results = {
        "q1": {"correct": True, "score": 5},
        "q2": {"correct": False, "score": 0},
        "q3": {"correct": True, "score": 10},
        "q4": {"correct": False, "score": 0},
        "q5": {"correct": False, "score": 5}
    }

    window = ExamResultWindow("Linux操作系统测试")
    window.set_result_data(exam_data, user_answers, question_results)
    window.show()

    sys.exit(app.exec_())