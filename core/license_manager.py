

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
core/license_manager.py
集成 AES 加密文件存储、RSA 签名验证、NTP 对时、防时间回滚
"""

import os
import sys
import json
import hashlib
import uuid
import base64
import platform
import subprocess
import socket
import struct
from typing import Tuple, Dict, Optional
from datetime import datetime, timedelta

# 加密库依赖
try:
    from Crypto.PublicKey import RSA
    from Crypto.Signature import pkcs1_15
    from Crypto.Hash import SHA256
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad, unpad
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("严重错误: 未安装 pycryptodome，授权功能将失效！")

class LicenseManager:
    """
    授权管理器 (AES 加密增强版)
    """

    # [1] RSA 公钥 (用于验证激活码签名)
    # 这里的 _K_DATA 是原本 PEM 文件的 ASCII 码值列表
    _K_DATA = [
        45, 45, 45, 45, 45, 66, 69, 71, 73, 78, 32, 80, 85, 66, 76, 73, 67, 32, 75, 69, 89, 45, 45, 45, 45, 45, 10, 
        77, 73, 73, 66, 73, 106, 65, 78, 66, 103, 107, 113, 104, 107, 105, 71, 57, 119, 48, 66, 65, 81, 69, 70, 65, 65, 79, 67, 65, 81, 56, 65, 77, 73, 73, 66, 67, 103, 75, 67, 65, 81, 69, 65, 116, 101, 80, 71, 66, 104, 103, 114, 79, 103, 122, 47, 120, 78, 113, 57, 77, 99, 78, 87, 10, 86, 82, 66, 84, 73, 71, 66, 56, 102, 70, 121, 79, 86, 81, 53, 86, 101, 43, 122, 103, 84, 104, 103, 47, 54, 78, 113, 88, 72, 48, 121, 122, 98, 75, 117, 47, 70, 84, 69, 49, 115, 72, 43, 43, 52, 68, 98, 74, 77, 86, 70, 55, 103, 85, 97, 84, 71, 80, 51, 71, 119, 113, 88, 89, 10, 106, 43, 56, 119, 53, 118, 80, 75, 79, 69, 66, 69, 70, 98, 101, 97, 110, 85, 107, 56, 49, 108, 119, 65, 52, 78, 87, 99, 75, 47, 76, 109, 67, 47, 116, 72, 43, 122, 48, 82, 87, 75, 56, 83, 48, 48, 74, 74, 49, 103, 110, 51, 52, 114, 119, 49, 68, 80, 76, 107, 111, 57, 100, 82, 10, 100, 78, 117, 113, 88, 82, 75, 51, 85, 43, 66, 89, 80, 78, 102, 77, 47, 100, 72, 43, 101, 104, 116, 57, 49, 100, 82, 107, 81, 113, 101, 106, 115, 101, 73, 102, 97, 90, 87, 111, 76, 43, 71, 79, 119, 106, 71, 88, 49, 54, 98, 111, 88, 114, 72, 111, 121, 73, 67, 50, 122, 111, 78, 120, 10, 81, 87, 112, 90, 79, 120, 107, 47, 104, 50, 51, 57, 55, 86, 43, 74, 108, 70, 100, 66, 114, 76, 54, 88, 56, 112, 47, 47, 72, 101, 67, 50, 71, 106, 51, 117, 108, 67, 113, 102, 83, 71, 74, 110, 83, 66, 83, 70, 83, 57, 69, 105, 105, 107, 97, 101, 85, 66, 109, 97, 73, 83, 66, 10, 70, 70, 51, 105, 76, 121, 56, 90, 110, 78, 71, 76, 70, 65, 54, 122, 120, 105, 115, 72, 54, 55, 114, 65, 57, 79, 100, 79, 84, 88, 110, 47, 73, 43, 78, 89, 107, 54, 86, 100, 68, 112, 75, 101, 118, 77, 99, 53, 108, 86, 73, 65, 69, 90, 79, 68, 87, 107, 107, 89, 70, 116, 98, 75, 10, 83, 81, 73, 68, 65, 81, 65, 66, 10, 45, 45, 45, 45, 45, 69, 78, 68, 32, 80, 85, 66, 76, 73, 67, 32, 75, 69, 89, 45, 45, 45, 45, 45
    ]

    # [2] AES 内部密钥 (混淆核心：请保持 16/24/32 位长度)
    # 这不是用来验签的，是用来加密本地 license.lic 文件的
    # 建议你在发布前随机修改这个字符串
    # 使用 hashlib.sha256 确保生成的密钥长度严格为 32 字节 (AES-256)
    # 这样你就不用去数手指头计算字符长度了
    _INTERNAL_K = hashlib.sha256(b'TikuSoft_Secret_Key_2024_@Admin').digest()
    
    # NTP 服务器
    NTP_SERVERS = ['ntp.aliyun.com', 'ntp.tencent.com', 'pool.ntp.org']

    def __init__(self, app_name="TikuSoft", company_name="TikuQuestionBank"):
        self.app_name = app_name
        self.company_name = company_name
        self.license_dir = self._get_license_dir()
        self.license_file = os.path.join(self.license_dir, "license.lic")
        
        if not os.path.exists(self.license_dir):
            try:
                os.makedirs(self.license_dir)
            except OSError: pass

        self.public_key = self._restore_and_load_key()
        self.license_info = self._load_license_file()

    def _get_license_dir(self):
        """获取存储路径"""
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        try:
            from PyQt5.QtCore import QStandardPaths
            data_dir = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
            return os.path.join(data_dir, self.company_name, self.app_name)
        except ImportError:
            return os.path.join(os.path.expanduser("~"), f".{self.app_name}")

    def _restore_and_load_key(self):
        """还原混淆的 RSA 公钥"""
        if not CRYPTO_AVAILABLE: return None
        try:
            return RSA.import_key(bytes(self._K_DATA).decode('utf-8'))
        except: return None

    # === AES 加密/解密核心方法 (保护本地文件不被篡改) ===
    def _encrypt_data(self, data_dict: Dict) -> str:
        """将字典加密为 Base64 字符串"""
        try:
            # 1. 转 JSON
            json_bytes = json.dumps(data_dict).encode('utf-8')
            # 2. 生成随机 IV (16字节)
            iv = os.urandom(16)
            # 3. AES 加密
            cipher = AES.new(self._INTERNAL_K, AES.MODE_CBC, iv)
            encrypted_bytes = cipher.encrypt(pad(json_bytes, AES.block_size))
            # 4. 组合 IV + 密文，并转 Base64
            combined = iv + encrypted_bytes
            return base64.b64encode(combined).decode('utf-8')
        except Exception as e:
            print(f"Encryption error: {e}")
            return ""

    def _decrypt_data(self, encrypted_str: str) -> Dict:
        """将加密字符串解密为字典"""
        if not encrypted_str: return {}
        try:
            # 1. Base64 解码
            combined = base64.b64decode(encrypted_str)
            # 2. 提取 IV 和 密文
            iv = combined[:16]
            encrypted_bytes = combined[16:]
            # 3. AES 解密
            cipher = AES.new(self._INTERNAL_K, AES.MODE_CBC, iv)
            decrypted_bytes = unpad(cipher.decrypt(encrypted_bytes), AES.block_size)
            # 4. 转回字典
            return json.loads(decrypted_bytes.decode('utf-8'))
        except Exception:
            # 如果解密失败（可能是文件被篡改），返回空字典
            return {}

    def _load_license_file(self) -> Dict:
        """读取并解密本地授权文件"""
        if os.path.exists(self.license_file):
            try:
                with open(self.license_file, 'r', encoding='utf-8') as f:
                    encrypted_content = f.read()
                    # 尝试解密
                    return self._decrypt_data(encrypted_content)
            except Exception:
                pass
        return {}

    def get_machine_code(self) -> str:
        """获取机器码"""
        # 为节省篇幅，此处简化，请使用你之前完整的机器码获取逻辑
        components = [f"Generic:{uuid.getnode()}"]
        try:
            if platform.system() == "Windows":
                 components.append("WIN_ID") # 替换为真实逻辑
        except: pass
        raw = "|".join(components)
        h = hashlib.sha256(raw.encode()).hexdigest().upper()
        return '-'.join([h[i:i+4] for i in range(0, 32, 4)])

    def get_network_time(self) -> Optional[datetime]:
        """从 NTP 获取网络时间"""
        for server in self.NTP_SERVERS:
            try:
                client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                client.settimeout(1.5)
                data = b'\x1b' + 47 * b'\0'
                client.sendto(data, (server, 123))
                data, address = client.recvfrom(1024)
                if data:
                    t = struct.unpack('!12I', data)[10] - 2208988800
                    client.close()
                    return datetime.fromtimestamp(t)
                client.close()
            except: continue
        return None

    def verify_license(self, license_code: str = None) -> Tuple[bool, str]:
        """核心验证逻辑"""
        if not license_code:
            license_code = self.license_info.get('license_code', '')
        
        if not license_code:
            return False, "未激活"

        try:
            # 1. 获取时间 (优先网络)
            net_time = self.get_network_time()
            if net_time:
                current_time = net_time
                time_source = "network"
            else:
                current_time = datetime.now()
                time_source = "local"
                
                # [防回滚] 检查 last_run_at
                last_run_str = self.license_info.get('last_run_at')
                if last_run_str:
                    try:
                        last_run_dt = datetime.fromisoformat(last_run_str)
                        # 如果当前时间早于上次运行时间 (放宽10分钟容差)
                        if current_time < (last_run_dt - timedelta(minutes=10)):
                            return False, "系统时间异常，请连接网络校准"
                    except: pass

            # 2. 解码与验签
            missing_padding = len(license_code) % 4
            if missing_padding: license_code += '=' * (4 - missing_padding)
            decoded_bytes = base64.b64decode(license_code)
            rec_machine_code, rec_expire_date, rec_app_name, rec_sig_b64 = decoded_bytes.decode('utf-8').split('|')
            
            # 3. 校验机器码
            if rec_machine_code != self.get_machine_code().replace('-', '').upper():
                return False, "机器码不匹配，授权无效"
            
            # 4. RSA 验签
            if CRYPTO_AVAILABLE and self.public_key:
                data_to_verify = f"{rec_machine_code}|{rec_expire_date}|{rec_app_name}".encode('utf-8')
                h = SHA256.new(data_to_verify)
                try:
                    pkcs1_15.new(self.public_key).verify(h, base64.b64decode(rec_sig_b64))
                except: return False, "非法注册码 (签名验证失败)"

            # 5. 校验过期时间
            expire_dt = datetime.strptime(rec_expire_date, '%Y-%m-%d')
            expire_dt_end = expire_dt.replace(hour=23, minute=59, second=59)
            
            if current_time > expire_dt_end:
                return False, f"授权已于 {rec_expire_date} 过期"

            # 6. 验证成功，保存加密文件 (更新 last_run_at)
            self.save_license(license_code, rec_expire_date, current_time)
            return True, f"激活成功 (有效期至 {rec_expire_date})"

        except Exception as e:
            # print(e)
            return False, "验证过程异常"

    def save_license(self, code: str, expire_date: str, current_run_dt: datetime):
        """加密并保存授权文件"""
        data = {
            "license_code": code,
            "expire_date": expire_date,
            "machine_code": self.get_machine_code(),
            "updated_at": datetime.now().isoformat(),
            "last_run_at": current_run_dt.isoformat() # 关键防回滚数据
        }
        
        try:
            # 这里调用 AES 加密
            encrypted_content = self._encrypt_data(data)
            with open(self.license_file, 'w', encoding='utf-8') as f:
                f.write(encrypted_content)
            
            # 内存中保留明文副本，方便快速读取
            self.license_info = data
        except Exception as e:
            print(f"授权文件保存失败: {e}")

    def is_activated(self) -> bool:
        s, _ = self.verify_license()
        return s

    def get_activation_info(self) -> Dict:
        info = self.license_info.copy()
        is_active, msg = self.verify_license()
        info['activated'] = is_active
        info['message'] = msg
        info['days_left'] = 0
        if is_active and 'expire_date' in info:
            try:
                expire = datetime.strptime(info['expire_date'], '%Y-%m-%d')
                info['days_left'] = max(0, (expire - datetime.now()).days + 1)
            except: pass
        return info

if __name__ == "__main__":
    lm = LicenseManager()
    print(f"机器码: {lm.get_machine_code()}")
    
    # 测试文件加密效果
    if os.path.exists(lm.license_file):
        print(f"\n[安全检查] license.lic 文件内容预览:")
        with open(lm.license_file, 'r') as f:
            content = f.read()
            print(f"{content[:50]}...") # 应该显示一堆乱码，而不是 {"license_code":...}
            if content.startswith("{"):
                print("警告: 文件未加密！")
            else:
                print("成功: 文件已加密。")
    
    status, msg = lm.verify_license()
    print(f"\n验证结果: {msg}")