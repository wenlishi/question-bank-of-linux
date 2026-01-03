#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
答题主窗口 - ExamWindow
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QFrame, QScrollArea, QRadioButton,
                             QButtonGroup, QGridLayout, QGroupBox,
                             QTextEdit, QSizePolicy, QSpacerItem, QLineEdit, QMessageBox)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon
import sys
import os
import html
import re

# 导入进度弹窗
from .progress_dialog import ProgressDialog

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



class ExamWindow(QWidget):
    """答题主窗口"""

    # 定义信号：返回试卷列表
    back_to_list_requested = pyqtSignal()

    @staticmethod
    def smart_escape(text):
        """智能转义HTML文本
        保留合法的HTML标签（如<br>、<span>等），转义像<Ctrl>、<stdio.h>这样的文本

        实现思路：
        1. 首先转义整个文本（将<转义为&lt;，>转义为&gt;等）
        2. 然后将允许的HTML标签恢复（将&lt;br&gt;恢复为<br>）
        """
        # 定义允许的HTML标签
        allowed_tags = {'br', 'span', 'div', 'p', 'b', 'strong', 'i', 'em', 'u', 'code'}

        # 首先转义整个文本
        escaped = html.escape(text)

        # 然后恢复允许的HTML标签
        for tag in allowed_tags:
            # 处理普通标签：<br> -> &lt;br&gt; -> <br>
            escaped = escaped.replace(f'&lt;{tag}&gt;', f'<{tag}>')
            # 处理闭合标签：</br> -> &lt;/br&gt; -> </br>
            escaped = escaped.replace(f'&lt;/{tag}&gt;', f'</{tag}>')
            # 处理自闭合标签：<br/> -> &lt;br/&gt; -> <br/>
            escaped = escaped.replace(f'&lt;{tag}/&gt;', f'<{tag}/>')
            # 处理带属性的标签：<span style="..."> -> &lt;span style="..."&gt; -> <span style="...">
            # 这里使用正则表达式来处理带属性的标签
            import re
            # 匹配 &lt;tag 属性&gt; 并恢复为 <tag 属性>
            pattern = f'&lt;({tag})([^&]*?)&gt;'
            escaped = re.sub(pattern, r'<\1\2>', escaped)
            # 匹配 &lt;/tag&gt; 并恢复为 </tag>
            pattern = f'&lt;/({tag})&gt;'
            escaped = re.sub(pattern, r'</\1>', escaped)

        return escaped

    def __init__(self, exam_id="exam_001", exam_name="Linux应用与开发技术", parent=None):
        super().__init__(parent)
        self.exam_id = exam_id
        self.exam_name = exam_name
        self.current_question_index = 0
        self.total_questions = 0
        self.time_remaining = 120 * 60  # 120分钟，转换为秒
        self.user_answers = {}  # 保存用户答案
        self.answered_questions = {}  # 已做题目的索引，格式：{题目索引: 已做item索引集合}
        
        self.questions = []  # 题目列表
        self.current_item_index = 0  # 当前聚焦的item索引（用于cloze_group类型）

        # 生成会话ID
        import time
        self.session_id = f"session_{int(time.time())}_{exam_id}"

        # 持久化文件路径
        import os
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "sessions")
        os.makedirs(data_dir, exist_ok=True)
        self.session_file = os.path.join(data_dir, f"{self.session_id}.json")

        # 初始化试题管理器
        if QUESTION_MANAGER_AVAILABLE:
            self.question_manager = QuestionManager()
        else:
            self.question_manager = None
            QMessageBox.warning(self, "错误", "试题管理器初始化失败")

        # 初始化进度管理器
        if PROGRESS_MANAGER_AVAILABLE:
            self.progress_manager = UserProgressManager()
            # 更新试卷总题数
            self.update_exam_total_questions()
        else:
            self.progress_manager = None
            print("警告: 进度管理器初始化失败")

        # 初始化UI
        self.init_ui()

        # 启动倒计时
        self.start_timer()

        # 加载真实题目
        self.load_real_questions()

        # 加载已保存的会话数据（如果存在）
        self.load_session_data()

    def save_session_data(self):
        """保存会话数据到文件"""
        try:
            import json
            # 将answered_questions中的集合转换为列表，以便JSON序列化
            # 同时将整数键转换为字符串键
            answered_questions_serializable = {}
            for key, value in self.answered_questions.items():
                str_key = str(key)  # 将整数键转换为字符串
                if isinstance(value, set):
                    answered_questions_serializable[str_key] = list(value)
                else:
                    answered_questions_serializable[str_key] = value

            session_data = {
                'exam_id': self.exam_id,
                'session_id': self.session_id,
                'user_answers': self.user_answers,
                'answered_questions': answered_questions_serializable,
                'current_question_index': self.current_question_index,
                'current_item_index': self.current_item_index,
                'time_remaining': self.time_remaining
            }

            # 使用临时文件写入，确保原子性操作
            import tempfile
            import os
            temp_file = self.session_file + '.tmp'

            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
                f.flush()  # 确保数据写入磁盘
                os.fsync(f.fileno())  # 强制同步到磁盘

            # 原子性地替换原文件
            if os.path.exists(self.session_file):
                os.remove(self.session_file)
            os.rename(temp_file, self.session_file)

            print(f"会话数据已保存: {self.session_file}")
        except Exception as e:
            print(f"保存会话数据失败: {e}")
            import traceback
            traceback.print_exc()

    def load_session_data(self):
        """从文件加载会话数据"""
        try:
            import json
            import os

            if os.path.exists(self.session_file):
                with open(self.session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)

                # 恢复数据
                self.user_answers = session_data.get('user_answers', {})

                # 将answered_questions中的列表转换回集合
                answered_questions_loaded = session_data.get('answered_questions', {})
                self.answered_questions = {}
                for key, value in answered_questions_loaded.items():
                    if isinstance(value, list):
                        self.answered_questions[int(key)] = set(value)
                    else:
                        self.answered_questions[int(key)] = value

                self.current_question_index = session_data.get('current_question_index', 0)
                self.current_item_index = session_data.get('current_item_index', 0)
                self.time_remaining = session_data.get('time_remaining', 120 * 60)

                print(f"会话数据已加载: {self.session_file}")
                print(f"已恢复 {len(self.user_answers)} 个题目的答案")
            else:
                print("无已保存的会话数据")
        except Exception as e:
            print(f"加载会话数据失败: {e}")

    def delete_session_data(self):
        """删除会话数据文件"""
        try:
            import os
            if os.path.exists(self.session_file):
                os.remove(self.session_file)
                print(f"会话数据已删除: {self.session_file}")
        except Exception as e:
            print(f"删除会话数据失败: {e}")

    def delete_all_sessions(self):
        """删除sessions目录中的所有文件"""
        try:
            import os
            import glob

            # 获取sessions目录路径
            data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "sessions")

            if os.path.exists(data_dir):
                # 获取所有文件
                files = glob.glob(os.path.join(data_dir, "*"))

                # 删除所有文件
                deleted_count = 0
                for file_path in files:
                    try:
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                            deleted_count += 1
                            print(f"已删除会话文件: {os.path.basename(file_path)}")
                    except Exception as e:
                        print(f"删除文件 {file_path} 失败: {e}")

                print(f"已删除所有会话文件，共 {deleted_count} 个文件")
            else:
                print(f"sessions目录不存在: {data_dir}")

        except Exception as e:
            print(f"删除所有会话文件失败: {e}")

    def update_exam_total_questions(self):
        """更新试卷总题数到进度管理器"""
        if self.progress_manager and self.questions:
            # 计算实际题目总数（对于cloze_group类型，每个item算作一道题）
            total_questions = 0
            for question in self.questions:
                question_type = question.get('type', 'single_choice')
                if question_type == "cloze_group":
                    items = question.get('items', [])
                    total_questions += len(items)
                else:
                    total_questions += 1

            self.progress_manager.update_exam_total_questions(
                self.exam_id, total_questions
            )

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle(f"答题 - {self.exam_name}")
        self.setGeometry(100, 100, 1200, 800)

        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 创建顶部区域
        self.create_top_area(main_layout)

        # 创建中部核心区域
        self.create_middle_area(main_layout)

        # 创建底部答题卡区域
        self.create_bottom_area(main_layout)

    def create_top_area(self, parent_layout):
        """创建顶部区域"""
        # 第一行：标题栏
        title_frame = QFrame()
        title_frame.setStyleSheet("""
            QFrame {
                background-color: #007bff;
                border: none;
            }
        """)
        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(20, 10, 20, 10)

        # 标题
        title_label = QLabel(self.exam_name)
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 22px;
                font-weight: bold;
            }
        """)
        title_layout.addWidget(title_label)

        # 倒计时
        self.timer_label = QLabel("120:00")
        self.timer_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
            }
        """)
        title_layout.addWidget(self.timer_label)

        # 交卷按钮
        submit_btn = QPushButton("交卷")
        submit_btn.setFixedSize(80, 35)
        submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #bd2130;
            }
        """)
        submit_btn.clicked.connect(self.submit_exam)
        title_layout.addWidget(submit_btn)

        parent_layout.addWidget(title_frame)

        # 第二行：题型标签
        type_frame = QFrame()
        type_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-bottom: 1px solid #dee2e6;
            }
        """)
        type_layout = QHBoxLayout(type_frame)
        type_layout.setContentsMargins(20, 8, 20, 8)
        type_layout.setSpacing(20)

        # 创建题型按钮
        self.type_buttons = {}
        self.current_type_button = None  # 当前选中的题型按钮
        type_names = ["选择题", "填空题", "综合题"]

        # 基础样式和选中样式（存储为实例变量以便其他方法使用）
        self.type_button_base_style = """
            QPushButton {
                background-color: #e9ecef;
                color: #495057;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
                padding: 0 20px;
            }
            QPushButton:hover {
                background-color: #dee2e6;
            }
        """

        self.type_button_selected_style = """
            QPushButton {
                background-color: #007bff;
                color: white;
                border-color: #007bff;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
                padding: 0 20px;
            }
            QPushButton:hover {
                background-color: #0056b3;
                border-color: #0056b3;
            }
        """

        for i, name in enumerate(type_names):
            btn = QPushButton(name)
            btn.setFixedHeight(35)

            if i == 0:
                # 默认选中选择题
                btn.setStyleSheet(self.type_button_selected_style)
                self.current_type_button = btn
            else:
                btn.setStyleSheet(self.type_button_base_style)

            btn.clicked.connect(self.on_type_changed)
            type_layout.addWidget(btn)
            self.type_buttons[name] = btn

        type_layout.addStretch()
        parent_layout.addWidget(type_frame)

        # 第三行已移除，只保留底部的翻页按钮

    def create_middle_area(self, parent_layout):
        """创建中部核心区域"""
        middle_frame = QFrame()
        middle_layout = QHBoxLayout(middle_frame)
        middle_layout.setContentsMargins(0, 0, 0, 0)
        middle_layout.setSpacing(0)

        # 左侧题目区域 (80%)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(20, 20, 20, 20)

        # 题目滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
            }
            QScrollBar:vertical {
                background-color: #f8f9fa;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #adb5bd;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #6c757d;
            }
        """)

        # 题目内容容器
        self.question_container = QWidget()
        self.question_layout = QVBoxLayout(self.question_container)
        self.question_layout.setContentsMargins(0, 0, 0, 0)
        self.question_layout.setSpacing(15)

        # 题干
        self.question_label = QLabel()
        self.question_label.setWordWrap(True)
        self.question_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                line-height: 1.6;
                color: #212529;
                font-weight: 500;
            }
        """)
        self.question_layout.addWidget(self.question_label)

        # 选项区域
        self.options_group = QButtonGroup(self)
        self.options_group.setExclusive(True)
        self.options_widget = QWidget()
        self.options_layout = QVBoxLayout(self.options_widget)
        self.options_layout.setContentsMargins(20, 0, 0, 0)
        self.options_layout.setSpacing(10)
        self.question_layout.addWidget(self.options_widget)

        # 解析面板（默认隐藏）
        self.analysis_frame = QFrame()
        self.analysis_frame.setVisible(False)
        self.analysis_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 15px;
                margin-top: 20px;
            }
        """)
        analysis_layout = QVBoxLayout(self.analysis_frame)

        # 正确答案
        self.correct_answer_label = QLabel()
        self.correct_answer_label.setTextFormat(Qt.RichText)  # 支持HTML格式
        self.correct_answer_label.setWordWrap(True)  # 启用自动换行
        self.correct_answer_label.setStyleSheet("""
            QLabel {
                color: #dc3545;
                font-weight: bold;
                font-size: 18px;
                font-family: "Microsoft YaHei";
                line-height: 1.6;
            }
        """)
        analysis_layout.addWidget(self.correct_answer_label)

        # 解析内容
        self.analysis_label = QLabel()
        self.analysis_label.setWordWrap(True)
        self.analysis_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-size: 18px;
                font-family: "Microsoft YaHei";
                line-height: 1.6;
                background-color: #e9ecef;
                padding: 12px;
                border-radius: 3px;
                margin-top: 12px;
            }
        """)
        analysis_layout.addWidget(self.analysis_label)

        self.question_layout.addWidget(self.analysis_frame)
        self.question_layout.addStretch()

        scroll_area.setWidget(self.question_container)
        left_layout.addWidget(scroll_area)

        middle_layout.addWidget(left_widget, 4)  # 左区域占4份（80%）

        # 右侧区域 (20%)
        right_widget = QWidget()
        right_widget.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-left: 1px solid #dee2e6;
            }
        """)
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(15, 30, 15, 20)
        right_layout.setSpacing(15)

        # 显示/隐藏解析按钮
        self.toggle_analysis_btn = QPushButton("📖 显示解析")
        self.toggle_analysis_btn.setCheckable(True)
        self.toggle_analysis_btn.setFixedHeight(45)
        self.toggle_analysis_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #495057;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
                text-align: left;
                padding-left: 15px;
            }
            QPushButton:checked {
                background-color: #007bff;
                color: white;
                border-color: #007bff;
            }
            QPushButton:hover:!checked {
                background-color: #e9ecef;
            }
        """)
        self.toggle_analysis_btn.clicked.connect(self.toggle_analysis)
        right_layout.addWidget(self.toggle_analysis_btn)

        # 答题进度按钮
        self.progress_btn = QPushButton("📊 答题进度")
        self.progress_btn.setFixedHeight(45)
        self.progress_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #495057;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
                text-align: left;
                padding-left: 15px;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
        """)
        self.progress_btn.clicked.connect(self.show_progress_dialog)
        right_layout.addWidget(self.progress_btn)

        right_layout.addStretch()
        middle_layout.addWidget(right_widget, 1)  # 右区域占1份（20%）

        parent_layout.addWidget(middle_frame, 1)  # 设置拉伸因子为1

    def create_bottom_area(self, parent_layout):
        """创建底部区域（已移除答题卡）"""
        bottom_frame = QFrame()
        bottom_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-top: 1px solid #dee2e6;
            }
        """)
        bottom_layout = QVBoxLayout(bottom_frame)
        bottom_layout.setContentsMargins(20, 20, 20, 15)

        # 底部按钮区域
        bottom_btn_layout = QHBoxLayout()

        # 返回按钮
        back_btn = QPushButton("返回列表")
        back_btn.setFixedSize(100, 35)
        back_btn.setStyleSheet("""
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
        back_btn.clicked.connect(self.back_to_list)
        bottom_btn_layout.addWidget(back_btn)

        bottom_btn_layout.addStretch()

        # 翻页按钮
        self.bottom_prev_btn = QPushButton("上一题")
        self.bottom_prev_btn.setFixedSize(100, 35)
        self.bottom_prev_btn.setStyleSheet("""
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
            QPushButton:disabled {
                background-color: #e9ecef;
                color: #adb5bd;
            }
        """)
        self.bottom_prev_btn.clicked.connect(self.prev_question)
        self.bottom_prev_btn.setEnabled(False)
        bottom_btn_layout.addWidget(self.bottom_prev_btn)

        self.bottom_next_btn = QPushButton("下一题")
        self.bottom_next_btn.setFixedSize(100, 35)
        self.bottom_next_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0069d9;
            }
            QPushButton:pressed {
                background-color: #0062cc;
            }
            QPushButton:disabled {
                background-color: #e9ecef;
                color: #adb5bd;
            }
        """)
        self.bottom_next_btn.clicked.connect(self.next_question)
        bottom_btn_layout.addWidget(self.bottom_next_btn)

        bottom_layout.addLayout(bottom_btn_layout)
        parent_layout.addWidget(bottom_frame)

    def start_timer(self):
        """启动倒计时"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)  # 每秒更新一次

    def update_timer(self):
        """更新倒计时"""
        if self.time_remaining <= 0:
            self.timer.stop()
            self.timeout_submit()
            return

        self.time_remaining -= 1
        minutes = self.time_remaining // 60
        seconds = self.time_remaining % 60
        self.timer_label.setText(f"{minutes:02d}:{seconds:02d}")

        # 最后5分钟显示红色警告
        if self.time_remaining <= 300:  # 5分钟
            self.timer_label.setStyleSheet("""
                QLabel {
                    color: #dc3545;
                    font-size: 16px;
                    font-weight: bold;
                }
            """)

    # def load_real_questions(self):
    #     """加载真实题目"""
    #     if not self.question_manager:
    #         QMessageBox.warning(self, "错误", "试题管理器不可用")
    #         return

    #     # 加载试卷数据
    #     exam_data = self.question_manager.load_exam(self.exam_id)
    #     if not exam_data:
    #         QMessageBox.warning(self, "错误", f"无法加载试卷: {self.exam_id}")
    #         return

    #     # 设置试卷信息
    #     self.exam_name = exam_data.get('exam_name', self.exam_name)
    #     self.setWindowTitle(f"答题 - {self.exam_name}")

    #     # 设置时间限制
    #     time_limit = exam_data.get('time_limit', 120)
    #     self.time_remaining = time_limit * 60

    #     # 加载题目
    #     original_questions = exam_data.get('questions', [])
    #     self.questions = []

    #     # 跟踪题目序号
    #     question_counter = 1

    #     for question in original_questions:
    #         question_type = question.get('type', 'single_choice')

    #         # 对于cloze_group类型，本身没有题号，只有它的item有题号
    #         if question_type == "cloze_group":
    #             items = question.get('items', [])
    #             # cloze_group本身没有题号
    #             question['question_number'] = None
    #             self.questions.append(question)
    #             # 为每个item设置题号
    #             for i, item in enumerate(items):
    #                 # 为item添加题号信息（用于显示）
    #                 if 'metadata' not in item:
    #                     item['metadata'] = {}
    #                 item['metadata']['question_number'] = question_counter + i
    #             # 增加题号计数器
    #             question_counter += len(items)
    #         else:
    #             # 其他题型：为题目添加题号
    #             question['question_number'] = question_counter
    #             self.questions.append(question)
    #             question_counter += 1

    #     # 计算实际题目总数（对于cloze_group类型，每个item算作一道题）
    #     self.total_questions = 0
    #     for question in self.questions:
    #         question_type = question.get('type', 'single_choice')
    #         if question_type == "cloze_group":
    #             items = question.get('items', [])
    #             self.total_questions += len(items)
    #         else:
    #             self.total_questions += 1

    #     if self.total_questions == 0:
    #         QMessageBox.warning(self, "错误", "试卷中没有题目")
    #         return

    #     # 更新答题卡数量
    #     self.update_answer_sheet_count()

    #     # 更新试卷总题数到进度管理器
    #     self.update_exam_total_questions()

    #     # 显示第一题
    #     self.show_question(0, 0)

    #     # 打印题目结构用于调试
    #     self.print_question_structure()

    def load_real_questions(self):
        """加载真实题目（含映射表构建）"""
        if not self.question_manager:
            return

        exam_data = self.question_manager.load_exam(self.exam_id)
        if not exam_data:
            return

        self.exam_name = exam_data.get('exam_name', self.exam_name)
        self.setWindowTitle(f"答题 - {self.exam_name}")
        
        original_questions = exam_data.get('questions', [])
        self.questions = []
        question_counter = 1
        self.total_questions = 0

        for q_idx, question in enumerate(original_questions):
            q_type = question.get('type', 'single_choice')

            # 添加到题目列表
            if q_type == "cloze_group":
                items = question.get('items', [])
                question['question_number'] = None
                self.questions.append(question)

                # 更新item元数据
                for item_idx in range(len(items)):
                    item = items[item_idx]
                    if 'metadata' not in item: item['metadata'] = {}
                    item['metadata']['question_number'] = question_counter + item_idx

                question_counter += len(items)
                self.total_questions += len(items)

            else:
                # 普通题目
                question['question_number'] = question_counter
                self.questions.append(question)

                question_counter += 1
                self.total_questions += 1

        self.update_exam_total_questions()
        self.show_question(0, 0)
    def print_question_structure(self):
        """打印题目结构用于调试"""
        print("\n=== 题目结构调试信息 ===")
        print(f"总题目数（questions列表）: {len(self.questions)}")
        print(f"总题目数（total_questions）: {self.total_questions}")

        for i, question in enumerate(self.questions):
            question_type = question.get('type', 'single_choice')
            if question_type == "cloze_group":
                items = question.get('items', [])
                print(f"题目{i}: type={question_type}, items={len(items)}")
            else:
                print(f"题目{i}: type={question_type}")
        print("=== 结束题目结构调试 ===\n")


    def show_question(self, index, item_index=0):
        """显示指定索引的题目

        Args:
            index: 题目索引
            item_index: 对于cloze_group类型，要聚焦的item索引（默认0）
        """
        if index < 0 or index >= len(self.questions):
            return

        self.current_question_index = index
        self.current_item_index = item_index
        question = self.questions[index]
        question_id = question.get('id', f'q_{index+1}')

        question_type = question.get('type', 'single_choice')

        # 检查是否是cloze_group或comprehensive类型
        is_cloze_group = question_type == "cloze_group"
        is_comprehensive = question_type == "comprehensive"

        if is_cloze_group or is_comprehensive:
            # 对于cloze_group和comprehensive类型，不在题目左边显示题号
            # 题号已经显示在题干中的______前面了
            question_html = f"""
            <div style="display: flex; align-items: flex-start; margin-bottom: 10px;">
                <span style="
                    font-size: 20px;
                    line-height: 1.6;
                    color: #212529;
                    font-weight: 500;
                    font-family: 'Microsoft YaHei';
                    flex-grow: 1;
                ">
                    &nbsp;
                </span>
            </div>
            """
        else:
            # 其他题型：转义HTML特殊字符并显示题号在题目左边
            question_text = html.escape(question['question'])
            question_number = question.get('question_number', index + 1)
            question_html = f"""
            <div style="display: flex; align-items: flex-start; margin-bottom: 10px;">
                <span style="
                    color: #007bff;
                    font-size: 20px;
                    font-weight: bold;
                    font-family: 'Microsoft YaHei';
                    margin-right: 10px;
                    min-width: 30px;
                ">
                    {question_number}.
                </span>
                <span style="
                    font-size: 20px;
                    line-height: 1.6;
                    color: #212529;
                    font-weight: 500;
                    font-family: 'Microsoft YaHei';
                    flex-grow: 1;
                ">
                    {question_text}
                </span>
            </div>
            """
        self.question_label.setText(question_html)

        # 清除之前的选项
        while self.options_layout.count():
            child = self.options_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # 根据题型创建不同的输入部件
        question_type = question.get('type', 'single_choice')

        if question_type == "single_choice":
            # 单选题：单选按钮
            options = question.get('options', [])
            for i, option in enumerate(options):
                # 选项已经包含字母前缀（如 "A.程序"），显示时只显示内容部分
                # 分割字母前缀和内容（如 "A.程序" -> "程序"）
                if '.' in option:
                    display_text = option.split('.', 1)[1].strip()
                else:
                    display_text = option
                # 处理&符号，在Qt中&需要转义为&&
                display_text_escaped = display_text.replace('&', '&&')
                radio = QRadioButton(f"{chr(65 + i)}. {display_text_escaped}")
                radio.setStyleSheet("""
                    QRadioButton {
                        font-size: 18px;
                        font-family: "Microsoft YaHei";
                        padding: 12px;
                        border-radius: 5px;
                        min-height: 35px;
                    }
                    QRadioButton:hover {
                        background-color: #f8f9fa;
                    }
                """)
                self.options_layout.addWidget(radio)
                self.options_group.addButton(radio, i)

                # 如果用户之前选择过这个选项，设置为选中并恢复颜色
                if question_id in self.user_answers:
                    user_answer = self.user_answers[question_id]
                    if isinstance(user_answer, list) and len(user_answer) > 0:
                        if user_answer[0] == option:
                            radio.setChecked(True)
                            # 检查答案是否正确并设置颜色
                            is_correct, _, _, _ = self.question_manager.check_answer(question, user_answer)
                            if is_correct:
                                # 正确 - 绿色
                                radio.setStyleSheet("""
                                    QRadioButton {
                                        font-size: 18px;
                                        font-family: "Microsoft YaHei";
                                        padding: 12px;
                                        border-radius: 5px;
                                        min-height: 35px;
                                        color: #28a745;
                                        font-weight: bold;
                                    }
                                    QRadioButton:hover {
                                        background-color: #f8f9fa;
                                    }
                                """)
                            else:
                                # 错误 - 红色
                                radio.setStyleSheet("""
                                    QRadioButton {
                                        font-size: 18px;
                                        font-family: "Microsoft YaHei";
                                        padding: 12px;
                                        border-radius: 5px;
                                        min-height: 35px;
                                        color: #dc3545;
                                        font-weight: bold;
                                    }
                                    QRadioButton:hover {
                                        background-color: #f8f9fa;
                                    }
                                """)

                # 为单选按钮添加点击事件，选择后立即显示答案和解析
                radio.clicked.connect(lambda checked, q=question, opt=option: self.on_single_choice_selected(q, opt))

        elif question_type == "fill_blank":
            # 填空题：支持多空题目
            question_text = question['question']

            # 检查是否是从cloze_group拆分出来的填空题
            is_cloze_derived = 'original_cloze_id' in question

            if is_cloze_derived:
                # 从cloze_group拆分出来的填空题：在输入框左边显示题号
                question_number = question.get('question_number', 1)

                # 创建空位标签和输入框的容器
                blank_widget = QWidget()
                blank_layout = QHBoxLayout(blank_widget)
                blank_layout.setContentsMargins(0, 0, 0, 0)
                blank_layout.setSpacing(10)

                # 空位标签：显示题号（如48、49）
                blank_label_text = f"{question_number}."
                blank_label = QLabel(blank_label_text)
                blank_label.setStyleSheet("""
                    QLabel {
                        font-size: 18px;
                        font-family: "Microsoft YaHei";
                        font-weight: bold;
                        color: #007bff;
                        min-width: 40px;
                    }
                """)
                blank_layout.addWidget(blank_label)

                # 输入框
                input_field = QLineEdit()
                input_field.setPlaceholderText(f"请输入答案")
                input_field.setStyleSheet("""
                    QLineEdit {
                        font-size: 18px;
                        font-family: "Microsoft YaHei";
                        padding: 12px;
                        border: 1px solid #dee2e6;
                        border-radius: 5px;
                        min-height: 35px;
                    }
                    QLineEdit:focus {
                        border-color: #007bff;
                    }
                """)

                # 如果用户之前填写过答案，设置为已填内容并恢复颜色
                if question_id in self.user_answers:
                    user_answer = self.user_answers[question_id]
                    if isinstance(user_answer, list) and len(user_answer) > 0:
                        input_field.setText(user_answer[0])
                        # 检查答案是否正确并设置颜色
                        if user_answer[0].strip():  # 只处理非空答案
                            is_correct, _, item_correctness, _ = self.question_manager.check_answer(question, user_answer)
                            if len(item_correctness) > 0:
                                is_item_correct = item_correctness[0]
                                # 使用统一的颜色设置方法
                                self.update_input_field_color(question_id, 0, is_item_correct)

                # 为输入框添加失去焦点事件（用户完成输入）
                input_field.editingFinished.connect(lambda q_id=question_id, idx=0, field=input_field: self.on_fill_blank_finished(q_id, idx, field))

                blank_layout.addWidget(input_field, 1)  # 设置拉伸因子
                self.options_layout.addWidget(blank_widget)
            else:
                # 普通填空题
                # 统计题目中的空位数量（通过______的数量）
                blank_count = question_text.count('______')

                if blank_count > 1:
                    # 多空填空题：为每个空创建输入框
                    for i in range(blank_count):
                        # 创建空位标签和输入框的容器
                        blank_widget = QWidget()
                        blank_layout = QHBoxLayout(blank_widget)
                        blank_layout.setContentsMargins(0, 0, 0, 0)
                        blank_layout.setSpacing(10)

                        # 空位标签（如【1】、【2】或根据题目中的编号）
                        # 尝试从题目中提取空位编号（如47______、48______）
                        import re
                        blank_num_match = re.findall(r'(\d+)______', question_text)
                        if i < len(blank_num_match):
                            blank_label_text = f"【{blank_num_match[i]}】"
                        else:
                            blank_label_text = f"【{i+1}】"

                        blank_label = QLabel(blank_label_text)
                        blank_label.setStyleSheet("""
                            QLabel {
                                font-size: 18px;
                                font-family: "Microsoft YaHei";
                                font-weight: bold;
                                color: #007bff;
                                min-width: 40px;
                            }
                        """)
                        blank_layout.addWidget(blank_label)

                        # 输入框
                        input_field = QLineEdit()
                        input_field.setPlaceholderText(f"请输入答案")
                        input_field.setStyleSheet("""
                            QLineEdit {
                                font-size: 18px;
                                font-family: "Microsoft YaHei";
                                padding: 12px;
                                border: 1px solid #dee2e6;
                                border-radius: 5px;
                                min-height: 35px;
                            }
                            QLineEdit:focus {
                                border-color: #007bff;
                            }
                        """)

                        # 如果用户之前填写过答案，设置为已填内容并恢复颜色
                        if question_id in self.user_answers:
                            user_answer = self.user_answers[question_id]
                            if isinstance(user_answer, list) and i < len(user_answer):
                                input_field.setText(user_answer[i])
                                # 检查答案是否正确并设置颜色
                                if user_answer[i].strip():  # 只处理非空答案
                                    is_correct, _, item_correctness, _ = self.question_manager.check_answer(question, user_answer)
                                    if i < len(item_correctness):
                                        is_item_correct = item_correctness[i]
                                        # 使用统一的颜色设置方法
                                        self.update_input_field_color(question_id, i, is_item_correct)

                        # 为输入框添加失去焦点事件（用户完成输入）
                        input_field.editingFinished.connect(lambda q_id=question_id, idx=i, field=input_field: self.on_fill_blank_finished(q_id, idx, field))

                        blank_layout.addWidget(input_field, 1)  # 设置拉伸因子
                        self.options_layout.addWidget(blank_widget)
                else:
                    # 单空填空题：单个输入框
                    input_field = QLineEdit()
                    input_field.setPlaceholderText("请输入答案")
                    input_field.setStyleSheet("""
                        QLineEdit {
                            font-size: 18px;
                            font-family: "Microsoft YaHei";
                            padding: 12px;
                            border: 1px solid #dee2e6;
                            border-radius: 5px;
                            min-height: 35px;
                        }
                        QLineEdit:focus {
                            border-color: #007bff;
                        }
                    """)

                    # 如果用户之前填写过答案，设置为已填内容并恢复颜色
                    if question_id in self.user_answers:
                        user_answer = self.user_answers[question_id]
                        if isinstance(user_answer, list) and len(user_answer) > 0:
                            input_field.setText(user_answer[0])
                            # 检查答案是否正确并设置颜色
                            if user_answer[0].strip():  # 只处理非空答案
                                is_correct, _, item_correctness, _ = self.question_manager.check_answer(question, user_answer)
                                if len(item_correctness) > 0:
                                    is_item_correct = item_correctness[0]
                                    # 使用统一的颜色设置方法
                                    self.update_input_field_color(question_id, 0, is_item_correct)

                    # 为输入框添加失去焦点事件（用户完成输入）
                    input_field.editingFinished.connect(lambda q_id=question_id, idx=0, field=input_field: self.on_fill_blank_finished(q_id, idx, field))

                    self.options_layout.addWidget(input_field)

        elif question_type == "cloze_group":
            # 完形填空组：多个空显示在一起
            items = question.get('items', [])
            question_text = question['question']
            analysis = question.get('analysis', '')

            # 修改题干：在每个______前加上对应的蓝色题号
            # 例如："用______命令增加，用______命令减少"
            #  -> "用<span style='color: #007bff; font-weight: bold;'>48.</span>______命令增加，用<span style='color: #007bff; font-weight: bold;'>49.</span>______命令减少"
            modified_question_text = question_text
            parts = modified_question_text.split('______')

            # 获取题号（第一个空的题号）
            # 从第一个item的metadata中获取题号
            first_question_number = 1
            if items and len(items) > 0:
                first_item = items[0]
                if 'metadata' in first_item and 'question_number' in first_item['metadata']:
                    first_question_number = first_item['metadata']['question_number']

            # 在每个______前加上对应的题号
            for i in range(len(parts) - 1):  # 最后一个部分后面没有______
                current_question_number = first_question_number + i
                parts[i] = parts[i] + f"<span style='color: #007bff; font-weight: bold;'>{current_question_number}.</span>"

            modified_question_text = '______'.join(parts)

            # 显示修改后的题干
            question_label = QLabel(modified_question_text)
            question_label.setStyleSheet("""
                QLabel {
                    font-size: 18px;
                    font-family: "Microsoft YaHei";
                    line-height: 1.6;
                    color: #212529;
                    font-weight: 500;
                    margin-bottom: 20px;
                }
            """)
            question_label.setWordWrap(True)
            self.options_layout.addWidget(question_label)

            # 为每个空创建输入框（显示在一起）
            for i, item in enumerate(items):
                item_id = item.get('id', '')
                item_index = item.get('index', 1)
                item_score = item.get('score', 1)
                current_question_number = first_question_number + i

                # 创建空位标签和输入框的容器
                blank_widget = QWidget()
                blank_layout = QHBoxLayout(blank_widget)
                blank_layout.setContentsMargins(0, 0, 0, 0)
                blank_layout.setSpacing(10)

                # 空位标签：显示题号（如48、49）
                blank_label_text = f"{current_question_number}."
                blank_label = QLabel(blank_label_text)
                blank_label.setStyleSheet("""
                    QLabel {
                        font-size: 18px;
                        font-family: "Microsoft YaHei";
                        font-weight: bold;
                        color: #007bff;
                        min-width: 40px;
                    }
                """)
                blank_layout.addWidget(blank_label)

                # 输入框
                input_field = QLineEdit()
                input_field.setPlaceholderText(f"请输入答案")
                input_field.setStyleSheet("""
                    QLineEdit {
                        font-size: 18px;
                        font-family: "Microsoft YaHei";
                        padding: 12px;
                        border: 1px solid #dee2e6;
                        border-radius: 5px;
                        min-height: 35px;
                    }
                    QLineEdit:focus {
                        border-color: #007bff;
                    }
                """)

                # 如果用户之前填写过答案，设置为已填内容
                if question_id in self.user_answers:
                    user_answer = self.user_answers[question_id]
                    if isinstance(user_answer, list) and i < len(user_answer):
                        input_field.setText(user_answer[i])

                # 为输入框添加文本变化事件（实时保存答案）
                input_field.textChanged.connect(lambda text, q_id=question_id, idx=i: self.on_cloze_text_changed(q_id, idx, text))
                # 为输入框添加失去焦点事件（检查是否所有空都填完）
                input_field.editingFinished.connect(lambda q_id=question_id, idx=i, field=input_field: self.on_cloze_finished(q_id, idx, field))

                blank_layout.addWidget(input_field, 1)  # 设置拉伸因子
                self.options_layout.addWidget(blank_widget)

        elif question_type == "comprehensive":
            # 综合题：使用items格式，类似cloze_group
            items = question.get('items', [])
            if not items:
                error_label = QLabel("综合题格式错误：缺少items")
                error_label.setStyleSheet("""
                    QLabel {
                        color: red;
                        font-size: 16px;
                    }
                """)
                self.options_layout.addWidget(error_label)
                return

            question_text = question['question']
            analysis = question.get('analysis', '')

            # 显示题干（包含占位符）
            question_label = QLabel()
            question_label.setTextFormat(Qt.RichText)
            # 将题干中的占位符格式化为更明显的样式
            # 首先转义HTML特殊字符
            escaped_question = html.escape(question_text)
            # 将 (52)______________ 替换为带样式的占位符
            import re
            formatted_question = re.sub(r'\((\d+)\)_{5,}',
                                      r'<span style="color: #007bff; font-weight: bold;">\1.</span>______',
                                      escaped_question)
            # 将换行符转换为HTML换行（需要在转义后处理）
            formatted_question = formatted_question.replace('\n', '<br>')
            question_label.setText(formatted_question)
            question_label.setStyleSheet("""
                QLabel {
                    font-size: 18px;
                    font-family: "Microsoft YaHei";
                    line-height: 1.6;
                    padding: 0px 0 10px 0;  /* 上边距减少，让题干稍微往上一点 */
                    margin-top: -20px;       /* 负边距进一步往上移动 */
                }
            """)
            question_label.setWordWrap(True)
            self.options_layout.addWidget(question_label)

            # 为每个空创建输入框（水平排列，类似cloze_group）
            for i, item in enumerate(items):
                item_id = item.get('id', '')
                item_index = item.get('index', i + 1)
                item_score = item.get('score', 1)

                # 创建空位标签和输入框的容器
                blank_widget = QWidget()
                blank_layout = QHBoxLayout(blank_widget)
                blank_layout.setContentsMargins(0, 0, 0, 0)
                blank_layout.setSpacing(10)

                # 空位标签：显示题号（如52、53）
                blank_label_text = f"{item_index}."
                blank_label = QLabel(blank_label_text)
                blank_label.setStyleSheet("""
                    QLabel {
                        font-size: 18px;
                        font-family: "Microsoft YaHei";
                        font-weight: bold;
                        color: #007bff;
                        min-width: 40px;
                    }
                """)
                blank_layout.addWidget(blank_label)

                # 输入框
                input_field = QLineEdit()
                input_field.setPlaceholderText(f"请输入答案")
                input_field.setStyleSheet("""
                    QLineEdit {
                        font-size: 18px;
                        font-family: "Microsoft YaHei";
                        padding: 12px;
                        border: 1px solid #dee2e6;
                        border-radius: 5px;
                        min-height: 35px;
                    }
                    QLineEdit:focus {
                        border-color: #007bff;
                    }
                """)

                # 如果用户之前填写过答案，设置为已填内容
                if question_id in self.user_answers:
                    user_answer = self.user_answers[question_id]
                    if isinstance(user_answer, list) and i < len(user_answer):
                        input_field.setText(user_answer[i])

                # 为输入框添加文本变化事件（实时保存答案）
                input_field.textChanged.connect(lambda text, q_id=question_id, idx=i: self.on_cloze_text_changed(q_id, idx, text))
                # 为输入框添加失去焦点事件（检查是否所有空都填完）
                input_field.editingFinished.connect(lambda q_id=question_id, idx=i, field=input_field: self.on_cloze_finished(q_id, idx, field))

                blank_layout.addWidget(input_field, 1)  # 设置拉伸因子
                self.options_layout.addWidget(blank_widget)

        # 更新解析内容
        question_text = question['question']

        # 初始化变量
        answer_text = "暂无正确答案"

        if question_type == "cloze_group":
            # 完形填空组：从items中获取正确答案
            items = question.get('items', [])
            # 对于cloze_group类型，从第一个item的metadata中获取题号
            first_question_number = 1
            if items and len(items) > 0:
                first_item = items[0]
                if 'metadata' in first_item and 'question_number' in first_item['metadata']:
                    first_question_number = first_item['metadata']['question_number']
                else:
                    # 如果metadata中没有question_number，使用默认值1
                    first_question_number = 1

            answer_parts = []
            for i, item in enumerate(items):
                item_answer = item.get('answer', '')
                current_question_number = first_question_number + i
                answer_parts.append(f"{current_question_number}. {item_answer}")

            # 使用HTML换行标签实现多行显示
            answer_text = "<br>".join(answer_parts)

        elif question_type == "fill_blank":
            correct_answer = question.get('answer', [])
            # 填空题：特殊处理多空题目
            blank_count = question_text.count('______')

            if blank_count > 1:
                # 多空填空题：显示每个空的正确答案
                import re
                blank_num_match = re.findall(r'(\d+)______', question_text)

                if isinstance(correct_answer, list):
                    answer_parts = []
                    for i, ans in enumerate(correct_answer):
                        if i < len(blank_num_match):
                            # 使用题目中的编号（如47、48）
                            answer_parts.append(f"【{blank_num_match[i]}】{ans}")
                        else:
                            # 使用顺序编号
                            answer_parts.append(f"【{i+1}】{ans}")
                    # 使用HTML换行标签实现多行显示
                    answer_text = "<br>".join(answer_parts)
                else:
                    answer_text = str(correct_answer)
            else:
                # 单空填空题
                if isinstance(correct_answer, list) and len(correct_answer) > 0:
                    answer_text = correct_answer[0]
                else:
                    answer_text = str(correct_answer)
        elif question_type == "single_choice":
            # 单选题：显示完整的选项文本
            correct_answer = question.get('answer', [])
            if isinstance(correct_answer, list):
                answer_parts = []
                for ans in correct_answer:
                    # 显示完整的选项文本，如 "C.资源"
                    answer_parts.append(ans)
                answer_text = "，".join(answer_parts)
            else:
                answer_text = str(correct_answer)
        elif question_type == "comprehensive":
            # 综合题：从items中获取正确答案，使用多行显示
            items = question.get('items', [])
            answer_parts = []
            for i, item in enumerate(items):
                item_answer = item.get('answer', '')
                # 综合题通常有题号，如52、53等
                item_index = item.get('index', i + 1)
                answer_parts.append(f"{item_index}. {item_answer}")
            # 使用HTML换行标签实现多行显示
            answer_text = "<br>".join(answer_parts)
        else:
            # 其他题型
            correct_answer = question.get('answer', [])
            if isinstance(correct_answer, list):
                answer_text = "，".join(correct_answer)
            else:
                answer_text = str(correct_answer)

        # 正确答案需要智能处理HTML特殊字符
        # 保留合法的HTML标签（如<br>），转义像<Ctrl>这样的文本
        answer_text_escaped = self.smart_escape(answer_text)
        self.correct_answer_label.setText(f"正确答案：{answer_text_escaped}")

        # 解析部分不需要处理&符号，可以正常显示
        analysis_text = question.get('analysis', '暂无解析')
        self.analysis_label.setText(analysis_text)

        # 保存要聚焦的item索引
        self.current_item_index = item_index

        # 更新导航按钮状态
        self.update_navigation_buttons()

        # 更新题型按钮
        self.update_type_buttons(question_type)

        # 检查题目是否已答，如果已答则显示解析
        question_id = question.get('id', f'q_{self.current_question_index+1}')
        is_answered = question_id in self.user_answers and any(self.user_answers[question_id])

        if is_answered:
            # 题目已答，显示解析
            self.analysis_frame.setVisible(True)
            self.toggle_analysis_btn.setChecked(True)
            self.toggle_analysis_btn.setText("📖 隐藏解析")
        else:
            # 题目未答，隐藏解析
            self.analysis_frame.setVisible(False)
            self.toggle_analysis_btn.setChecked(False)
            self.toggle_analysis_btn.setText("📖 显示解析")

        # 使用定时器延迟聚焦和恢复颜色，确保输入框已经创建
        from PyQt5.QtCore import QTimer
        if is_answered:
            # 延迟恢复颜色，确保输入框已经创建
            QTimer.singleShot(150, lambda: self.restore_input_field_colors(question, question_id))
        # 聚焦到当前输入框
        QTimer.singleShot(100, self.focus_current_item)

    def restore_input_field_colors(self, question, question_id):
        """恢复已答题目的输入框颜色状态"""
        if question_id not in self.user_answers:
            return

        user_answer = self.user_answers[question_id]
        if not user_answer:
            return

        question_type = question.get('type', 'single_choice')

        # 检查答案是否正确
        is_correct, _, item_correctness, _ = self.question_manager.check_answer(question, user_answer)

        # 根据题型恢复颜色
        if question_type in ["cloze_group", "comprehensive"]:
            # 对于cloze_group和综合题，恢复每个输入框的颜色
            items = question.get('items', [])
            for i in range(len(items)):
                if i < len(user_answer) and user_answer[i].strip():  # 只恢复已填写的空
                    if i < len(item_correctness):
                        is_item_correct = item_correctness[i]
                        self.update_input_field_color(question_id, i, is_item_correct)
        elif question_type == "fill_blank":
            # 对于填空题，恢复输入框颜色
            # 首先尝试从题目中获取空位数量
            question_text = question['question']
            blank_count = question_text.count('______')

            # 如果题干中没有______，可能是从cloze_group拆分出来的填空题
            if blank_count == 0:
                # 从cloze_group拆分出来的填空题只有1个空
                blank_count = 1

            for i in range(blank_count):
                if i < len(user_answer) and user_answer[i].strip():
                    if i < len(item_correctness):
                        is_item_correct = item_correctness[i]
                        self.update_input_field_color(question_id, i, is_item_correct)
        elif question_type == "single_choice":
            # 对于单选题，恢复单选按钮颜色
            self.restore_radio_button_color(question, user_answer, is_correct)

    def restore_radio_button_color(self, question, user_answer, is_correct):
        """恢复单选题的单选按钮颜色状态"""
        if not user_answer or len(user_answer) == 0:
            return

        selected_option = user_answer[0]
        options = question.get('options', [])

        # 查找选中的选项
        for i, option in enumerate(options):
            if option == selected_option:
                # 找到对应的单选按钮
                radio_button = self.options_group.button(i)
                if radio_button:
                    # 设置选中状态
                    radio_button.setChecked(True)
                    # 恢复颜色
                    if is_correct:
                        # 正确 - 绿色
                        radio_button.setStyleSheet("""
                            QRadioButton {
                                font-size: 18px;
                                font-family: "Microsoft YaHei";
                                padding: 12px;
                                border-radius: 5px;
                                min-height: 35px;
                                color: #28a745;
                                font-weight: bold;
                            }
                            QRadioButton:hover {
                                background-color: #f8f9fa;
                            }
                        """)
                    else:
                        # 错误 - 红色
                        radio_button.setStyleSheet("""
                            QRadioButton {
                                font-size: 18px;
                                font-family: "Microsoft YaHei";
                                padding: 12px;
                                border-radius: 5px;
                                min-height: 35px;
                                color: #dc3545;
                                font-weight: bold;
                            }
                            QRadioButton:hover {
                                background-color: #f8f9fa;
                            }
                        """)
                break

    def focus_current_item(self):
        """聚焦到当前题目的指定item输入框"""
        question = self.questions[self.current_question_index] if self.current_question_index < len(self.questions) else None
        if not question:
            return

        question_type = question.get('type', 'single_choice')
        if question_type != "cloze_group":
            return

        # 查找对应的输入框
        item_index = getattr(self, 'current_item_index', 0)

        # 对于cloze_group类型，输入框在options_layout中
        # 第一个widget是题干标签，所以从1开始
        input_field_index = 1 + item_index  # 跳过题干标签

        if input_field_index < self.options_layout.count():
            widget_item = self.options_layout.itemAt(input_field_index)
            if widget_item:
                widget = widget_item.widget()
                if isinstance(widget, QWidget):
                    # 查找widget中的QLineEdit
                    container_layout = widget.layout()
                    if container_layout:
                        for i in range(container_layout.count()):
                            child_widget = container_layout.itemAt(i).widget()
                            if isinstance(child_widget, QLineEdit):
                                child_widget.setFocus()
                                break

    # def update_answer_sheet(self):
    #     """更新答题卡按钮状态"""
    #     # 获取当前选中的题型按钮
    #     current_type_button_text = self.current_type_button.text() if self.current_type_button else "选择题"

    #     # 根据按钮文本确定要显示的题型
    #     type_mapping = {
    #         "选择题": ["single_choice"],
    #         "填空题": ["fill_blank", "cloze_group"],  # 填空题包括fill_blank和cloze_group两种类型
    #         "综合题": ["comprehensive"]
    #     }
    #     target_types = type_mapping.get(current_type_button_text, ["single_choice"])

    #     # 获取当前题型的所有答题卡按钮索引
    #     current_type_button_indices = []
    #     answer_sheet_index = 0
    #     for i, question in enumerate(self.questions):
    #         question_type = question.get('type', 'single_choice')
    #         if question_type in target_types:
    #             if question_type == "cloze_group":
    #                 items = question.get('items', [])
    #                 # 对于cloze_group类型，每个item对应一个答题卡按钮
    #                 for item_index in range(len(items)):
    #                     current_type_button_indices.append(answer_sheet_index)
    #                     answer_sheet_index += 1
    #             else:
    #                 # 其他题型，每个题目对应一个答题卡按钮
    #                 current_type_button_indices.append(answer_sheet_index)
    #                 answer_sheet_index += 1
    #         else:
    #             # 不是当前题型，跳过对应的答题卡按钮
    #             if question_type == "cloze_group":
    #                 items = question.get('items', [])
    #                 answer_sheet_index += len(items)
    #             else:
    #                 answer_sheet_index += 1

    #     # 获取当前题目的答题卡按钮索引
    #     current_answer_sheet_index = self.get_answer_sheet_index(self.current_question_index, self.current_item_index)
    #     print(f"DEBUG: update_answer_sheet - current_question_index={self.current_question_index}, current_item_index={self.current_item_index}, current_answer_sheet_index={current_answer_sheet_index}")

    #     for i, btn in enumerate(self.answer_buttons):
    #         # 只显示当前题型的题目
    #         if i not in current_type_button_indices:
    #             btn.setVisible(False)
    #             continue

    #         btn.setVisible(True)

    #         if i == current_answer_sheet_index:
    #             # 当前题目 - 变大效果
    #             btn.setChecked(True)
    #             # 检查当前题目是否已做
    #             is_answered = self.is_question_answered_by_button_index(i)
    #             if is_answered:
    #                 # 已做题目选中时 - 绿色变大
    #                 btn.setFixedSize(42, 42)  # 变大
    #                 btn.setStyleSheet("""
    #                     QPushButton {
    #                         background-color: #28a745;
    #                         color: white;
    #                         border: 2px solid #28a745;
    #                         border-radius: 21px;
    #                         font-weight: bold;
    #                         font-size: 15px;
    #                     }
    #                     QPushButton:hover {
    #                         background-color: #218838;
    #                         border-color: #1e7e34;
    #                     }
    #                 """)
    #             else:
    #                 # 未做题目选中时 - 白底变大
    #                 btn.setFixedSize(42, 42)  # 变大
    #                 btn.setStyleSheet("""
    #                     QPushButton {
    #                         background-color: white;
    #                         color: #495057;
    #                         border: 2px solid #007bff;
    #                         border-radius: 21px;
    #                         font-weight: bold;
    #                         font-size: 15px;
    #                     }
    #                     QPushButton:hover {
    #                         background-color: #f8f9fa;
    #                         border-color: #0069d9;
    #                     }
    #                 """)
    #         elif self.is_question_answered_by_button_index(i):
    #             # 已做题目 - 绿色（正常大小）
    #             btn.setChecked(False)
    #             btn.setFixedSize(36, 36)  # 恢复正常大小
    #             btn.setStyleSheet("""
    #                 QPushButton {
    #                     background-color: #28a745;
    #                     color: white;
    #                     border: 2px solid #28a745;
    #                     border-radius: 18px;
    #                     font-weight: bold;
    #                     font-size: 14px;
    #                 }
    #                 QPushButton:hover {
    #                     background-color: #218838;
    #                     border-color: #1e7e34;
    #                 }
    #             """)
    #         else:
    #             # 未做题目 - 白底默认（正常大小）
    #             btn.setChecked(False)
    #             btn.setFixedSize(36, 36)  # 恢复正常大小
    #             btn.setStyleSheet("""
    #                 QPushButton {
    #                     background-color: white;
    #                     color: #495057;
    #                     border: 2px solid #dee2e6;
    #                     border-radius: 18px;
    #                     font-weight: bold;
    #                     font-size: 14px;
    #                 }
    #                 QPushButton:hover {
    #                     background-color: #f8f9fa;
    #                     border-color: #adb5bd;
    #                 }
    #             """)
    # def update_answer_sheet(self):
    #     """
    #     更新答题卡按钮状态 (修复V5版)
    #     """
    #     if not self.questions:
    #         return

    #     # --- 1. 计算目标按钮索引 ---
    #     target_absolute_index = 0
        
    #     # 核心逻辑：只累加【当前题号之前】的题目
    #     # range(47) 生成 0..46，绝不会包含 47，所以绝对不会把当前题的长度加进去
    #     for i in range(self.current_question_index):
    #         q = self.questions[i]
    #         q_type = q.get('type', 'single_choice')
            
    #         if q_type == "cloze_group":
    #             target_absolute_index += len(q.get('items', []))
    #         else:
    #             target_absolute_index += 1
        
    #     # 加上当前的内部偏移 (第1空为0，第2空为1)
    #     current_offset = getattr(self, 'current_item_index', 0)
    #     target_absolute_index += current_offset

    #     # ★★★ 唯一特征码：请检查控制台是否有这一行输出 ★★★
    #     print(f"DEBUG【修复V5】: Q_Index={self.current_question_index}, Offset={current_offset} -> 目标按钮={target_absolute_index} (Label {target_absolute_index+1})")

    #     # --- 2. 刷新按钮 ---
    #     # 筛选逻辑
    #     current_type_btn = self.current_type_button.text() if self.current_type_button else "选择题"
    #     type_map = {
    #         "选择题": ["single_choice"], 
    #         "填空题": ["fill_blank", "cloze_group"], 
    #         "综合题": ["comprehensive"]
    #     }
    #     target_types = type_map.get(current_type_btn, ["single_choice"])

    #     btn_cursor = 0
    #     for q in self.questions:
    #         q_type = q.get('type', 'single_choice')
    #         count = len(q.get('items', [])) if q_type == "cloze_group" else 1
    #         is_visible = q_type in target_types
            
    #         for _ in range(count):
    #             if btn_cursor < len(self.answer_buttons):
    #                 btn = self.answer_buttons[btn_cursor]
    #                 btn.setVisible(is_visible)
                    
    #                 # 强制重置样式，防止状态残留
    #                 btn.setChecked(False)
                    
    #                 if btn_cursor == target_absolute_index:
    #                     # 命中：高亮
    #                     btn.setChecked(True)
    #                     if self.is_question_answered_by_button_index(btn_cursor):
    #                         # 绿色大圈
    #                         btn.setFixedSize(42, 42)
    #                         btn.setStyleSheet("QPushButton { background-color: #28a745; color: white; border: 2px solid #28a745; border-radius: 21px; font-weight: bold; font-size: 15px; }")
    #                     else:
    #                         # 白底大圈
    #                         btn.setFixedSize(42, 42)
    #                         btn.setStyleSheet("QPushButton { background-color: white; color: #495057; border: 2px solid #007bff; border-radius: 21px; font-weight: bold; font-size: 15px; }")
    #                 else:
    #                     # 未命中：普通
    #                     btn.setFixedSize(36, 36)
    #                     if self.is_question_answered_by_button_index(btn_cursor):
    #                         # 绿色小圈
    #                         btn.setStyleSheet("QPushButton { background-color: #28a745; color: white; border: 2px solid #28a745; border-radius: 18px; font-weight: bold; font-size: 14px; }")
    #                     else:
    #                         # 白底小圈
    #                         btn.setStyleSheet("QPushButton { background-color: white; color: #495057; border: 2px solid #dee2e6; border-radius: 18px; font-weight: bold; font-size: 14px; } QPushButton:hover { background-color: #f8f9fa; border-color: #adb5bd; }")
                
    #             btn_cursor += 1
    


    def update_navigation_buttons(self):
        """更新导航按钮状态"""
        # 上一题按钮
        has_prev = self.current_question_index > 0
        self.bottom_prev_btn.setEnabled(has_prev)

        # 下一题按钮
        has_next = self.current_question_index < len(self.questions) - 1
        self.bottom_next_btn.setEnabled(has_next)

    def update_type_buttons(self, question_type):
        """更新题型按钮状态（仅用于显示当前题目的题型）"""
        # 根据题目类型找到对应的按钮文本
        type_mapping = {
            "single_choice": "选择题",
            "fill_blank": "填空题",
            "cloze_group": "填空题",  # cloze_group也属于填空题
            "comprehensive": "综合题"
        }

        type_name = type_mapping.get(question_type, "选择题")

        # 基础样式和选中样式（使用实例变量）
        base_style = self.type_button_base_style
        selected_style = self.type_button_selected_style

        # 更新按钮样式
        for name, btn in self.type_buttons.items():
            if name == type_name:
                btn.setStyleSheet(selected_style)
                self.current_type_button = btn
            else:
                btn.setStyleSheet(base_style)

    def save_current_answer(self):
        """保存当前题目的答案"""
        if self.current_question_index >= len(self.questions):
            return

        question = self.questions[self.current_question_index]
        question_id = question.get('id', f'q_{self.current_question_index+1}')
        question_type = question.get('type', 'single_choice')

        user_answer = []

        if question_type == "single_choice":
            # 单选题：获取选中的单选按钮
            checked_button = self.options_group.checkedButton()
            if checked_button:
                # 获取按钮索引
                button_id = self.options_group.id(checked_button)
                # 获取对应的完整选项文本（如 "C.资源"）
                options = self.questions[self.current_question_index].get('options', [])
                if 0 <= button_id < len(options):
                    user_answer.append(options[button_id])
                else:
                    # 如果索引无效，使用显示文本
                    answer_text = checked_button.text().split(". ", 1)[1]
                    user_answer.append(answer_text)

        elif question_type == "fill_blank":
            # 填空题：获取输入框内容（支持多空题目）
            for i in range(self.options_layout.count()):
                widget = self.options_layout.itemAt(i).widget()

                if isinstance(widget, QLineEdit):
                    # 单空填空题：直接获取QLineEdit内容
                    answer_text = widget.text().strip()
                    if answer_text:
                        user_answer.append(answer_text)
                elif isinstance(widget, QWidget):
                    # 多空填空题：QWidget容器中包含QLabel和QLineEdit
                    # 遍历容器中的子部件，找到QLineEdit
                    container_layout = widget.layout()
                    if container_layout:
                        for j in range(container_layout.count()):
                            child_widget = container_layout.itemAt(j).widget()
                            if isinstance(child_widget, QLineEdit):
                                answer_text = child_widget.text().strip()
                                if answer_text:
                                    user_answer.append(answer_text)
                                else:
                                    # 对于多空填空题，即使为空也添加空字符串以保持顺序
                                    user_answer.append("")

        elif question_type == "comprehensive":
            # 综合题：获取所有输入框内容（类似cloze_group）
            items = question.get('items', [])
            item_count = len(items)

            # 初始化答案列表，长度与items相同
            user_answer = [''] * item_count

            # 遍历所有输入框容器
            # 注意：第一个widget是题干标签，所以从1开始
            container_index = 0
            for i in range(1, self.options_layout.count()):  # 跳过题干标签
                widget = self.options_layout.itemAt(i).widget()
                if isinstance(widget, QWidget):
                    container_layout = widget.layout()
                    if container_layout:
                        # 查找容器中的QLineEdit
                        for j in range(container_layout.count()):
                            child_widget = container_layout.itemAt(j).widget()
                            if isinstance(child_widget, QLineEdit):
                                answer_text = child_widget.text().strip()
                                if container_index < item_count:
                                    user_answer[container_index] = answer_text
                                    container_index += 1

        elif question_type == "cloze_group":
            # 完形填空组：获取所有输入框内容
            items = question.get('items', [])
            item_count = len(items)

            # 初始化答案列表，长度与items相同
            user_answer = [''] * item_count

            # 遍历所有输入框容器
            # 注意：第一个widget是题干标签，所以从1开始
            container_index = 0
            for i in range(1, self.options_layout.count()):  # 跳过题干标签
                widget = self.options_layout.itemAt(i).widget()
                if isinstance(widget, QWidget):
                    container_layout = widget.layout()
                    if container_layout:
                        # 查找容器中的QLineEdit
                        for j in range(container_layout.count()):
                            child_widget = container_layout.itemAt(j).widget()
                            if isinstance(child_widget, QLineEdit):
                                answer_text = child_widget.text().strip()
                                if container_index < item_count:
                                    user_answer[container_index] = answer_text
                                    container_index += 1


        # 保存答案
        # 检查是否有非空答案
        has_non_empty_answer = any(answer for answer in user_answer if answer)

        if has_non_empty_answer:
            self.user_answers[question_id] = user_answer

            # 更新answered_questions
            question_type = question.get('type', 'single_choice')
            if question_type == "cloze_group":
                # 对于cloze_group类型，记录哪些item有答案
                answered_items = set()
                for i, answer in enumerate(user_answer):
                    if answer:  # 非空答案
                        answered_items.add(i)

                if answered_items:
                    self.answered_questions[self.current_question_index] = answered_items
                elif self.current_question_index in self.answered_questions:
                    # 如果所有答案都清空了，移除记录
                    del self.answered_questions[self.current_question_index]
            else:
                # 对于其他题型，记录整个题目已做
                self.answered_questions[self.current_question_index] = {0}  # 使用{0}表示整个题目已做
        elif question_id in self.user_answers:
            # 如果用户清空了答案，移除保存的记录
            del self.user_answers[question_id]
            if self.current_question_index in self.answered_questions:
                del self.answered_questions[self.current_question_index]

        # 检查答案并显示结果（如果是单选题，立即显示答案和解析）
        self.check_and_show_answer_result(question, user_answer, question_type)

        # 保存会话数据到文件
        self.save_session_data()

    def check_and_show_answer_result(self, question, user_answer, question_type):
        """检查答案并显示结果"""
        if not user_answer:
            return

        question_id = question.get('id', f'q_{self.current_question_index+1}')

        # 检查答案是否正确
        is_correct, correct_answer, item_correctness, item_earned_scores = self.question_manager.check_answer(
            question, user_answer
        )

        # 根据题型处理
        if question_type == "single_choice":
            # 单选题：立即显示答案和解析
            self.show_answer_and_analysis(question)
        elif question_type in ["cloze_group", "comprehensive"]:
            # cloze_group和综合题：检查是否所有空都已填写
            # 获取题目中的空位数量
            if question_type == "cloze_group":
                items = question.get('items', [])
                expected_answer_count = len(items)
            else:  # comprehensive
                items = question.get('items', [])
                expected_answer_count = len(items)

            # 统计用户实际填写的答案数量（非空答案）
            filled_answer_count = sum(1 for answer in user_answer if answer)

            # 如果所有空都已填写，显示答案和解析
            if filled_answer_count >= expected_answer_count:
                self.show_answer_and_analysis(question)
                self.show_correctness_labels(question_type, user_answer, item_correctness)
            else:
                # 如果还有空没填，只显示对错标签（针对已填写的空）
                self.show_correctness_labels(question_type, user_answer, item_correctness)
        else:
            # 填空题：显示对错标签
            self.show_correctness_labels(question_type, user_answer, item_correctness)

    def show_answer_and_analysis(self, question):
        """显示答案和解析"""
        # 获取正确答案
        question_type = question.get('type', 'single_choice')
        question_text = question['question']

        # 初始化变量
        answer_text = "暂无正确答案"

        if question_type == "cloze_group":
            # 完形填空组：从items中获取正确答案
            items = question.get('items', [])
            # 对于cloze_group类型，从第一个item的metadata中获取题号
            first_question_number = 1
            if items and len(items) > 0:
                first_item = items[0]
                if 'metadata' in first_item and 'question_number' in first_item['metadata']:
                    first_question_number = first_item['metadata']['question_number']
                else:
                    # 如果metadata中没有question_number，使用默认值1
                    first_question_number = 1

            answer_parts = []
            for i, item in enumerate(items):
                item_answer = item.get('answer', '')
                current_question_number = first_question_number + i
                answer_parts.append(f"{current_question_number}. {item_answer}")

            # 使用HTML换行标签实现多行显示
            answer_text = "<br>".join(answer_parts)

        elif question_type == "fill_blank":
            correct_answer = question.get('answer', [])
            # 填空题：特殊处理多空题目
            blank_count = question_text.count('______')

            if blank_count > 1:
                import re
                blank_num_match = re.findall(r'(\d+)______', question_text)

                if isinstance(correct_answer, list):
                    answer_parts = []
                    for i, ans in enumerate(correct_answer):
                        if i < len(blank_num_match):
                            # 使用题目中的编号（如47、48）
                            answer_parts.append(f"【{blank_num_match[i]}】{ans}")
                        else:
                            answer_parts.append(f"【{i+1}】{ans}")
                    # 使用HTML换行标签实现多行显示
                    answer_text = "<br>".join(answer_parts)
                else:
                    answer_text = str(correct_answer)
            else:
                # 单空填空题
                if isinstance(correct_answer, list) and len(correct_answer) > 0:
                    answer_text = correct_answer[0]
                else:
                    answer_text = str(correct_answer)
        elif question_type == "single_choice":
            # 单选题：显示完整的选项文本
            correct_answer = question.get('answer', [])
            if isinstance(correct_answer, list):
                answer_parts = []
                for ans in correct_answer:
                    # 显示完整的选项文本，如 "C.资源"
                    answer_parts.append(ans)
                answer_text = "，".join(answer_parts)
            else:
                answer_text = str(correct_answer)
        elif question_type == "comprehensive":
            # 综合题：从items中获取正确答案，使用多行显示
            items = question.get('items', [])
            answer_parts = []
            for i, item in enumerate(items):
                item_answer = item.get('answer', '')
                # 综合题通常有题号，如52、53等
                item_index = item.get('index', i + 1)
                answer_parts.append(f"{item_index}. {item_answer}")
            # 使用HTML换行标签实现多行显示
            answer_text = "<br>".join(answer_parts)
        else:
            # 其他题型
            correct_answer = question.get('answer', [])
            if isinstance(correct_answer, list):
                answer_text = "，".join(correct_answer)
            else:
                answer_text = str(correct_answer)

        # 正确答案需要智能处理HTML特殊字符
        # 保留合法的HTML标签（如<br>），转义像<Ctrl>这样的文本
        answer_text_escaped = self.smart_escape(answer_text)
        self.correct_answer_label.setText(f"正确答案：{answer_text_escaped}")

        # 解析部分不需要处理&符号，可以正常显示
        analysis_text = question.get('analysis', '暂无解析')
        self.analysis_label.setText(f"{analysis_text}")

        # 显示解析区域
        self.analysis_frame.show()

    def on_single_choice_selected(self, question, selected_option):
        """单选题选项被选中时的处理"""
        # 保存用户答案
        question_id = question.get('id', f'q_{self.current_question_index+1}')
        self.user_answers[question_id] = [selected_option]

        # 更新answered_questions
        self.answered_questions[self.current_question_index] = {0}

        # 检查答案是否正确
        user_answer = self.user_answers[question_id]
        is_correct, _, _, _ = self.question_manager.check_answer(question, user_answer)

        # 更新单选按钮颜色
        self.update_radio_button_color(question, selected_option, is_correct)

        # 立即显示答案和解析
        self.show_answer_and_analysis(question)

    def on_fill_blank_finished(self, question_id, index, input_field):
        """填空题输入框失去焦点时的处理（用户完成输入）"""
        # 获取当前题目
        if self.current_question_index >= len(self.questions):
            return

        question = self.questions[self.current_question_index]
        current_question_id = question.get('id', f'q_{self.current_question_index+1}')

        # 确保是当前题目
        if current_question_id != question_id:
            return

        # 获取输入框文本
        text = input_field.text().strip()

        # 更新用户答案
        if question_id not in self.user_answers:
            self.user_answers[question_id] = []

        # 确保答案列表足够长
        while len(self.user_answers[question_id]) <= index:
            self.user_answers[question_id].append("")

        self.user_answers[question_id][index] = text

        # 如果用户填写了答案（非空），显示答案和解析，并判断对错
        if text:
            # 显示答案和解析
            self.show_answer_and_analysis(question)

            # 检查答案是否正确
            user_answer = self.user_answers[question_id]
            is_correct, _, item_correctness, _ = self.question_manager.check_answer(question, user_answer)

            # 更新输入框颜色
            self.update_input_field_color(question_id, index, is_correct if index == 0 else (item_correctness[index] if index < len(item_correctness) else False))
        else:
            # 如果用户清空了答案，恢复默认颜色
            self.update_input_field_color(question_id, index, None)

    def on_fill_blank_changed(self, question_id, index, text):
        """填空题输入框文本变化时的处理（保留方法，可能其他地方使用）"""
        pass

    def on_cloze_text_changed(self, question_id, index, text):
        """cloze_group或综合题输入框文本变化时的处理（实时保存答案）"""
        # 获取当前题目
        if self.current_question_index >= len(self.questions):
            return

        question = self.questions[self.current_question_index]
        current_question_id = question.get('id', f'q_{self.current_question_index+1}')

        # 确保是当前题目
        if current_question_id != question_id:
            return

        # 更新用户答案
        if question_id not in self.user_answers:
            self.user_answers[question_id] = []

        # 确保答案列表足够长
        while len(self.user_answers[question_id]) <= index:
            self.user_answers[question_id].append("")

        self.user_answers[question_id][index] = text.strip()

    def on_cloze_finished(self, question_id, index, input_field):
        """cloze_group或综合题输入框失去焦点时的处理"""
        # 获取当前题目
        if self.current_question_index >= len(self.questions):
            return

        question = self.questions[self.current_question_index]
        current_question_id = question.get('id', f'q_{self.current_question_index+1}')

        # 确保是当前题目
        if current_question_id != question_id:
            return

        # 获取输入框文本
        text = input_field.text().strip()

        # 检查是否所有空都已填写
        question_type = question.get('type', 'cloze_group')
        if question_type in ["cloze_group", "comprehensive"]:
            # 获取题目中的空位数量
            if question_type == "cloze_group":
                items = question.get('items', [])
                expected_count = len(items)
            else:  # comprehensive
                items = question.get('items', [])
                expected_count = len(items)

            # 统计非空答案数量
            filled_count = sum(1 for ans in self.user_answers[question_id] if ans.strip())

            # 如果所有空都已填写，显示答案和解析并判断对错
            if filled_count >= expected_count:
                # 显示答案和解析
                self.show_answer_and_analysis(question)

                # 检查答案是否正确
                user_answer = self.user_answers[question_id]
                is_correct, _, item_correctness, _ = self.question_manager.check_answer(question, user_answer)

                # 更新所有输入框颜色（只更新已填写的空）
                for i in range(expected_count):
                    if i < len(user_answer) and user_answer[i].strip():  # 只更新已填写的空
                        is_item_correct = item_correctness[i] if i < len(item_correctness) else False
                        self.update_input_field_color(question_id, i, is_item_correct)
                    else:
                        # 未填写的空保持默认颜色
                        self.update_input_field_color(question_id, i, None)
            elif text:
                # 如果用户填写了答案但还没填完所有空，只更新当前输入框的颜色
                # 检查当前空的答案是否正确
                user_answer = self.user_answers[question_id]
                is_correct, _, item_correctness, _ = self.question_manager.check_answer(question, user_answer)

                # 只更新当前输入框的颜色
                if index < len(item_correctness):
                    is_item_correct = item_correctness[index]
                    self.update_input_field_color(question_id, index, is_item_correct)
            else:
                # 如果用户清空了答案，恢复默认颜色
                self.update_input_field_color(question_id, index, None)

    def update_input_field_color(self, question_id, index, is_correct):
        """更新输入框文字颜色
        Args:
            question_id: 题目ID
            index: 输入框索引
            is_correct: True=正确，False=错误，None=默认颜色
        """
        # 查找对应的输入框
        input_field = self.find_input_field(question_id, index)
        if not input_field:
            return

        # 设置颜色
        if is_correct is None:
            # 默认颜色
            input_field.setStyleSheet("""
                QLineEdit {
                    font-size: 18px;
                    font-family: "Microsoft YaHei";
                    padding: 12px;
                    border: 1px solid #dee2e6;
                    border-radius: 5px;
                    min-height: 35px;
                    color: #212529;
                }
                QLineEdit:focus {
                    border-color: #007bff;
                }
            """)
        elif is_correct:
            # 正确 - 绿色
            input_field.setStyleSheet("""
                QLineEdit {
                    font-size: 18px;
                    font-family: "Microsoft YaHei";
                    padding: 12px;
                    border: 2px solid #28a745;
                    border-radius: 5px;
                    min-height: 35px;
                    color: #28a745;
                    font-weight: bold;
                }
                QLineEdit:focus {
                    border-color: #218838;
                }
            """)
        else:
            # 错误 - 红色
            input_field.setStyleSheet("""
                QLineEdit {
                    font-size: 18px;
                    font-family: "Microsoft YaHei";
                    padding: 12px;
                    border: 2px solid #dc3545;
                    border-radius: 5px;
                    min-height: 35px;
                    color: #dc3545;
                    font-weight: bold;
                }
                QLineEdit:focus {
                    border-color: #c82333;
                }
            """)

    def find_input_field(self, question_id, index):
        """查找指定题目和索引的输入框"""
        # 遍历所有输入框
        input_index = 0
        for i in range(self.options_layout.count()):
            widget = self.options_layout.itemAt(i).widget()

            if isinstance(widget, QLineEdit):
                # 直接输入框
                if input_index == index:
                    return widget
                input_index += 1
            elif isinstance(widget, QWidget):
                # 容器中的输入框
                container_layout = widget.layout()
                if container_layout:
                    for j in range(container_layout.count()):
                        child_widget = container_layout.itemAt(j).widget()
                        if isinstance(child_widget, QLineEdit):
                            if input_index == index:
                                return child_widget
                            input_index += 1

        return None

    def update_radio_button_color(self, question, selected_option, is_correct):
        """更新单选按钮颜色
        Args:
            question: 题目数据
            selected_option: 用户选择的选项
            is_correct: 是否正确
        """
        # 查找对应的单选按钮
        options = question.get('options', [])
        for i, option in enumerate(options):
            if option == selected_option:
                # 找到对应的单选按钮
                radio_button = self.options_group.button(i)
                if radio_button:
                    if is_correct:
                        # 正确 - 绿色
                        radio_button.setStyleSheet("""
                            QRadioButton {
                                font-size: 18px;
                                font-family: "Microsoft YaHei";
                                padding: 12px;
                                border-radius: 5px;
                                min-height: 35px;
                                color: #28a745;
                                font-weight: bold;
                            }
                            QRadioButton:hover {
                                background-color: #f8f9fa;
                            }
                        """)
                    else:
                        # 错误 - 红色
                        radio_button.setStyleSheet("""
                            QRadioButton {
                                font-size: 18px;
                                font-family: "Microsoft YaHei";
                                padding: 12px;
                                border-radius: 5px;
                                min-height: 35px;
                                color: #dc3545;
                                font-weight: bold;
                            }
                            QRadioButton:hover {
                                background-color: #f8f9fa;
                            }
                        """)
                break

    def show_correctness_labels(self, question_type, user_answer, item_correctness):
        """在输入框右边显示正确/错误标签"""
        print(f"=== 判题结果 ===")
        print(f"题型: {question_type}")
        print(f"用户答案: {user_answer}")
        print(f"正确性: {item_correctness}")

        # 先清除所有现有的正确/错误标签
        self.clear_correctness_labels()

        # 遍历所有输入框，添加正确/错误标签
        input_index = 0
        for i in range(self.options_layout.count()):
            widget = self.options_layout.itemAt(i).widget()

            if isinstance(widget, QLineEdit):
                # 单空填空题的直接输入框
                if input_index < len(user_answer) and input_index < len(item_correctness):
                    answer = user_answer[input_index]
                    is_correct = item_correctness[input_index]
                    if answer:  # 有答案才显示
                        self.add_correctness_label_to_widget(widget, is_correct)
                    input_index += 1
            elif isinstance(widget, QWidget):
                # 容器中的输入框（多空填空题、cloze_group、综合题）
                container_layout = widget.layout()
                if container_layout:
                    for j in range(container_layout.count()):
                        child_widget = container_layout.itemAt(j).widget()
                        if isinstance(child_widget, QLineEdit):
                            if input_index < len(user_answer) and input_index < len(item_correctness):
                                answer = user_answer[input_index]
                                is_correct = item_correctness[input_index]
                                if answer:  # 有答案才显示
                                    self.add_correctness_label_to_container(container_layout, j, is_correct)
                                input_index += 1

    def clear_correctness_labels(self):
        """清除所有正确/错误标签"""
        # 遍历所有容器，移除正确/错误标签
        for i in range(self.options_layout.count()):
            widget = self.options_layout.itemAt(i).widget()

            if isinstance(widget, QWidget):
                container_layout = widget.layout()
                if container_layout:
                    # 从后往前遍历，避免索引变化
                    for j in range(container_layout.count() - 1, -1, -1):
                        child_widget = container_layout.itemAt(j).widget()
                        if isinstance(child_widget, QLabel):
                            # 检查是否是正确/错误标签
                            text = child_widget.text()
                            if text in ["正确", "错误"]:
                                child_widget.deleteLater()
                                container_layout.removeWidget(child_widget)

    def add_correctness_label_to_widget(self, widget, is_correct):
        """为单个输入框添加正确/错误标签"""
        # 由于QLineEdit是直接添加到options_layout的，我们需要修改布局
        # 暂时在控制台显示
        status = "正确" if is_correct else "错误"
        color = "绿色" if is_correct else "红色"
        print(f"  输入框: {status} ({color})")

    def add_correctness_label_to_container(self, container_layout, input_index, is_correct):
        """为容器中的输入框添加正确/错误标签"""
        # 在输入框后面添加一个标签
        status_label = QLabel("正确" if is_correct else "错误")
        if is_correct:
            status_label.setStyleSheet("""
                QLabel {
                    color: #28a745;
                    font-size: 16px;
                    font-weight: bold;
                    font-family: "Microsoft YaHei";
                    margin-left: 10px;
                }
            """)
        else:
            status_label.setStyleSheet("""
                QLabel {
                    color: #dc3545;
                    font-size: 16px;
                    font-weight: bold;
                    font-family: "Microsoft YaHei";
                    margin-left: 10px;
                }
            """)

        # 在输入框后面插入标签
        container_layout.insertWidget(input_index + 1, status_label)

    def prev_question(self):
        """上一题"""
        if self.current_question_index > 0:
            self.save_current_answer()
            # 跳转到上一题
            self.show_question(self.current_question_index - 1, 0)
       

    def next_question(self):
        """下一题"""
        if self.current_question_index < len(self.questions) - 1:
            self.save_current_answer()
            # 跳转到下一题
            self.show_question(self.current_question_index + 1, 0)
        





       

    def on_type_changed(self):
        """题型切换事件"""
        # 获取被点击的按钮
        clicked_button = self.sender()
        if not clicked_button:
            return

        # 如果点击的是当前已选中的按钮，直接返回
        if clicked_button == self.current_type_button:
            return

        # 基础样式和选中样式（使用实例变量）
        base_style = self.type_button_base_style
        selected_style = self.type_button_selected_style

        # 将当前选中的按钮恢复为基础样式
        if self.current_type_button:
            self.current_type_button.setStyleSheet(base_style)

        # 设置新选中的按钮样式
        clicked_button.setStyleSheet(selected_style)
        self.current_type_button = clicked_button

        # 根据按钮文本找到对应的题型
        clicked_button_text = clicked_button.text()
        type_mapping = {
            "选择题": "single_choice",
            "填空题": ["fill_blank", "cloze_group"],  # 填空题包括fill_blank和cloze_group两种类型
            "综合题": "comprehensive"
        }
        target_types = type_mapping.get(clicked_button_text, ["single_choice"])
        # 如果是字符串类型，转换为列表
        if isinstance(target_types, str):
            target_types = [target_types]

        # 找到该题型的第一个题目
        target_index = -1
        for i, question in enumerate(self.questions):
            if question.get('type') in target_types:
                target_index = i
                break

        # 如果找到该题型的题目，跳转到第一题
        if target_index >= 0:
            self.save_current_answer()
            self.show_question(target_index, 0)
        else:
            # 如果没有该题型的题目，恢复原来的选中状态
            # 获取当前题目的题型
            current_question = self.questions[self.current_question_index] if self.questions else None
            current_type = current_question.get('type', 'single_choice') if current_question else 'single_choice'
            self.update_type_buttons(current_type)

    def toggle_analysis(self, checked):
        """显示/隐藏解析"""
        self.analysis_frame.setVisible(checked)
        self.toggle_analysis_btn.setText("📖 隐藏解析" if checked else "📖 显示解析")

    def submit_exam(self):
        """交卷"""
        self.save_current_answer()

        if not self.question_manager:
            QMessageBox.warning(self, "错误", "试题管理器不可用")
            return

        # 计算成绩
        total_score = 0
        obtained_score = 0
        correct_count = 0
        # 初始化总题数：对于cloze_group类型，每个item算作一道题
        total_count = 0
        for question in self.questions:
            question_type = question.get('type', 'single_choice')
            if question_type == "cloze_group":
                items = question.get('items', [])
                total_count += len(items)
            else:
                total_count += 1

        # 生成会话ID（在循环之前）
        import time
        session_id = f"session_{int(time.time())}"

        for question in self.questions:
            question_id = question.get('id')
            user_answer = self.user_answers.get(question_id, [])

            # 只记录用户实际做了的题目（user_answer不为空）
            if user_answer:
                # 检查答案
                is_correct, _, item_correctness, item_earned_scores = self.question_manager.check_answer(question, user_answer)

                # 记录用户进度
                if self.progress_manager:
                    question_type = question.get('type', 'single_choice')
                    if question_type == "cloze_group":
                        # 对于cloze_group类型，为每个item记录独立的答题结果
                        items = question.get('items', [])
                        for i, item in enumerate(items):
                            item_id = f"{question_id}_item{i+1}"
                            item_is_correct = item_correctness[i] if i < len(item_correctness) else False
                            # 只记录用户实际做了的item
                            if i < len(user_answer) and user_answer[i]:
                                self.progress_manager.record_answer(
                                    exam_id=self.exam_id,
                                    question_id=item_id,
                                    is_correct=item_is_correct,
                                    user_answer=[user_answer[i]] if i < len(user_answer) else [],
                                    session_id=session_id
                                )
                    else:
                        # 对于其他题型，记录整个题目的答题结果
                        self.progress_manager.record_answer(
                            exam_id=self.exam_id,
                            question_id=question_id,
                            is_correct=is_correct,
                            user_answer=user_answer,
                            session_id=session_id  # 传递会话ID
                        )

                # 获取题目分值
                question_type = question.get('type', 'single_choice')
                if question_type == "cloze_group":
                    # 对于cloze_group类型，从items中获取每个item的分值
                    items = question.get('items', [])
                    item_scores = []
                    for item in items:
                        item_score = item.get('score', 1)
                        item_scores.append(item_score)

                    # 使用item_scores的总和作为题目分值
                    question_score = sum(item_scores) if item_scores else 0
                    # 对于cloze_group类型，使用实际得分而不是整体判断
                    earned_score = sum(item_earned_scores) if item_earned_scores else 0
                    total_score += question_score
                    obtained_score += earned_score

                    # 对于cloze_group类型，基于item_correctness计算正确的item数量
                    if item_correctness:
                        correct_items = sum(1 for is_correct in item_correctness if is_correct)
                        correct_count += correct_items
                else:
                    question_score = question.get('score', 5)
                    total_score += question_score
                    if is_correct:
                        correct_count += 1
                        obtained_score += question_score
            else:
                # 用户没有做这道题，不计入统计
                question_type = question.get('type', 'single_choice')
                if question_type == "cloze_group":
                    items = question.get('items', [])
                    total_count -= len(items)  # 减少对应的item数量
                else:
                    total_count -= 1  # 减少总题数统计

        # 计算正确率
        accuracy = (correct_count / total_count * 100) if total_count > 0 else 0

        # 记录交卷会话的正确率
        if self.progress_manager:
            # 记录交卷正确率（使用前面生成的session_id）
            self.progress_manager.record_exam_session(
                exam_id=self.exam_id,
                accuracy=accuracy,
                session_id=session_id
            )

        # 显示成绩（使用原来的简单弹窗）
        result_text = f"""
        <h3>试卷完成!</h3>
        <p><b>总题数:</b> {total_count}</p>
        <p><b>正确数:</b> {correct_count}</p>
        <p><b>得分:</b> {obtained_score}/{total_score}</p>
        <p><b>正确率:</b> {accuracy:.1f}%</p>
        """
        QMessageBox.information(self, "试卷完成", result_text)

        # 交卷后删除sessions目录中的所有文件
        self.delete_all_sessions()


    def timeout_submit(self):
        """时间到自动交卷"""
        print("考试时间到，自动交卷")
        self.submit_exam()

    def back_to_list(self):
        """返回试卷列表"""
        # 保存当前答案
        self.save_current_answer()
        # 保存会话数据
        self.save_session_data()
        # 发出返回信号
        self.back_to_list_requested.emit()

    def closeEvent(self, event):
        """窗口关闭事件"""
        # 保存当前答案
        self.save_current_answer()
        # 保存会话数据
        self.save_session_data()
        print(f"窗口关闭，会话数据已保存: {self.session_file}")
        event.accept()

    def show_progress_dialog(self):
        """显示答题进度弹窗"""
        if not self.questions:
            QMessageBox.warning(self, "提示", "暂无题目数据")
            return

        # 创建并显示进度弹窗
        dialog = ProgressDialog(self.questions, self.user_answers, self)
        # 连接信号，当用户点击题号时跳转到对应题目
        dialog.question_clicked.connect(self.on_progress_question_clicked)
        dialog.exec_()

    def on_progress_question_clicked(self, question_index, item_index):
        """处理进度弹窗中的题目点击事件"""
        # 跳转到对应题目
        self.show_question(question_index, item_index)
        # 更新进度管理器中的题目总数（确保与当前统计一致）
        self.update_exam_total_questions()
        # 可以添加一些视觉反馈，比如滚动到对应位置
        print(f"跳转到题目 {question_index}, item_index: {item_index}")

    def resizeEvent(self, event):
        """窗口大小改变事件"""
        super().resizeEvent(event)
        # 这里不再动态设置最小宽度，避免递归调整
        # 左右区域的比例已经在布局中通过拉伸因子设置