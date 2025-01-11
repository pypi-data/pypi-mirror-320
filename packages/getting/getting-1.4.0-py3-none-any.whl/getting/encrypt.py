from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# AES加密
def aes_encrypt(data, key, iv):
    """
    AES加密

    data: 待加密数据

    key: 密钥

    iv: 偏移量
    """
    data = data.encode('utf-8')
    key = key.encode('utf-8') if isinstance(key, str) else key
    iv = iv.encode('utf-8') if isinstance(iv, str) else iv
    aes = AES.new(key, AES.MODE_CBC, iv)
    padded_data = pad(data, AES.block_size)
    encrypted_data = aes.encrypt(padded_data)
    return base64.b64encode(encrypted_data).decode('utf-8') 

# AES解密
def aes_decrypt(rData, key, iv):
    """
    AES解密

    rData: 加密数据
    
    key: 密钥
    
    iv: 偏移量
    """
    key = key.encode('utf-8') if isinstance(key, str) else key
    iv = iv.encode('utf-8') if isinstance(iv, str) else iv
    aes = AES.new(key,AES.MODE_CBC,iv)
    decoded_data = base64.b64decode(rData)
    # 解密
    decrypted_data = aes.decrypt(decoded_data)
    padding_length = decrypted_data[-1]
    decrypted_data = decrypted_data[:-padding_length]
    return decrypted_data.decode('utf-8') 

import rsa
import os
import base64
import json

# 读取公钥
def read_pub_key(path):
    """
    读取公钥
    """
    with open(path, "rb") as f:
        pub_key = rsa.PublicKey.load_pkcs1(f.read(), format="PEM")
    return pub_key

# 读取私钥
def read_pri_key(path):
    """
    读取私钥
    """
    with open(path, "rb") as f:
        pri_key = rsa.PrivateKey.load_pkcs1(f.read(), format="PEM")
    return pri_key

# RSA加密
def rsa_encrypt(data, pub_key_path):
    """
    RSA加密

    data: 待加密数据
    """
    # 读取公钥
    pub_key = read_pub_key(pub_key_path)
    # 使用公钥加密
    encrypted_data = rsa.encrypt(data.encode(), pub_key)
    # 将加密后的数据进行 Base64 编码以便传输
    return base64.b64encode(encrypted_data).decode()

# RSA解密
def rsa_decrypt(rData, pri_key_path):
    """
    RSA解密

    rData: 加密数据
    """
    # 读取私钥
    pri_key = read_pri_key(pri_key_path)
    decoded_data = base64.b64decode(rData)
    decrypted_data = rsa.decrypt(decoded_data, pri_key)
    return decrypted_data.decode()

# 解密ARS加密数据再解密RSA加密数据
def decrypt_data(data, pri_key_path):
    """
    解密 ARS 加密数据再解密 RSA 加密数据

    data: RSA 加密数据
    """
    # 将 Base64 编码的数据解码
    data = base64.b64decode(data).decode()
    # 将 JSON 字符串解析为字典
    jsonData = json.loads(data)
    # 解密 RSA 加密数据，得到包含 AES 加密数据的 JSON 字符串
    arsData = rsa_decrypt(jsonData.get('v'), pri_key_path)
    # 将 RSA 解密后的 JSON 字符串解析为字典
    arsData = json.loads(arsData)
    # 使用 AES 解密数据
    aesData = aes_decrypt(jsonData.get('data') , arsData.get('key'), arsData.get('iv'))
    return aesData

# 测试使用
if __name__ == "__main__":
    # 当前脚本路径
    path = os.path.dirname(os.path.abspath(__file__))
    # 拼接公钥、私钥文件路径
    pub_key_path = os.path.join(path, "pub.pem")
    pri_key_path = os.path.join(path, "pri.pem")
    
    data = "hello"
    print("原始数据：", data)
    # AES加密
    key = "1234567890123456"
    iv = "1234567890123456"
    rData = aes_encrypt(data, key, iv)
    print("AES加密后：", rData)
    # AES解密
    dData = aes_decrypt(rData, key, iv)
    print("AES解密后：", dData)
    # RSA加密
    rData = rsa_encrypt(data, pub_key_path)
    print("RSA加密后：", rData)
    # RSA解密
    dData = rsa_decrypt(rData, pri_key_path)
    print("RSA解密后：", dData)
