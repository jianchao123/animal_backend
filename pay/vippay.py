# coding:utf-8

"""
vip支付
"""
import hashlib
import base64
from django.conf import settings
from urllib import quote
from collections import OrderedDict
from pyDes import des, CBC, PAD_PKCS5
import binascii

KEY = settings.DESKEY
md5key = settings.MD5KEY
syspwd = settings.SYSPWD
p_url = settings.VIPPAY_NOTIFY


def vip_pay(amounts, out_trade_no, p_remarks, p_type, merchant_no):

    m2 = hashlib.md5()
    m2.update(syspwd + md5key)
    p_syspwd = m2.hexdigest()

    param = OrderedDict()
    param["p_name"] = merchant_no
    param["p_type"] = p_type
    param["p_oid"] = out_trade_no
    param["p_money"] = amounts
    param["p_bank"] = "10006"
    param["p_url"] = p_url
    param["p_remarks"] = p_remarks
    param["p_syspwd"] = p_syspwd

    param = "!".join([k + "=" + str(v) for k, v in param.items()])

    url = "http://call.vipway01.com/api/pay?params=" + \
          des_encrypt(quote(param, 'utf8')) + "&uname=" + merchant_no

    return url, param


def des_encrypt(s):
    """
    DES 加密
    :param s: 原始字符串
    :return: 加密后字符串，16进制
    """
    secret_key = KEY
    iv = secret_key
    k = des(secret_key, CBC, iv, pad=None, padmode=PAD_PKCS5)
    en = k.encrypt(s, padmode=PAD_PKCS5)
    return base64.b64encode(en)


def des_descrypt(s):
    """
    DES 解密
    :param s: 加密后的字符串，16进制
    :return:  解密后的字符串
    """
    secret_key = KEY
    iv = secret_key
    k = des(secret_key, CBC, iv, pad=None, padmode=PAD_PKCS5)
    de = k.decrypt(binascii.a2b_hex(s), padmode=PAD_PKCS5)


def signature(p_name, p_oid, p_money):
    param = p_name + p_oid + p_money + settings.SYSPWD
    m2 = hashlib.md5()
    m2.update(param + settings.MD5KEY)
    return m2.hexdigest()