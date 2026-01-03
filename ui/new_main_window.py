#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新的主窗口 - 管理试卷列表窗口和答题窗口的切换
"""

from PyQt5.QtWidgets import QMainWindow, QStackedWidget
from PyQt5.QtCore import Qt
from .exam_list_window import ExamListWindow
from .exam_window import ExamWindow


class NewMainWindow(QMainWindow):
    """新的主窗口，管理窗口切换"""

    def __init__(self, question_bank=None):
        super().__init__()
        self.question_bank = question_bank
        self.setWindowTitle("题库刷题软件")
        self.setGeometry(100, 100, 1200, 800)

        # 创建堆叠窗口
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # 创建试卷列表窗口
        self.exam_list_window = ExamListWindow()
        self.exam_list_window.study_exam_requested.connect(self.show_exam_window)
        self.stacked_widget.addWidget(self.exam_list_window)

        # 创建答题窗口（初始不显示）
        self.exam_window = None

        # 显示试卷列表窗口
        self.stacked_widget.setCurrentWidget(self.exam_list_window)

    def show_exam_window(self, exam_id):
        """显示答题窗口"""
        # 根据exam_id获取试卷名称（这里使用示例数据）
        exam_names = {
            "exam_001": "Linux应用与开发技术",
            "exam_002": "Linux应用与开发技术",
            "exam_003": "Linux应用与开发技术",
            "exam_004": "Linux应用与开发技术",
            "exam_005": "Linux应用与开发技术",
            "exam_006": "Linux应用与开发技术"
        }
        exam_name = exam_names.get(exam_id, "Linux应用与开发技术")

        # 创建答题窗口
        self.exam_window = ExamWindow(exam_id, exam_name)
        self.exam_window.back_to_list_requested.connect(self.show_exam_list)
        self.stacked_widget.addWidget(self.exam_window)
        self.stacked_widget.setCurrentWidget(self.exam_window)

        # 隐藏当前窗口（试卷列表窗口）
        self.exam_list_window.hide()

    def show_exam_list(self):
        """显示试卷列表窗口"""
        if self.exam_window:
            # 移除答题窗口
            self.stacked_widget.removeWidget(self.exam_window)
            self.exam_window.deleteLater()
            self.exam_window = None

        # 显示试卷列表窗口
        self.exam_list_window.show()
        self.stacked_widget.setCurrentWidget(self.exam_list_window)

    def closeEvent(self, event):
        """关闭事件"""
        # 这里可以添加保存数据等逻辑
        event.accept()