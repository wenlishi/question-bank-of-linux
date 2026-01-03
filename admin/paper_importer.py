#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
管理员专用试卷导入工具
需要密码验证才能使用
"""

import sys
import os
import json
import hashlib
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QLineEdit,
                             QTextEdit, QMessageBox, QGroupBox, QFormLayout,
                             QFileDialog, QListWidget, QListWidgetItem,
                             QTabWidget, QProgressBar, QTableWidget,
                             QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor

# 添加core模块到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.paper_manager import PaperManager, QuestionType

class AdminPaperImporter(QMainWindow):
    """管理员试卷导入工具"""

    def __init__(self):
        super().__init__()
        self.admin_password = self._load_admin_password()
        self.is_authenticated = False
        self.paper_manager = None
        self.init_ui()

    def _load_admin_password(self):
        """加载管理员密码"""
        password_file = "data/admin_password.hash"
        if os.path.exists(password_file):
            with open(password_file, 'r') as f:
                return f.read().strip()
        else:
            # 默认密码：admin123
            default_hash = hashlib.sha256("admin123".encode()).hexdigest()
            os.makedirs("data", exist_ok=True)
            with open(password_file, 'w') as f:
                f.write(default_hash)
            return default_hash

    def _verify_password(self, password):
        """验证密码"""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        return password_hash == self.admin_password

    def _change_password(self, old_password, new_password):
        """修改密码"""
        if self._verify_password(old_password):
            new_hash = hashlib.sha256(new_password.encode()).hexdigest()
            self.admin_password = new_hash
            with open("data/admin_password.hash", 'w') as f:
                f.write(new_hash)
            return True
        return False

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("管理员试卷导入工具")
        self.setGeometry(100, 100, 900, 700)

        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)

        if not self.is_authenticated:
            # 登录界面
            self.show_login_interface(main_layout)
        else:
            # 主界面
            self.show_main_interface(main_layout)

    def show_login_interface(self, layout):
        """显示登录界面"""
        login_group = QGroupBox("管理员登录")
        login_layout = QVBoxLayout()

        # 密码输入
        form_layout = QFormLayout()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("请输入管理员密码")
        form_layout.addRow("密码:", self.password_edit)

        login_layout.addLayout(form_layout)

        # 登录按钮
        login_btn = QPushButton("登录")
        login_btn.clicked.connect(self.login)
        login_btn.setDefault(True)
        login_layout.addWidget(login_btn)

        # 默认密码提示
        hint_label = QLabel("默认密码: admin123")
        hint_label.setStyleSheet("color: gray; font-size: 10pt;")
        login_layout.addWidget(hint_label)

        login_group.setLayout(login_layout)
        layout.addWidget(login_group)

        # 版本信息
        info_label = QLabel("© 2025 题库软件 - 管理员工具 v1.0")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("color: gray; margin-top: 20px;")
        layout.addWidget(info_label)

    def show_main_interface(self, layout):
        """显示主界面"""
        # 初始化试卷管理器
        self.paper_manager = PaperManager()

        # 创建标签页
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # 创建各个标签页
        self.create_import_tab()
        self.create_manage_tab()
        self.create_stats_tab()
        self.create_settings_tab()

        # 状态栏
        self.statusBar().showMessage("就绪 - 管理员模式")

    def create_import_tab(self):
        """创建导入标签页"""
        import_widget = QWidget()
        layout = QVBoxLayout(import_widget)

        # 文件选择
        file_group = QGroupBox("选择试卷文件")
        file_layout = QVBoxLayout()

        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("点击浏览选择试卷文件...")
        self.file_path_edit.setReadOnly(True)
        file_layout.addWidget(self.file_path_edit)

        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(browse_btn)

        file_group.setLayout(file_layout)
        layout.addWidget(file_group)

        # 文件预览
        preview_group = QGroupBox("文件预览")
        preview_layout = QVBoxLayout()

        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(200)
        preview_layout.addWidget(self.preview_text)

        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)

        # 导入选项
        options_group = QGroupBox("导入选项")
        options_layout = QVBoxLayout()

        self.replace_existing_check = QPushButton("覆盖现有试卷")
        self.replace_existing_check.setCheckable(True)
        self.replace_existing_check.setChecked(False)
        options_layout.addWidget(self.replace_existing_check)

        self.backup_check = QPushButton("导入前备份")
        self.backup_check.setCheckable(True)
        self.backup_check.setChecked(True)
        options_layout.addWidget(self.backup_check)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # 导入按钮
        import_btn = QPushButton("开始导入")
        import_btn.clicked.connect(self.import_papers)
        import_btn.setFont(QFont("Arial", 12))
        layout.addWidget(import_btn)

        # 进度显示
        self.import_progress = QProgressBar()
        layout.addWidget(self.import_progress)

        # 导入结果
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)

        self.tab_widget.addTab(import_widget, "导入试卷")

    def create_manage_tab(self):
        """创建管理标签页"""
        manage_widget = QWidget()
        layout = QVBoxLayout(manage_widget)

        # 试卷列表
        self.paper_table = QTableWidget()
        self.paper_table.setColumnCount(6)
        self.paper_table.setHorizontalHeaderLabels([
            "ID", "标题", "题目数", "时间限制", "总分", "状态"
        ])
        self.paper_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.paper_table)

        # 操作按钮
        button_layout = QHBoxLayout()

        refresh_btn = QPushButton("刷新列表")
        refresh_btn.clicked.connect(self.load_paper_list)

        delete_btn = QPushButton("删除选中试卷")
        delete_btn.clicked.connect(self.delete_selected_paper)

        export_btn = QPushButton("导出选中试卷")
        export_btn.clicked.connect(self.export_selected_paper)

        button_layout.addWidget(refresh_btn)
        button_layout.addWidget(delete_btn)
        button_layout.addWidget(export_btn)

        layout.addLayout(button_layout)

        # 加载数据
        self.load_paper_list()

        self.tab_widget.addTab(manage_widget, "管理试卷")

    def create_stats_tab(self):
        """创建统计标签页"""
        stats_widget = QWidget()
        layout = QVBoxLayout(stats_widget)

        # 统计信息
        stats = self.paper_manager.get_statistics()

        stats_text = f"""
        <h3>系统统计</h3>
        <table border="1" cellpadding="5">
        <tr><td><b>总题目数:</b></td><td>{stats['total_questions']}</td></tr>
        <tr><td><b>总试卷数:</b></td><td>{stats['total_papers']}</td></tr>
        </table>

        <h4>题目类型分布</h4>
        <table border="1" cellpadding="5">
        """

        for q_type, count in stats['question_types'].items():
            type_name = {
                "single_choice": "单选题",
                "multiple_choice": "多选题",
                "true_false": "判断题",
                "fill_blank": "填空题"
            }.get(q_type, q_type)
            stats_text += f"<tr><td>{type_name}</td><td>{count}</td></tr>"

        stats_text += "</table>"

        stats_label = QLabel(stats_text)
        stats_label.setTextFormat(Qt.RichText)
        layout.addWidget(stats_label)

        # 刷新按钮
        refresh_btn = QPushButton("刷新统计")
        refresh_btn.clicked.connect(self.refresh_stats)
        layout.addWidget(refresh_btn)

        self.tab_widget.addTab(stats_widget, "系统统计")

    def create_settings_tab(self):
        """创建设置标签页"""
        settings_widget = QWidget()
        layout = QVBoxLayout(settings_widget)

        # 修改密码
        password_group = QGroupBox("修改管理员密码")
        password_layout = QFormLayout()

        self.old_password_edit = QLineEdit()
        self.old_password_edit.setEchoMode(QLineEdit.Password)
        password_layout.addRow("旧密码:", self.old_password_edit)

        self.new_password_edit = QLineEdit()
        self.new_password_edit.setEchoMode(QLineEdit.Password)
        password_layout.addRow("新密码:", self.new_password_edit)

        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setEchoMode(QLineEdit.Password)
        password_layout.addRow("确认新密码:", self.confirm_password_edit)

        change_btn = QPushButton("修改密码")
        change_btn.clicked.connect(self.change_password)
        password_layout.addRow("", change_btn)

        password_group.setLayout(password_layout)
        layout.addWidget(password_group)

        # 数据管理
        data_group = QGroupBox("数据管理")
        data_layout = QVBoxLayout()

        backup_btn = QPushButton("备份数据")
        backup_btn.clicked.connect(self.backup_data)
        data_layout.addWidget(backup_btn)

        restore_btn = QPushButton("恢复数据")
        restore_btn.clicked.connect(self.restore_data)
        data_layout.addWidget(restore_btn)

        data_group.setLayout(data_layout)
        layout.addWidget(data_group)

        layout.addStretch()

        self.tab_widget.addTab(settings_widget, "设置")

    def login(self):
        """登录"""
        password = self.password_edit.text().strip()
        if not password:
            QMessageBox.warning(self, "错误", "请输入密码")
            return

        if self._verify_password(password):
            self.is_authenticated = True
            # 重新初始化界面
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            main_layout = QVBoxLayout(central_widget)
            self.show_main_interface(main_layout)
        else:
            QMessageBox.critical(self, "错误", "密码错误")

    def browse_file(self):
        """浏览文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择试卷文件", "", "JSON文件 (*.json);;所有文件 (*.*)"
        )

        if file_path:
            self.file_path_edit.setText(file_path)
            self.preview_file(file_path)

    def preview_file(self, file_path):
        """预览文件内容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            preview_text = "文件结构预览:\n"
            preview_text += f"文件大小: {os.path.getsize(file_path)} 字节\n"

            if "questions" in data:
                preview_text += f"题目数量: {len(data['questions'])}\n"

            if "papers" in data:
                preview_text += f"试卷数量: {len(data['papers'])}\n"
                for i, paper in enumerate(data['papers'][:3], 1):  # 只显示前3套
                    preview_text += f"  试卷{i}: {paper.get('title', '未命名')}\n"
                if len(data['papers']) > 3:
                    preview_text += f"  ... 还有 {len(data['papers']) - 3} 套试卷\n"

            self.preview_text.setPlainText(preview_text)

        except Exception as e:
            self.preview_text.setPlainText(f"读取文件失败: {e}")

    def import_papers(self):
        """导入试卷"""
        file_path = self.file_path_edit.text().strip()
        if not file_path:
            QMessageBox.warning(self, "错误", "请先选择文件")
            return

        if not os.path.exists(file_path):
            QMessageBox.critical(self, "错误", "文件不存在")
            return

        # 备份现有数据
        if self.backup_check.isChecked():
            self.backup_data()

        try:
            self.import_progress.setValue(10)

            # 导入数据
            imported_count = self.paper_manager.import_from_json(file_path)
            self.import_progress.setValue(100)

            # 显示结果
            stats = self.paper_manager.get_statistics()
            result_text = f"""
            ✅ 导入成功!

            导入统计:
            - 导入题目数: {imported_count}
            - 总题目数: {stats['total_questions']}
            - 总试卷数: {stats['total_papers']}

            导入时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """

            self.result_text.setPlainText(result_text)
            self.statusBar().showMessage(f"导入成功: {imported_count}道题目")

            # 刷新管理页面
            self.load_paper_list()

        except Exception as e:
            self.result_text.setPlainText(f"❌ 导入失败:\n{str(e)}")
            QMessageBox.critical(self, "导入失败", f"导入过程中发生错误:\n{str(e)}")

    def load_paper_list(self):
        """加载试卷列表"""
        papers = self.paper_manager.list_papers()

        self.paper_table.setRowCount(len(papers))

        for row, paper in enumerate(papers):
            questions = self.paper_manager.get_paper_questions(paper["id"])

            # ID
            self.paper_table.setItem(row, 0, QTableWidgetItem(str(paper["id"])))

            # 标题
            self.paper_table.setItem(row, 1, QTableWidgetItem(paper.get("title", "")))

            # 题目数
            self.paper_table.setItem(row, 2, QTableWidgetItem(str(len(questions))))

            # 时间限制
            self.paper_table.setItem(row, 3, QTableWidgetItem(f"{paper.get('time_limit', 0)}分钟"))

            # 总分
            self.paper_table.setItem(row, 4, QTableWidgetItem(str(paper.get('total_score', 0))))

            # 状态
            status_item = QTableWidgetItem(paper.get("status", "unknown"))
            if paper.get("status") == "active":
                status_item.setForeground(QColor("green"))
            elif paper.get("status") == "draft":
                status_item.setForeground(QColor("orange"))
            self.paper_table.setItem(row, 5, status_item)

    def delete_selected_paper(self):
        """删除选中试卷"""
        selected_rows = self.paper_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "提示", "请先选择要删除的试卷")
            return

        # 获取选中的试卷ID
        paper_ids = set()
        for item in selected_rows:
            if item.column() == 0:  # ID列
                paper_ids.add(int(item.text()))

        if not paper_ids:
            return

        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除选中的 {len(paper_ids)} 套试卷吗？\n此操作不可恢复！",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            deleted_count = 0
            for paper_id in paper_ids:
                if self.paper_manager.delete_paper(paper_id):
                    deleted_count += 1

            QMessageBox.information(self, "删除完成", f"已删除 {deleted_count} 套试卷")
            self.load_paper_list()

    def export_selected_paper(self):
        """导出选中试卷"""
        selected_rows = self.paper_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "提示", "请先选择要导出的试卷")
            return

        # 获取选中的试卷ID
        paper_ids = set()
        for item in selected_rows:
            if item.column() == 0:  # ID列
                paper_ids.add(int(item.text()))

        if not paper_ids:
            return

        # 选择保存位置
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存试卷文件", f"papers_export_{datetime.now().strftime('%Y%m%d')}.json",
            "JSON文件 (*.json)"
        )

        if not file_path:
            return

        # 导出数据
        export_data = {
            "questions": [],
            "papers": []
        }

        # 收集所有相关题目
        all_question_ids = set()
        for paper_id in paper_ids:
            paper = self.paper_manager.get_paper(paper_id)
            if paper:
                export_data["papers"].append(paper)
                all_question_ids.update(paper.get("question_ids", []))

        # 收集题目数据
        for q_id in all_question_ids:
            question = self.paper_manager.get_question(q_id)
            if question:
                export_data["questions"].append(question)

        # 保存到文件
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)

            QMessageBox.information(
                self, "导出成功",
                f"已导出 {len(paper_ids)} 套试卷，{len(export_data['questions'])} 道题目\n"
                f"保存到: {file_path}"
            )

        except Exception as e:
            QMessageBox.critical(self, "导出失败", f"导出过程中发生错误:\n{str(e)}")

    def refresh_stats(self):
        """刷新统计信息"""
        # 切换到统计标签页
        self.tab_widget.setCurrentIndex(2)
        # 这里可以重新加载统计信息
        self.statusBar().showMessage("统计信息已刷新")

    def change_password(self):
        """修改密码"""
        old_password = self.old_password_edit.text().strip()
        new_password = self.new_password_edit.text().strip()
        confirm_password = self.confirm_password_edit.text().strip()

        if not old_password or not new_password:
            QMessageBox.warning(self, "错误", "请填写所有字段")
            return

        if new_password != confirm_password:
            QMessageBox.warning(self, "错误", "新密码和确认密码不一致")
            return

        if len(new_password) < 6:
            QMessageBox.warning(self, "错误", "新密码至少需要6位")
            return

        if self._change_password(old_password, new_password):
            QMessageBox.information(self, "成功", "密码修改成功")
            # 清空输入框
            self.old_password_edit.clear()
            self.new_password_edit.clear()
            self.confirm_password_edit.clear()
        else:
            QMessageBox.critical(self, "错误", "旧密码错误")

    def backup_data(self):
        """备份数据"""
        backup_dir = "backups"
        os.makedirs(backup_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_dir, f"backup_{timestamp}.json")

        try:
            count = self.paper_manager.export_to_json(backup_file)
            QMessageBox.information(
                self, "备份成功",
                f"已备份 {count} 条记录\n保存到: {backup_file}"
            )
        except Exception as e:
            QMessageBox.critical(self, "备份失败", f"备份过程中发生错误:\n{str(e)}")

    def restore_data(self):
        """恢复数据"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择备份文件", "backups", "JSON文件 (*.json)"
        )

        if not file_path:
            return

        reply = QMessageBox.question(
            self, "确认恢复",
            "确定要恢复备份数据吗？\n当前所有数据将被覆盖！",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                # 先备份当前数据
                self.backup_data()

                # 恢复数据
                imported_count = self.paper_manager.import_from_json(file_path)

                QMessageBox.information(
                    self, "恢复成功",
                    f"已恢复 {imported_count} 条记录\n来自: {file_path}"
                )

                # 刷新界面
                self.load_paper_list()

            except Exception as e:
                QMessageBox.critical(self, "恢复失败", f"恢复过程中发生错误:\n{str(e)}")

def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setApplicationName("管理员试卷导入工具")
    app.setOrganizationName("TikuSoft")

    window = AdminPaperImporter()
    window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()