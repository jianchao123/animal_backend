# -*- coding: utf-8 -*-
"""
修改(商品)域名
"""

import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import db
from db import transaction
import conf
import utils
logger = utils.get_logger(conf.log_path)


@transaction(is_commit=True)
def change_img_domain(mysql_cursor):
    """
    改变图片域名
    改变用户头像域名
    """
    mysql_db = db.MysqlDbUtil(mysql_cursor)
    commodities = mysql_db.query("SELECT `id`,`cover` FROM `commodity`")
    for row in commodities:
        cover = row[1]
        pk = row[0]
        data = {
            "id": pk,
            "cover": cover.replace('shopping.strongbug.com',
                                   'img-shopping-test.xhty.site')
        }
        mysql_db.update(data, table_name='commodity')


if __name__ == "__main__":
    change_img_domain()
