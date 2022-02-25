# coding:utf-8
from datetime import datetime
import db
from cache_util import CacheUtil


class CacheTimer(object):
    period_sql = "SELECT p.`id`,c.`commodity_name`,p.`rate`," \
                 "c.`reward_type`,c.`cover` FROM `period` AS p " \
                 "INNER JOIN `commodity` as c ON c.`id` = " \
                 "p.`commodity_id` WHERE p.`status` = 1 " \
                 "ORDER BY p.`rate` DESC limit 4"
    banner_sql = "SELECT `id`,`title`,`link`,`image_path` " \
                 "FROM `banner` WHERE `status`=1 "

    def __init__(self, logger):
        self.logger = logger

    @db.get_conn
    def homepage_rest_cache(self):
        """主页其他的一些缓存 3s"""
        mysql_db = db.MysqlDbUtil(self.mysql_cur)

        # 缓存banner
        result = mysql_db.query(CacheTimer.banner_sql)
        data = []
        for row in result:
            path = row[3]
            s = "http://shopping.strongbug.com"
            if path[0] != '/':
                s += '/'
            s += row[3]
            data.append({
                "id": row[0],
                "title": row[1],
                "link": row[2],
                "image_path": s
            })
        CacheUtil.cache_banner(data)

        # 缓存走势图
        cdy_result = mysql_db.query("SELECT `id`,`snatch_treasure_amounts` "
                                    "FROM `commodity`")
        for cdy_row in cdy_result:
            commodity_id = cdy_row[0]
            snatch_treasure_amounts = cdy_row[1]

            # Y轴
            part_count = snatch_treasure_amounts / 5
            y_axis = [0, part_count * 1, part_count * 2, part_count * 3,
                      part_count * 4, part_count * 5 + (
                          snatch_treasure_amounts % 5)]
            section = [str(y_axis[1] - 1) + "-" + str(y_axis[0]),
                       str(y_axis[2] - 1) + "-" + str(y_axis[1]),
                       str(y_axis[3] - 1) + "-" + str(y_axis[2]),
                       str(y_axis[4] - 1) + "-" + str(y_axis[3]),
                       str(y_axis[5]) + "-" + str(y_axis[4])]
            section.reverse()

            # X轴
            x_axis = []
            each_part_data = [0, 0, 0, 0, 0]
            trend_map = []

            sql = """SELECT `id` FROM `period` WHERE `commodity_id`={}
                      AND `status`=6 ORDER BY `id` DESC LIMIT 20""".format(
                commodity_id)
            result = mysql_db.query(sql)
            period_ids = [str(row[0]) for row in result]

            if period_ids:
                sql = "SELECT dpr.`residue`,p.`period_no` FROM " \
                      "`duobao_participate_record` AS dpr INNER JOIN " \
                      "`period` AS p ON p.`id`=dpr.`period_id` WHERE p.`id` " \
                      "IN ({}) AND dpr.`is_win_prize`=1 ORDER BY p.`id` DESC" \
                      "".format(",".join(period_ids))

                dpr_records = mysql_db.query(sql)
            else:
                dpr_records = []

            dpr_records = dpr_records[::-1]
            for row in dpr_records:
                x_axis.append(row[1])
                if y_axis[0] <= row[0] < y_axis[1]:
                    each_part_data[0] += 1
                if y_axis[1] <= row[0] < y_axis[2]:
                    each_part_data[1] += 1
                if y_axis[2] <= row[0] < y_axis[3]:
                    each_part_data[2] += 1
                if y_axis[3] <= row[0] < y_axis[4]:
                    each_part_data[3] += 1
                if y_axis[4] <= row[0] < y_axis[5]:
                    each_part_data[4] += 1
                trend_map.append({
                    "period_no": row[1],
                    "residue_ren_ci": row[0]
                })

            data = {
                "y_axis_data": y_axis,
                "x_axis_data": x_axis,
                "trend_map_data": trend_map,
                "period_numbers": len(trend_map),
                "each_part_data": each_part_data,
                "section": section
            }
            CacheUtil.cache_trend_map(commodity_id, data)

        # 清除无用的redis key
        cur_time = datetime.now()
        if cur_time.hour == 1 and cur_time.minute == 1:
            CacheUtil.del_robot_phone_set()
            keys = CacheUtil.keys_by("dialog:*")
            for row in keys:
                CacheUtil.del_key(row)