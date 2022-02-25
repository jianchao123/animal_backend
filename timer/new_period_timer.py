# coding:utf-8
from datetime import date
from cache_util import CacheUtil
import db


class NewPeriodTimer(object):

    def __init__(self, logger):
        self.logger = logger

    @db.transaction(is_commit=True)
    def start_period(self):
        """开始新的周期 (2s执行一次)"""
        mysql_db = db.MysqlDbUtil(self.mysql_cur)

        commodity_sql = \
            """SELECT `id`, `total_renci`, `count`
            FROM `commodity` WHERE `is_continue` = 1 and `status` = 1"""
        # 参与中的周期
        period_sql = \
            """SELECT `id`, `target_amounts`, `amounts_prepared`
            FROM `period` WHERE `status` = 1 and commodity_id = {}"""

        count_sql = "SELECT `id`, `period_no` FROM `period` WHERE " \
                    "`commodity_id` = {} ORDER BY `id` DESC"

        flag = 0
        result = mysql_db.query(commodity_sql)
        for row in result:
            commodity_id = row[0]
            total_renci = row[1]
            commodity_count = row[2]

            periods = mysql_db.get(period_sql.format(commodity_id))

            if periods:
                pass
            else:
                period_count = mysql_db.get(count_sql.format(commodity_id))
                if period_count:
                    cur_period_no = int(period_count[1])
                    period_no = "%09d" % (cur_period_no + 1)
                else:
                    period_no = "000000001"
                # 生成token
                token_list = []
                for inx in xrange(total_renci):
                    token_list.append("1%07d" % (inx + 1))
                token_str = ",".join(token_list)
                insert_data = {
                    "period_no": period_no,
                    "commodity_id": commodity_id,
                    "target_amounts": total_renci,
                    "amounts_prepared": 0.0,
                    "rate": 0.0,
                    "status": 1,
                    "content": "{}",
                    "token_str": token_str,
                    "residue_token_str": token_str,
                    "create_time": "now()",
                    "ssc_period_no": 0,
                    "open_index": 9999999
                }
                mysql_db.insert(insert_data, table_name='period')
                # 更新commodity的周期数量
                update_data = {
                    "id": commodity_id,
                    "count": commodity_count + 1 if commodity_count else 1
                }
                mysql_db.update(update_data, table_name='commodity')
                # 记录到redis
                p = mysql_db.get(period_sql.format(commodity_id))
                CacheUtil.set_period_amounts(p[0], p[1])
                flag = 1
        if flag:
            result = mysql_db.query(
                "SELECT `id` FROM `period` WHERE `status`=1")
            l = [str(row[0]) for row in result]
            CacheUtil.cache_underway_period_id(",".join(l))