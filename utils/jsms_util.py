# coding:utf-8
import requests
import json
import base64
from django.conf import settings
import logging
logger = logging.getLogger(__name__)


def send_sms(phone, code):
    authorization = \
        "Basic " + base64.b64encode(
            settings.J_APPKEY + ":" + settings.J_APPSECRET)
    logger.error(authorization)
    headers = {
        "Authorization": authorization,
        "Content-Type": "application/json"
    }
    params = {"mobile": phone, "temp_id": 1,
              "temp_para": {"code": code}}

    res = requests.post(settings.JSMS_URL,
                        data=json.dumps(params).encode('utf-8'),
                        headers=headers, timeout=6)
    content = json.loads(res.content)

    logger.error(str(content))

#
# def send_text_sms(phone, text):
#     authorization = \
#         "Basic " + base64.b64encode(
#             settings.J_APPKEY + ":" + settings.J_APPSECRET)
#     logger.error(authorization)
#     headers = {
#         "Authorization": authorization,
#         "Content-Type": "application/json"
#     }
#     params = {"mobile": phone, "temp_id": 1,
#               "temp_para": {"code": code}}
#
#     res = requests.post(settings.JSMS_URL,
#                         data=json.dumps(params).encode('utf-8'),
#                         headers=headers, timeout=6)
#     content = json.loads(res.content)
#
#     logger.error(str(content))
