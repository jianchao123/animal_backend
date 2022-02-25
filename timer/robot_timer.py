# coding:utf-8
import requests
import time
import json
import random
from datetime import datetime, date
import db
from db import rds_conn, logger


class RobotTimer(object):
    """机器人购买定时器"""

    def __init__(self, url, logger):
        """
        """
        self.logger = logger
        self.url = url

    time_dict = {
        '0': 100, '1': 100, '2': 180, '3': 200, '4': 200, '5': 180, '6': 170,
        '7': 100, '8': 50, '9': 15, '10': 15, '11': 15, '12': 15,
        '13': 13, '14': 13, '15': 13, '16': 13, '17': 13, '18': 13,
        '19': 15, '20': 15, '21': 15, '22': 15, '23': 60,
    }

    def _get_forward_selection_periods(self, mysql_db, is_robot=0):
        """获取预选周期"""
        sql = "SELECT dpr.`period_id` FROM `duobao_participate_record` " \
              "AS dpr INNER JOIN `period` AS p ON p.`id` = dpr.`period_id` " \
              "INNER JOIN `game_player` AS gp ON " \
              "gp.`userprofilebasic_ptr_id` = dpr.`player_id` " \
              "WHERE p.`status` = 1 AND gp.is_robot = {} " \
              "ORDER BY p.`amounts_prepared` DESC".format(is_robot)
        result = mysql_db.query(sql)
        return list(set([row[0] for row in result]))

    def _get_random_number(self, residue):
        """获取随机数"""
        if residue > 1000:
            return random.randint(1, 1000)
        else:
            return random.randint(1, residue)

    def _robot_user_selected(self, mysql_db, cur_time):
        """选择机器人用户"""
        morning = [6, 7, 8, 9, 10, 11, 12, 13]
        afternoon = [14, 15, 16, 17, 18, 19, 20]
        night = [21, 22, 23, 0, 1, 2, 3, 4, 5]
        query_sql = "SELECT `userprofilebasic_ptr_id` FROM game_player " \
                    "WHERE is_robot = 1"
        result = mysql_db.query(query_sql)

        # 用户习惯模拟
        habit_value = 0
        cur_hour = cur_time.hour
        if cur_hour in morning:
            habit_value = 0
        if cur_hour in afternoon:
            habit_value = 1
        if cur_hour in night:
            habit_value = 2
        user_ids = [row[0] for row in result if row[0] % 3 == habit_value]

        # 最终决定用户
        buy_user_id = random.choice(user_ids)

        result = mysql_db.get("SELECT `phone` FROM `user_profile_basic` "
                              "WHERE `id` = {}".format(buy_user_id))
        params = {
            "phone": result[0],
            "password": "kIhHAWexFy7pU8qM"
        }
        r = requests.post(self.url + "user/app/signin/",
                          data=json.dumps(params), headers=
                          {"Content-Type": "application/json"},
                          verify=False)
        json_dict = json.loads(r.content)
        if json_dict['code']:
            return
        data = json_dict["data"]
        headers = {
            "Content-Type": "application/json",
            "Cookie": "sessionid=" + data["sessionid"] + "; csrftoken=" +
                      data["csrftoken"] + "; tabstyle=raw-tab",
            "X-CSRFTOKEN": ""
        }
        return headers

    def _period_selected(self, mysql_db, people_fwd_select):
        """周期选择"""
        from collections import OrderedDict

        sql = "SELECT p.`id`,c.`snatch_treasure_amounts` FROM `period` as p " \
              "INNER JOIN `commodity` as c ON c.`id`=p.`commodity_id` " \
              "WHERE p.`status`=1 {} " \
              "ORDER BY c.`snatch_treasure_amounts` ASC"
        if people_fwd_select:
            people_fwd_select_ids = ",".join(map(str, people_fwd_select))
            result = mysql_db.query(
                sql.format("AND p.`id` NOT IN (" + people_fwd_select_ids + ")"))
        else:
            result = mysql_db.query(sql.format(" "))

        max = result[-1][1] + 1000

        d = OrderedDict()
        d1 = OrderedDict()
        x = []
        for row in result:
            cur_amounts = row[1]
            if cur_amounts < 500:
                cur_amounts = cur_amounts + 1000
            amounts = max - cur_amounts
            if str(amounts) in x:
                number = str(amounts) + ".1"
            else:
                number = str(amounts)
            x.append(number)
            d[number] = row[0]
        x = sorted(x)

        x1 = []
        current = 0
        for index, row in enumerate(x):
            c = float(row) + float(current)
            x1.append(c)
            d1[str(c)] = d[str(row)]
            current = c

        max = int(x1[-1])

        selected_period_one = 0
        selected_period_two = 0
        digit = random.randint(0, max)
        for row in x1:
            if digit < row:
                selected_period_one = d1[str(row)]
                break

        digit = random.randint(0, max)
        for row in x1:
            if digit < row:
                selected_period_two = d1[str(row)]
                break
        return selected_period_one, selected_period_two

    @db.transaction(is_commit=True)
    def robot_buy(self):
        """5s跑一次, 每次随机数>7进行购买
        """

        mysql_db = db.MysqlDbUtil(self.mysql_cur)
        cur_time = datetime.now()
        number = random.randint(1, RobotTimer.time_dict[str(cur_time.hour)])
        if number < 10:
            headers = self._robot_user_selected(mysql_db, cur_time)

            # 获取真实用户参与的周期
            people_fwd_select = self._get_forward_selection_periods(mysql_db)
            forward_selection = people_fwd_select[:5]
            forward_selection *= 3

            # 获取没有真实用户参与的周期
            selected_period_one, selected_period_two = \
                self._period_selected(mysql_db, people_fwd_select)
            if selected_period_two:
                forward_selection.append(selected_period_two)
            if selected_period_one:
                forward_selection.append(selected_period_one)

            # ["真1","真1","真1","真2","真2","真2","other1","other2", "other3"]
            if forward_selection:
                selected_period_id = random.choice(forward_selection)
                rds_data = rds_conn.get(
                    "period:target:amounts:{}".format(selected_period_id))
                if rds_data:
                    cur_period = mysql_db.get(
                        "SELECT p.`target_amounts`,`quota_str` FROM `period` as p \
                        INNER JOIN `commodity` as c ON c.`id`=p.`commodity_id`\
                            WHERE p.`id` ={}".format(selected_period_id))
                    target_amounts = cur_period[0]
                    quota_str = cur_period[1]

                    # 方式 1:百十个位取整 2:保留随机数 3:[50, 100, 200, 500]
                    mode_select = random.choice([1, 1, 2, 3])
                    buy_volume = self.calculate_buy_volume(mode_select,
                                                           rds_data,
                                                           target_amounts,
                                                           quota_str)

                    params = {
                        "period_id": selected_period_id,
                        "amounts": buy_volume
                    }
                    requests.post(
                        self.url + "snatchtreasure/participate/",
                        data=json.dumps(params), headers=headers, verify=False)

    def calculate_buy_volume(self, mode_select, rds_data,
                             target_amounts, quota_str):
        residue = int(rds_data)
        if quota_str:
            quota_str_arr = map(lambda obj: int(obj), quota_str.split(","))
            if residue in quota_str_arr:
                buy_volume = residue
            else:
                if 1 in quota_str_arr:
                    quota_str_arr.remove(1)
                buy_volume = random.choice(quota_str_arr)
        else:
            if residue < (int(target_amounts) / random.choice([10, 12])):
                buy_volume = residue
            else:
                buy_volume = self._get_random_number(residue)
                if mode_select == 1 and (9 < buy_volume < 700):
                    if 99 < buy_volume < 700:
                        buy_volume = buy_volume / 100 * 100
                    elif 9 < buy_volume < 100:
                        buy_volume = buy_volume / 10 * 10
                elif mode_select == 3:
                    if int(target_amounts) > 5000:
                        buy_volume = (target_amounts / 100) * \
                                     random.choice([10, 12, 14, 16, 18])
                    else:
                        if residue >= 3000:
                            l = [200, 450, 600, 800]
                        else:
                            l = [50, 100, 200, 500]
                        buy_volume = random.choice(l)
                        if buy_volume > residue:
                            buy_volume = residue
        return buy_volume
