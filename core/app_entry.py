

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
core/app_entry.py - 修改版
1. 增加全局单实例检测（防止多开）
2. 保持原有的授权与防护逻辑
"""

import sys
import time
import random
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QSharedMemory  # 必须导入

# 导入核心模块
from core.license_manager import LicenseManager
from core.protection import SoftwareProtector
from core.question_bank import QuestionBank
from ui.main_window import MainWindow
from ui.license_dialog import LicenseDialog

# 必须在全局定义，防止被垃圾回收
_shared_memory = None

def check_single_instance():
    """检查是否已有程序在运行"""
    global _shared_memory
    # 这个 ID 必须是全系统唯一的，建议包含你的软件名
    _shared_memory = QSharedMemory("TikuSoftware_Global_Unique_Lock")
    
    # 尝试附着到现有内存
    if _shared_memory.attach():
        # 如果附着成功，说明已经有一个实例在运行了
        return False
    
    # 如果附着失败，尝试创建它（证明我是第一个）
    if not _shared_memory.create(1):
        return False
    
    return True

def check_license():
    license_manager = LicenseManager("极智考典", "TikuSoft")
    if license_manager.is_activated():
        return True, license_manager.get_activation_info()
    return False, None

def show_license_dialog():
    dialog = LicenseDialog()
    if dialog.exec_() == LicenseDialog.Accepted:
        return True
    return False

def run_application():
    # 1. 初始化 Qt 应用
    app = QApplication(sys.argv)
    app.setApplicationName("极智考典")
    
    # --- 2. 关键：单实例检测 ---
    if not check_single_instance():
        # 这里使用独立的 QMessageBox，不依赖主窗口
        QMessageBox.warning(None, "程序已运行", 
                            "极智考典已经在运行中。\n\n"
                            "请在任务栏中查找并打开已运行的窗口。")
        sys.exit(0)

    # --- 3. 安全防护检查 (打包环境) ---
    if getattr(sys, 'frozen', False):
        try:
            protector = SoftwareProtector("极智考典")
            time.sleep(random.uniform(0.1, 0.3))
            check_results = protector.run_protection_checks()
            protector.apply_protection_response(check_results)
        except Exception:
            sys.exit(1)

    # --- 4. 授权验证 ---
    is_licensed, license_info = check_license()
    if not is_licensed:
        if not show_license_dialog():
            sys.exit(0)
        is_licensed, license_info = check_license()
        if not is_licensed:
            QMessageBox.warning(None, "错误", "授权验证失败，无法启动。")
            sys.exit(1)

    # --- 5. 启动主窗口 ---
    try:
        question_bank = QuestionBank(license_info)
        # 这里的 MainWindow 会包含 ExamListWindow
        window = MainWindow(question_bank)
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"启动错误: {e}")
        sys.exit(1)