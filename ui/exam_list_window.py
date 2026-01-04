"""
试卷列表窗口 - ExamListWindow
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

        # === 标题区域布局 (左对齐) ===
        header_layout = QHBoxLayout()
        # [已删除左侧弹簧，保持左对齐]

        # 1. 主标题
        title_label = QLabel("Linux三级题库")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_font.setFamily("Microsoft YaHei")
        title_label.setFont(title_font)
        
        # 使用指定的颜色 #496EA3
        title_label.setStyleSheet("color: #496EA3;")
        
        # 将标题加入布局，底部对齐
        header_layout.addWidget(title_label, 0, Qt.AlignBottom)

        # 2. 右侧小字体提示
        subtitle_label = QLabel("点击下方的学习按钮，即可进入相应的分类学习>>")
        subtitle_font = QFont()
        subtitle_font.setPointSize(11)
        subtitle_font.setFamily("Microsoft YaHei")
        subtitle_label.setFont(subtitle_font)
        # 设置颜色为灰色，左边距10px
        subtitle_label.setStyleSheet("color: #7f8c8d; margin-left: 12px; margin-bottom: 5px;") 
        # 将副标题加入布局，底部对齐
        header_layout.addWidget(subtitle_label, 0, Qt.AlignBottom)

        header_layout.addStretch() # [保留] 右侧弹簧，将内容挤向左边
        
        main_layout.addLayout(header_layout)

        # 创建表格
        self.create_table(main_layout)

        # 底部按钮区域
        self.create_bottom_buttons(main_layout)

    def create_table(self, parent_layout):
        """创建试卷表格 - 样式优化版（大字体，无选中效果）"""
        # 创建表格
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(6)  # 状态、名称、题目总数、学习进度、正确率、操作
        self.table_widget.setHorizontalHeaderLabels([
            "状态", "试卷名称", "题目总数", "学习进度", "正确率", "操作"
        ])

        # 设置不可选中（彻底去掉点击变蓝的效果）
        self.table_widget.setSelectionMode(QAbstractItemView.NoSelection)
        # 设置无焦点（去掉点击时的虚线框）
        self.table_widget.setFocusPolicy(Qt.NoFocus)
        # 禁止编辑
        self.table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # === 列宽设置 ===
        header = self.table_widget.horizontalHeader()
        
        # 0. 状态列：固定宽度
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        self.table_widget.setColumnWidth(0, 80)
        
        # 1. 试卷名称列：自动伸缩 (Stretch)，占满剩余所有空间
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        
        # 2. 题目总数：固定宽度
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        self.table_widget.setColumnWidth(2, 130)
        
        # 3. 学习进度：固定宽度
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        self.table_widget.setColumnWidth(3, 220)
        
        # 4. 正确率：固定宽度
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        self.table_widget.setColumnWidth(4, 130)
        
        # 5. 操作列：固定宽度
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        self.table_widget.setColumnWidth(5, 220)

        # === 行高设置 ===
        self.table_widget.verticalHeader().setDefaultSectionSize(60)

        # 设置表头样式
        header.setStyleSheet("""
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a6fa5, stop:1 #2c3e50);
                color: white;
                font-weight: bold;
                font-size: 18px;
                font-family: "Microsoft YaHei";
                padding: 12px 8px;
                border: none;
                border-right: 1px solid #34495e;
                border-bottom: 2px solid #2c3e50;
            }
            QHeaderView::section:first {
                border-left: none;
            }
            QHeaderView::section:last {
                border-right: none;
            }
        """)

        # 设置表格属性
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.setStyleSheet("""
            QTableWidget {
                background-color: #f5f7fa;
                alternate-background-color: #ffffff;
                gridline-color: #e1e8ed;
                border: 2px solid #dce4ec;
                border-radius: 8px;
                font-family: "Microsoft YaHei";
                font-size: 18px;
            }
            QTableWidget::item {
                padding: 5px 8px;
                border-bottom: 1px solid #e1e8ed;
            }
            /* 鼠标悬停时的效果保留 */
            QTableWidget::item:hover {
                background-color: #ecf0f1;
            }
            QTableWidget QScrollBar:vertical {
                border: none;
                background: #ecf0f1;
                width: 14px;
                margin: 0px;
            }
            QTableWidget QScrollBar::handle:vertical {
                background: #bdc3c7;
                border-radius: 7px;
                min-height: 20px;
            }
            QTableWidget QScrollBar::handle:vertical:hover {
                background: #95a5a6;
            }
            QTableWidget QScrollBar::add-line:vertical,
            QTableWidget QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
        """)

        # 设置表头对齐方式
        header.setDefaultAlignment(Qt.AlignCenter)

        parent_layout.addWidget(self.table_widget)

    def create_bottom_buttons(self, parent_layout):
        """创建底部按钮"""
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # === 修改处：刷新按钮 - 改为和谐的青色(Teal) ===
        refresh_btn = QPushButton("刷新列表")
        refresh_btn.setFixedSize(130, 45)
        refresh_btn.setStyleSheet("""
            QPushButton {
                /* 青色渐变，清新且与蓝色主题和谐 */
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #17a2b8, stop:1 #138496);
                color: white;
                border: 1px solid #117a8b;
                border-radius: 6px;
                font-weight: bold;
                font-size: 16px;
                font-family: "Microsoft YaHei";
            }
            QPushButton:hover {
                /* 悬停变亮 */
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1be6ff, stop:1 #17a2b8);
            }
            QPushButton:pressed {
                /* 点击变深 */
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #138496, stop:1 #117a8b);
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
            progress_layout.setContentsMargins(15, 0, 15, 0)

            progress_bar = QProgressBar()
            progress_bar.setFixedHeight(24)
            progress_bar.setValue(int(progress_percentage))
            progress_bar.setTextVisible(True)
            progress_bar.setFormat(f"{progress_percentage:.1f}%")

            # 根据进度设置不同颜色
            if progress_percentage >= 100:
                progress_color = "#28a745"
            elif progress_percentage >= 50:
                progress_color = "#17a2b8"
            elif progress_percentage > 0:
                progress_color = "#ffc107"
            else:
                progress_color = "#007bff"

            # 修复进度条圆角问题
            progress_bar.setStyleSheet(f"""
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
                    background-color: {progress_color};
                    border-radius: 10px;
                    margin: 1px;
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
                accuracy_color = "#28a745"
            elif accuracy_percentage >= 60:
                accuracy_color = "#ffc107"
            elif accuracy_percentage > 0:
                accuracy_color = "#fd7e14"
            else:
                accuracy_color = "#6c757d"

            accuracy_item.setForeground(QBrush(QColor(accuracy_color)))
            self.table_widget.setItem(row, 4, accuracy_item)

            # 操作列 - 学习按钮和清除进度按钮
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(5, 0, 5, 0)
            btn_layout.setSpacing(8)

            # === 学习按钮 - 颜色 #46689A ===
            study_btn = QPushButton("学习")
            study_btn.setFixedSize(80, 36)
            study_btn.setCursor(Qt.PointingHandCursor)
            study_btn.setStyleSheet("""
                QPushButton {
                    /* 使用 #46689A 作为基础色，渐变微调 */
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #5C7DAF, stop:1 #46689A);
                    color: white;
                    border: 1px solid #355688;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 15px;
                    font-family: "Microsoft YaHei";
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #6B8CC0, stop:1 #5C7DAF);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #46689A, stop:1 #355688);
                }
            """)
            study_btn.clicked.connect(lambda checked, eid=exam["id"]: self.on_study_clicked(eid))
            btn_layout.addWidget(study_btn)

            # === 重置按钮 - 中性灰色 (Silver/Gray) ===
            clear_btn = QPushButton("重置")
            clear_btn.setFixedSize(80, 36)
            clear_btn.setCursor(Qt.PointingHandCursor)
            clear_btn.setStyleSheet("""
                QPushButton {
                    /* 中性灰渐变，优雅且不突兀 */
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #99a3a4, stop:1 #7f8c8d);
                    color: white;
                    border: 1px solid #707b7c;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 15px;
                    font-family: "Microsoft YaHei";
                }
                QPushButton:hover {
                    /* 悬停变浅 */
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #b2babb, stop:1 #95a5a6);
                }
                QPushButton:pressed {
                    /* 点击变深 */
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #7f8c8d, stop:1 #707b7c);
                }
            """)
            clear_btn.clicked.connect(lambda checked, eid=exam["id"]: self.on_clear_progress_clicked(eid))
            btn_layout.addWidget(clear_btn)

            btn_layout.setAlignment(Qt.AlignCenter)
            self.table_widget.setCellWidget(row, 5, btn_widget)

    def get_exam_progress_data(self, exam_id: str, total_questions: int) -> Dict[str, Any]:
        if self.progress_manager:
            progress_data = self.progress_manager.get_exam_progress(exam_id)
            if progress_data["total_questions"] != total_questions:
                self.progress_manager.update_exam_total_questions(exam_id, total_questions)
                progress_data = self.progress_manager.get_exam_progress(exam_id)
            return progress_data
        else:
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
        print(f"开始学习试卷: {exam_id}")
        self.study_exam_requested.emit(exam_id)

    def on_clear_progress_clicked(self, exam_id):
        print(f"清除试卷进度: {exam_id}")
        reply = QMessageBox.question(
            self,
            "确认清除进度",
            f"确定要清除试卷 '{exam_id}' 的学习进度吗？\n此操作将删除所有答题记录，无法恢复。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if self.progress_manager:
                if self.progress_manager.clear_exam_progress(exam_id):
                    QMessageBox.information(self, "清除成功", f"试卷 '{exam_id}' 的学习进度已清除")
                    self.refresh_list()
                else:
                    QMessageBox.warning(self, "清除失败", "清除进度失败，请重试")
            else:
                QMessageBox.warning(self, "错误", "进度管理器不可用")

    def refresh_list(self):
        print("刷新试卷列表")
        if self.progress_manager:
            if self.progress_manager.reload_data():
                print("进度数据已重新加载")
            else:
                print("警告: 重新加载进度数据失败")
        self.load_real_data()
        print("试卷列表已刷新，进度数据已更新")
        QMessageBox.information(self, "刷新完成", "试卷列表已刷新，学习进度和正确率已更新到最新状态")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        pass

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = ExamListWindow()
    window.show()
    sys.exit(app.exec_())