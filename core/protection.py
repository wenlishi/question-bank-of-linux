#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
软件防护模块 - 防止反编译和破解
"""

import os
import sys
import hashlib
import time
import random
from datetime import datetime

# 尝试导入psutil，如果不可用则使用备用方案
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

class SoftwareProtector:
    """软件防护器"""

    def __init__(self, app_name="极智考典"):
        self.app_name = app_name
        self.start_time = time.time()
        self.obfuscation_key = self._generate_obfuscation_key()

        # 关键文件哈希值（打包后计算并硬编码）
        self.critical_files = {
            'license_manager.py': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',  # 空文件的SHA256
            'protection.py': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
        }

    def _generate_obfuscation_key(self):
        """生成混淆密钥（基于硬件信息）"""
        import uuid
        try:
            # 使用MAC地址和计算机名
            mac = uuid.getnode()
            computer_name = os.environ.get('COMPUTERNAME', 'Unknown')
            key_source = f"{mac}_{computer_name}_{self.app_name}"
            return hashlib.sha256(key_source.encode()).digest()
        except:
            # 备用方案
            return hashlib.sha256(b"default_protection_key").digest()

    def obfuscate_string(self, plaintext):
        """混淆字符串"""
        if not plaintext:
            return ""

        # 多层混淆
        result = []
        key = self.obfuscation_key

        # 第一层：XOR加密
        xor_encrypted = bytearray()
        for i, char in enumerate(plaintext.encode('utf-8')):
            xor_encrypted.append(char ^ key[i % len(key)])

        # 第二层：Base64编码
        import base64
        base64_encoded = base64.b64encode(xor_encrypted).decode('ascii')

        # 第三层：字符替换
        replace_map = {
            'A': 'Z', 'B': 'Y', 'C': 'X', 'D': 'W', 'E': 'V',
            'F': 'U', 'G': 'T', 'H': 'S', 'I': 'R', 'J': 'Q',
            'K': 'P', 'L': 'O', 'M': 'N', 'N': 'M', 'O': 'L',
            'P': 'K', 'Q': 'J', 'R': 'I', 'S': 'H', 'T': 'G',
            'U': 'F', 'V': 'E', 'W': 'D', 'X': 'C', 'Y': 'B',
            'Z': 'A',
            'a': 'z', 'b': 'y', 'c': 'x', 'd': 'w', 'e': 'v',
            'f': 'u', 'g': 't', 'h': 's', 'i': 'r', 'j': 'q',
            'k': 'p', 'l': 'o', 'm': 'n', 'n': 'm', 'o': 'l',
            'p': 'k', 'q': 'j', 'r': 'i', 's': 'h', 't': 'g',
            'u': 'f', 'v': 'e', 'w': 'd', 'x': 'c', 'y': 'b',
            'z': 'a'
        }

        replaced = ''.join(replace_map.get(c, c) for c in base64_encoded)

        # 第四层：插入随机字符
        final_result = []
        for i, char in enumerate(replaced):
            final_result.append(char)
            if i % 3 == 0:
                final_result.append(chr(random.randint(65, 90)))  # 随机大写字母

        return ''.join(final_result)

    def deobfuscate_string(self, obfuscated):
        """解混淆字符串"""
        if not obfuscated:
            return ""

        # 第四层：移除随机字符
        cleaned = []
        for i, char in enumerate(obfuscated):
            if i % 4 != 3:  # 每4个字符保留3个，跳过第4个（随机插入的）
                cleaned.append(char)
        step1 = ''.join(cleaned)

        # 第三层：字符替换还原
        replace_map = {v: k for k, v in {
            'A': 'Z', 'B': 'Y', 'C': 'X', 'D': 'W', 'E': 'V',
            'F': 'U', 'G': 'T', 'H': 'S', 'I': 'R', 'J': 'Q',
            'K': 'P', 'L': 'O', 'M': 'N', 'N': 'M', 'O': 'L',
            'P': 'K', 'Q': 'J', 'R': 'I', 'S': 'H', 'T': 'G',
            'U': 'F', 'V': 'E', 'W': 'D', 'X': 'C', 'Y': 'B',
            'Z': 'A',
            'a': 'z', 'b': 'y', 'c': 'x', 'd': 'w', 'e': 'v',
            'f': 'u', 'g': 't', 'h': 's', 'i': 'r', 'j': 'q',
            'k': 'p', 'l': 'o', 'm': 'n', 'n': 'm', 'o': 'l',
            'p': 'k', 'q': 'j', 'r': 'i', 's': 'h', 't': 'g',
            'u': 'f', 'v': 'e', 'w': 'd', 'x': 'c', 'y': 'b',
            'z': 'a'
        }.items()}

        step2 = ''.join(replace_map.get(c, c) for c in step1)

        # 第二层：Base64解码
        import base64
        try:
            step3 = base64.b64decode(step2)
        except:
            return "[解密失败]"

        # 第一层：XOR解密
        key = self.obfuscation_key
        decrypted = bytearray()
        for i, char in enumerate(step3):
            decrypted.append(char ^ key[i % len(key)])

        return decrypted.decode('utf-8', errors='ignore')

    def check_debugger(self):
        """检测调试器"""
        # 方法1：检查运行时间（调试时运行较慢）
        elapsed = time.time() - self.start_time
        if elapsed > 10:  # 如果启动时间超过10秒，可能在被调试
            return True

        # 方法2：检查调试器进程
        if PSUTIL_AVAILABLE:
            debuggers = ['ollydbg.exe', 'ida.exe', 'x64dbg.exe', 'windbg.exe',
                        'devenv.exe', 'pycharm.exe', 'vscode.exe']
            try:
                for proc in psutil.process_iter(['name']):
                    name = proc.info['name']
                    if name and any(debugger in name.lower() for debugger in debuggers):
                        return True
            except:
                pass

        # 方法3：检查父进程
        try:
            parent_pid = os.getppid()
            if parent_pid > 0 and PSUTIL_AVAILABLE:
                parent = psutil.Process(parent_pid)
                parent_name = parent.name().lower()
                if 'python' in parent_name or 'debug' in parent_name:
                    return True
        except:
            pass

        return False

    def check_virtual_machine(self):
        """检测虚拟机"""
        # 方法1：检查特定文件或注册表
        vm_indicators = [
            r"C:\Program Files\VMware",
            r"C:\Program Files\Oracle\VirtualBox",
            r"C:\Program Files (x86)\VMware",
            r"C:\Program Files (x86)\Oracle\VirtualBox"
        ]

        for indicator in vm_indicators:
            if os.path.exists(indicator):
                return True

        # 方法2：检查进程
        if PSUTIL_AVAILABLE:
            vm_processes = ['vmware.exe', 'vbox.exe', 'vboxtray.exe']
            try:
                for proc in psutil.process_iter(['name']):
                    name = proc.info['name']
                    if name and any(vm_proc in name.lower() for vm_proc in vm_processes):
                        return True
            except:
                pass

        return False

    def check_file_integrity(self):
        """检查文件完整性"""
        for filename, expected_hash in self.critical_files.items():
            filepath = os.path.join(os.path.dirname(__file__), filename)
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'rb') as f:
                        content = f.read()
                        actual_hash = hashlib.sha256(content).hexdigest()
                        if actual_hash != expected_hash:
                            return False, f"文件 {filename} 已被修改"
                except Exception as e:
                    return False, f"检查文件 {filename} 时出错: {e}"

        return True, "所有文件完整"

    def check_license_tampering(self, license_manager):
        """检查授权信息是否被篡改"""
        try:
            if not hasattr(license_manager, 'license_info'):
                return True, "无授权信息"

            license_info = license_manager.license_info
            if not license_info:
                return True, "无授权信息"

            # 检查必要字段
            required_fields = ['machine_code', 'license_code', 'issue_date']
            for field in required_fields:
                if field not in license_info:
                    return False, f"授权信息缺少字段: {field}"

            # 检查日期格式
            from datetime import datetime
            try:
                datetime.fromisoformat(license_info['issue_date'])
            except:
                return False, "授权日期格式错误"

            return True, "授权信息完整"
        except Exception as e:
            return False, f"检查授权信息时出错: {e}"

    def run_protection_checks(self, license_manager=None):
        """运行所有防护检查"""
        checks = []

        # 检查1：调试器检测
        if self.check_debugger():
            checks.append(("调试器检测", "FAIL", "检测到调试器运行"))
        else:
            checks.append(("调试器检测", "PASS", "未检测到调试器"))

        # 检查2：虚拟机检测
        if self.check_virtual_machine():
            checks.append(("虚拟机检测", "WARN", "可能在虚拟机中运行"))
        else:
            checks.append(("虚拟机检测", "PASS", "未检测到虚拟机"))

        # 检查3：文件完整性
        integrity_ok, integrity_msg = self.check_file_integrity()
        if integrity_ok:
            checks.append(("文件完整性", "PASS", integrity_msg))
        else:
            checks.append(("文件完整性", "FAIL", integrity_msg))

        # 检查4：授权信息完整性
        if license_manager:
            license_ok, license_msg = self.check_license_tampering(license_manager)
            if license_ok:
                checks.append(("授权完整性", "PASS", license_msg))
            else:
                checks.append(("授权完整性", "FAIL", license_msg))

        # 汇总结果
        failed_checks = [c for c in checks if c[1] == "FAIL"]
        warning_checks = [c for c in checks if c[1] == "WARN"]

        return {
            'checks': checks,
            'failed': failed_checks,
            'warnings': warning_checks,
            'all_passed': len(failed_checks) == 0
        }

    def apply_protection_response(self, check_results):
        """根据检查结果采取相应措施"""
        if not check_results['all_passed']:
            # 有严重失败，采取强硬措施
            failed_names = [c[0] for c in check_results['failed']]

            # 记录日志
            log_msg = f"防护检测失败: {', '.join(failed_names)}"
            self._log_security_event(log_msg)

            # 延迟响应（增加破解难度）
            time.sleep(random.uniform(1.0, 3.0))

            # 抛出异常或退出
            error_msg = "软件安全检查失败，请重新安装软件。"

            # 尝试使用混淆的错误消息
            obfuscated_msg = self.obfuscate_string(error_msg)
            print(f"安全错误: {obfuscated_msg}")

            # 退出程序
            sys.exit(1)

        elif check_results['warnings']:
            # 只有警告，记录日志但不阻止运行
            warning_names = [c[0] for c in check_results['warnings']]
            log_msg = f"防护检测警告: {', '.join(warning_names)}"
            self._log_security_event(log_msg)

    def _log_security_event(self, message):
        """记录安全事件"""
        try:
            log_dir = os.path.join(os.path.expanduser('~'), '.tikusoft', 'logs')
            os.makedirs(log_dir, exist_ok=True)

            log_file = os.path.join(log_dir, 'security.log')
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] {message}\n")
        except:
            pass  # 静默失败，不暴露错误