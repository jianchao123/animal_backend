# coding:utf-8
import urllib
import hashlib
import time
import json
import requests
from django.conf import settings

account_sid = settings.MD_ACCOUNT_SID
acct_key = settings.MD_ACCT_KEY


def send_code(phone, code):
    """发送验证码"""
    timestamp = str(int(round(time.time() * 1000)))
    m = hashlib.md5()
    m.update(account_sid + acct_key + timestamp)
    sig = m.hexdigest()
    data = {'accountSid': account_sid,
            'templateid': 2075,
            'to': phone,
            'timestamp': timestamp,
            'sig': sig,
            'param': code}
    return send_sms(data)


def send_deposit_success(phone, amounts, present_amounts):
    """发送充值成功通知"""
    timestamp = str(int(round(time.time() * 1000)))
    m = hashlib.md5()
    m.update(account_sid + acct_key + timestamp)
    sig = m.hexdigest()
    data = {'accountSid': account_sid,
            'templateid': 2091,
            'to': phone,
            'timestamp': timestamp,
            'sig': sig,
            'param': '{},{}'.format(amounts, present_amounts)}
    return send_sms(data)


def send_signup_present_success(phone, amounts):
    """发送注册赠送通知"""
    timestamp = str(int(round(time.time() * 1000)))
    m = hashlib.md5()
    m.update(account_sid + acct_key + timestamp)
    sig = m.hexdigest()
    data = {'accountSid': account_sid,
            'templateid': 3417,
            'to': phone,
            'timestamp': timestamp,
            'sig': sig,
            'param': '{}'.format(amounts)}
    return send_sms(data)


def send_present_notice(phones, present_amounts):
    """赠送通知"""
    timestamp = str(int(round(time.time() * 1000)))
    m = hashlib.md5()
    m.update(account_sid + acct_key + timestamp)
    sig = m.hexdigest()
    data = {'accountSid': account_sid,
            'templateid': 2189,
            'to': phones,
            'timestamp': timestamp,
            'sig': sig,
            'param': '{}'.format(present_amounts)}
    return send_sms(data)


def send_sms(data):
    industry_url = "https://openapi.miaodiyun.com/distributor/sendSMS"
    print data
    params = urllib.urlencode(data)

    headers = {"Content-Type": "application/x-www-form-urlencoded",
               "Accept": "application/json"}
    res = requests.post(industry_url, data=params, headers=headers)
    data = json.loads(res.content)
    return data['respCode'], data['respDesc']

# tos可以是一个或者多个号码，若是多个号码，以英文逗号分开
# send_code('18508217537')
# send_sms('18508217537', "【动物世界】您充值的300金额已到账，赠送金额15，请查阅．退订回T")
# send_deposit_success("18575872684", 100, 2)
