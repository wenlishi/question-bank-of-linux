#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
激活码管理后台
用于生成和管理激活码
"""

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QLineEdit,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QGroupBox, QFormLayout, QSpinBox, QMessageBox,
                             QTextEdit, QComboBox, QTabWidget, QSplitter,
                             QMenu, QAction, QDialog, QDialogButtonBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor
from datetime import datetime, timedelta
import json

# 添加父目录到路径，以便导入core模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.activation import ActivationManager

class ActivationAdmin(QMainWindow):
    """激活码管理后台"""

    def __init__(self):
        super().__init__()
        self.activation_manager = ActivationManager()
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("激活码管理后台")
        self.setGeometry(100, 100, 1000, 700)

        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)

        # 创建标签页
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # 创建各个标签页
        self.create_generate_tab()
        self.create_manage_tab()
        self.create_stats_tab()

        # 状态栏
        self.statusBar().showMessage("就绪")

    def create_generate_tab(self):
        """创建生成激活码标签页"""
        generate_widget = QWidget()
        layout = QVBoxLayout(generate_widget)

        # 生成设置
        settings_group = QGroupBox("生成设置")
        settings_layout = QFormLayout()

        # 有效期设置
        self.days_spin = QSpinBox()
        self.days_spin.setRange(1, 3650)  # 最多10年
        self.days_spin.setValue(365)  # 默认1年
        settings_layout.addRow("有效期(天):", self.days_spin)

        # 最大使用次数
        self.max_uses_spin = QSpinBox()
        self.max_uses_spin.setRange(1, 100)
        self.max_uses_spin.setValue(1)  # 默认单设备使用
        settings_layout.addRow("最大使用次数:", self.max_uses_spin)

        # 生成数量
        self.count_spin = QSpinBox()
        self.count_spin.setRange(1, 100)
        self.count_spin.setValue(1)
        settings_layout.addRow("生成数量:", self.count_spin)

        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        # 生成按钮
        generate_btn = QPushButton("生成激活码")
        generate_btn.clicked.connect(self.generate_activation_codes)
        generate_btn.setFont(QFont("Arial", 12))
        layout.addWidget(generate_btn)

        # 生成的激活码显示
        self.generated_codes_display = QTextEdit()
        self.generated_codes_display.setReadOnly(True)
        self.generated_codes_display.setPlaceholderText("生成的激活码将显示在这里...")
        layout.addWidget(self.generated_codes_display)

        # 操作按钮
        button_layout = QHBoxLayout()
        copy_btn = QPushButton("复制到剪贴板")
        copy_btn.clicked.connect(self.copy_to_clipboard)
        save_btn = QPushButton("保存到文件")
        save_btn.clicked.connect(self.save_to_file)
        clear_btn = QPushButton("清空")
        clear_btn.clicked.connect(self.clear_generated_codes)

        button_layout.addWidget(copy_btn)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(clear_btn)
        layout.addLayout(button_layout)

        self.tab_widget.addTab(generate_widget, "生成激活码")

    def create_manage_tab(self):
        """创建管理激活码标签页"""
        manage_widget = QWidget()
        layout = QVBoxLayout(manage_widget)

        # 搜索框
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("搜索:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("输入激活码或设备ID进行搜索...")
        self.search_edit.textChanged.connect(self.search_activations)
        search_layout.addWidget(self.search_edit)

        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(self.refresh_activations)
        search_layout.addWidget(refresh_btn)

        layout.addLayout(search_layout)

        # 激活码表格
        self.activation_table = QTableWidget()
        self.activation_table.setColumnCount(7)
        self.activation_table.setHorizontalHeaderLabels([
            "激活码", "状态", "创建时间", "过期时间", "使用次数", "最大次数", "设备数"
        ])
        self.activation_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.activation_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.activation_table.customContextMenuRequested.connect(self.show_context_menu)

        layout.addWidget(self.activation_table)

        # 详情显示
        self.details_display = QTextEdit()
        self.details_display.setReadOnly(True)
        self.details_display.setMaximumHeight(150)
        layout.addWidget(self.details_display)

        # 加载数据
        self.load_activations()

        self.tab_widget.addTab(manage_widget, "管理激活码")

    def create_stats_tab(self):
        """创建统计标签页"""
        stats_widget = QWidget()
        layout = QVBoxLayout(stats_widget)

        # 统计信息
        stats = self.activation_manager.get_activation_stats()

        stats_text = f"""
        <h3>激活码统计</h3>
        <table border="1" cellpadding="5">
        <tr><td><b>总激活码数:</b></td><td>{stats['total']}</td></tr>
        <tr><td><b>有效激活码:</b></td><td>{stats['active']}</td></tr>
        <tr><td><b>已过期:</b></td><td>{stats['expired']}</td></tr>
        <tr><td><b>已撤销:</b></td><td>{stats['revoked']}</td></tr>
        <tr><td><b>总使用次数:</b></td><td>{stats['used']}</td></tr>
        </table>
        """

        stats_label = QLabel(stats_text)
        stats_label.setTextFormat(Qt.RichText)
        layout.addWidget(stats_label)

        # 刷新按钮
        refresh_btn = QPushButton("刷新统计")
        refresh_btn.clicked.connect(self.refresh_stats)
        layout.addWidget(refresh_btn)

        layout.addStretch()

        self.tab_widget.addTab(stats_widget, "统计信息")

    def generate_activation_codes(self):
        """生成激活码"""
        days = self.days_spin.value()
        max_uses = self.max_uses_spin.value()
        count = self.count_spin.value()

        generated_codes = []
        for i in range(count):
            code = self.activation_manager.generate_activation_code(days, max_uses)
            generated_codes.append(code)

        # 显示生成的激活码
        display_text = f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        display_text += f"有效期: {days}天\n"
        display_text += f"最大使用次数: {max_uses}\n"
        display_text += "=" * 50 + "\n\n"

        for i, code in enumerate(generated_codes, 1):
            display_text += f"{i}. {code}\n"

        self.generated_codes_display.setPlainText(display_text)
        self.statusBar().showMessage(f"成功生成 {count} 个激活码")

        # 刷新管理页面
        self.load_activations()

    def copy_to_clipboard(self):
        """复制到剪贴板"""
        text = self.generated_codes_display.toPlainText()
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            self.statusBar().showMessage("已复制到剪贴板")
        else:
            QMessageBox.warning(self, "提示", "没有内容可复制！")

    def save_to_file(self):
        """保存到文件"""
        text = self.generated_codes_display.toPlainText()
        if not text:
            QMessageBox.warning(self, "提示", "没有内容可保存！")
            return

        # 这里可以添加文件保存对话框
        # 暂时先显示消息
        QMessageBox.information(self, "保存", "保存功能需要实现文件对话框")

    def clear_generated_codes(self):
        """清空生成的激活码"""
        self.generated_codes_display.clear()
        self.statusBar().showMessage("已清空")

    def load_activations(self):
        """加载激活码数据"""
        activations = self.activation_manager.list_activations()

        self.activation_table.setRowCount(len(activations))

        for row, (code, info) in enumerate(activations.items()):
            # 激活码
            self.activation_table.setItem(row, 0, QTableWidgetItem(code))

            # 检查info类型，如果是字符串则跳过
            if isinstance(info, str):
                # 可能是加密数据，跳过或显示错误
                status_item = QTableWidgetItem("数据错误")
                status_item.setForeground(QColor("red"))
                self.activation_table.setItem(row, 1, status_item)
                # 设置其他列为空
                for col in range(2, 7):
                    self.activation_table.setItem(row, col, QTableWidgetItem(""))
                continue

            # 状态
            status = info.get("status", "unknown")
            status_item = QTableWidgetItem(status)
            if status == "active":
                status_item.setForeground(QColor("green"))
            elif status == "expired":
                status_item.setForeground(QColor("red"))
            elif status == "revoked":
                status_item.setForeground(QColor("gray"))
            self.activation_table.setItem(row, 1, status_item)

            # 创建时间
            created = info.get("created", "")
            if created:
                created_dt = datetime.fromisoformat(created)
                created_str = created_dt.strftime("%Y-%m-%d %H:%M")
            else:
                created_str = "未知"
            self.activation_table.setItem(row, 2, QTableWidgetItem(created_str))

            # 过期时间
            expires = info.get("expires", "")
            if expires:
                expire_dt = datetime.fromisoformat(expires)
                expire_str = expire_dt.strftime("%Y-%m-%d %H:%M")

                # 检查是否即将过期（7天内）
                days_left = (expire_dt - datetime.now()).days
                if 0 <= days_left <= 7:
                    expire_item = QTableWidgetItem(f"{expire_str} ({days_left}天后过期)")
                    expire_item.setForeground(QColor("orange"))
                elif days_left < 0:
                    expire_item = QTableWidgetItem(f"{expire_str} (已过期)")
                    expire_item.setForeground(QColor("red"))
                else:
                    expire_item = QTableWidgetItem(expire_str)
                self.activation_table.setItem(row, 3, expire_item)
            else:
                self.activation_table.setItem(row, 3, QTableWidgetItem("未知"))

            # 使用次数
            used_count = info.get("used_count", 0)
            self.activation_table.setItem(row, 4, QTableWidgetItem(str(used_count)))

            # 最大次数
            max_uses = info.get("max_uses", 1)
            self.activation_table.setItem(row, 5, QTableWidgetItem(str(max_uses)))

            # 设备数
            devices = info.get("devices", [])
            self.activation_table.setItem(row, 6, QTableWidgetItem(str(len(devices))))

        self.statusBar().showMessage(f"加载了 {len(activations)} 个激活码")

    def search_activations(self):
        """搜索激活码"""
        search_text = self.search_edit.text().strip().lower()
        if not search_text:
            # 显示所有
            for row in range(self.activation_table.rowCount()):
                self.activation_table.setRowHidden(row, False)
            return

        # 搜索激活码和设备ID
        for row in range(self.activation_table.rowCount()):
            code_item = self.activation_table.item(row, 0)
            if code_item and search_text in code_item.text().lower():
                self.activation_table.setRowHidden(row, False)
            else:
                self.activation_table.setRowHidden(row, True)

    def refresh_activations(self):
        """刷新激活码列表"""
        self.load_activations()
        self.search_edit.clear()
        self.statusBar().showMessage("已刷新")

    def show_context_menu(self, position):
        """显示右键菜单"""
        row = self.activation_table.rowAt(position.y())
        if row < 0:
            return

        code_item = self.activation_table.item(row, 0)
        if not code_item:
            return

        code = code_item.text()

        # 创建菜单
        menu = QMenu()

        # 查看详情
        view_action = QAction("查看详情", self)
        view_action.triggered.connect(lambda: self.view_activation_details(code))
        menu.addAction(view_action)

        # 延长有效期
        extend_action = QAction("延长有效期", self)
        extend_action.triggered.connect(lambda: self.extend_activation(code))
        menu.addAction(extend_action)

        # 撤销激活码
        revoke_action = QAction("撤销激活码", self)
        revoke_action.triggered.connect(lambda: self.revoke_activation(code))
        menu.addAction(revoke_action)

        menu.addSeparator()

        # 复制激活码
        copy_action = QAction("复制激活码", self)
        copy_action.triggered.connect(lambda: self.copy_activation_code(code))
        menu.addAction(copy_action)

        # 显示菜单
        menu.exec_(self.activation_table.viewport().mapToGlobal(position))

    def view_activation_details(self, code):
        """查看激活码详情"""
        info = self.activation_manager.get_activation_info(code)
        if not info:
            QMessageBox.warning(self, "错误", "激活码不存在！")
            return

        details = f"""
        <h3>激活码详情: {code}</h3>
        <table border="1" cellpadding="5">
        <tr><td><b>状态:</b></td><td>{info.get('status', 'unknown')}</td></tr>
        <tr><td><b>创建时间:</b></td><td>{info.get('created', '未知')}</td></tr>
        <tr><td><b>过期时间:</b></td><td>{info.get('expires', '未知')}</td></tr>
        <tr><td><b>使用次数:</b></td><td>{info.get('used_count', 0)} / {info.get('max_uses', 1)}</td></tr>
        <tr><td><b>设备数量:</b></td><td>{len(info.get('devices', []))}</td></tr>
        </table>
        """

        # 显示设备列表
        devices = info.get('devices', [])
        if devices:
            details += "<h4>已激活设备:</h4><ul>"
            for device in devices:
                details += f"<li>{device}</li>"
            details += "</ul>"

        self.details_display.setHtml(details)

    def extend_activation(self, code):
        """延长激活码有效期"""
        dialog = ExtendDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            days = dialog.get_days()
            if self.activation_manager.extend_activation(code, days):
                QMessageBox.information(self, "成功", f"已延长激活码 {days} 天")
                self.load_activations()
            else:
                QMessageBox.warning(self, "失败", "延长激活码失败！")

    def revoke_activation(self, code):
        """撤销激活码"""
        reply = QMessageBox.question(self, "确认撤销",
                                    f"确定要撤销激活码 {code} 吗？\n"
                                    "撤销后该激活码将无法再使用。",
                                    QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            if self.activation_manager.revoke_activation(code):
                QMessageBox.information(self, "成功", "激活码已撤销")
                self.load_activations()
            else:
                QMessageBox.warning(self, "失败", "撤销激活码失败！")

    def copy_activation_code(self, code):
        """复制激活码"""
        clipboard = QApplication.clipboard()
        clipboard.setText(code)
        self.statusBar().showMessage(f"已复制激活码: {code}")

    def refresh_stats(self):
        """刷新统计信息"""
        # 切换到统计标签页并刷新
        self.tab_widget.setCurrentIndex(2)
        # 这里可以重新加载统计信息
        self.statusBar().showMessage("统计信息已刷新")

class ExtendDialog(QDialog):
    """延长有效期对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("延长有效期")
        self.setFixedSize(300, 150)

        layout = QVBoxLayout()

        # 天数输入
        form_layout = QFormLayout()
        self.days_spin = QSpinBox()
        self.days_spin.setRange(1, 3650)
        self.days_spin.setValue(30)
        form_layout.addRow("延长天数:", self.days_spin)

        layout.addLayout(form_layout)

        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def get_days(self):
        """获取输入的天数"""
        return self.days_spin.value()

def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setApplicationName("激活码管理后台")
    app.setOrganizationName("TikuSoft")

    window = ActivationAdmin()
    window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()