

# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# """
# LicenseGenerator.py
# 管理员工具 - 使用 RSA 私钥生成带签名的注册码
# """

# import sys
# import base64
# from datetime import datetime, timedelta
# from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
#                              QFormLayout, QLabel, QLineEdit, QSpinBox, 
#                              QPushButton, QTextEdit, QMessageBox, QGroupBox)
# from PyQt5.QtGui import QFont

# # RSA加密库
# try:
#     from Crypto.PublicKey import RSA
#     from Crypto.Signature import pkcs1_15
#     from Crypto.Hash import SHA256
#     RSA_AVAILABLE = True
# except ImportError:
#     RSA_AVAILABLE = False

# class LicenseGenerator(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("注册码生成器 (管理员)")
#         self.setGeometry(100, 100, 700, 600)
#         self.rsa_key = None
#         self.init_ui()
#         self.generate_new_keys() # 启动时自动生成或加载一对新密钥

#     def init_ui(self):
#         central = QWidget()
#         self.setCentralWidget(central)
#         layout = QVBoxLayout(central)

#         # 1. 密钥区域
#         key_group = QGroupBox("1. RSA 密钥管理")
#         key_layout = QVBoxLayout()
        
#         self.pub_key_edit = QTextEdit()
#         self.pub_key_edit.setPlaceholderText("公钥将显示在这里 (复制到客户端代码中)...")
#         self.pub_key_edit.setMaximumHeight(100)
#         key_layout.addWidget(QLabel("公钥 (Public Key):"))
#         key_layout.addWidget(self.pub_key_edit)
        
#         btn_regen = QPushButton("重新生成密钥对")
#         btn_regen.clicked.connect(self.generate_new_keys)
#         key_layout.addWidget(btn_regen)
        
#         key_group.setLayout(key_layout)
#         layout.addWidget(key_group)

#         # 2. 生成设置
#         form_group = QGroupBox("2. 生成授权")
#         form = QFormLayout()
        
#         self.input_machine = QLineEdit()
#         self.input_machine.setPlaceholderText("粘贴用户发来的机器码...")
#         form.addRow("机器码:", self.input_machine)
        
#         self.spin_days = QSpinBox()
#         self.spin_days.setRange(1, 36500)
#         self.spin_days.setValue(365)
#         form.addRow("有效期(天):", self.spin_days)
        
#         self.input_app = QLineEdit("TikuSoft")
#         form.addRow("应用名:", self.input_app)
        
#         btn_gen = QPushButton("生成注册码")
#         btn_gen.setFixedHeight(40)
#         btn_gen.setFont(QFont("Arial", 11, QFont.Bold))
#         btn_gen.clicked.connect(self.generate_license)
#         form.addRow(btn_gen)
        
#         form_group.setLayout(form)
#         layout.addWidget(form_group)

#         # 3. 结果显示
#         res_group = QGroupBox("3. 生成结果")
#         res_layout = QVBoxLayout()
#         self.result_area = QTextEdit()
#         self.result_area.setPlaceholderText("注册码将显示在这里...")
#         res_layout.addWidget(self.result_area)
        
#         btn_copy = QPushButton("复制注册码")
#         btn_copy.clicked.connect(lambda: QApplication.clipboard().setText(self.result_area.toPlainText()))
#         res_layout.addWidget(btn_copy)
        
#         res_group.setLayout(res_layout)
#         layout.addWidget(res_group)

#     def generate_new_keys(self):
#         """生成新的RSA密钥对"""
#         if not RSA_AVAILABLE:
#             self.result_area.setText("错误: 未安装 pycryptodome 库")
#             return
            
#         try:
#             self.rsa_key = RSA.generate(2048)
#             pub_key = self.rsa_key.publickey().export_key().decode()
#             self.pub_key_edit.setText(pub_key)
#             QMessageBox.information(self, "密钥已更新", "请务必将【公钥】复制并更新到客户端代码(LicenseManager.py)中！")
#         except Exception as e:
#             QMessageBox.critical(self, "错误", str(e))

#     def generate_license(self):
#         """生成带签名的注册码"""
#         machine_code = self.input_machine.text().strip().replace('-', '').upper()
#         days = self.spin_days.value()
#         app_name = self.input_app.text().strip()

#         if not machine_code or len(machine_code) != 32:
#             QMessageBox.warning(self, "错误", "机器码格式无效 (应为32位字符)")
#             return

#         if not self.rsa_key:
#             QMessageBox.warning(self, "错误", "密钥未初始化")
#             return

#         try:
#             # 1. 准备数据
#             expire_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
#             # 原始数据字符串
#             raw_data = f"{machine_code}|{expire_date}|{app_name}"
            
