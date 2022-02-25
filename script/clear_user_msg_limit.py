# coding:utf-8
"""
清除KEY (每日发送登陆验证码限制)
"""
import datetime as datetime_m
from db import rds_conn, transaction


@transaction()
def clear_user_msg_limit(mysql_cursor):
    today = datetime_m.date.today().strftime('%Y%m%d')
    dialog_keys = rds_conn.keys("user:msg:limit:*")
    for row in dialog_keys:
        key_l = row.split(":")
        if key_l[3] != today:
            rds_conn.delete(row)


if __name__ == "__main__":
    clear_user_msg_limit()