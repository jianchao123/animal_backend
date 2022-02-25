# coding:utf-8
"""
爱立付  后更名为西西支付
"""
import hashlib
from datetime import datetime
from collections import defaultdict
from django.conf import settings


def signature(d, key=None):
    key_set = d.keys()
    key_set.sort()
    sign_arr = []
    for k in key_set:
        sign_arr.append("{}={}".format(k, d[k]))
    sign_str = "&".join(sign_arr)
    if key:
        sign_str += "&key=" + key
    print sign_str
    m = hashlib.md5(sign_str.encode("utf8"))
    return m.hexdigest().upper()


def xixi_pay(amounts, out_trade_no, pay_accounts_conf):
    d = defaultdict()
    d["pay_memberid"] = pay_accounts_conf.merchant_no
    d["pay_orderid"] = out_trade_no
    d["pay_applydate"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    d["pay_bankcode"] = int(pay_accounts_conf.pay_channel.code)
    d["pay_notifyurl"] = settings.ALIFU_NOTIFY_URL
    d["pay_callbackurl"] = settings.ALIFU_CALLBACK_URL + "?amounts=" + str(
        amounts)
    d["pay_amount"] = amounts
    sign_str = signature(d, settings.ALIFU_KEY)
    d["pay_md5sign"] = sign_str
    d["pay_productname"] = u"藤椒牛肉面2两"
    return d