#             # 2. 计算哈希并签名 (使用私钥)
#             h = SHA256.new(raw_data.encode('utf-8'))
#             signature = pkcs1_15.new(self.rsa_key).sign(h)
#             sig_b64 = base64.b64encode(signature).decode()

#             # 3. 组合最终包: Base64(原始数据|签名)
#             # 这样客户端可以解包看到原始数据，然后用公钥验证签名
#             final_payload = f"{raw_data}|{sig_b64}"
#             license_code = base64.b64encode(final_payload.encode('utf-8')).decode()

#             self.result_area.setText(license_code)
            
#         except Exception as e:
#             self.result_area.setText(f"生成失败: {e}")

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     win = LicenseGenerator()
#     win.show()
#     sys.exit(app.exec_())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
商业版注册机 - 加载固定私钥
"""
import sys
import os
import base64
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QFormLayout, QLabel, QLineEdit, QSpinBox, 
                             QPushButton, QTextEdit, QMessageBox, QGroupBox, QFileDialog)
from PyQt5.QtGui import QFont

try:
    from Crypto.PublicKey import RSA
    from Crypto.Signature import pkcs1_15
    from Crypto.Hash import SHA256
    RSA_AVAILABLE = True
except ImportError:
    RSA_AVAILABLE = False

class LicenseGenerator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("商业版注册机 (固定私钥)")
        self.setGeometry(100, 100, 600, 500)
        
        # 初始化时加载私钥
        self.rsa_key = None
        self.load_fixed_private_key()
        
        self.init_ui()

 
    def load_fixed_private_key(self):
        """加载固定的私钥文件"""
        
        # === 修改开始 ===
        # 获取当前脚本(license_generator.py)所在的绝对目录
        # 这样无论你在根目录还是admin目录运行，它都能找到同级的文件
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 拼接完整路径：admin目录/private_key.pem
        key_path = os.path.join(current_dir, "private_key.pem")
        # === 修改结束 ===
        
        if os.path.exists(key_path):
            try:
                with open(key_path, 'r') as f:
                    self.rsa_key = RSA.import_key(f.read())
            except Exception as e:
                QMessageBox.critical(self, "错误", f"私钥文件损坏: {e}")
        else:
            # 如果没找到，提醒用户
            QMessageBox.warning(self, "未找到私钥", 
                                f"未找到文件：\n{key_path}\n\n" # 显示具体在找哪个路径
                                "请确保 private_key.pem 就在本程序代码的同一级目录下。")
    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # 状态显示
        status_group = QGroupBox("系统状态")
        status_layout = QVBoxLayout()
        if self.rsa_key:
            lbl = QLabel("✅ 私钥已加载 (准备就绪)")
            lbl.setStyleSheet("color: green; font-weight: bold;")
        else:
            lbl = QLabel("❌ 私钥未加载 (无法生成)")
            lbl.setStyleSheet("color: red; font-weight: bold;")
        status_layout.addWidget(lbl)
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

        # 生成表单
        form_group = QGroupBox("生成授权")
        form = QFormLayout()
        
        self.input_machine = QLineEdit()
        self.input_machine.setPlaceholderText("粘贴用户机器码...")
        form.addRow("机器码:", self.input_machine)
        
        self.spin_days = QSpinBox()
        self.spin_days.setRange(1, 36500)
        self.spin_days.setValue(365)
        form.addRow("有效期:", self.spin_days)
        
        self.input_app = QLineEdit("TikuSoft")
        form.addRow("应用名:", self.input_app)
        
        btn_gen = QPushButton("生成注册码")
        btn_gen.setFixedHeight(40)
        btn_gen.clicked.connect(self.generate_license)
        # 如果没有key，禁用按钮
        if not self.rsa_key:
            btn_gen.setEnabled(False)
            
        form.addRow(btn_gen)
        form_group.setLayout(form)
        layout.addWidget(form_group)

        # 结果区域
        self.result_area = QTextEdit()
        layout.addWidget(self.result_area)

    def generate_license(self):
        machine_code = self.input_machine.text().strip().replace('-', '').upper()
        days = self.spin_days.value()
        app_name = self.input_app.text().strip()

        if not self.rsa_key:
            return

        try:
            expire_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
            # 原始数据
            raw_data = f"{machine_code}|{expire_date}|{app_name}"
            
            # 签名
            h = SHA256.new(raw_data.encode('utf-8'))
            signature = pkcs1_15.new(self.rsa_key).sign(h)
            sig_b64 = base64.b64encode(signature).decode()

            # 组合最终注册码
            final_payload = f"{raw_data}|{sig_b64}"
            license_code = base64.b64encode(final_payload.encode('utf-8')).decode()

            self.result_area.setText(license_code)
            
        except Exception as e:
            self.result_area.setText(f"生成错误: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = LicenseGenerator()
    win.show()
    sys.exit(app.exec_())