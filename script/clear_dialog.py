# coding:utf-8
"""
清除dialog
"""
from db import rds_conn, transaction


@transaction()
def clear_dialog(mysql_cursor):
    dialog_keys = rds_conn.keys("dialog:*")
    for row in dialog_keys:
        rds_conn.delete(row)


if __name__ == "__main__":
    clear_dialog()