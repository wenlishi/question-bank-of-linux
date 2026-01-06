#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
core/license_manager.py
客户端授权管理器 - 修复版 (包含 get_activation_info)
"""

import os
import sys
import json
import hashlib
import uuid
import base64
import platform
import subprocess
from datetime import datetime
from PyQt5.QtCore import QSettings

# RSA加密相关
try:
    from Crypto.PublicKey import RSA
    from Crypto.Signature import pkcs1_15
    from Crypto.Hash import SHA256
    RSA_AVAILABLE = True
except ImportError:
    RSA_AVAILABLE = False
    print("严重警告: 未安装 pycryptodome，无法进行安全验证！")

class LicenseManager:
    """授权管理器"""

    # 【重要】请将注册机生成的【公钥】粘贴在这里
    # 必须与注册机用的私钥配对
    PUBLIC_KEY_PEM = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAtePGBhgrOgz/xNq9McNW
VRBTIGB8fFyOVQ5Ve+zgThg/6NqXH0yzbKu/FTE1sH++4DbJMVF7gUaTGP3GwqXY
j+8w5vPKOEBEFbeanUk81lwA4NWcK/LmC/tH+z0RWK8S00JJ1gn34rw1DPLko9dR
dNuqXRK3U+BYPNfM/dH+eht91dRkQqejseIfaZWoL+GOwjGX16boXrHoyIC2zoNx
QWpZOxk/h2397V+JlFdBrL6X8p//HeC2GjJ3ulCqfSGJnSBSFS9EiikaeUBmaISB
FF3iLy8ZnNGLFA6zxisH67rA9OdOTXn/I+NYk6VdDpKevMc5lVIAEZODWkkYFtbK
SQIDAQAB
-----END PUBLIC KEY-----"""

    def __init__(self, app_name="TikuSoft", company_name="TikuQuestionBank"):
        self.app_name = app_name
        self.company_name = company_name
        
        # 路径处理
        self.license_dir = self._get_license_dir()
        self.license_file = os.path.join(self.license_dir, "license.lic")
        
        if not os.path.exists(self.license_dir):
            os.makedirs(self.license_dir)

        # 加载公钥
        self.public_key = self._load_public_key()
        
        # 加载本地已保存的授权
        self.license_info = self._load_license_file()

    def _get_license_dir(self):
        """获取存储路径"""
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        from PyQt5.QtCore import QStandardPaths
        data_dir = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
        return os.path.join(data_dir, self.company_name, self.app_name)

    def _load_public_key(self):
        """加载公钥"""
        if RSA_AVAILABLE and self.PUBLIC_KEY_PEM:
            try:
                # 处理可能粘贴带来的格式问题
                key_str = self.PUBLIC_KEY_PEM.strip()
                return RSA.import_key(key_str)
            except Exception as e:
                print(f"公钥加载失败: {e}")
        return None

    def _load_license_file(self):
        """读取本地授权文件"""
        if os.path.exists(self.license_file):
            try:
                with open(self.license_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {}

    def get_machine_code(self):
        """获取机器码 (跨平台安全版)"""
        components = []
        
        try:
            # 1. 平台特定ID
            system = platform.system()
            if system == "Windows":
                cmd = "wmic cpu get processorid"
                try:
                    cpu_id = subprocess.check_output(cmd, shell=True).decode().split('\n')[1].strip()
                    components.append(f"WIN_CPU:{cpu_id}")
                except: pass
                
                cmd = "wmic baseboard get serialnumber"
                try:
                    mb_id = subprocess.check_output(cmd, shell=True).decode().split('\n')[1].strip()
                    components.append(f"WIN_MB:{mb_id}")
                except: pass
                
            elif system == "Linux":
                if os.path.exists("/etc/machine-id"):
                    with open("/etc/machine-id", "r") as f:
                        components.append(f"LIN_ID:{f.read().strip()}")
                else:
                    mac = uuid.getnode()
                    components.append(f"MAC:{mac}")
            else:
                components.append(f"GENERIC:{uuid.getnode()}")

        except Exception as e:
            print(f"硬件信息获取失败: {e}")
            components.append(f"FALLBACK:{uuid.getnode()}")

        # 生成哈希
        raw_info = "|".join(components)
        machine_hash = hashlib.sha256(raw_info.encode()).hexdigest().upper()
        return '-'.join([machine_hash[i:i+4] for i in range(0, 32, 4)])

    def verify_license(self, license_code=None):
        """验证授权核心逻辑 (公钥验签)"""
        if not license_code:
            license_code = self.license_info.get('license_code', '')
        
        if not license_code:
            return False, "未激活"

        try:
            # 1. Base64 解码大包
            decoded_bytes = base64.b64decode(license_code)
            decoded_str = decoded_bytes.decode('utf-8')
            
            # 2. 拆分数据
            parts = decoded_str.split('|')
            if len(parts) != 4:
                return False, "注册码格式错误"
            
            rec_machine_code, rec_expire_date, rec_app_name, rec_sig_b64 = parts
            
            # 3. 验证机器码
            current_machine = self.get_machine_code().replace('-', '').upper()
            if rec_machine_code != current_machine:
                return False, "机器码不匹配，授权不可用"
            
            # 4. 验证过期时间
            expire_dt = datetime.strptime(rec_expire_date, '%Y-%m-%d')
            if datetime.now() > expire_dt:
                return False, f"授权已于 {rec_expire_date} 过期"

            # 5. RSA 验签
            if RSA_AVAILABLE and self.public_key:
                data_to_verify = f"{rec_machine_code}|{rec_expire_date}|{rec_app_name}".encode('utf-8')
                h = SHA256.new(data_to_verify)
                try:
                    signature = base64.b64decode(rec_sig_b64)
                    pkcs1_15.new(self.public_key).verify(h, signature)
                except (ValueError, TypeError):
                    return False, "非法注册码 (签名验证失败)"
            
            # 验证成功，保存到本地
            self.save_license(license_code, rec_expire_date)
            return True, f"已激活，有效期至 {rec_expire_date}"

        except Exception as e:
            print(f"验证异常: {e}")
            return False, "注册码无效"

    def save_license(self, code, expire_date):
        """保存授权到文件"""
        data = {
            "license_code": code,
            "expire_date": expire_date,
            "machine_code": self.get_machine_code(),
            "updated_at": datetime.now().isoformat()
        }
        try:
            with open(self.license_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            self.license_info = data
        except Exception as e:
            print(f"保存失败: {e}")

    def is_activated(self):
        """快速检查状态"""
        success, _ = self.verify_license()
        return success

    # === 【这里是修复部分】新增的方法 ===
    def get_activation_info(self):
        """获取激活详情（供UI显示用）"""
        if not self.is_activated():
             return {
                "activated": False,
                "message": "软件未激活",
                "days_left": 0
            }

        info = self.license_info.copy()
        info['activated'] = True
        
        # 计算剩余天数
        if 'expire_date' in info:
            try:
                expire_dt = datetime.strptime(info['expire_date'], '%Y-%m-%d')
                days_left = (expire_dt - datetime.now()).days
                info['days_left'] = max(0, days_left)
            except:
                info['days_left'] = 0
        else:
            info['days_left'] = 0
            
        return info