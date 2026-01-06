# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# """
# 数据加密模块 - 用于保护试卷数据
# 使用AES-256-CBC加密算法
# """
# from dotenv import load_dotenv
# load_dotenv()
# import base64
# import json
# import os
# import hashlib
# from Crypto.Cipher import AES
# from Crypto.Util.Padding import pad, unpad
# from typing import Any, Dict, List, Union


# class DataEncryptor:
#     """数据加密器"""

#     # 固定密钥（在实际部署时应更改为随机密钥）
#     # 注意：这里使用固定密钥仅用于演示，生产环境应该使用更安全的密钥管理方案
#     SECRET_KEY = b"tiku_software_2024_key_32bytes_long!!"
#     SALT = b"tiku_salt_2024"

#     def __init__(self):
#         """初始化加密器"""
#         # 使用密钥和盐值生成加密密钥
#         self.key = self._generate_key(self.SECRET_KEY, self.SALT)

#     def _generate_key(self, secret_key: bytes, salt: bytes) -> bytes:
#         """生成加密密钥"""
#         # 使用PBKDF2生成密钥
#         key = hashlib.pbkdf2_hmac(
#             'sha256',
#             secret_key,
#             salt,
#             100000,  # 迭代次数
#             dklen=32  # 密钥长度32字节（AES-256）
#         )
#         return key

#     def encrypt_data(self, data: Union[Dict, List, str]) -> str:
#         """
#         加密数据

#         Args:
#             data: 要加密的数据（字典、列表或字符串）

#         Returns:
#             加密后的base64字符串
#         """
#         # 将数据转换为JSON字符串
#         if isinstance(data, (dict, list)):
#             json_str = json.dumps(data, ensure_ascii=False)
#         else:
#             json_str = str(data)

#         # 生成随机IV（初始化向量）
#         iv = os.urandom(16)

#         # 创建AES加密器
#         cipher = AES.new(self.key, AES.MODE_CBC, iv)

#         # 加密数据
#         encrypted_bytes = cipher.encrypt(pad(json_str.encode('utf-8'), AES.block_size))

#         # 将IV和加密数据组合，然后base64编码
#         combined = iv + encrypted_bytes
#         encrypted_b64 = base64.b64encode(combined).decode('utf-8')

#         return encrypted_b64

#     def decrypt_data(self, encrypted_b64: str) -> Union[Dict, List, str]:
#         """
#         解密数据

#         Args:
#             encrypted_b64: 加密的base64字符串

#         Returns:
#             解密后的数据（自动解析JSON）
#         """
#         # base64解码
#         combined = base64.b64decode(encrypted_b64.encode('utf-8'))

#         # 提取IV和加密数据
#         iv = combined[:16]
#         encrypted_bytes = combined[16:]

#         # 创建AES解密器
#         cipher = AES.new(self.key, AES.MODE_CBC, iv)

#         # 解密数据
#         decrypted_bytes = unpad(cipher.decrypt(encrypted_bytes), AES.block_size)
#         json_str = decrypted_bytes.decode('utf-8')

#         # 尝试解析JSON
#         try:
#             return json.loads(json_str)
#         except json.JSONDecodeError:
#             # 如果不是JSON，返回字符串
#             return json_str

#     def encrypt_file(self, input_file: str, output_file: str = None) -> str:
#         """
#         加密文件

#         Args:
#             input_file: 输入文件路径（JSON格式）
#             output_file: 输出文件路径（可选，默认添加.enc后缀）

#         Returns:
#             输出文件路径
#         """
#         if not output_file:
#             output_file = input_file + '.enc'

#         # 读取原始JSON文件
#         with open(input_file, 'r', encoding='utf-8') as f:
#             data = json.load(f)

#         # 加密数据
#         encrypted_data = self.encrypt_data(data)

#         # 写入加密文件
#         with open(output_file, 'w', encoding='utf-8') as f:
#             f.write(encrypted_data)

#         print(f"文件已加密: {input_file} -> {output_file}")
#         return output_file

