# coding:utf-8

import hashlib
from collections import defaultdict
from django.conf import settings


def a_eight_pay(amounts, out_trade_no, merchant_no, code):
    d = defaultdict()
    d["merchant_no"] = merchant_no
    d["order_no"] = out_trade_no
    d["order_money"] = amounts * 100 # 分
    d["channel"] = int(code)
    d["sync_url"] = settings.A_EIGHT_SYNC
    d["async_url"] = settings.A_EIGHT_ASYNC

    raw_sign_str = merchant_no + settings.A_EIGHT_KEY + out_trade_no
    m = hashlib.md5(raw_sign_str.encode('utf-8'))
    d["sign"] = m.hexdigest()
    return d