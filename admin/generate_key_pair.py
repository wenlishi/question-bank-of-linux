# generate_key_pair.py
from Crypto.PublicKey import RSA

# 1. 生成 2048 位密钥对
key = RSA.generate(2048)
private_key = key.export_key()
public_key = key.publickey().export_key()

# 2. 保存私钥 (这个文件要锁在你的保险柜里，用于注册机)
with open("private_key.pem", "wb") as f:
    f.write(private_key)

# 3. 保存公钥 (这个文件的内容要复制到客户端代码里)
with open("public_key.pem", "wb") as f:
    f.write(public_key)

print("密钥生成完毕！")
print("1. private_key.pem -> 放进注册机目录，或者硬编码进注册机")
print("2. public_key.pem -> 打开复制内容，粘贴到 client 代码的 PUBLIC_KEY_PEM 变量中")