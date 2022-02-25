# coding:utf-8
import db
from db import rds_conn, transaction


@transaction()
def clear_rds(mysql_cursor):
    period_sql = "SELECT `id`,`status` FROM `period` WHERE `id`={}"
    mysql_db = db.MysqlDbUtil(mysql_cursor)
    period_keys = rds_conn.keys("period:target:amounts:*")
    for row in period_keys:
        period_pk = row.split(":")[-1]
        result = mysql_db.get(period_sql.format(period_pk))
        print result
        if result:
            if result[1] != 1:
                rds_conn.delete(row)
        else:
            rds_conn.delete(row)


if __name__ == "__main__":
    clear_rds()