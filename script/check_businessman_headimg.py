# -*- coding: utf-8 -*-
"""
检查机器人是否有卡商的图片
"""
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import db
from db import transaction
import conf
import time
import utils
import ocr_util
import json
import requests
from io import BytesIO
from gevent import monkey
monkey.patch_all()
import gevent

app_key = 'pk5sYmJtVxDYswIH'
app_id = '2126705053'

logger = utils.get_logger(conf.log_path)

l = []

@transaction(is_commit=True)
def check_businessman_headimg(mysql_cursor):
    """
    检查机器人是否有卡商的图片
    """
    sql = "SELECT ubp.`id`,ubp.`headimage` FROM `user_profile_basic` as ubp " \
          "INNER JOIN `game_player` as gp ON gp.`userprofilebasic_ptr_id`=" \
          "ubp.`id` WHERE ubp.`id` < {} AND gp.`is_robot`=1 ORDER BY " \
          "ubp.`id` DESC LIMIT 10"
    mysql_db = db.MysqlDbUtil(mysql_cursor)
    cur_mix_id = 4000
    user_profile_basics = mysql_db.query(sql.format(cur_mix_id))
    while len(user_profile_basics):
        for row in user_profile_basics:
            gevent.spawn(is_businessman_img, mysql_db, row[0], row[1]).join()
        time.sleep(1)
        cur_mix_id = user_profile_basics[-1][0]
        user_profile_basics = mysql_db.query(sql.format(cur_mix_id))


def is_businessman_img(mysql_db, pk, img):
    response = requests.get("http://img-shopping-test.xhty.site/" + img)
    image_data = BytesIO(response.content).read()
    ai_obj = ocr_util.AiPlat(app_id, app_key)
    rsp = ai_obj.getOcrGeneralocr(image_data)

    if rsp['ret'] == 0:
        item_list = rsp["data"]["item_list"]
        for row in item_list:
            if u"收卡" in row["itemstring"] or u"收货" in row["itemstring"] or \
                    u"夺宝" in row["itemstring"] or \
                    u"1元" in row["itemstring"] or u"零钱" in row["itemstring"]:
                data = {
                    "id": pk,
                    "headimage": "headimg/default1.jpg"
                }
                mysql_db.update(data, table_name='user_profile_basic')
                print "----------{}".format(pk)
    else:
        l.append(str(pk))
        print(",".join(l))


@transaction(is_commit=True)
def check_businessman_headimg_by_ids(mysql_cursor, pks):
    """
    检查机器人是否有卡商的图片
    """
    sql = "SELECT ubp.`id`,ubp.`headimage` FROM `user_profile_basic` as ubp " \
          "INNER JOIN `game_player` as gp ON gp.`userprofilebasic_ptr_id`=" \
          "ubp.`id` WHERE ubp.`id`in ({}) AND gp.`is_robot`=1 ORDER BY " \
          "ubp.`id` DESC".format(pks)
    mysql_db = db.MysqlDbUtil(mysql_cursor)
    user_profile_basics = mysql_db.query(sql)
    for row in user_profile_basics:
        gevent.spawn(is_businessman_img, mysql_db, row[0], row[1]).join()
        time.sleep(0.1)


if __name__ == '__main__':
    #check_businessman_headimg()
    check_businessman_headimg_by_ids("1366,1304,1230,892,771,599,536,518,404,226,180,137")
