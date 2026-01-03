#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
激活码管理系统
"""

import json
import hashlib
import random
import string
import os
from datetime import datetime, timedelta
from PyQt5.QtCore import QSettings
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import uuid

class ActivationManager:
    """激活码管理器"""

    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.activation_file = os.path.join(data_dir, "activations.json")
        self.settings = QSettings("TikuSoft", "TikuQuestionBank")

        # 确保数据目录存在
        os.makedirs(data_dir, exist_ok=True)

        # 加载激活码数据
        self.activations = self._load_activations()

        # AES加密密钥（实际使用时应该更安全地存储）
        self.encryption_key = self._get_encryption_key()

    def _get_encryption_key(self):
        """获取加密密钥"""
        key = self.settings.value("encryption_key", "")
        if not key:
            # 生成新的密钥
            key = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()[:32]
            self.settings.setValue("encryption_key", key)
        return key.encode()

    def _encrypt(self, data):
        """加密数据"""
        cipher = AES.new(self.encryption_key, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(data.encode(), AES.block_size))
        iv = cipher.iv
        return base64.b64encode(iv + ct_bytes).decode()

    def _decrypt(self, enc_data):
        """解密数据"""
        enc_data = base64.b64decode(enc_data)
        iv = enc_data[:16]
        ct = enc_data[16:]
        cipher = AES.new(self.encryption_key, AES.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ct), AES.block_size)
        return pt.decode()

    def _load_activations(self):
        """加载激活码数据"""
        if os.path.exists(self.activation_file):
            try:
                with open(self.activation_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 解密激活码数据
                    decrypted_data = {}
                    for code, encrypted_info in data.items():
                        if isinstance(encrypted_info, dict):
                            # 已经是字典，直接使用
                            decrypted_data[code] = encrypted_info
                        elif isinstance(encrypted_info, str):
                            # 是字符串，尝试解密
                            try:
                                decrypted_info = json.loads(self._decrypt(encrypted_info))
                                decrypted_data[code] = decrypted_info
                            except Exception as e:
                                print(f"警告: 激活码 {code} 解密失败: {e}")
                                # 解密失败，保存原始字符串
                                decrypted_data[code] = encrypted_info
                        else:
                            # 其他类型，保存原始数据
                            decrypted_data[code] = encrypted_info
                    return decrypted_data
            except Exception as e:
                print(f"加载激活码文件失败: {e}")
                return {}
        return {}

    def _save_activations(self):
        """保存激活码数据"""
        # 加密激活码数据
        encrypted_data = {}
        for code, info in self.activations.items():
            encrypted_data[code] = self._encrypt(json.dumps(info))

        with open(self.activation_file, 'w', encoding='utf-8') as f:
            json.dump(encrypted_data, f, ensure_ascii=False, indent=2)

    def generate_activation_code(self, days=365, max_uses=1):
        """
        生成激活码

        Args:
            days: 有效天数
            max_uses: 最大使用次数
        """
        # 生成16位激活码，格式：XXXX-XXXX-XXXX-XXXX
        code_parts = []
        for _ in range(4):
            part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            code_parts.append(part)
        code = '-'.join(code_parts)

        # 计算过期时间
        expire_date = datetime.now() + timedelta(days=days)

        # 存储激活码信息
        self.activations[code] = {
            "created": datetime.now().isoformat(),
            "expires": expire_date.isoformat(),
            "max_uses": max_uses,
            "used_count": 0,
            "devices": [],  # 已激活的设备列表
            "status": "active"  # active, expired, revoked
        }

        self._save_activations()
        return code

    def verify_activation(self, code, device_id):
        """
        验证激活码

        Args:
            code: 激活码
            device_id: 设备ID
        """
        # 清理格式
        code = code.strip().upper()

        # 检查激活码是否存在
        if code not in self.activations:
            return False

        activation = self.activations[code]

        # 检查activation类型，如果是字符串则尝试解密
        if isinstance(activation, str):
            try:
                # 尝试解密字符串
                decrypted = self._decrypt(activation)
                activation = json.loads(decrypted)
                # 更新到内存中
                self.activations[code] = activation
            except Exception as e:
                print(f"解密失败 {code}: {e}")
                # 解密失败，返回False
                return False

        # 确保activation是字典
        if not isinstance(activation, dict):
            print(f"激活码 {code} 数据格式错误: {type(activation)}")
            return False

        # 检查状态
        if activation.get("status") != "active":
            return False

        # 检查是否过期
        expires = activation.get("expires")
        if expires:
            try:
                expire_date = datetime.fromisoformat(expires)
                if datetime.now() > expire_date:
                    activation["status"] = "expired"
                    self._save_activations()
                    return False
            except Exception as e:
                print(f"日期解析失败 {code}: {e}")
                # 日期格式错误，返回False
                return False

        # 检查使用次数
        used_count = activation.get("used_count", 0)
        max_uses = activation.get("max_uses", 1)
        if used_count >= max_uses:
            return False

        # 检查设备是否已激活
        devices = activation.get("devices", [])
        if device_id in devices:
            return True

        # 如果是新设备，检查是否还可以激活
        if used_count < max_uses:
            activation["used_count"] = used_count + 1
            activation.setdefault("devices", []).append(device_id)
            self._save_activations()
            return True

        return False

    def activate_software(self, code, device_id):
        """
        激活软件

        Args:
            code: 激活码
            device_id: 设备ID
        """
        if self.verify_activation(code, device_id):
            # 保存激活信息
            self.settings.setValue("activated", True)
            self.settings.setValue("activation_code", code)
            self.settings.setValue("activation_date", datetime.now().isoformat())
            self.settings.setValue("device_id", device_id)
            return True
        return False

    def revoke_activation(self, code):
        """撤销激活码"""
        if code in self.activations:
            self.activations[code]["status"] = "revoked"
            self._save_activations()
            return True
        return False

    def extend_activation(self, code, additional_days):
        """延长激活码有效期"""
        if code in self.activations:
            expire_date = datetime.fromisoformat(self.activations[code]["expires"])
            new_expire_date = expire_date + timedelta(days=additional_days)
            self.activations[code]["expires"] = new_expire_date.isoformat()
            self._save_activations()
            return True
        return False

    def get_activation_info(self, code):
        """获取激活码信息"""
        if code in self.activations:
            return self.activations[code].copy()
        return None

    def list_activations(self):
        """列出所有激活码"""
        return self.activations.copy()

    def get_activation_stats(self):
        """获取激活码统计信息"""
        total = len(self.activations)
        active = 0
        expired = 0
        revoked = 0
        used = 0

        for a in self.activations.values():
            if isinstance(a, dict):
                if a.get("status") == "active":
                    active += 1
                elif a.get("status") == "expired":
                    expired += 1
                elif a.get("status") == "revoked":
                    revoked += 1
                used += a.get("used_count", 0)
            # 如果是字符串，跳过统计

        return {
            "total": total,
            "active": active,
            "expired": expired,
            "revoked": revoked,
            "used": used
        }