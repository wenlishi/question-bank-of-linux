#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新的主窗口 - 管理试卷列表窗口和答题窗口的切换
修改说明：
1. 简化了页面切换逻辑，利用 QStackedWidget 自动管理子窗口显隐。
2. 强化了 ExamWindow 的销毁逻辑，防止内存泄漏。
"""

from PyQt5.QtWidgets import QMainWindow, QStackedWidget
from PyQt5.QtCore import Qt
from .exam_list_window import get_exam_list_window
from .exam_window import ExamWindow


class NewMainWindow(QMainWindow):
    """新的主窗口，管理窗口切换"""

    def __init__(self, question_bank=None):
        super().__init__()
        self.question_bank = question_bank
        self.setWindowTitle("极智题典")
        self.setGeometry(100, 100, 1200, 800)

        # 1. 创建堆叠窗口作为中心控件
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # 2. 获取并添加试卷列表窗口（单例）
        # 注意：这里不再需要手动控制 show/hide，添加进 StackedWidget 即可
        self.exam_list_window = get_exam_list_window()
        self.exam_list_window.study_exam_requested.connect(self.show_exam_window)
        self.stacked_widget.addWidget(self.exam_list_window)

        # 3. 初始化答题窗口变量
        self.exam_window = None

        # 4. 默认显示试卷列表
        self.stacked_widget.setCurrentWidget(self.exam_list_window)

    def show_exam_window(self, exam_id):
        """显示答题窗口"""
        # A. 如果之前已经有打开的答题窗口，先进行清理
        if self.exam_window:
            self.stacked_widget.removeWidget(self.exam_window)
            self.exam_window.deleteLater()
            self.exam_window = None

        # B. 模拟根据 ID 获取试卷名称
        exam_names = {
            "exam_001": "Linux应用与开发技术",
            "exam_002": "Linux应用与开发技术",
            "exam_003": "Linux应用与开发技术"
        }
        exam_name = exam_names.get(exam_id, "Linux应用与开发技术")

        # C. 创建新的答题窗口实例
        self.exam_window = ExamWindow(exam_id, exam_name)
        self.exam_window.back_to_list_requested.connect(self.show_exam_list)
        
        # D. 添加到堆叠窗口并切换
        # QStackedWidget 会自动将之前的 exam_list_window 设置为不可见
        self.stacked_widget.addWidget(self.exam_window)
        self.stacked_widget.setCurrentWidget(self.exam_window)

    def show_exam_list(self):
        """返回并显示试卷列表窗口"""
        # A. 切换到列表页
        self.stacked_widget.setCurrentWidget(self.exam_list_window)

        # B. 释放答题窗口占用的内存
        if self.exam_window:
            # 将其从堆栈中移除并标记为延迟删除
            self.stacked_widget.removeWidget(self.exam_window)
            self.exam_window.deleteLater()
            self.exam_window = None

    def closeEvent(self, event):
        """窗口关闭时的处理"""
        # 在这里可以执行数据保存等收尾工作
        event.accept()