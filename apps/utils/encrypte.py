# _*_ encoding:utf-8 _*_
import hashlib
import hmac
import binascii
from pyDes import des, CBC, PAD_PKCS5
import base64
import rsa
from rsa import common

# MD5消息摘要算法（英语：MD5 Message-Digest Algorithm），一种被广泛使用的密码散列函数，可以产生出一个128位（16字节）的散列值
# （hash value），用于确保信息传输完整一致。md5加密算法是不可逆的，所以解密一般都是通过暴力穷举方法，通过网站的接口实现解密
def get_md5(data):
    # hashlib.md5(data.encode(encoding='GBK')).hexdigest()
    # hashlib.md5(data.encode(encoding='GB2312')).hexdigest()
    # hashlib.md5(data.encode(encoding='GB18030')).hexdigest()
    # GBK/GB2312/GB18030均是针对汉字的编码，以上三个加密的结果是一样的，但和UTF-8 编码加密结果不一样
    return hashlib.md5(data.encode(encoding='UTF-8')).hexdigest()

# base64，一种算法。下面是base64的解加密：
# 加密
def get_lockbase64(data):
    return str(base64.b64encode(data.encode("utf-8")), 'utf-8')
# 解密
def get_unlockbase64(data):
    return str(base64.b64decode(data.decode("utf-8")), 'utf-8')

# SHA1加密 安全哈希算法（Secure Hash Algorithm）主要适用于数字签名标准（Digital Signature Standard DSS）
# 里面定义的数字签名算法（Digital Signature Algorithm DSA），SHA1比MD5的安全性更强。对于长度小于2^ 64位的消息，
# SHA1会产生一个160位的消息摘要
def get_sha1(data):
    sha1 = hashlib.sha1()
    sha1.update(data.encode('utf-8'))
    sha1_data = sha1.hexdigest()
    # print(sha1_data)
    return sha1_data

# 全称：散列消息鉴别码（Hash Message Authentication Code）， HMAC加密算法是一种安全的基于加密hash函数和共享密钥
# 的消息认证协议。实现原理是用公开函数和密钥产生一个固定长度的值作为认证标识，用这个标识鉴别消息的完整性。使用一个
# 密钥生成一个固定大小的小数据块，即 MAC，并将其加入到消息中，然后传输。接收方利用与发送方共享的密钥进行鉴别认证等
def get_hmac(key, msg, digestmod=None):
    # 第一个参数是密钥key，第二个参数是待加密的字符串，第三个参数是hash函数
    # key--加密用的盐值
    # msg--要加密码的内容，可为空而后用update方法设置
    # digestmod--加密算法，默认为md5，所有支持的算法名看上边hashlib.algorithms_available
    # {'dsaWithSHA', 'sha256', 'whirlpool', 'sha384', 'shake_256', 'SHA256', 'shake_128', 'blake2b', 'sha3_256',
    #  'sha3_384', 'SHA1', 'SHA384', 'DSA', 'sha', 'SHA', 'DSA-SHA', 'RIPEMD160', 'sha3_224', 'MD5', 'md4', 'sha512',
    #  'SHA512', 'SHA224', 'blak
    #  e2s', 'sha1', 'dsaEncryption', 'MD4', 'ecdsa -
    # with-SHA1', 'md5', 'sha224', 'ripemd160', 'sha3_512'}
    mac = hmac.new(key.encode('utf-8'), msg.encode('utf-8'), digestmod=digestmod)
    # mac = hmac.new(str(key), msg, digestmod='sha1')
    # mac.digest()  # 字符串的ascii格式
    mac.hexdigest()  # 加密后字符串的十六进制格式
    return mac.hexdigest()

# DES数据加密标准（Data Encryption Standard），属于对称加密算法。DES是一个分组加密算法，典型的DES以64位为分组对数据加密，
# 和解密用的是同一个算法。它的密钥长度是56位（因为每个第8 位都用作奇偶校验），密钥可以是任意的56位的数，而且可以任意时候改变。
# DES加密
def get_des_encrypt(secret_key, s):
    iv = secret_key
    k = des(secret_key, CBC, iv, pad=None, padmode=PAD_PKCS5)
    en = k.encrypt(s, padmode=PAD_PKCS5)
    return binascii.b2a_hex(en)
# DES解密
def get_des_decrypt(secret_key, s):
    iv = secret_key
    k = des(secret_key, CBC, iv, pad=None, padmode=PAD_PKCS5)
    de = k.decrypt(binascii.a2b_hex(s), padmode=PAD_PKCS5)
    return de
#
# secret_str = get_des_encrypt('12345678', 'I love YOU~')
# print(secret_str)
# clear_str = get_des_decrypt('12345678', secret_str)
# print(clear_str)

# ccc = get_hmac('sdfadf ','zhognguo','MD5')
# print(ccc)