#     def decrypt_file(self, input_file: str, output_file: str = None) -> str:
#         """
#         解密文件

#         Args:
#             input_file: 输入文件路径（.enc格式）
#             output_file: 输出文件路径（可选，默认移除.enc后缀）

#         Returns:
#             输出文件路径
#         """
#         if not output_file:
#             if input_file.endswith('.enc'):
#                 output_file = input_file[:-4]  # 移除.enc后缀
#             else:
#                 output_file = input_file + '.decrypted'

#         # 读取加密文件
#         with open(input_file, 'r', encoding='utf-8') as f:
#             encrypted_data = f.read().strip()

#         # 解密数据
#         decrypted_data = self.decrypt_data(encrypted_data)

#         # 写入解密文件
#         with open(output_file, 'w', encoding='utf-8') as f:
#             json.dump(decrypted_data, f, ensure_ascii=False, indent=2)

#         print(f"文件已解密: {input_file} -> {output_file}")
#         return output_file

#     def is_encrypted_file(self, file_path: str) -> bool:
#         """
#         检查文件是否已加密

#         Args:
#             file_path: 文件路径

#         Returns:
#             True如果文件已加密，False否则
#         """
#         if not os.path.exists(file_path):
#             return False

#         # 检查文件扩展名
#         if file_path.endswith('.enc'):
#             return True

#         # 尝试读取并检查内容
#         try:
#             with open(file_path, 'r', encoding='utf-8') as f:
#                 content = f.read(100).strip()  # 读取前100个字符

#             # 检查是否是base64编码（加密数据特征）
#             if len(content) > 50 and all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=' for c in content):
#                 # 尝试base64解码
#                 decoded = base64.b64decode(content.encode('utf-8'))
#                 # 检查是否有足够的长度包含IV
#                 return len(decoded) >= 32  # IV(16) + 至少16字节加密数据
#         except:
#             pass

#         return False


# # 创建全局加密器实例
# encryptor = DataEncryptor()


# def encrypt_existing_files():
#     """加密现有的JSON试卷文件"""
#     data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
#     exams_dir = os.path.join(data_dir, "exams")

#     if not os.path.exists(exams_dir):
#         print(f"试卷目录不存在: {exams_dir}")
#         return

#     # 加密所有JSON文件
#     for filename in os.listdir(exams_dir):
#         if filename.endswith('.json') and not filename.endswith('.enc'):
#             input_file = os.path.join(exams_dir, filename)
#             encryptor.encrypt_file(input_file)

#     print("所有试卷文件已加密完成")


# if __name__ == "__main__":
#     # 测试加密解密
#     test_data = {"test": "数据", "number": 123, "list": [1, 2, 3]}

#     print("测试数据:", test_data)

#     # 加密
#     encrypted = encryptor.encrypt_data(test_data)
#     print("加密后:", encrypted[:50] + "...")

#     # 解密
#     decrypted = encryptor.decrypt_data(encrypted)
#     print("解密后:", decrypted)

