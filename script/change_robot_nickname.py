# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding("utf-8")
"""
改变机器人昵称
"""
import db
from db import transaction
import conf
import utils
logger = utils.get_logger(conf.log_path)


@transaction(is_commit=True)
def change_robot_nickname(mysql_cursor):
    """
    改变机器人昵称
    """
    mysql_db = db.MysqlDbUtil(mysql_cursor)
    users = mysql_db.query("SELECT `id`,`nickname` FROM `user_profile_basic`")
    for row in users:
        user_pk = row[0]
        nickname = row[1]

        if nickname:
            nickname = nickname.decode("utf-8")
            if u"优库" in nickname:
                data = {
                    "id": user_pk,
                    "nickname":  nickname.replace(u"动物世界", "")
                }
                mysql_db.update(data, table_name='user_profile_basic')


if __name__ == "__main__":
    change_robot_nickname()
