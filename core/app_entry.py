# # #!/usr/bin/env python3
# # # -*- coding: utf-8 -*-
# # """
# # core/app_entry.py
# # 【核心加密文件】真正的程序入口逻辑
# # """

# # import sys
# # import time
# # import random
# # from PyQt5.QtWidgets import QApplication, QMessageBox
# # from core.license_manager import LicenseManager
# # from core.protection import SoftwareProtector
# # from core.question_bank import QuestionBank
# # from ui.new_main_window import MainWindow
# # from ui.license_dialog import LicenseDialog

# # def check_license():
# #     """检查授权状态"""
# #     license_manager = LicenseManager("极智题典", "TikuSoft")
# #     if license_manager.is_activated():
# #         # 【关键点】返回授权信息，里面包含解密题库需要的因子（可选）
# #         return True, license_manager.get_activation_info()
# #     return False, {"message": "软件未激活"}

# # def show_license_dialog():
# #     dialog = LicenseDialog()
# #     if dialog.exec_() == LicenseDialog.Accepted:
# #         return True
# #     return False

# # def run_application():
# #     """
# #     启动应用程序
# #     这个函数将被 PyArmor 加密，黑客无法修改内部的 if 判断
# #     """
# #     app = QApplication(sys.argv)
# #     app.setApplicationName("极智题典")
# #     app.setOrganizationName("TikuSoft")

# #     # --- 1. 防护检查 ---
# #     # (此处省略 SoftwareProtector 代码，保持你原有的即可)
    
# #     # --- 2. 授权检查 ---
# #     is_licensed, license_info = check_license()

# #     if not is_licensed:
# #         # 第一次尝试激活
# #         if not show_license_dialog():
# #             sys.exit(0) # 用户取消激活，直接退出
        
# #         # 再次检查
# #         is_licensed, license_info = check_license()
# #         if not is_licensed:
# #             QMessageBox.warning(None, "错误", "授权验证失败")
# #             sys.exit(1)

# #     # --- 3. 启动主窗口 ---
# #     # 只有代码运行到这里，且 is_licensed 为真，才能启动
# #     # 黑客无法修改这个文件的字节码来跳过上面的 if
    
# #     question_bank = QuestionBank()
# #     window = MainWindow(question_bank)
# #     window.show()

# #     sys.exit(app.exec_())

# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-

# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# """
# core/app_entry.py
# 【核心加密文件】真正的程序入口逻辑
# 此文件将被 PyArmor 加密，包含防护检查、授权验证和逻辑耦合初始化
# """

# import sys
# import time
# import random
# from PyQt5.QtWidgets import QApplication, QMessageBox

# # 导入核心模块
# from core.license_manager import LicenseManager
# from core.protection import SoftwareProtector
# from core.question_bank import QuestionBank
# from ui.new_main_window import MainWindow
# from ui.license_dialog import LicenseDialog

# def check_license():
#     """
#     检查授权状态
#     返回: (is_activated, license_info_dict)
#     """
#     license_manager = LicenseManager("极智题典", "TikuSoft")
    
#     # 检查是否已激活
#     if license_manager.is_activated():
#         # 【关键点】获取详细的授权信息（包含机器码等）
#         # 这些信息将作为“密钥”传递给题库
#         return True, license_manager.get_activation_info()
    
#     return False, None

# def show_license_dialog():
#     """显示激活对话框"""
#     dialog = LicenseDialog()
#     if dialog.exec_() == LicenseDialog.Accepted:
#         return True
#     return False

# def run_application():
#     """
#     启动应用程序的主逻辑
#     """
#     # 1. 初始化 Qt 应用
#     app = QApplication(sys.argv)
#     app.setApplicationName("极智题典")
#     app.setOrganizationName("TikuSoft")

#     # --- 2. 安全防护检查 (区分开发环境与打包环境) ---
#     # getattr(sys, 'frozen', False) 是 PyInstaller 打包后的特征标志
#     if getattr(sys, 'frozen', False):
#         # 【打包环境】：启用严格防护
#         try:
#             protector = SoftwareProtector("极智题典")
            
#             # 随机延迟，对抗时间分析
#             time.sleep(random.uniform(0.1, 0.5))
            
#             # 运行检查
#             check_results = protector.run_protection_checks()
            
#             # 如果发现威胁，protector 内部会处理（如退出或报错）
#             protector.apply_protection_response(check_results)
            
#         except Exception:
#             # 防护模块报错时静默退出
#             sys.exit(1)
#     else:
#         # 【开发环境】：跳过防护
#         print("【开发模式】检测到源码运行，已自动跳过 SoftwareProtector 防护检查...")

#     # --- 3. 授权验证 (License Check) ---
#     is_licensed, license_info = check_license()

#     if not is_licensed:
#         # 如果未授权，弹出激活框
#         if not show_license_dialog():
#             # 用户点击取消，直接退出
#             sys.exit(0)
        
#         # 用户尝试激活后，再次检查状态
#         # 必须重新获取 license_info，因为刚才的激活可能生成了新文件
#         is_licensed, license_info = check_license()
        
#         if not is_licensed:
#             QMessageBox.warning(None, "错误", "授权验证失败，无法启动。")
#             sys.exit(1)

#     # --- 4. 启动主窗口 (逻辑耦合关键点) ---
    
#     # 【逻辑耦合防护】
#     # 我们将 license_info 传递给 QuestionBank。
#     # 如果黑客通过修改字节码跳过了上面的 if not is_licensed 判断，
#     # 这里的 license_info 将是 None 或无效值。
#     # 导致 QuestionBank 初始化时的解密因子计算为 0，从而加载乱码数据。
    
#     try:
#         question_bank = QuestionBank(license_info)
        
#         # 创建并显示主窗口
#         window = MainWindow(question_bank)
#         window.show()

#         # 进入事件循环
#         sys.exit(app.exec_())
        
#     except Exception as e:
#         # 兜底错误处理
#         print(f"启动错误: {e}")
#         # 在开发模式下打印堆栈方便调试
#         if not getattr(sys, 'frozen', False):
#             import traceback
#             traceback.print_exc()
#         sys.exit(1)

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
    license_manager = LicenseManager("极智题典", "TikuSoft")
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
    app.setApplicationName("极智题典")
    
    # --- 2. 关键：单实例检测 ---
    if not check_single_instance():
        # 这里使用独立的 QMessageBox，不依赖主窗口
        QMessageBox.warning(None, "程序已运行", 
                            "极智题典已经在运行中。\n\n"
                            "请在任务栏中查找并打开已运行的窗口。")
        sys.exit(0)

    # --- 3. 安全防护检查 (打包环境) ---
    if getattr(sys, 'frozen', False):
        try:
            protector = SoftwareProtector("极智题典")
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