#     # 检查是否相等
#     print("数据是否一致:", test_data == decrypted)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据加密模块 - 用于保护试卷数据
使用 AES-256-CBC 加密算法，支持动态盐值与环境变量密钥管理
"""

import base64
import json
import os
import hashlib
import sys
from dotenv import load_dotenv
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from typing import Any, Dict, List, Union

# 加载 .env 环境变量
load_dotenv()

class DataEncryptor:
    """数据加密器"""

    def __init__(self):
        """初始化加密器，从环境变量加载主密钥"""
        # 从环境变量获取密钥，若不存在则抛出错误防止数据意外泄露
        master_key = os.getenv("EXAM_DATA_ENCRYPTION_KEY")
        if not master_key:
            print("错误: 未在 .env 文件或环境变量中找到 'EXAM_DATA_ENCRYPTION_KEY'")
            sys.exit(1)
        
        self.secret_key = master_key.encode('utf-8')

    def _generate_derived_key(self, salt: bytes) -> bytes:
        """根据主密钥和动态盐值，通过 PBKDF2 派生出实际的 AES 密钥"""
        return hashlib.pbkdf2_hmac(
            'sha256',
            self.secret_key,
            salt,
            100000,  # 迭代次数
            dklen=32  # 32字节长度对应 AES-256
        )

    def encrypt_data(self, data: Union[Dict, List, str]) -> str:
        """
        加密数据 (动态盐值版)
        存储结构: Base64(Salt[16B] + IV[16B] + CipherText[...])
        """
        # 1. 序列化数据
        if isinstance(data, (dict, list)):
            json_str = json.dumps(data, ensure_ascii=False)
        else:
            json_str = str(data)

        # 2. 生成随机盐值和初始化向量
        salt = os.urandom(16)
        iv = os.urandom(16)

        # 3. 派生本次加密专用的密钥
        derived_key = self._generate_derived_key(salt)

        # 4. 执行加密
        cipher = AES.new(derived_key, AES.MODE_CBC, iv)
        encrypted_bytes = cipher.encrypt(pad(json_str.encode('utf-8'), AES.block_size))

        # 5. 组合存储：Salt + IV + Data
        combined = salt + iv + encrypted_bytes
        return base64.b64encode(combined).decode('utf-8')

    def decrypt_data(self, encrypted_b64: str) -> Union[Dict, List, str]:
        """
        解密数据
        会自动从加密包中提取盐值并还原密钥
        """
        # 1. Base64 解码
        try:
            combined = base64.b64decode(encrypted_b64.encode('utf-8'))
        except Exception:
            raise ValueError("非法的加密字符串格式")

        if len(combined) < 32:
            raise ValueError("加密数据长度不足")

        # 2. 提取数据：前16字节为盐，中间16字节为IV
        salt = combined[:16]
        iv = combined[16:32]
        encrypted_bytes = combined[32:]

        # 3. 还原派生密钥
        derived_key = self._generate_derived_key(salt)

        # 4. 创建解密器并解压
        cipher = AES.new(derived_key, AES.MODE_CBC, iv)
        try:
            decrypted_bytes = unpad(cipher.decrypt(encrypted_bytes), AES.block_size)
            json_str = decrypted_bytes.decode('utf-8')
        except Exception:
            raise ValueError("解密失败：可能是密钥错误或数据被篡改")

        # 5. 解析 JSON
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return json_str

    def encrypt_file(self, input_file: str, output_file: str = None) -> str:
        """加密文件并保存"""
        if not output_file:
            output_file = input_file + '.enc'

        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        encrypted_data = self.encrypt_data(data)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(encrypted_data)

        print(f"✅ 文件已加密: {os.path.basename(input_file)} -> {os.path.basename(output_file)}")
        return output_file

    def decrypt_file(self, input_file: str, output_file: str = None) -> str:
        """解密文件并还原 JSON"""
        if not output_file:
            output_file = input_file[:-4] if input_file.endswith('.enc') else input_file + '.dec'

        with open(input_file, 'r', encoding='utf-8') as f:
            encrypted_data = f.read().strip()

        decrypted_data = self.decrypt_data(encrypted_data)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(decrypted_data, f, ensure_ascii=False, indent=2)

        print(f"🔓 文件已解密: {os.path.basename(input_file)} -> {os.path.basename(output_file)}")
        return output_file

# 创建全局单例
encryptor = DataEncryptor()

if __name__ == "__main__":
    # --- 测试流程 ---
    test_case = {"title": "2024数学试卷", "id": 1001, "tags": ["难", "必考"]}
    print(f"原始数据: {test_case}")

    # 加密
    cipher_text = encryptor.encrypt_data(test_case)
    print(f"加密字符串 (前50位): {cipher_text[:50]}...")

    # 解密
    plain_data = encryptor.decrypt_data(cipher_text)
    print(f"解密后数据: {plain_data}")
    
    # 验证两次加密结果是否不同（动态盐测试）
    cipher_text_2 = encryptor.encrypt_data(test_case)
    print(f"第二次加密是否与第一次不同: {cipher_text != cipher_text_2}")