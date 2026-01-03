#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的激活码生成脚本
不依赖PyQt5，用于测试
"""

import json
import os
import hashlib
import random
import string
from datetime import datetime, timedelta
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import uuid

class SimpleActivationManager:
    """简化的激活码管理器"""

    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.activation_file = os.path.join(data_dir, "activations.json")

        # 确保数据目录存在
        os.makedirs(data_dir, exist_ok=True)

        # 加载激活码数据
        self.activations = self._load_activations()

        # AES加密密钥
        self.encryption_key = self._get_encryption_key()

    def _get_encryption_key(self):
        """获取加密密钥"""
        key_file = os.path.join(self.data_dir, ".key")
        if os.path.exists(key_file):
            with open(key_file, 'r') as f:
                return f.read().strip().encode()
        else:
            # 生成新的密钥
            key = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()[:32]
            with open(key_file, 'w') as f:
                f.write(key)
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
                        try:
                            decrypted_info = json.loads(self._decrypt(encrypted_info))
                            decrypted_data[code] = decrypted_info
                        except Exception as e:
                            print(f"解密错误 {code}: {e}")
                            decrypted_data[code] = encrypted_info
                    return decrypted_data
            except Exception as e:
                print(f"加载文件错误: {e}")
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

    def generate_activation_code(self, days=365, max_uses=1, note=""):
        """生成激活码"""
        # 生成16位激活码
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
            "devices": [],
            "status": "active",
            "note": note
        }

        self._save_activations()
        return code

    def list_activations(self):
        """列出所有激活码"""
        return self.activations

def main():
    """主函数"""
    print("=== 激活码生成工具 ===\n")

    # 创建管理器
    manager = SimpleActivationManager()

    while True:
        print("\n请选择操作:")
        print("1. 生成激活码")
        print("2. 查看所有激活码")
        print("3. 退出")

        choice = input("\n请输入选项 (1-3): ").strip()

        if choice == "1":
            print("\n--- 生成激活码 ---")
            try:
                days = int(input("有效期(天): ") or "365")
                max_uses = int(input("最大使用次数: ") or "1")
                note = input("备注: ") or ""

                code = manager.generate_activation_code(days, max_uses, note)
                print(f"\n✅ 生成成功!")
                print(f"激活码: {code}")
                print(f"有效期: {days}天")
                print(f"最大次数: {max_uses}")
                if note:
                    print(f"备注: {note}")

            except ValueError:
                print("❌ 输入错误，请输入数字")

        elif choice == "2":
            print("\n--- 所有激活码 ---")
            activations = manager.list_activations()

            if not activations:
                print("暂无激活码")
            else:
                for code, info in activations.items():
                    print(f"\n激活码: {code}")
                    if isinstance(info, dict):
                        print(f"  状态: {info.get('status', '未知')}")
                        print(f"  有效期: {info.get('expires', '未知')}")
                        print(f"  使用: {info.get('used_count', 0)}/{info.get('max_uses', 1)}")
                        if info.get('note'):
                            print(f"  备注: {info.get('note')}")
                    else:
                        print(f"  数据: {info}")

        elif choice == "3":
            print("\n再见!")
            break

        else:
            print("❌ 无效选项")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序已退出")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        print("\n请安装依赖: pip install pycryptodome")