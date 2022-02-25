# -*- coding: utf-8 -*-
"""
修改卡商邀请码
"""
import sys

reload(sys)
sys.setdefaultencoding("utf-8")

import os
import qrcode
import time
from qiniu import BucketManager
from db import transaction
import conf
import utils
from PIL import Image
from qiniu import Auth, put_file, etag
import db

logger = utils.get_logger(conf.log_path)

access_key = 'h8BESeO6mxQNX-DjMS2YdCBXhwY_c2faJcpq572H'
secret_key = 'dPorICJ8l_oGsRcnFSF0lGuCgmYXJ8qWGRZuRjy3'
q = Auth(access_key, secret_key)
bucket = BucketManager(q)
bucket_name = 'shopping-test'

QINIU_ACCESS_KEY = 'h8BESeO6mxQNX-DjMS2YdCBXhwY_c2faJcpq572H'
QINIU_SECRET_KEY = 'dPorICJ8l_oGsRcnFSF0lGuCgmYXJ8qWGRZuRjy3'
QINIU_BUCKET_NAME = 'shopping-test'
QINIU_SECURE_URL = False  # 使用http


def upload_image(image_file_name, localfile_path):
    # 构建鉴权对象
    q = Auth(QINIU_ACCESS_KEY, QINIU_SECRET_KEY)
    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(QINIU_BUCKET_NAME, image_file_name, 3600)
    from qiniu import config
    from qiniu import zone

    config.set_default(
        default_zone=zone.Zone(home_dir="/data/tmp/qr_code"))
    ret, info = put_file(token, image_file_name, localfile_path)


def generate_qr_code(string, random_str):
    # 生成路径
    current_time = time.time()
    image_file_name = str(random_str) + str(
        int(current_time)) + ".png"
    img_path = "/data/tmp/qr_code/" + image_file_name

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


INVITE_LINK = "http://www.shalilai.cn/static/invitelink/register.html"


@transaction(is_commit=True)
def change_busnessman_qrcode_func(mysql_cursor):
    mysql_db = db.MysqlDbUtil(mysql_cursor)
    busnessman = mysql_db.query(
        "SELECT `userprofilebasic_ptr_id`,`invite_code` FROM `recycle_businessman`")
    for row in busnessman:
        pk = row[0]
        invite_code = row[1]
        path = generate_qr_code(
            INVITE_LINK + "?" + "invite_code=" + invite_code, "invitecode")
        data = {
            "userprofilebasic_ptr_id": pk,
            "`invite_qr_code`": path
        }
        mysql_db.update(data, table_name="recycle_businessman")


if __name__ == "__main__":
    change_busnessman_qrcode_func()
