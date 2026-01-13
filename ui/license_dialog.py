#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新版授权对话框 - 术语优化版 (用户友好型)
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox, QGroupBox,
                             QTextEdit, QFormLayout, QTextBrowser, 
                             QWidget, QFrame, QApplication)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont
from core.license_manager import LicenseManager

class LicenseDialog(QDialog):
    """授权对话框"""

    licensed = pyqtSignal(str)  # 授权成功信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.license_manager = LicenseManager("极智考典", "TikuSoft")
        self.machine_code = self.license_manager.get_machine_code()
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("软件激活")
        self.setFixedSize(600, 560) 

        # 主布局
        main_layout = QVBoxLayout()

        # 标题
        title_label = QLabel("欢迎使用极智考典！")
        title_label.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)

        # 说明信息
        info_group = QGroupBox("激活步骤")
        info_layout = QVBoxLayout()
        # 【修改点】文案去技术化
        info_text = QLabel(
            "1. 点击下方按钮复制您的【申请码】并发送给客服。\n"
            "2. 客服将为您提供专属的【激活码】。\n"
            "3. 将激活码粘贴到下方输入框中，点击“立即激活”即可。"
        )
        info_text.setStyleSheet("color: #555; line-height: 24px; font-size: 13px;")
        info_layout.addWidget(info_text)
        info_group.setLayout(info_layout)
        main_layout.addWidget(info_group)

        # 申请码区域 (原机器码)
        # 【修改点】改为“申请码”
        machine_group = QGroupBox("第一步：获取申请码")
        machine_layout = QHBoxLayout() 

        machine_display = QLineEdit() 
        machine_display.setText(self.machine_code)
        machine_display.setReadOnly(True)
        machine_display.setStyleSheet("background: #f0f0f0; padding: 5px; border: 1px solid #ccc; color: #666;")
        machine_display.setFont(QFont("Consolas", 10))

        copy_machine_btn = QPushButton("复制")
        copy_machine_btn.setCursor(Qt.PointingHandCursor)
        copy_machine_btn.setFixedSize(80, 32)
        copy_machine_btn.setStyleSheet("""
            QPushButton { background-color: #007bff; color: white; border-radius: 3px; font-family: "Microsoft YaHei"; }
            QPushButton:hover { background-color: #0056b3; }
        """)
        copy_machine_btn.clicked.connect(self.copy_machine_code)

        machine_layout.addWidget(machine_display)
        machine_layout.addWidget(copy_machine_btn)
        machine_group.setLayout(machine_layout)
        main_layout.addWidget(machine_group)

        # 激活码输入区域 (原注册码)
        # 【修改点】改为“激活码”
        license_group = QGroupBox("第二步：输入激活码")
        license_layout = QVBoxLayout()

        self.license_code_edit = QTextEdit()
        # 【修改点】提示文案优化
        self.license_code_edit.setPlaceholderText("在此处粘贴客服发送给您的完整激活码...")
        self.license_code_edit.setFont(QFont("Consolas", 9))
        self.license_code_edit.setAcceptRichText(False)
        self.license_code_edit.setStyleSheet("border: 1px solid #ccc; border-radius: 3px;")
        license_layout.addWidget(self.license_code_edit)

        license_group.setLayout(license_layout)
        main_layout.addWidget(license_group)

        # 按钮区域
        button_layout = QHBoxLayout()
        self.activate_button = QPushButton("立即激活")
        self.activate_button.clicked.connect(self.activate_license)
        self.activate_button.setCursor(Qt.PointingHandCursor)
        self.activate_button.setFixedSize(140, 45)
        # 按钮样式美化
        self.activate_button.setStyleSheet("""
            QPushButton { 
                background-color: #28a745; 
                color: white; 
                font-weight: bold; 
                border-radius: 5px; 
                font-size: 15px; 
                font-family: "Microsoft YaHei";
            }
            QPushButton:hover { background-color: #218838; }
            QPushButton:disabled { background-color: #94d3a2; }
        """)

        self.cancel_button = QPushButton("稍后激活")
        self.cancel_button.setCursor(Qt.PointingHandCursor)
        self.cancel_button.setFixedSize(100, 45)
        self.cancel_button.setStyleSheet("""
            QPushButton { 
                background-color: #f8f9fa; 
                color: #333; 
                border: 1px solid #ddd;
                border-radius: 5px; 
                font-size: 14px; 
                font-family: "Microsoft YaHei";
            }
            QPushButton:hover { background-color: #e2e6ea; }
        """)
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(self.activate_button)
        button_layout.addWidget(self.cancel_button)
        button_layout.addStretch()

        main_layout.addLayout(button_layout)

        # 状态信息
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-family: 'Microsoft YaHei';")
        main_layout.addWidget(self.status_label)

        self.setLayout(main_layout)

    def copy_machine_code(self):
        """复制申请码"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.machine_code)
        # 【修改点】提示文案
        self.status_label.setText("申请码已复制，请发送给客服 ✓")
        self.status_label.setStyleSheet("color: green; font-weight: bold;")
        QTimer.singleShot(3000, lambda: self.status_label.setText(""))

    def activate_license(self):
        """执行激活逻辑"""
        # 获取输入内容 (去除首尾空格)
        license_code = self.license_code_edit.toPlainText().strip()

        # 【修改点】提示文案
        if len(license_code) < 50: 
            QMessageBox.warning(self, "提示", "激活码格式似乎不完整，请检查是否复制了全部内容。")
            return

        self.activate_button.setEnabled(False)
        self.activate_button.setText("验证中...")
        self.status_label.setText("正在连接验证...")
        
        # 为了让界面刷新，给一点点延时体验（可选，这里直接调用）
        # 调用核心验证
        success, message = self.license_manager.verify_license(license_code)

        if success:
            self.status_label.setText("激活成功")
            QMessageBox.information(self, "欢迎", f"软件激活成功！\n\n{message}\n\n祝您使用愉快！")
            self.licensed.emit(license_code)
            self.accept()
        else:
            self.status_label.setText("激活失败")
            self.status_label.setStyleSheet("color: #dc3545; font-weight: bold;")
            QMessageBox.critical(self, "激活失败", f"无效的激活码。\n\n错误信息：{message}\n\n请联系客服核对。")
            self.activate_button.setEnabled(True)
            self.activate_button.setText("立即激活")

    def _validate_license_code(self, code):
        return True