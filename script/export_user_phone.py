# coding:utf-8
"""
导出用户号码
"""
import db
from db import transaction


@transaction(is_commit=True)
def export_user_phone(mysql_cursor):
    mysql_db = db.MysqlDbUtil(mysql_cursor)
    result = mysql_db.query("SELECT upb.`phone` FROM `user_profile_basic` "
                            "AS upb INNER JOIN `game_player` AS gp ON "
                            "gp.userprofilebasic_ptr_id=upb.`id` WHERE "
                            "gp.`is_robot`=0")
    phones = []
    for row in result:
        phones.append(row[0])
    with open('./phone.txt', 'w') as fd:
        fd.write("\n".join(phones))


if __name__ == "__main__":
    export_user_phone()