# coding:utf-8
from M2Crypto import *
from base64 import b64encode, b64decode


def read_key(file_path, type):
    """
    读取RSA密钥
    :param file_path: 文件路径
    :param type: 密钥类型，private：私钥|public：公钥
    :return:
    """
    with open(file_path, "rb") as file_handler:
        rea_key = BIO.MemoryBuffer(file_handler.read())
    if type == "private":
        return RSA.load_key_bio(rea_key)
    else:
        return RSA.load_pub_key_bio(rea_key)


def hash(message, algorithm="md5"):
    """
    计算散列值
    :param message: 消息
    :param algorithm: 散列算法
    :return:
    """
    hash = EVP.MessageDigest(algorithm)
    hash.update(message.encode(encoding='utf-8'))
    return hash.digest()


def sign(message, private_key, algorithm="md5"):
    """
    RSA签名
    :param message: 消息
    :param private_key: 私钥
    :param algorithm: 散列算法
    :return:
    """
    digest = hash(message, algorithm)
    return b64encode(private_key.sign(digest, algorithm)).decode(encoding='utf-8')


def verify(message, sign, public_key, algorithm="md5"):
    """
    RSA验签
    :param message: 消息
    :param sign: 签名
    :param public_key: 公钥
    :param algorithm: 散列算法
    :return:
    """
    digest = hash(message, algorithm)
    return public_key.verify(digest, b64decode(sign), algorithm)


def rsa_pkcs1_encrypt(plaintext, public_key):
    """
    RSA公钥加密
    :param plaintext: 明文
    :param public_key: 公钥
    :return:
    """
    # 密钥长度为1024时，最大加密块
    max_encrypt_block = 117
    # 填充方式
    padding = RSA.pkcs1_padding

    # 字节编码
    plainBytes = plaintext.encode(encoding='utf-8')

    # 明文长度
    plaintext_length = len(plainBytes)

    # 不需要分段加密
    if plaintext_length < max_encrypt_block:
        return b64encode(public_key.public_encrypt(plainBytes, padding)).decode(encoding='utf-8')

    # 分段加密
    offset = 0
    ciphers = []
    while plaintext_length - offset > 0:
        if plaintext_length - offset > max_encrypt_block:
            ciphers.append(public_key.public_encrypt(plainBytes[offset:offset + max_encrypt_block], padding))
        else:
            ciphers.append(public_key.public_encrypt(plainBytes[offset:], padding))
        offset += max_encrypt_block
    return b64encode("".join(ciphers)).decode(encoding='utf-8')


def rsa_pkcs1_decrypt(ciphertext, private_key):
    """
    RSA私钥解密
    :param ciphertext:
    :param private_key:
    :return:
    """
    encrypt_result = b64decode(ciphertext)
    # 密钥长度为1024时，最大解密块
    max_decrypt_block = 128
    # 加密结果长度
    encrypt_result_length = len(encrypt_result)
    # 填充方式
    padding = RSA.pkcs1_padding

    # 不需要分段解密
    if encrypt_result_length < max_decrypt_block:
        return private_key.private_decrypt(encrypt_result, padding)

    # 分段解密
    offset = 0
    plains = []
    while encrypt_result_length - offset > 0:
        if encrypt_result_length - offset > max_decrypt_block:
            plains.append(private_key.private_decrypt(encrypt_result[offset:offset + max_decrypt_block], padding))
        else:
            plains.append(private_key.private_decrypt(encrypt_result[offset:], padding))
        offset += max_decrypt_block
    return b"".join(plains).decode(encoding='utf-8')


if __name__ == '__main__':
    # RSA公钥加密
    data = "user=18582510916&time=1556159837&sign=bac79d79038209e983c8c158beec8ddc673db34b"
    public_key_path = "../docs/rsa_public_key.pem"
    public_key = read_key(public_key_path, "public")
    plaintext = rsa_pkcs1_encrypt(data, public_key)
    print(plaintext)

    # RSA私钥解密
    private_key_path = "../docs/rsa_private_key.pem"
    private_key = read_key(private_key_path, "private")
    s = rsa_pkcs1_decrypt(plaintext, private_key)
    print(s)

