# coding:utf-8
"""
清除七牛无用图片
"""
import sys

reload(sys)
sys.setdefaultencoding("utf-8")

# 清理七牛无用的图片
import json
import db
from db import transaction
from qiniu import Auth
from qiniu import BucketManager

access_key = 'tA7N_dheubA81ew5GIRtuDBsj7pIn2lH3ym427QC'
secret_key = 'aMagvjYzFUIt1_SkTMLRQ3cbLUWZ9hRHQAFRkjmk'
q = Auth(access_key, secret_key)
bucket = BucketManager(q)
bucket_name = 'shopping'


@transaction(is_commit=True)
def test(mysql_cursor):
    mysql_db = db.MysqlDbUtil(mysql_cursor)
    # 前缀
    prefix = None
    # 列举条目
    limit = None
    # 列举出除'/'的所有文件以及以'/'为分隔的所有前缀
    delimiter = None
    # 标记
    marker = None
    mysql_db = db.MysqlDbUtil(mysql_cursor)
    while True:
        ret, eof, info = bucket.list(bucket_name, prefix, marker, limit,
                                     delimiter)
        items = ret.get('items')
        if len(items):
            for row in items:
                result = mysql_db.query(
                    "SELECT `id` FROM `user_profile_basic` WHERE `headimage` = '" +
                    row["key"] + "'")
                print(result)
        if "marker" not in ret:
            break
        marker = ret["marker"]


@transaction(is_commit=True)
def clear_qiniu_img(mysql_cursor):
    # 前缀
    prefix = None
    # 列举条目
    limit = None
    # 列举出除'/'的所有文件以及以'/'为分隔的所有前缀
    delimiter = None
    # 标记
    marker = None
    mysql_db = db.MysqlDbUtil(mysql_cursor)

    del_count_user = 0
    del_count_cmt = 0
    del_count_banner = 0
    del_count_qrcode = 0
    other_count = 0
    while True:
        ret, eof, info = bucket.list(bucket_name, prefix, marker, limit,
                                     delimiter)
        items = ret.get('items')
        if len(items):
            for row in items:
                key = row["key"]
                key_tmp = key
                if key_tmp[0] == "/":
                    key_tmp = key_tmp[1:]
                arr = key_tmp.split("/")

                if arr[0] == u'headimg':
                    result = mysql_db.query(
                        "SELECT `id` FROM `user_profile_basic` WHERE "
                        "`headimage` = '" + key + "'")
                    if not len(result):
                        bucket.delete(bucket_name, key)
                        del_count_user += 1
                elif arr[0] == u"banner":
                    result = mysql_db.query(
                        "SELECT `id` FROM `banner` WHERE "
                        "`image_path` = '" + key + "'")
                    if not len(result):
                        bucket.delete(bucket_name, key)
                        del_count_banner += 1
                elif arr[0] == u"commodity":
                    result = mysql_db.query(
                        "SELECT `id` FROM `imgs` WHERE "
                        "`image_path` = '" + key + "'")
                    if not len(result):
                        bucket.delete(bucket_name, key)
                        del_count_cmt += 1
                elif arr[0] == u"qr_code":
                    result = mysql_db.query(
                        "SELECT `id` FROM `recycle_businessman` WHERE "
                        "`invite_qr_code` = '" + key + "'")
                    if not len(result):
                        bucket.delete(bucket_name, key)
                        del_count_qrcode += 1
                else:
                    other_count += 1
                    ret, info = bucket.delete(bucket_name, key)

        if "marker" not in ret:
            break
        marker = ret["marker"]
    print(del_count_qrcode, del_count_banner, del_count_cmt, del_count_user, other_count)


if __name__ == "__main__":
    clear_qiniu_img()
    # test()
