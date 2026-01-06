#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
激活对话框
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox, QGroupBox,
                             QTextEdit, QFormLayout)
from PyQt5.QtCore import Qt, pyqtSignal
from core.activation import ActivationManager
import hashlib
import uuid
import os

class ActivationDialog(QDialog):
    """激活对话框"""

    activated = pyqtSignal(str)  # 激活成功信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.activation_manager = ActivationManager()
        self.device_id = self._get_device_fingerprint()
        self.init_ui()

    def _get_device_fingerprint(self):
        """获取设备指纹"""
        try:
            # 使用MAC地址和计算机名生成设备指纹
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                           for elements in range(0, 2*6, 2)][::-1])
            computer_name = os.environ.get('COMPUTERNAME', 'Unknown')
            fingerprint = hashlib.sha256(f"{mac}_{computer_name}".encode()).hexdigest()[:32]
            return fingerprint
        except:
            return "unknown_device"

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("软件激活")
        self.setFixedSize(500, 400)

        # 主布局
        main_layout = QVBoxLayout()

        # 说明信息
        info_group = QGroupBox("激活说明")
        info_layout = QVBoxLayout()
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setPlainText(
            "欢迎使用极智题典！\n\n"
            "本软件需要激活才能使用。\n\n"
            "激活步骤：\n"
            "1. 购买软件激活码\n"
            "2. 在下方输入激活码\n"
            "3. 点击'激活'按钮\n\n"
            "激活码格式：XXXX-XXXX-XXXX-XXXX\n"
            "激活后软件将绑定到当前设备。\n\n"
            "如需购买激活码，请联系软件提供商。"
        )
        info_text.setMaximumHeight(150)
        info_layout.addWidget(info_text)
        info_group.setLayout(info_layout)
        main_layout.addWidget(info_group)

        # 激活码输入
        form_group = QGroupBox("激活信息")
        form_layout = QFormLayout()

        self.activation_code_edit = QLineEdit()
        self.activation_code_edit.setPlaceholderText("请输入激活码（格式：XXXX-XXXX-XXXX-XXXX）")
        form_layout.addRow("激活码：", self.activation_code_edit)

        device_label = QLabel(self.device_id[:16] + "...")
        device_label.setToolTip(f"设备ID：{self.device_id}")
        form_layout.addRow("设备ID：", device_label)

        form_group.setLayout(form_layout)
        main_layout.addWidget(form_group)

        # 按钮区域
        button_layout = QHBoxLayout()

        self.activate_button = QPushButton("激活")
        self.activate_button.clicked.connect(self.activate)
        self.activate_button.setDefault(True)

        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(self.activate_button)
        button_layout.addWidget(self.cancel_button)

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def activate(self):
        """激活软件"""
        activation_code = self.activation_code_edit.text().strip().upper()

        # 验证激活码格式
        if not self._validate_activation_code(activation_code):
            QMessageBox.warning(self, "格式错误",
                               "激活码格式不正确！\n"
                               "正确格式：XXXX-XXXX-XXXX-XXXX")
            return

        # 尝试激活
        if self.activation_manager.activate_software(activation_code, self.device_id):
            QMessageBox.information(self, "激活成功",
                                   "软件激活成功！\n"
                                   "现在可以开始使用极智题典。")
            self.activated.emit(activation_code)
            self.accept()
        else:
            QMessageBox.critical(self, "激活失败",
                                "激活码无效或已过期！\n"
                                "请检查激活码是否正确，或联系软件提供商。")

    def _validate_activation_code(self, code):
        """验证激活码格式"""
        # 格式：XXXX-XXXX-XXXX-XXXX
        parts = code.split('-')
        if len(parts) != 4:
            return False

        for part in parts:
            if len(part) != 4:
                return False
            if not all(c.isalnum() for c in part):
                return False

        return True

    def keyPressEvent(self, event):
        """键盘事件处理"""
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.activate()
        elif event.key() == Qt.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)