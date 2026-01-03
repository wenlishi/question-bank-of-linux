#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
试卷列表窗口 - ExamListWindow
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QHeaderView, QPushButton,
                             QLabel, QFrame, QProgressBar, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QBrush
import os
import sys
from typing import Dict, Any

# 添加core模块到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from core.question_manager import QuestionManager
    from core.user_progress_manager import UserProgressManager
    QUESTION_MANAGER_AVAILABLE = True
    PROGRESS_MANAGER_AVAILABLE = True
except ImportError:
    QUESTION_MANAGER_AVAILABLE = False
    PROGRESS_MANAGER_AVAILABLE = False
    print("警告: 试题管理器或进度管理器模块不可用")


class ExamListWindow(QWidget):
    """试卷列表窗口"""

    # 定义信号：点击学习按钮时触发，传递试卷ID
    study_exam_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("试卷列表")
        self.setGeometry(100, 100, 1000, 600)

        # 初始化试题管理器
        if QUESTION_MANAGER_AVAILABLE:
            self.question_manager = QuestionManager()
        else:
            self.question_manager = None
            QMessageBox.warning(self, "错误", "试题管理器初始化失败")

        # 初始化进度管理器
        if PROGRESS_MANAGER_AVAILABLE:
            self.progress_manager = UserProgressManager()
            # 迁移旧数据（如果存在）
            self.progress_manager.migrate_from_old_stats()
        else:
            self.progress_manager = None
            print("警告: 进度管理器初始化失败")

        # 初始化UI
        self.init_ui()

        # 加载真实数据
        self.load_real_data()

    def init_ui(self):
        """初始化界面"""
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # 标题
        title_label = QLabel("试卷列表")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # 创建表格
        self.create_table(main_layout)

        # 底部按钮区域
        self.create_bottom_buttons(main_layout)

    def create_table(self, parent_layout):
        """创建试卷表格"""
        # 创建表格
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(6)  # 状态、名称、题目总数、学习进度、正确率、操作
        self.table_widget.setHorizontalHeaderLabels([
            "状态", "试卷名称", "题目总数", "学习进度", "正确率", "操作"
        ])

        # 设置表头样式
        header = self.table_widget.horizontalHeader()
        header.setStyleSheet("""
            QHeaderView::section {
                background-color: #f8f9fa;
                color: #007bff;
                font-weight: bold;
                font-size: 16px;
                padding: 8px;
                border: 1px solid #dee2e6;
            }
        """)

        # 设置列宽
        self.table_widget.setColumnWidth(0, 60)   # 状态列
        self.table_widget.setColumnWidth(1, 300)  # 试卷名称列
        self.table_widget.setColumnWidth(2, 100)  # 题目总数列
        self.table_widget.setColumnWidth(3, 150)  # 学习进度列
        self.table_widget.setColumnWidth(4, 100)  # 正确率列
        self.table_widget.setColumnWidth(5, 100)  # 操作列

        # 设置表格属性
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f8f9fa;
                gridline-color: #dee2e6;
                border: 1px solid #dee2e6;
            }
            QTableWidget::item {
                padding: 8px;
            }
        """)

        # 设置表头对齐方式
        header.setDefaultAlignment(Qt.AlignCenter)

        parent_layout.addWidget(self.table_widget)

    def create_bottom_buttons(self, parent_layout):
        """创建底部按钮"""
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # 刷新按钮
        refresh_btn = QPushButton("刷新列表")
        refresh_btn.setFixedSize(100, 35)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
            QPushButton:pressed {
                background-color: #545b62;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_list)
        button_layout.addWidget(refresh_btn)

        parent_layout.addLayout(button_layout)

    def load_real_data(self):
        """加载真实数据"""
        if not self.question_manager:
            QMessageBox.warning(self, "错误", "试题管理器不可用")
            return

        # 获取真实试卷列表
        exams = self.question_manager.list_exams()

        if not exams:
            QMessageBox.information(self, "提示", "未找到试卷数据，请将试卷JSON文件放入data/exams目录")
            return

        self.table_widget.setRowCount(len(exams))

        for row, exam in enumerate(exams):
            exam_id = exam["id"]

            # 获取试卷进度数据
            progress_data = self.get_exam_progress_data(exam_id, exam["total_questions"])
            progress_percentage = progress_data["progress_percentage"]
            accuracy_percentage = progress_data["accuracy_percentage"]
            attempted_questions = progress_data["attempted_questions"]
            correct_questions = progress_data["correct_questions"]

            # 状态列 - 根据进度显示不同图标
            if progress_percentage >= 100:
                status_icon = "✅"  # 完成
                status_color = "#28a745"  # 绿色
            elif progress_percentage > 0:
                status_icon = "📚"  # 学习中
                status_color = "#007bff"  # 蓝色
            else:
                status_icon = "🔓"  # 未开始
                status_color = "#6c757d"  # 灰色

            status_item = QTableWidgetItem(status_icon)
            status_item.setForeground(QBrush(QColor(status_color)))
            status_item.setTextAlignment(Qt.AlignCenter)
            self.table_widget.setItem(row, 0, status_item)

            # 试卷名称列 - 左对齐
            name_item = QTableWidgetItem(exam["name"])
            name_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.table_widget.setItem(row, 1, name_item)

            # 题目总数列 - 居中，显示已做/总数
            total_text = f"{attempted_questions}/{exam['total_questions']}"
            total_item = QTableWidgetItem(total_text)
            total_item.setTextAlignment(Qt.AlignCenter)
            self.table_widget.setItem(row, 2, total_item)

            # 学习进度列 - 进度条（真实进度）
            progress_widget = QWidget()
            progress_layout = QHBoxLayout(progress_widget)
            progress_layout.setContentsMargins(0, 0, 0, 0)

            progress_bar = QProgressBar()
            progress_bar.setValue(int(progress_percentage))
            progress_bar.setTextVisible(True)
            progress_bar.setFormat(f"{progress_percentage:.1f}%")

            # 根据进度设置不同颜色
            if progress_percentage >= 100:
                progress_color = "#28a745"  # 绿色
            elif progress_percentage >= 50:
                progress_color = "#17a2b8"  # 青色
            elif progress_percentage > 0:
                progress_color = "#ffc107"  # 黄色
            else:
                progress_color = "#007bff"  # 蓝色

            progress_bar.setStyleSheet(f"""
                QProgressBar {{
                    border: 1px solid #dee2e6;
                    border-radius: 3px;
                    text-align: center;
                }}
                QProgressBar::chunk {{
                    background-color: {progress_color};
                    border-radius: 3px;
                }}
            """)
            progress_layout.addWidget(progress_bar)

            self.table_widget.setCellWidget(row, 3, progress_widget)

            # 正确率列（真实正确率）
            accuracy_text = f"{accuracy_percentage:.1f}%"
            accuracy_item = QTableWidgetItem(accuracy_text)
            accuracy_item.setTextAlignment(Qt.AlignCenter)

            # 根据正确率设置颜色
            if accuracy_percentage >= 80:
                accuracy_color = "#28a745"  # 绿色
            elif accuracy_percentage >= 60:
                accuracy_color = "#ffc107"  # 黄色
            elif accuracy_percentage > 0:
                accuracy_color = "#fd7e14"  # 橙色
            else:
                accuracy_color = "#6c757d"  # 灰色

            accuracy_item.setForeground(QBrush(QColor(accuracy_color)))
            self.table_widget.setItem(row, 4, accuracy_item)

            # 操作列 - 学习按钮（全部可学习）
            study_btn = QPushButton("学习")
            study_btn.setFixedSize(70, 30)
            study_btn.setStyleSheet("""
                QPushButton {
                    background-color: #007bff;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #0069d9;
                }
                QPushButton:pressed {
                    background-color: #0062cc;
                }
            """)

            # 使用lambda传递试卷ID
            study_btn.clicked.connect(lambda checked, eid=exam["id"]: self.on_study_clicked(eid))

            # 将按钮添加到表格单元格
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_layout.addWidget(study_btn)
            btn_layout.setAlignment(Qt.AlignCenter)

            self.table_widget.setCellWidget(row, 5, btn_widget)

    def get_exam_progress_data(self, exam_id: str, total_questions: int) -> Dict[str, Any]:
        """
        获取试卷进度数据

        Args:
            exam_id: 试卷ID
            total_questions: 总题数

        Returns:
            进度数据字典
        """
        if self.progress_manager:
            progress_data = self.progress_manager.get_exam_progress(exam_id)
            # 确保总题数是最新的
            if progress_data["total_questions"] != total_questions:
                self.progress_manager.update_exam_total_questions(exam_id, total_questions)
                progress_data = self.progress_manager.get_exam_progress(exam_id)
            return progress_data
        else:
            # 如果没有进度管理器，返回默认数据
            return {
                "exam_id": exam_id,
                "total_questions": total_questions,
                "attempted_questions": 0,
                "correct_questions": 0,
                "progress_percentage": 0,
                "accuracy_percentage": 0,
                "last_attempt": None,
                "best_score": 0
            }

    def on_study_clicked(self, exam_id):
        """学习按钮点击事件"""
        print(f"开始学习试卷: {exam_id}")
        self.study_exam_requested.emit(exam_id)

    def refresh_list(self):
        """刷新列表"""
        print("刷新试卷列表")

        # 重新加载进度数据，确保获取最新状态
        if self.progress_manager:
            if self.progress_manager.reload_data():
                print("进度数据已重新加载")
            else:
                print("警告: 重新加载进度数据失败")

        # 重新加载真实数据
        self.load_real_data()

        # 显示刷新完成提示
        print("试卷列表已刷新，进度数据已更新")

        # 可选：显示提示消息
        QMessageBox.information(self, "刷新完成", "试卷列表已刷新，学习进度和正确率已更新到最新状态")

    def resizeEvent(self, event):
        """窗口大小改变事件"""
        super().resizeEvent(event)
        # 调整表格列宽
        if hasattr(self, 'table_widget'):
            width = self.width() - 40  # 减去边距
            self.table_widget.setColumnWidth(1, int(width * 0.4))  # 试卷名称列占40%
            self.table_widget.setColumnWidth(3, int(width * 0.2))  # 学习进度列占20%