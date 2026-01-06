#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主窗口界面
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QTabWidget, QGroupBox,
                             QRadioButton, QCheckBox, QLineEdit, QTextEdit,
                             QMessageBox, QListWidget, QListWidgetItem,
                             QSplitter, QProgressBar, QComboBox, QSpinBox,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QDialog, QFormLayout, QDialogButtonBox)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor
import random
from datetime import datetime
import sys
import os

# 添加core模块到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from core.paper_manager import PaperManager
    PAPER_MANAGER_AVAILABLE = True
except ImportError:
    PAPER_MANAGER_AVAILABLE = False
    print("警告: 试卷模块不可用")

class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self, question_bank):
        super().__init__()
        self.question_bank = question_bank
        self.current_questions = []
        self.current_question_index = 0
        self.user_answers = {}  # 保存用户答案
        self.test_start_time = None

        # 初始化试卷管理器
        if PAPER_MANAGER_AVAILABLE:
            self.paper_manager = PaperManager()
        else:
            self.paper_manager = None

        # 倒计时相关变量
        self.paper_time_limit = 0  # 试卷时间限制（分钟）
        self.paper_time_remaining = 0  # 剩余时间（秒）
        self.paper_timer = None  # 倒计时定时器

        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("极智题典 - 已激活")
        self.setGeometry(100, 100, 1200, 800)

        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)

        # 顶部状态栏
        status_layout = QHBoxLayout()
        self.status_label = QLabel("就绪")
        self.progress_label = QLabel("进度: 0/0")
        self.time_label = QLabel("时间: 00:00")

        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.progress_label)
        status_layout.addWidget(self.time_label)

        main_layout.addLayout(status_layout)

        # 创建标签页
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # 创建各个标签页
        self.create_practice_tab()
        self.create_test_tab()
        if PAPER_MANAGER_AVAILABLE:
            self.create_paper_tab()
        self.create_review_tab()
        self.create_stats_tab()
        self.create_settings_tab()

        # 初始化定时器更新时间
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # 每秒更新一次

    def create_practice_tab(self):
        """创建练习标签页"""
        practice_widget = QWidget()
        layout = QVBoxLayout(practice_widget)

        # 练习设置
        settings_group = QGroupBox("练习设置")
        settings_layout = QHBoxLayout()

        # 分类选择
        settings_layout.addWidget(QLabel("分类:"))
        self.category_combo = QComboBox()
        self.category_combo.addItem("全部")
        self.category_combo.addItems(self.question_bank.get_categories())
        settings_layout.addWidget(self.category_combo)


        # 题目数量
        settings_layout.addWidget(QLabel("题目数量:"))
        self.question_count_spin = QSpinBox()
        self.question_count_spin.setRange(1, 100)
        self.question_count_spin.setValue(10)
        settings_layout.addWidget(self.question_count_spin)

        # 开始练习按钮
        self.start_practice_btn = QPushButton("开始练习")
        self.start_practice_btn.clicked.connect(self.start_practice)
        settings_layout.addWidget(self.start_practice_btn)

        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        # 题目显示区域
        self.question_display = QTextEdit()
        self.question_display.setReadOnly(True)
        self.question_display.setMinimumHeight(200)
        layout.addWidget(self.question_display)

        # 答案选项区域
        self.answer_widget = QWidget()
        self.answer_layout = QVBoxLayout(self.answer_widget)
        layout.addWidget(self.answer_widget)

        # 导航按钮
        nav_layout = QHBoxLayout()
        self.prev_btn = QPushButton("上一题")
        self.prev_btn.clicked.connect(self.prev_question)
        self.prev_btn.setEnabled(False)

        self.next_btn = QPushButton("下一题")
        self.next_btn.clicked.connect(self.next_question)
        self.next_btn.setEnabled(False)

        self.submit_btn = QPushButton("提交答案")
        self.submit_btn.clicked.connect(self.submit_answer)
        self.submit_btn.setEnabled(False)

        nav_layout.addWidget(self.prev_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(self.submit_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(self.next_btn)

        layout.addLayout(nav_layout)

        # 结果显示
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        self.result_display.setMaximumHeight(100)
        layout.addWidget(self.result_display)

        self.tab_widget.addTab(practice_widget, "练习模式")

    def create_test_tab(self):
        """创建测试标签页"""
        test_widget = QWidget()
        layout = QVBoxLayout(test_widget)

        # 测试设置
        test_settings = QGroupBox("测试设置")
        test_settings_layout = QHBoxLayout()

        test_settings_layout.addWidget(QLabel("测试时长(分钟):"))
        self.test_duration_spin = QSpinBox()
        self.test_duration_spin.setRange(10, 180)
        self.test_duration_spin.setValue(60)
        test_settings_layout.addWidget(self.test_duration_spin)

        test_settings_layout.addWidget(QLabel("题目数量:"))
        self.test_count_spin = QSpinBox()
        self.test_count_spin.setRange(10, 200)
        self.test_count_spin.setValue(50)
        test_settings_layout.addWidget(self.test_count_spin)

        self.start_test_btn = QPushButton("开始测试")
        self.start_test_btn.clicked.connect(self.start_test)
        test_settings_layout.addWidget(self.start_test_btn)

        test_settings.setLayout(test_settings_layout)
        layout.addWidget(test_settings)

        # 测试进度
        self.test_progress = QProgressBar()
        layout.addWidget(self.test_progress)

        # 测试题目显示
        self.test_question_display = QTextEdit()
        self.test_question_display.setReadOnly(True)
        layout.addWidget(self.test_question_display)

        # 测试答案选项
        self.test_answer_widget = QWidget()
        self.test_answer_layout = QVBoxLayout(self.test_answer_widget)
        layout.addWidget(self.test_answer_widget)

        # 测试控制按钮
        test_control_layout = QHBoxLayout()
        self.test_prev_btn = QPushButton("上一题")
        self.test_prev_btn.clicked.connect(self.test_prev_question)
        self.test_prev_btn.setEnabled(False)

        self.test_next_btn = QPushButton("下一题")
        self.test_next_btn.clicked.connect(self.test_next_question)
        self.test_next_btn.setEnabled(False)

        self.finish_test_btn = QPushButton("结束测试")
        self.finish_test_btn.clicked.connect(self.finish_test)
        self.finish_test_btn.setEnabled(False)

        test_control_layout.addWidget(self.test_prev_btn)
        test_control_layout.addStretch()
        test_control_layout.addWidget(self.finish_test_btn)
        test_control_layout.addStretch()
        test_control_layout.addWidget(self.test_next_btn)

        layout.addLayout(test_control_layout)

        self.tab_widget.addTab(test_widget, "测试模式")

    def create_paper_tab(self):
        """创建试卷模式标签页"""
        paper_widget = QWidget()
        layout = QVBoxLayout(paper_widget)

        # 试卷选择
        paper_group = QGroupBox("试卷选择")
        paper_layout = QVBoxLayout()

        # 试卷列表
        self.paper_list = QListWidget()
        self.load_paper_list()
        self.paper_list.itemClicked.connect(self.on_paper_selected)
        paper_layout.addWidget(self.paper_list)

        # 刷新按钮
        refresh_btn = QPushButton("刷新试卷列表")
        refresh_btn.clicked.connect(self.load_paper_list)
        paper_layout.addWidget(refresh_btn)

        paper_group.setLayout(paper_layout)
        layout.addWidget(paper_group)

        # 试卷信息
        self.paper_info_display = QTextEdit()
        self.paper_info_display.setReadOnly(True)
        self.paper_info_display.setMaximumHeight(150)
        layout.addWidget(self.paper_info_display)

        # 开始做题按钮
        self.start_paper_btn = QPushButton("开始做这套试卷")
        self.start_paper_btn.clicked.connect(self.start_paper)
        self.start_paper_btn.setEnabled(False)
        layout.addWidget(self.start_paper_btn)

        # 试卷做题界面（初始隐藏）
        self.paper_question_widget = QWidget()
        self.paper_question_layout = QVBoxLayout(self.paper_question_widget)

        # 题目显示
        self.paper_question_display = QTextEdit()
        self.paper_question_display.setReadOnly(True)
        self.paper_question_layout.addWidget(self.paper_question_display)

        # 答案选项
        self.paper_answer_widget = QWidget()
        self.paper_answer_layout = QVBoxLayout(self.paper_answer_widget)
        self.paper_question_layout.addWidget(self.paper_answer_widget)

        # 导航按钮
        paper_nav_layout = QHBoxLayout()
        self.paper_prev_btn = QPushButton("上一题")
        self.paper_prev_btn.clicked.connect(self.paper_prev_question)
        self.paper_prev_btn.setEnabled(False)

        self.paper_next_btn = QPushButton("下一题")
        self.paper_next_btn.clicked.connect(self.paper_next_question)
        self.paper_next_btn.setEnabled(False)

        self.finish_paper_btn = QPushButton("交卷")
        self.finish_paper_btn.clicked.connect(self.finish_paper)
        self.finish_paper_btn.setEnabled(False)

        paper_nav_layout.addWidget(self.paper_prev_btn)
        paper_nav_layout.addStretch()
        paper_nav_layout.addWidget(self.finish_paper_btn)
        paper_nav_layout.addStretch()
        paper_nav_layout.addWidget(self.paper_next_btn)

        self.paper_question_layout.addLayout(paper_nav_layout)

        # 进度显示
        self.paper_progress = QProgressBar()
        self.paper_question_layout.addWidget(self.paper_progress)

        # 初始隐藏做题界面
        self.paper_question_widget.setVisible(False)
        layout.addWidget(self.paper_question_widget)

        self.tab_widget.addTab(paper_widget, "试卷模式")

    def create_review_tab(self):
        """创建复习标签页"""
        review_widget = QWidget()
        layout = QVBoxLayout(review_widget)

        # 错题列表
        self.wrong_questions_list = QListWidget()
        self.wrong_questions_list.itemClicked.connect(self.show_wrong_question)
        layout.addWidget(self.wrong_questions_list)

        # 错题详情
        self.wrong_question_display = QTextEdit()
        self.wrong_question_display.setReadOnly(True)
        layout.addWidget(self.wrong_question_display)

        # 刷新按钮
        refresh_btn = QPushButton("刷新错题本")
        refresh_btn.clicked.connect(self.refresh_wrong_questions)
        layout.addWidget(refresh_btn)

        self.tab_widget.addTab(review_widget, "错题复习")

    def create_stats_tab(self):
        """创建统计标签页"""
        stats_widget = QWidget()
        layout = QVBoxLayout(stats_widget)

        # 总体统计
        overall_stats = self.question_bank.get_overall_stats()
        stats_text = f"""
        <h3>学习统计</h3>
        <p>总答题数: {overall_stats['total_questions']}</p>
        <p>正确数: {overall_stats['total_correct']}</p>
        <p>正确率: {overall_stats['accuracy']}%</p>
        <p>学习天数: {overall_stats['days_studied']}</p>
        """

        stats_label = QLabel(stats_text)
        stats_label.setTextFormat(Qt.RichText)
        layout.addWidget(stats_label)

        # 详细统计表格
        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(4)
        self.stats_table.setHorizontalHeaderLabels(["日期", "答题数", "正确数", "正确率"])
        self.stats_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 加载统计数据
        self.load_stats_data()
        layout.addWidget(self.stats_table)

        self.tab_widget.addTab(stats_widget, "学习统计")

    def create_settings_tab(self):
        """创建设置标签页"""
        settings_widget = QWidget()
        layout = QVBoxLayout(settings_widget)

        # 激活信息
        activation_group = QGroupBox("激活信息")
        activation_layout = QFormLayout()

        from PyQt5.QtCore import QSettings
        settings = QSettings("TikuSoft", "TikuQuestionBank")

        activation_code = settings.value("activation_code", "未激活")
        activation_date = settings.value("activation_date", "未知")
        device_id = settings.value("device_id", "未知")

        activation_layout.addRow("激活码:", QLabel(activation_code))
        activation_layout.addRow("激活日期:", QLabel(activation_date))
        activation_layout.addRow("设备ID:", QLabel(device_id[:16] + "..."))

        activation_group.setLayout(activation_layout)
        layout.addWidget(activation_group)

        # 软件信息
        info_group = QGroupBox("软件信息")
        info_layout = QFormLayout()

        info_layout.addRow("版本:", QLabel("1.0.0"))
        info_layout.addRow("题目总数:", QLabel(str(self.question_bank.get_question_count())))
        info_layout.addRow("分类数量:", QLabel(str(len(self.question_bank.get_categories()))))

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        layout.addStretch()

        self.tab_widget.addTab(settings_widget, "设置")

    def start_practice(self):
        """开始练习"""
        # 获取设置
        category = self.category_combo.currentText()
        count = self.question_count_spin.value()

        # 获取题目
        if category == "全部":
            category = None

        self.current_questions = self.question_bank.get_random_questions(
            count, category
        )

        if not self.current_questions:
            QMessageBox.warning(self, "提示", "没有找到符合条件的题目！")
            return

        # 重置状态
        self.current_question_index = 0
        self.user_answers = {}
        self.result_display.clear()

        # 启用按钮
        self.prev_btn.setEnabled(False)
        self.next_btn.setEnabled(len(self.current_questions) > 1)
        self.submit_btn.setEnabled(True)

        # 显示第一题
        self.show_question()

        self.status_label.setText("练习模式 - 进行中")
        self.update_progress()

    def show_question(self):
        """显示当前题目"""
        if not self.current_questions:
            return

        question = self.current_questions[self.current_question_index]

        # 显示题目
        question_text = f"""
        <h3>第 {self.current_question_index + 1} 题</h3>
        <p><b>分类:</b> {question.get('category', '未知')}</p>
        <p><b>题型:</b> {self.get_question_type_name(question.get('type'))}</p>
        <hr>
        <p>{question.get('question', '')}</p>
        """

        if self.tab_widget.currentIndex() == 0:  # 练习模式
            self.question_display.setHtml(question_text)
            self.create_answer_widgets(question)
        else:  # 测试模式
            self.test_question_display.setHtml(question_text)
            self.create_test_answer_widgets(question)

    def get_question_type_name(self, question_type):
        """获取题型名称"""
        type_names = {
            "single_choice": "单选题",
            "fill_blank": "填空题",
            "comprehensive": "综合题"
        }
        return type_names.get(question_type, "未知题型")

    def create_answer_widgets(self, question):
        """创建答案选项部件（练习模式）"""
        # 清除之前的选项
        while self.answer_layout.count():
            child = self.answer_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        question_type = question.get('type')
        options = question.get('options', [])
        question_id = question.get('id')

        # 获取用户已保存的答案
        saved_answer = self.user_answers.get(question_id, [])

        if question_type == "single_choice":
            # 单选题：单选按钮
            for option in options:
                radio = QRadioButton(option)
                if option in saved_answer:
                    radio.setChecked(True)
                self.answer_layout.addWidget(radio)

        elif question_type == "multiple_choice":
            # 多选题：复选框
            for option in options:
                checkbox = QCheckBox(option)
                if option in saved_answer:
                    checkbox.setChecked(True)
                self.answer_layout.addWidget(checkbox)

        elif question_type == "true_false":
            # 判断题：单选按钮
            for option in options:
                radio = QRadioButton(option)
                if option in saved_answer:
                    radio.setChecked(True)
                self.answer_layout.addWidget(radio)

        elif question_type == "fill_blank":
            # 填空题：输入框
            input_field = QLineEdit()
            if saved_answer:
                input_field.setText(saved_answer[0])
            input_field.setPlaceholderText("请输入答案")
            self.answer_layout.addWidget(input_field)

    def create_test_answer_widgets(self, question):
        """创建答案选项部件（测试模式）"""
        # 清除之前的选项
        while self.test_answer_layout.count():
            child = self.test_answer_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        question_type = question.get('type')
        options = question.get('options', [])
        question_id = question.get('id')

        # 获取用户已保存的答案
        saved_answer = self.user_answers.get(question_id, [])

        if question_type == "single_choice":
            for option in options:
                radio = QRadioButton(option)
                if option in saved_answer:
                    radio.setChecked(True)
                self.test_answer_layout.addWidget(radio)

        elif question_type == "multiple_choice":
            for option in options:
                checkbox = QCheckBox(option)
                if option in saved_answer:
                    checkbox.setChecked(True)
                self.test_answer_layout.addWidget(checkbox)

        elif question_type == "true_false":
            for option in options:
                radio = QRadioButton(option)
                if option in saved_answer:
                    radio.setChecked(True)
                self.test_answer_layout.addWidget(radio)

        elif question_type == "fill_blank":
            input_field = QLineEdit()
            if saved_answer:
                input_field.setText(saved_answer[0])
            input_field.setPlaceholderText("请输入答案")
            self.test_answer_layout.addWidget(input_field)

    def get_user_answer(self):
        """获取用户答案"""
        question = self.current_questions[self.current_question_index]
        question_type = question.get('type')
        question_id = question.get('id')

        user_answer = []

        if question_type in ["single_choice", "true_false"]:
            # 单选题或判断题
            if self.tab_widget.currentIndex() == 0:  # 练习模式
                for i in range(self.answer_layout.count()):
                    widget = self.answer_layout.itemAt(i).widget()
                    if isinstance(widget, QRadioButton) and widget.isChecked():
                        user_answer.append(widget.text())
            else:  # 测试模式
                for i in range(self.test_answer_layout.count()):
                    widget = self.test_answer_layout.itemAt(i).widget()
                    if isinstance(widget, QRadioButton) and widget.isChecked():
                        user_answer.append(widget.text())

        elif question_type == "multiple_choice":
            # 多选题
            if self.tab_widget.currentIndex() == 0:  # 练习模式
                for i in range(self.answer_layout.count()):
                    widget = self.answer_layout.itemAt(i).widget()
                    if isinstance(widget, QCheckBox) and widget.isChecked():
                        user_answer.append(widget.text())
            else:  # 测试模式
                for i in range(self.test_answer_layout.count()):
                    widget = self.test_answer_layout.itemAt(i).widget()
                    if isinstance(widget, QCheckBox) and widget.isChecked():
                        user_answer.append(widget.text())

        elif question_type == "fill_blank":
            # 填空题
            if self.tab_widget.currentIndex() == 0:  # 练习模式
                for i in range(self.answer_layout.count()):
                    widget = self.answer_layout.itemAt(i).widget()
                    if isinstance(widget, QLineEdit):
                        user_answer.append(widget.text().strip())
            else:  # 测试模式
                for i in range(self.test_answer_layout.count()):
                    widget = self.test_answer_layout.itemAt(i).widget()
                    if isinstance(widget, QLineEdit):
                        user_answer.append(widget.text().strip())

        # 保存答案
        if user_answer:
            self.user_answers[question_id] = user_answer

        return user_answer

    def submit_answer(self):
        """提交答案"""
        user_answer = self.get_user_answer()
        if not user_answer:
            QMessageBox.warning(self, "提示", "请先选择答案！")
            return

        question = self.current_questions[self.current_question_index]
        question_id = question.get('id')

        # 检查答案
        is_correct, explanation = self.question_bank.check_answer(question_id, user_answer)

        # 显示结果
        result_text = f"""
        <h4>{"✓ 回答正确" if is_correct else "✗ 回答错误"}</h4>
        <p><b>你的答案:</b> {', '.join(user_answer)}</p>
        <p><b>正确答案:</b> {', '.join(question.get('answer', []))}</p>
        <p><b>解析:</b> {explanation}</p>
        """

        self.result_display.setHtml(result_text)

        # 更新进度
        self.update_progress()

    def prev_question(self):
        """上一题"""
        if self.current_question_index > 0:
            self.current_question_index -= 1
            self.show_question()
            self.update_progress()

            # 更新按钮状态
            self.prev_btn.setEnabled(self.current_question_index > 0)
            self.next_btn.setEnabled(True)

    def next_question(self):
        """下一题"""
        if self.current_question_index < len(self.current_questions) - 1:
            self.current_question_index += 1
            self.show_question()
            self.update_progress()

            # 更新按钮状态
            self.prev_btn.setEnabled(True)
            self.next_btn.setEnabled(self.current_question_index < len(self.current_questions) - 1)

    def update_progress(self):
        """更新进度显示"""
        if self.current_questions:
            total = len(self.current_questions)
            current = self.current_question_index + 1
            self.progress_label.setText(f"进度: {current}/{total}")

    def update_time(self):
        """更新时间显示"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.setText(f"时间: {current_time}")

    def start_test(self):
        """开始测试"""
        # 获取设置
        duration = self.test_duration_spin.value()
        count = self.test_count_spin.value()

        # 获取题目
        self.current_questions = self.question_bank.get_random_questions(count)

        if not self.current_questions:
            QMessageBox.warning(self, "提示", "没有足够的题目！")
            return

        # 重置状态
        self.current_question_index = 0
        self.user_answers = {}
        self.test_start_time = datetime.now()

        # 启用按钮
        self.test_prev_btn.setEnabled(False)
        self.test_next_btn.setEnabled(len(self.current_questions) > 1)
        self.finish_test_btn.setEnabled(True)
        self.start_test_btn.setEnabled(False)

        # 显示第一题
        self.show_question()

        # 更新进度条
        self.test_progress.setMaximum(len(self.current_questions))
        self.test_progress.setValue(1)

        self.status_label.setText(f"测试模式 - 进行中 (时长: {duration}分钟)")

        # 切换到测试标签页
        self.tab_widget.setCurrentIndex(1)

    def test_prev_question(self):
        """测试模式上一题"""
        if self.current_question_index > 0:
            self.current_question_index -= 1
            self.show_question()
            self.test_progress.setValue(self.current_question_index + 1)

            self.test_prev_btn.setEnabled(self.current_question_index > 0)
            self.test_next_btn.setEnabled(True)

    def test_next_question(self):
        """测试模式下一题"""
        if self.current_question_index < len(self.current_questions) - 1:
            self.current_question_index += 1
            self.show_question()
            self.test_progress.setValue(self.current_question_index + 1)

            self.test_prev_btn.setEnabled(True)
            self.test_next_btn.setEnabled(self.current_question_index < len(self.current_questions) - 1)

    def finish_test(self):
        """结束测试"""
        # 计算成绩
        correct_count = 0
        total_count = len(self.current_questions)

        for question in self.current_questions:
            question_id = question.get('id')
            user_answer = self.user_answers.get(question_id, [])
            is_correct, _ = self.question_bank.check_answer(question_id, user_answer)
            if is_correct:
                correct_count += 1

        score = (correct_count / total_count * 100) if total_count > 0 else 0

        # 显示成绩
        QMessageBox.information(self, "测试完成",
                               f"测试完成！\n\n"
                               f"总题数: {total_count}\n"
                               f"正确数: {correct_count}\n"
                               f"得分: {score:.1f}分")

        # 重置状态
        self.start_test_btn.setEnabled(True)
        self.finish_test_btn.setEnabled(False)
        self.test_prev_btn.setEnabled(False)
        self.test_next_btn.setEnabled(False)

        self.status_label.setText("测试模式 - 已完成")

    def refresh_wrong_questions(self):
        """刷新错题本"""
        self.wrong_questions_list.clear()
        # 这里可以添加获取错题的逻辑
        self.wrong_question_display.clear()

    def show_wrong_question(self, item):
        """显示错题详情"""
        # 这里可以添加显示错题详情的逻辑
        pass

    def load_stats_data(self):
        """加载统计数据"""
        stats = self.question_bank.get_user_stats()

        self.stats_table.setRowCount(len(stats))
        for row, (date, data) in enumerate(sorted(stats.items(), reverse=True)):
            total = data.get('total', 0)
            correct = data.get('correct', 0)
            accuracy = (correct / total * 100) if total > 0 else 0

            self.stats_table.setItem(row, 0, QTableWidgetItem(date))
            self.stats_table.setItem(row, 1, QTableWidgetItem(str(total)))
            self.stats_table.setItem(row, 2, QTableWidgetItem(str(correct)))
            self.stats_table.setItem(row, 3, QTableWidgetItem(f"{accuracy:.1f}%"))

    # 试卷模式相关方法
    def load_paper_list(self):
        """加载试卷列表"""
        if not self.paper_manager:
            QMessageBox.warning(self, "错误", "试卷模块未加载")
            return

        self.paper_list.clear()
        papers = self.paper_manager.list_papers(status="active")

        if not papers:
            self.paper_list.addItem("暂无试卷")
            return

        for paper in papers:
            questions = self.paper_manager.get_paper_questions(paper["id"])
            item_text = f"{paper['id']}. {paper['title']} ({len(questions)}题)"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, paper["id"])  # 保存试卷ID
            self.paper_list.addItem(item)

    def on_paper_selected(self, item):
        """试卷被选中"""
        if not self.paper_manager:
            return

        paper_id = item.data(Qt.UserRole)
        if not paper_id:
            return

        paper = self.paper_manager.get_paper(paper_id)
        if not paper:
            return

        questions = self.paper_manager.get_paper_questions(paper_id)

        # 显示试卷信息
        info_text = f"""
        <h3>{paper['title']}</h3>
        <p><b>描述:</b> {paper.get('description', '')}</p>
        <p><b>题目数量:</b> {len(questions)}题</p>
        <p><b>时间限制:</b> {paper.get('time_limit', 0)}分钟</p>
        <p><b>总分:</b> {paper.get('total_score', 0)}分</p>
        <p><b>创建时间:</b> {paper.get('created', '')}</p>
        """

        self.paper_info_display.setHtml(info_text)
        self.start_paper_btn.setEnabled(True)
        self.selected_paper_id = paper_id

    def start_paper(self):
        """开始做试卷"""
        if not hasattr(self, 'selected_paper_id'):
            QMessageBox.warning(self, "错误", "请先选择试卷")
            return

        # 获取试卷信息
        paper = self.paper_manager.get_paper(self.selected_paper_id)
        if not paper:
            QMessageBox.warning(self, "错误", "试卷不存在")
            return

        # 获取试卷题目
        questions = self.paper_manager.get_paper_questions(self.selected_paper_id)
        if not questions:
            QMessageBox.warning(self, "错误", "试卷中没有题目")
            return

        # 设置当前题目
        self.current_questions = questions
        self.current_question_index = 0
        self.user_answers = {}

        # 设置倒计时
        self.paper_time_limit = paper.get("time_limit", 120)  # 默认120分钟
        self.paper_time_remaining = self.paper_time_limit * 60  # 转换为秒

        # 显示做题界面
        self.paper_question_widget.setVisible(True)
        self.start_paper_btn.setEnabled(False)

        # 设置进度条
        self.paper_progress.setMaximum(len(questions))
        self.paper_progress.setValue(1)

        # 启用导航按钮
        self.paper_prev_btn.setEnabled(False)
        self.paper_next_btn.setEnabled(len(questions) > 1)
        self.finish_paper_btn.setEnabled(True)

        # 显示第一题
        self.show_paper_question()

        # 启动倒计时定时器
        if self.paper_timer:
            self.paper_timer.stop()
        self.paper_timer = QTimer()
        self.paper_timer.timeout.connect(self.update_paper_timer)
        self.paper_timer.start(1000)  # 每秒更新一次

        # 更新状态栏显示倒计时
        self.update_paper_timer_display()

        self.status_label.setText(f"试卷模式 - 进行中")

    def update_paper_timer(self):
        """更新试卷倒计时"""
        if self.paper_time_remaining <= 0:
            # 时间到，自动交卷
            self.paper_timer.stop()
            self.timeout_finish_paper()
            return

        self.paper_time_remaining -= 1
        self.update_paper_timer_display()

    def update_paper_timer_display(self):
        """更新倒计时显示"""
        hours = self.paper_time_remaining // 3600
        minutes = (self.paper_time_remaining % 3600) // 60
        seconds = self.paper_time_remaining % 60

        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        # 在状态栏显示倒计时
        self.time_label.setText(f"倒计时: {time_str}")

        # 最后5分钟显示红色警告
        if self.paper_time_remaining <= 300:  # 5分钟 = 300秒
            self.time_label.setStyleSheet("color: red; font-weight: bold;")
        else:
            self.time_label.setStyleSheet("")

    def timeout_finish_paper(self):
        """时间到自动交卷"""
        QMessageBox.warning(self, "时间到", "考试时间已到，系统将自动交卷！")
        self.finish_paper()

    def show_paper_question(self):
        """显示试卷题目"""
        if not self.current_questions:
            return

        question = self.current_questions[self.current_question_index]
        question_type = question.get('type')

        # 显示题目
        question_text = f"""
        <h3>第 {self.current_question_index + 1} 题 (共 {len(self.current_questions)} 题)</h3>
        <p><b>分类:</b> {question.get('category', '未知')}</p>
        <p><b>题型:</b> {self.get_question_type_name(question_type)}</p>
        <p><b>分值:</b> {question.get('score', 5)}分</p>
        <hr>
        <p>{question.get('question', '')}</p>
        """

        # 如果是综合题，显示子题目
        if question_type == "comprehensive":
            sub_questions = question.get('sub_questions', [])
            if sub_questions:
                question_text += "<h4>子题目:</h4>"
                for i, sub_q in enumerate(sub_questions, 1):
                    question_text += f"<p>{i}. {sub_q.get('question', '')}</p>"

        self.paper_question_display.setHtml(question_text)
        self.create_paper_answer_widgets(question)

        # 更新进度
        self.paper_progress.setValue(self.current_question_index + 1)

    def create_paper_answer_widgets(self, question):
        """创建试卷答案选项部件"""
        # 清除之前的选项
        while self.paper_answer_layout.count():
            child = self.paper_answer_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        question_type = question.get('type')
        question_id = question.get('id')

        # 获取用户已保存的答案
        saved_answer = self.user_answers.get(question_id, [])

        if question_type == "single_choice":
            options = question.get('options', [])
            for option in options:
                radio = QRadioButton(option)
                if option in saved_answer:
                    radio.setChecked(True)
                self.paper_answer_layout.addWidget(radio)

        elif question_type == "fill_blank":
            input_field = QLineEdit()
            if saved_answer:
                input_field.setText(saved_answer[0])
            input_field.setPlaceholderText("请输入答案")
            self.paper_answer_layout.addWidget(input_field)

        elif question_type == "comprehensive":
            sub_questions = question.get('sub_questions', [])
            for i, sub_q in enumerate(sub_questions):
                # 子题目标签
                sub_label = QLabel(f"{i+1}. {sub_q.get('question', '')}")
                self.paper_answer_layout.addWidget(sub_label)

                # 子题目输入框
                input_field = QLineEdit()
                if i < len(saved_answer):
                    input_field.setText(saved_answer[i])
                input_field.setPlaceholderText(f"请输入第{i+1}小题答案")
                input_field.setProperty("sub_index", i)  # 保存子题目索引
                self.paper_answer_layout.addWidget(input_field)

    def get_paper_user_answer(self):
        """获取试卷用户答案"""
        question = self.current_questions[self.current_question_index]
        question_type = question.get('type')
        question_id = question.get('id')

        user_answer = []

        if question_type == "single_choice":
            for i in range(self.paper_answer_layout.count()):
                widget = self.paper_answer_layout.itemAt(i).widget()
                if isinstance(widget, QRadioButton) and widget.isChecked():
                    user_answer.append(widget.text())

        elif question_type == "fill_blank":
            for i in range(self.paper_answer_layout.count()):
                widget = self.paper_answer_layout.itemAt(i).widget()
                if isinstance(widget, QLineEdit):
                    user_answer.append(widget.text().strip())

        elif question_type == "comprehensive":
            # 综合题：收集所有子题目的答案
            sub_questions = question.get('sub_questions', [])
            sub_answers = [""] * len(sub_questions)

            for i in range(self.paper_answer_layout.count()):
                widget = self.paper_answer_layout.itemAt(i).widget()
                if isinstance(widget, QLineEdit):
                    sub_index = widget.property("sub_index")
                    if sub_index is not None and 0 <= sub_index < len(sub_questions):
                        sub_answers[sub_index] = widget.text().strip()

            user_answer = sub_answers

        # 保存答案
        if user_answer:
            self.user_answers[question_id] = user_answer

        return user_answer

    def paper_prev_question(self):
        """试卷上一题"""
        # 保存当前答案
        self.get_paper_user_answer()

        if self.current_question_index > 0:
            self.current_question_index -= 1
            self.show_paper_question()

            self.paper_prev_btn.setEnabled(self.current_question_index > 0)
            self.paper_next_btn.setEnabled(True)

    def paper_next_question(self):
        """试卷下一题"""
        # 保存当前答案
        self.get_paper_user_answer()

        if self.current_question_index < len(self.current_questions) - 1:
            self.current_question_index += 1
            self.show_paper_question()

            self.paper_prev_btn.setEnabled(True)
            self.paper_next_btn.setEnabled(self.current_question_index < len(self.current_questions) - 1)

    def finish_paper(self):
        """交卷"""
        # 停止倒计时定时器
        if self.paper_timer:
            self.paper_timer.stop()
            self.paper_timer = None

        # 保存最后一题的答案
        self.get_paper_user_answer()

        # 计算成绩
        total_score = 0
        obtained_score = 0
        correct_count = 0
        total_count = len(self.current_questions)

        for question in self.current_questions:
            question_id = question.get('id')
            user_answer = self.user_answers.get(question_id, [])
            is_correct, _ = self.question_bank.check_answer(question_id, user_answer)

            question_score = question.get('score', 5)
            total_score += question_score

            if is_correct:
                correct_count += 1
                obtained_score += question_score

        score_percentage = (obtained_score / total_score * 100) if total_score > 0 else 0

        # 显示成绩
        result_text = f"""
        <h3>试卷完成!</h3>
        <p><b>总题数:</b> {total_count}</p>
        <p><b>正确数:</b> {correct_count}</p>
        <p><b>得分:</b> {obtained_score}/{total_score}</p>
        <p><b>正确率:</b> {score_percentage:.1f}%</p>
        """

        QMessageBox.information(self, "试卷完成", result_text)

        # 重置状态
        self.paper_question_widget.setVisible(False)
        self.start_paper_btn.setEnabled(True)
        self.paper_prev_btn.setEnabled(False)
        self.paper_next_btn.setEnabled(False)
        self.finish_paper_btn.setEnabled(False)

        # 恢复时间显示
        self.time_label.setText("时间: 00:00:00")
        self.time_label.setStyleSheet("")

        self.status_label.setText("试卷模式 - 已完成")

    def closeEvent(self, event):
        """关闭事件"""
        reply = QMessageBox.question(self, '确认退出',
                                    '确定要退出极智题典吗？',
                                    QMessageBox.Yes | QMessageBox.No,
                                    QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()