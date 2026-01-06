#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
试卷列表窗口 - ExamListWindow
修改说明：
1. 移除了底层文件锁逻辑，彻底解决 nul 文件报错。
2. 严格保留原有 UI 布局、颜色和字体样式。
3. 优化进度条样式：解决进度较小时显示为方形的问题，确保始终保持圆形边缘。
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QHeaderView, QPushButton,
                             QLabel, QFrame, QProgressBar, QMessageBox, 
                             QAbstractItemView)
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

        self.setWindowTitle("Linux三级题库")
        self.setGeometry(100, 100, 1200, 750)

        # 初始化管理器
        if QUESTION_MANAGER_AVAILABLE:
            self.question_manager = QuestionManager()
        else:
            self.question_manager = None
            QMessageBox.warning(self, "错误", "试题管理器初始化失败")

        if PROGRESS_MANAGER_AVAILABLE:
            self.progress_manager = UserProgressManager()
            self.progress_manager.migrate_from_old_stats()
        else:
            self.progress_manager = None

        # 初始化UI
        self.init_ui()

        # 加载真实数据
        self.load_real_data()

    def init_ui(self):
        """初始化界面"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        header_layout = QHBoxLayout()

        title_label = QLabel("Linux三级题库")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_font.setFamily("Microsoft YaHei")
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #496EA3;")
        header_layout.addWidget(title_label, 0, Qt.AlignBottom)

        subtitle_label = QLabel("点击下方的学习按钮，即可进入相应的分类学习>>")
        subtitle_font = QFont()
        subtitle_font.setPointSize(11)
        subtitle_font.setFamily("Microsoft YaHei")
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setStyleSheet("color: #7f8c8d; margin-left: 12px; margin-bottom: 5px;") 
        header_layout.addWidget(subtitle_label, 0, Qt.AlignBottom)

        header_layout.addStretch() 
        main_layout.addLayout(header_layout)

        self.create_table(main_layout)
        self.create_bottom_buttons(main_layout)

    def create_table(self, parent_layout):
        """创建试卷表格 - 保持原有视觉风格"""
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(6)
        self.table_widget.setHorizontalHeaderLabels([
            "状态", "试卷名称", "题目总数", "学习进度", "正确率", "操作"
        ])

        self.table_widget.setSelectionMode(QAbstractItemView.NoSelection)
        self.table_widget.setFocusPolicy(Qt.NoFocus)
        self.table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)

        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        self.table_widget.setColumnWidth(0, 80)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        self.table_widget.setColumnWidth(2, 130)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        self.table_widget.setColumnWidth(3, 220)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        self.table_widget.setColumnWidth(4, 130)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        self.table_widget.setColumnWidth(5, 220)

        self.table_widget.verticalHeader().setDefaultSectionSize(60)

        header.setStyleSheet("""
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4a6fa5, stop:1 #2c3e50);
                color: white; font-weight: bold; font-size: 18px; font-family: "Microsoft YaHei";
                padding: 12px 8px; border: none; border-right: 1px solid #34495e; border-bottom: 2px solid #2c3e50;
            }
        """)

        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.setStyleSheet("""
            QTableWidget {
                background-color: #f5f7fa; alternate-background-color: #ffffff;
                gridline-color: #e1e8ed; border: 2px solid #dce4ec; border-radius: 8px;
                font-family: "Microsoft YaHei"; font-size: 18px;
            }
        """)

        header.setDefaultAlignment(Qt.AlignCenter)
        parent_layout.addWidget(self.table_widget)

    def create_bottom_buttons(self, parent_layout):
        """创建底部按钮"""
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        refresh_btn = QPushButton("刷新列表")
        refresh_btn.setFixedSize(130, 45)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #17a2b8, stop:1 #138496);
                color: white; border: 1px solid #117a8b; border-radius: 6px;
                font-weight: bold; font-size: 16px; font-family: "Microsoft YaHei";
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1be6ff, stop:1 #17a2b8);
            }
        """)
        refresh_btn.clicked.connect(self.refresh_list)
        button_layout.addWidget(refresh_btn)
        parent_layout.addLayout(button_layout)

    def load_real_data(self):
        """加载数据及进度条视觉优化"""
        if not self.question_manager:
            return
        exams = self.question_manager.list_exams()
        if not exams:
            return

        self.table_widget.setRowCount(len(exams))

        for row, exam in enumerate(exams):
            exam_id = exam["id"]
            progress_data = self.get_exam_progress_data(exam_id, exam["total_questions"])
            p_percent = progress_data["progress_percentage"]
            
            # 状态列
            s_icon, s_color = ("✅", "#28a745") if p_percent >= 100 else ("📚", "#007bff") if p_percent > 0 else ("🔓", "#6c757d")
            status_item = QTableWidgetItem(s_icon)
            status_item.setForeground(QBrush(QColor(s_color)))
            status_item.setTextAlignment(Qt.AlignCenter)
            self.table_widget.setItem(row, 0, status_item)

            # 试卷名称列
            self.table_widget.setItem(row, 1, QTableWidgetItem(exam["name"]))

            # 题目总数
            total_item = QTableWidgetItem(f"{progress_data['attempted_questions']}/{exam['total_questions']}")
            total_item.setTextAlignment(Qt.AlignCenter)
            self.table_widget.setItem(row, 2, total_item)

            # === 进度条优化区域 ===
            progress_widget = QWidget()
            p_layout = QHBoxLayout(progress_widget)
            p_layout.setContentsMargins(15, 0, 15, 0)
            pb = QProgressBar()
            pb.setFixedHeight(24)
            pb.setValue(int(p_percent))
            pb.setFormat(f"{p_percent:.1f}%")
            
            p_color = "#28a745" if p_percent >= 100 else "#17a2b8" if p_percent >= 50 else "#ffc107" if p_percent > 0 else "#007bff"
            
            # 核心修复：通过 border-radius 和取消 margin 确保即使 1% 也是圆的
            pb.setStyleSheet(f"""
                QProgressBar {{
                    border: 1px solid #ced4da;
                    border-radius: 12px;
                    text-align: center;
                    font-size: 14px;
                    font-weight: bold;
                    color: #495057;
                    background-color: #e9ecef;
                }}
                QProgressBar::chunk {{
                    background-color: {p_color};
                    border-radius: 11px;
                    margin: 0px; 
                }}
            """)
            p_layout.addWidget(pb)
            self.table_widget.setCellWidget(row, 3, progress_widget)

            # 正确率
            acc_percent = progress_data["accuracy_percentage"]
            acc_item = QTableWidgetItem(f"{acc_percent:.1f}%")
            acc_item.setTextAlignment(Qt.AlignCenter)
            a_color = "#28a745" if acc_percent >= 80 else "#ffc107" if acc_percent >= 60 else "#fd7e14" if acc_percent > 0 else "#6c757d"
            acc_item.setForeground(QBrush(QColor(a_color)))
            self.table_widget.setItem(row, 4, acc_item)

            # 操作按钮
            btn_widget = QWidget()
            bl = QHBoxLayout(btn_widget)
            bl.setContentsMargins(5, 0, 5, 0)
            
            study_btn = QPushButton("学习")
            study_btn.setFixedSize(80, 36)
            study_btn.setStyleSheet("QPushButton { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #5C7DAF, stop:1 #46689A); color: white; border-radius: 4px; font-weight: bold; }")
            study_btn.clicked.connect(lambda checked, eid=exam_id: self.on_study_clicked(eid))
            bl.addWidget(study_btn)

            clear_btn = QPushButton("重置")
            clear_btn.setFixedSize(80, 36)
            clear_btn.setStyleSheet("QPushButton { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #99a3a4, stop:1 #7f8c8d); color: white; border-radius: 4px; font-weight: bold; }")
            clear_btn.clicked.connect(lambda checked, eid=exam_id: self.on_clear_progress_clicked(eid))
            bl.addWidget(clear_btn)

            self.table_widget.setCellWidget(row, 5, btn_widget)

    def get_exam_progress_data(self, exam_id: str, total_questions: int) -> Dict[str, Any]:
        if self.progress_manager:
            return self.progress_manager.get_exam_progress(exam_id)
        return {"progress_percentage": 0, "accuracy_percentage": 0, "attempted_questions": 0}

    def on_study_clicked(self, exam_id):
        self.study_exam_requested.emit(exam_id)

    def on_clear_progress_clicked(self, exam_id):
        reply = QMessageBox.question(self, "确认清除进度", "确定要清除该试卷的学习进度吗？", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes and self.progress_manager:
            self.progress_manager.clear_exam_progress(exam_id)
            self.refresh_list()

    def refresh_list(self):
        if self.progress_manager:
            self.progress_manager.reload_data()
        self.load_real_data()

    def closeEvent(self, event):
        super().closeEvent(event)
        global _exam_list_window_instance
        if _exam_list_window_instance is self:
            _exam_list_window_instance = None

_exam_list_window_instance = None
def get_exam_list_window(parent=None):
    global _exam_list_window_instance
    if _exam_list_window_instance is None:
        _exam_list_window_instance = ExamListWindow(parent)
    return _exam_list_window_instance

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = get_exam_list_window()
    window.show()
    sys.exit(app.exec_())