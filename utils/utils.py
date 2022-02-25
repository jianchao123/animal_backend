# coding:utf-8
import re
import os
import time
import random
import qrcode
import jpush
import json
import decimal
import hashlib
import smtplib
from datetime import date
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.header import Header
from PIL import Image
from django.conf import settings
from qiniu import Auth, put_file, etag


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        super(DecimalEncoder, self).default(o)


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return time.mktime(obj.timetuple())
        elif isinstance(obj, (decimal.Decimal, float,)):
            return '{:.8f}'.format(obj)
        else:
            return json.JSONEncoder.default(self, obj)


def md5(raw_str):
    return hashlib.new("md5", str(raw_str)).hexdigest()


def create_link_string(params):
    params_sort_ls = sorted(params)
    str_ls = []
    for pr in params_sort_ls:
        pr += '=%s' % params[pr]
        str_ls.append(pr)
    return '&'.join(str_ls)


def change_time_zone(time, time_zone=8):
    if type(time) == int:
        time = datetime.utcfromtimestamp(time)
    return time - timedelta(hours=time_zone) if time else 0


def pwd_match(pwd):
    pattern = re.compile('[A-Za-z0-9_]{8,16}')
    match = pattern.match(pwd)
    return match


def email_match(email):
    pattern = re.compile('^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$')
    match = pattern.match(email)
    return match


def upload_image(image_file_name, localfile_path):
    # 构建鉴权对象
    q = Auth(settings.QINIU_ACCESS_KEY, settings.QINIU_SECRET_KEY)
    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(settings.QINIU_BUCKET_NAME, image_file_name, 3600)
    from qiniu import config
    from qiniu import zone

    config.set_default(
        default_zone=zone.Zone(home_dir=settings.TMP_PATH + "/qr_code"))
    ret, info = put_file(token, image_file_name, localfile_path)


def generate_code():
    """随机生成6位的验证码"""
    code_list = []
    # 每一位验证码都有三种可能（大写字母，小写字母，数字）
    for i in range(6):
        random_num = random.randint(0, 9)
        code_list.append(str(random_num))

    verification_code = "".join(code_list)
    return verification_code


# def generate_qr_code(string, radom_str):
#     """生成二维码"""
#
#     img = qrcode.make(string)
#     img.get_image().show()
#     current_time = time.time()
#     image_file_name = str(radom_str) + str(
#         int(current_time)) + ".jpg"
#     img_path = settings.TMP_PATH + "/qr_code/" + image_file_name
#     img.save(img_path)
#
#     upload_image("/qr_code/" + image_file_name, img_path)
#     return "/qr_code/" + image_file_name


def generate_qr_code(string, random_str):
    # 生成路径
    current_time = time.time()
    image_file_name = str(random_str) + str(
        int(current_time)) + ".png"
    img_path = settings.TMP_PATH + "/qr_code/" + image_file_name

    # 生成图片
    qr = qrcode.QRCode(version=5,
                       error_correction=qrcode.constants.ERROR_CORRECT_H,
                       box_size=5, border=1)
    qr.add_data(string)  # 要生成二维码的内容
    qr.make(fit=True)
    img = qr.make_image()
    img = img.convert("RGBA")
    cur_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    icon = Image.open(cur_dir + "/static/logo.png")  # logo图片默认在当前py文件目录下
    img_w, img_h = img.size
    factor = 1
    size_w = int(img_w / factor)
    size_h = int(img_h / factor)
    icon_w, icon_h = icon.size
    icon = icon.resize((icon_w, icon_h), Image.ANTIALIAS)
    w = int((img_w - icon_w) / 2)
    h = int((img_h - icon_h) / 2)
    icon = icon.convert("RGBA")
    img.paste(icon, (w, h), icon)

    # 保存图片
    img.save(img_path)
    upload_image("/qr_code/" + image_file_name, img_path)
    return "/qr_code/" + image_file_name


def send_mail(sender, mail_user, mail_password, receivers, msg_str,
              subject_str):
    """
    发送邮件
    """
    message = MIMEText(msg_str, 'html', 'utf-8')
    message['From'] = Header(sender, 'utf-8')
    message['To'] = Header(receivers[0], 'utf-8')

    message['Subject'] = Header(subject_str, 'utf-8')
    smtpObj = smtplib.SMTP_SSL("smtp.exmail.qq.com", 465)
    smtpObj.login(mail_user, mail_password)
    smtpObj.sendmail(sender, receivers, message.as_string())


def get_qiniu_token(upload_file_name):
    policy = {}
    q = Auth(settings.QINIU_ACCESS_KEY, settings.QINIU_SECRET_KEY)
    token = q.upload_token(settings.QINIU_BUCKET_NAME,
                           upload_file_name, 3600, policy)
    return {"upload_token": token, "expire": 3600}


def generate_out_trade_no(prefix=None):
    """生成交易号"""
    cur_time = datetime.now().strftime("%Y%m%d%H%M%S")
    number = random.randint(0, 9)
    return prefix + cur_time + ("%04d" % number)


def get_next_ssc_open_interval(cur_time):
    """获取下一次时时彩的开奖时间"""
    hour = cur_time.hour
    next_time = 20
    # if hour >= 0 and hour < 2:
    #     next_time = 5
    # if hour >= 10 and hour < 22:
    #     next_time = 10
    # if hour >= 22 and hour < 24:
    #     next_time = 5
    return next_time


class PushHelper(object):
    def __init__(self):
        self.__jpush = None

    def __init__(self, app_key, master_secret):
        self.__jpush = jpush.JPush(app_key, master_secret)
        self.__jpush.set_logging("DEBUG")

    def push_to_user(self, msg_data, android_alert_data,
                     ios_alert_data, title, *user_list):
        push = self.__jpush.create_push()
        push.platform = jpush.all_
        push.audience = jpush.audience(
            jpush.alias(*user_list)
        )
        androidmsg = {
            "alert": android_alert_data,
            "title": title
        }
        iosmsg = {
            "alert": ios_alert_data,
        }

        push.notification = jpush.notification(alert=ios_alert_data,
                                               android=androidmsg, ios=iosmsg)
        push.message = jpush.message(msg_content=msg_data,
                                     title=title,
                                     content_type=None,
                                     extras=None)
        # push.options = {"apns_production": False}
        response = push.send()
        return response


if __name__ == "__main__":
    send_mail(sender="service@satoshiduobao.com",
              mail_user="service@satoshiduobao.com",
              mail_password="dtQPYTGrc6",
              receivers=['657923372@qq.com'], msg_str='<h3>验证码:146579</h3>',
              subject_str="主题")
