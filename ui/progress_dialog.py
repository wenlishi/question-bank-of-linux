#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
答题进度弹窗 - 显示已作答和未作答的题目
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFrame,
                             QLabel, QPushButton, QScrollArea, QWidget,
                             QGridLayout, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon


class ProgressDialog(QDialog):
    """答题进度弹窗"""

    # 定义信号：当用户点击题号按钮时发出
    question_clicked = pyqtSignal(int, int)  # 参数：题目索引, item索引（对于cloze_group）

    def __init__(self, questions, user_answers, parent=None):
        super().__init__(parent)
        self.questions = questions
        self.user_answers = user_answers
        self.setWindowTitle("答题进度")
        self.setFixedSize(500, 600)
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
        """)

        self.init_ui()
        self.update_progress()

    def init_ui(self):
        """初始化界面"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 顶部统计信息区域
        self.create_top_stats(main_layout)

        # 主体滚动区域
        self.create_scroll_area(main_layout)

        # 底部关闭按钮
        self.create_bottom_buttons(main_layout)

    def create_top_stats(self, parent_layout):
        """创建顶部统计信息"""
        stats_frame = QFrame()
        stats_frame.setFixedHeight(80)
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-bottom: 1px solid #dee2e6;
            }
        """)

        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(20, 0, 20, 0)

        # 总题量
        self.total_label = QLabel("总题量: 0")
        self.total_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #495057;
            }
        """)
        stats_layout.addWidget(self.total_label)

        stats_layout.addSpacerItem(QSpacerItem(40, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # 已作答进度
        self.answered_label = QLabel("已作答: 0")
        self.answered_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #28a745;
            }
        """)
        stats_layout.addWidget(self.answered_label)

        parent_layout.addWidget(stats_frame)

    def create_scroll_area(self, parent_layout):
        """创建主体滚动区域"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
            }
            QScrollBar:vertical {
                background-color: #f8f9fa;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #dee2e6;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #adb5bd;
            }
        """)

        # 中心容器
        self.center_widget = QWidget()
        self.center_layout = QVBoxLayout(self.center_widget)
        self.center_layout.setContentsMargins(20, 20, 20, 20)
        self.center_layout.setSpacing(15)

        scroll_area.setWidget(self.center_widget)
        parent_layout.addWidget(scroll_area)

    def create_bottom_buttons(self, parent_layout):
        """创建底部按钮"""
        button_frame = QFrame()
        button_frame.setFixedHeight(60)
        button_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-top: 1px solid #dee2e6;
            }
        """)

        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(20, 0, 20, 0)

        button_layout.addSpacerItem(QSpacerItem(40, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.setFixedSize(100, 35)
        close_btn.setStyleSheet("""
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
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)

        parent_layout.addWidget(button_frame)

    def update_progress(self):
        """更新进度信息"""
        if not self.questions:
            return

        # 计算统计数据 - 考虑cloze_group的每个item
        total_count = 0
        answered_count = 0
        for i, question in enumerate(self.questions):
            question_type = question.get('type', 'single_choice')
            question_id = question.get('id', f'q_{i+1}')

            if question_type == 'cloze_group' or question_type == 'comprehensive':
                # 对于cloze_group和comprehensive，每个item算作一道题
                items = question.get('items', [])
                total_count += len(items)

                # 检查每个item是否有答案
                if question_id in self.user_answers:
                    user_answer_list = self.user_answers[question_id]
                    for item_idx in range(len(items)):
                        if item_idx < len(user_answer_list) and user_answer_list[item_idx]:
                            answered_count += 1
            else:
                # 对于普通题目
                total_count += 1
                if question_id in self.user_answers:
                    answered_count += 1

        # 更新统计标签
        self.total_label.setText(f"总题量: {total_count}")
        self.answered_label.setText(f"已作答: {answered_count}")

        # 首先为所有题目（包括cloze_group的每个item）计算全局显示编号
        display_number = 1
        question_display_numbers = {}  # 存储每个题目的显示编号

        for i, question in enumerate(self.questions):
            question_type = question.get('type', 'single_choice')

            if question_type == 'cloze_group' or question_type == 'comprehensive':
                # 对于cloze_group和comprehensive，每个item都有一个显示编号
                items = question.get('items', [])
                for item_idx, item in enumerate(items):
                    key = (i, item_idx)  # 使用(题目索引, item索引)作为键
                    question_display_numbers[key] = display_number
                    display_number += 1
            else:
                # 对于普通题目
                key = (i, None)  # 使用(题目索引, None)作为键
                question_display_numbers[key] = display_number
                display_number += 1

        # 按题型分组题目 - 将cloze_group合并到fill_blank中，并展开每个item
        questions_by_type = {}
        for i, question in enumerate(self.questions):
            question_type = question.get('type', 'single_choice')

            # 处理cloze_group和comprehensive
            if question_type == 'cloze_group' or question_type == 'comprehensive':
                # cloze_group合并到fill_blank，comprehensive单独显示
                if question_type == 'cloze_group':
                    display_type = 'fill_blank'
                else:  # comprehensive
                    display_type = 'comprehensive'

                if display_type not in questions_by_type:
                    questions_by_type[display_type] = []
                # 展开cloze_group/comprehensive的每个item为独立的题目
                items = question.get('items', [])
                for item_idx, item in enumerate(items):
                    # 创建item的副本，添加item信息
                    item_question = question.copy()
                    item_question['item_id'] = item.get('id', f'item_{item_idx+1}')
                    item_question['item_index'] = item_idx
                    item_question['original_question_index'] = i
                    # 添加显示编号
                    key = (i, item_idx)
                    item_question['display_number'] = question_display_numbers.get(key, 0)
                    questions_by_type[display_type].append((i, item_question))
            else:
                display_type = question_type
                if display_type not in questions_by_type:
                    questions_by_type[display_type] = []
                # 添加显示编号
                key = (i, None)
                question['display_number'] = question_display_numbers.get(key, 0)
                questions_by_type[display_type].append((i, question))

        # 清除现有内容
        while self.center_layout.count():
            child = self.center_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # 创建题型分组
        type_names = {
            'single_choice': '选择题',
            'fill_blank': '填空题',
            'comprehensive': '综合题'
        }

        for question_type, type_questions in questions_by_type.items():
            if not type_questions:
                continue

            # 创建题型分组容器
            type_group = self.create_type_group(type_names.get(question_type, question_type), type_questions)
            self.center_layout.addWidget(type_group)

        self.center_layout.addStretch()

    def create_type_group(self, type_name, type_questions):
        """创建题型分组"""
        group_widget = QWidget()
        group_layout = QVBoxLayout(group_widget)
        group_layout.setContentsMargins(0, 0, 0, 0)
        group_layout.setSpacing(0)

        # 标题栏
        title_frame = QFrame()
        title_frame.setFixedHeight(40)
        title_frame.setStyleSheet("""
            QFrame {
                background-color: #e9ecef;
                border: 1px solid #dee2e6;
                border-radius: 5px 5px 0 0;
            }
        """)

        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(15, 0, 15, 0)

        # 题型图标和名称
        title_label = QLabel(type_name)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #495057;
            }
        """)
        title_layout.addWidget(title_label)

        title_layout.addStretch()

        # 题目数量
        count_label = QLabel(f"{len(type_questions)}题")
        count_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #6c757d;
            }
        """)
        title_layout.addWidget(count_label)

        group_layout.addWidget(title_frame)

        # 题目序号区域
        numbers_frame = QFrame()
        numbers_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #dee2e6;
                border-top: none;
                border-radius: 0 0 5px 5px;
            }
        """)

        # 使用网格布局排列按钮
        grid_layout = QGridLayout(numbers_frame)
        grid_layout.setContentsMargins(15, 15, 15, 15)
        grid_layout.setHorizontalSpacing(8)
        grid_layout.setVerticalSpacing(8)

        # 每行显示10个按钮
        buttons_per_row = 10
        for idx, (question_index, question) in enumerate(type_questions):
            row = idx // buttons_per_row
            col = idx % buttons_per_row

            # 确定按钮文本：使用计算好的显示编号
            display_num = question.get('display_number', idx + 1)
            # 显示为两位数字
            btn_text = f"{display_num:02d}"

            btn = QPushButton(btn_text)
            btn.setFixedSize(36, 36)

            # 为按钮添加点击事件
            question_type = question.get('type', 'single_choice')
            if question_type == 'cloze_group' or question_type == 'comprehensive':
                # 对于cloze_group或comprehensive的item
                item_index = question.get('item_index', 0)
                btn.clicked.connect(lambda checked, q_idx=question_index, i_idx=item_index:
                                  self.on_question_clicked(q_idx, i_idx))
            else:
                # 对于普通题目，item_index为-1表示整个题目
                btn.clicked.connect(lambda checked, q_idx=question_index:
                                  self.on_question_clicked(q_idx, -1))

            # 检查是否已作答
            question_id = question.get('id', f'q_{question_index+1}')
            if question_id in self.user_answers:
                # 检查cloze_group或comprehensive的item是否有答案
                if question_type == 'cloze_group' or question_type == 'comprehensive':
                    item_index = question.get('item_index', 0)
                    user_answer_list = self.user_answers.get(question_id, [])
                    # 检查该item是否有答案（非空字符串）
                    if item_index < len(user_answer_list) and user_answer_list[item_index]:
                        is_answered = True
                    else:
                        is_answered = False
                else:
                    is_answered = True
            else:
                is_answered = False

            if is_answered:
                # 已作答 - 绿色
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #28a745;
                        color: white;
                        border: 2px solid #28a745;
                        border-radius: 18px;
                        font-weight: bold;
                        font-size: 14px;
                    }
                    QPushButton:hover {
                        background-color: #218838;
                        border-color: #1e7e34;
                    }
                """)
            else:
                # 未作答 - 灰色
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #f8f9fa;
                        color: #6c757d;
                        border: 2px solid #dee2e6;
                        border-radius: 18px;
                        font-weight: bold;
                        font-size: 14px;
                    }
                    QPushButton:hover {
                        background-color: #e9ecef;
                        border-color: #adb5bd;
                    }
                """)

            grid_layout.addWidget(btn, row, col, Qt.AlignCenter)

        group_layout.addWidget(numbers_frame)

        return group_widget

    def on_question_clicked(self, question_index, item_index):
        """处理题号按钮点击事件"""
        # 发出信号，通知父窗口跳转到对应题目
        self.question_clicked.emit(question_index, item_index)
        # 关闭弹窗
        self.accept()