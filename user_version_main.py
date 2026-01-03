#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户版本主程序
只有做题功能，没有导入功能
"""

import sys
import os
from core.activation import ActivationManager
from core.question_bank import QuestionBank
from ui.main_window import MainWindow
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QSettings
import hashlib
import uuid

def get_device_fingerprint():
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

def check_activation():
    """检查激活状态"""
    settings = QSettings("TikuSoft", "TikuQuestionBank")
    activation_manager = ActivationManager()

    # 检查是否已激活
    is_activated = settings.value("activated", False, type=bool)
    activation_code = settings.value("activation_code", "")

    if is_activated and activation_code:
        # 验证激活码是否有效
        device_id = get_device_fingerprint()
        if activation_manager.verify_activation(activation_code, device_id):
            return True

    return False

def show_activation_dialog():
    """显示激活对话框"""
    from ui.activation_dialog import ActivationDialog

    app = QApplication.instance() or QApplication(sys.argv)
    dialog = ActivationDialog()
    result = dialog.exec_()

    if result == ActivationDialog.Accepted:
        return True
    return False

def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setApplicationName("题库刷题软件")
    app.setOrganizationName("TikuSoft")

    # 检查激活状态
    if not check_activation():
        if not show_activation_dialog():
            QMessageBox.warning(None, "激活失败",
                               "软件需要激活才能使用。\n请购买激活码后重新启动软件。")
            sys.exit(1)

    # 初始化题目库
    question_bank = QuestionBank()

    # 创建主窗口
    window = MainWindow(question_bank)

    # 移除用户不需要的功能
    window.setWindowTitle("题库刷题软件 - 用户版")

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()