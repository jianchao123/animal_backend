# coding:utf-8
import time
import json
import traceback
from datetime import timedelta
from collections import defaultdict
from decimal import Decimal
import datetime as datetime_m
from datetime import datetime
from utils import PushHelper
from cache_util import CacheUtil, lock_funclock
from open_lottery_business import OpenLotteryBusiness
import db
import conf


class OpenLotteryTimer(object):
    conf_sql = "SELECT `id`, `conf_name`, `conf_key`, `conf_value` " \
               "FROM `common_param_conf` WHERE `conf_key` = '{}'"
    period_sql = \
        """SELECT `id`, `target_amounts`, `b_value`, `a_value`,
        `commodity_id`,`period_no`, `ssc_period_no`, `content` FROM `period`
        WHERE `status` = 4"""
    commodity_sql = \
        """
        SELECT `id`, `reward_type`, `dh_price_cny`,`commodity_name`
        FROM `commodity` WHERE `id` = {}
        """
    dpr_sql = \
        """
        SELECT `id`, `player_id`,`token_str` FROM `duobao_participate_record`
        WHERE `period_id` = {} AND `token_str` like '{}'
        """
    shishicai_sql = "SELECT `id`,`number` FROM `shi_shi_cai` " \
                    "WHERE `ssc_period_no` = {}"
    appoint_winner_sql = "SELECT `player_id` FROM `appoint_winner` " \
                         "WHERE `period_id`={}"

    cdy_period_sql = """SELECT p.`id`,p.`status`,p.`ssc_period_no`,
                             p.`target_amounts`,p.`amounts_prepared`,p.`content`,c.`reward_type`
                             FROM `period` AS p INNER JOIN `commodity` AS c ON c.`id` = p.`commodity_id`
                             WHERE p.`status` = 1 AND p.`id`={}"""

    query_prize_sql = "SELECT `id` FROM `prize_record` " \
                      "WHERE player_id={} and period_id={}"
    user_sql = " SELECT `uid` FROM `user_profile_basic` WHERE `id` = {}"

    def __init__(self, logger):
        self.logger = logger
        self.jpush_obj = PushHelper(conf.NOTIFY_APP_KEY,
                                    conf.NOTIFY_SCRECT_KEY)
        self.open_lottery_business = OpenLotteryBusiness(logger)

    @staticmethod
    def _get_waiting_scc_period(mysql_db):
        sql = "SELECT `ssc_period_no`,`open_time` FROM `shi_shi_cai` " \
              "ORDER BY `ssc_period_no` DESC LIMIT 1"
        result = mysql_db.get(sql)
        ssc_period_no = result[0]
        open_time = result[1]

        ssc_period_no = str(ssc_period_no)
        prefix = ssc_period_no[:8]
        today_open_count = ssc_period_no[-3:]

        next_open_time = open_time + datetime_m.timedelta(minutes=20)
        next_open_time_timestamp = \
            int(time.mktime(next_open_time.timetuple()))
        cur_timestamp = int(
            time.mktime(datetime.now().timetuple()))
        different_time = next_open_time_timestamp - cur_timestamp

        if int(today_open_count) < 59:
            return prefix + (
                        '%03d' % (int(today_open_count) + 1)), different_time
        else:
            cur_date = datetime.strptime(prefix, "%Y%m%d")
            cur_date += timedelta(days=1)
            return cur_date.strftime("%Y%m%d") + "001", different_time

    @staticmethod
    def _update_order_status(mysql_db, period_pk):
        r = mysql_db.query("SELECT `id` FROM `order` WHERE "
                           "`period_id`={}".format(period_pk))
        order_ids = [str(row[0]) for row in r]
        update_order_data = {
            "id": order_ids,
            "status": 2
        }
        mysql_db.update(update_order_data, table_name='order')

    @db.transaction(is_commit=True)
    def _participate_finish_commit(self, period_pk):
        mysql_db = db.MysqlDbUtil(self.mysql_cur)
        result = mysql_db.get(
            OpenLotteryTimer.cdy_period_sql.format(period_pk))
        if result:
            target_amounts = result[3]
            amounts_prepared = result[4]
            content = result[5]
            reward_type = result[6]

            # 数量已满,可以开奖
            if amounts_prepared == target_amounts:
                period_dict = defaultdict()
                period_dict["id"] = period_pk
                period_dict["finish_time"] = 'now()'

                # 50条时间
                fifty_time = CacheUtil.get_fifty_time()
                a_value = 0
                a_time_list = []
                for row in fifty_time:
                    d = json.loads(row)
                    a_value += int(d[1])
                    a_time_list.append(d)

                period_dict["a_value"] = a_value
                content_json = json.loads(content)
                content_json["a_time_list"] = a_time_list
                period_dict["content"] = json.dumps(content_json).replace("\\",
                                                                          "\\\\")

                # 判断开奖类型,修改状态和相关信息
                if reward_type == 1:  # 秒开直接设置为倒计时
                    period_dict["status"] = 4
                    # 设置计算结果倒计时
                    CacheUtil.set_calculate_result(period_pk, 25000)
                    # 设置开奖倒计时
                    CacheUtil.set_pttl_expire(period_pk, 30000)
                    CacheUtil.add_period_to_set(
                        CacheUtil.PERIOD_STATUS_COUNTDOWN, period_pk)
                elif reward_type == 2:  # B值
                    period_dict["status"] = 3
                    waiting_scc_period, different_time = \
                        OpenLotteryTimer._get_waiting_scc_period(mysql_db)
                    period_dict["ssc_period_no"] = waiting_scc_period

                    # 设置计算结果倒计时
                    CacheUtil.set_calculate_result(period_pk,
                                                   different_time * 1000)
                    # 设置开奖倒计时
                    CacheUtil.set_pttl_expire(period_pk,
                                              (different_time + 5) * 1000)
                    CacheUtil.add_period_to_set(
                        CacheUtil.PERIOD_STATUS_WAIT_B, period_pk)
                mysql_db.update(period_dict, table_name="period")
                # 更新订单
                OpenLotteryTimer._update_order_status(mysql_db, period_pk)

                # 删除redis里记录周期剩余数量的key
                CacheUtil.del_period_key(period_pk)

    def participate_finish(self):
        """[1]参与完成,修改状态为[等待B值|妙开]"""

        period_keys = CacheUtil.keys_by("period:target:amounts:*")
        for row in period_keys:
            period_pk = row.split(":")[-1]
            amount = CacheUtil.get_period_amounts(period_pk)
            if amount and int(amount) == 0:
                control = "participate:finish:setnx:{}".format(period_pk)
                if CacheUtil.set_nx(control, 1):
                    try:
                        self._participate_finish_commit(period_pk)
                    finally:
                        CacheUtil.del_key(control)

    @db.transaction(is_commit=True)
    def set_countdown_key(self):
        """
        [2]等待B值修改为倒计时状态 (1s执行一次)
        """
        mysql_db = db.MysqlDbUtil(self.mysql_cur)

        dpr_sql = "SELECT `id`, `time` FROM `duobao_participate_record` " \
                  "WHERE `period_id` = {} ORDER BY `id` DESC limit 1"
        # 等待B值状态中的
        period_sql = "SELECT `id`, `status`, `ssc_period_no` " \
                     "FROM `period` WHERE `status` = 3 "
        shishicai_sql = "SELECT `id`,`number` FROM `shi_shi_cai` " \
                        "WHERE `ssc_period_no` = {}"

        keys = CacheUtil.get_period_set_by(CacheUtil.PERIOD_STATUS_WAIT_B)
        if len(keys) <= 0:
            return
        result = mysql_db.query(period_sql)
        for row in result:
            pk = row[0]
            ssc_period_no = row[2]
            # 如果已经出值修改状态为倒计时
            ssc = mysql_db.get(shishicai_sql.format(
                str(ssc_period_no)))
            if ssc:
                # 修改状态为倒计时中
                update_period_data = {
                    "id": pk,
                    "status": 4
                }
                mysql_db.update(update_period_data, table_name='period')
                CacheUtil.rem_period_from_set(CacheUtil.PERIOD_STATUS_WAIT_B, pk)
                CacheUtil.add_period_to_set(
                    CacheUtil.PERIOD_STATUS_COUNTDOWN, pk)
            else:
                # 如果没有时时彩没有开奖并且最后参与时间超过2小时 (且等待的时时彩期号不能是每天的10期)
                dpr = mysql_db.get(dpr_sql.format(pk))
                dpr_time = dpr[1]
                if (dpr_time + datetime_m.timedelta(hours=2)) < datetime.now():
                    # if str(ssc_period_no)[-2:] == "10":
                    #     if datetime.now().hour > 4:
                    #         # 修改周期的时时彩期号为0000
                    #         d = {
                    #             "id": pk,
                    #             "ssc_period_no": 0
                    #         }
                    #         mysql_db.update(d, table_name='period')
                    # else:
                    # 修改周期的时时彩期号为0000
                    d = {
                        "id": pk,
                        "ssc_period_no": 0
                    }
                    mysql_db.update(d, table_name='period')

    @db.transaction(is_commit=True)
    def _open_lottery_commit(self, cache_data):
        mysql_db = db.MysqlDbUtil(self.mysql_cur)
        luck_token = cache_data["luck_token"]
        open_prize_count = cache_data["open_prize_count"]
        v_value = cache_data["v_value"]
        period_pk = cache_data["period_pk"]
        win_prize_player_id = cache_data["win_prize_player_id"]
        commodity_dh_price_cny = cache_data[
            "commodity_dh_price_cny"]
        commodity_commodity_name = \
            cache_data["commodity_commodity_name"]
        period_no = cache_data["period_no"]
        win_prize_player_dpr_id = cache_data[
            "win_prize_player_dpr_id"]
        commodity_pk = cache_data["commodity_pk"]

        # 更新周期数据
        OpenLotteryTimer._update_period_data(
            mysql_db, luck_token, open_prize_count,
            period_pk, v_value, win_prize_player_id)

        # 更新参与记录
        OpenLotteryTimer._update_dpr_data(
            mysql_db, win_prize_player_dpr_id)

        prize_record = mysql_db.get(
            OpenLotteryTimer.query_prize_sql.format(
                win_prize_player_id, period_pk))
        if not prize_record:
            # 插入中奖记录
            OpenLotteryTimer._insert_prize_data(
                mysql_db, commodity_dh_price_cny, period_pk,
                win_prize_player_dpr_id, win_prize_player_id)

            # 插入消息
            OpenLotteryTimer._insert_msg_data(
                mysql_db, commodity_commodity_name,
                period_no, win_prize_player_id)

            # 弹窗提示
            OpenLotteryTimer._pop_up_window(
                mysql_db, commodity_commodity_name,
                period_no, period_pk, win_prize_player_id)

        # 缓存走势图
        OpenLotteryTimer._save_trend_map(mysql_db, period_pk,
                                         win_prize_player_dpr_id)

        win_player = mysql_db.get(
            "SELECT `is_robot` FROM `game_player` WHERE "
            "userprofilebasic_ptr_id = {}".format(
                win_prize_player_id))

        # 中奖尾号88送8888
        if win_player[0] != 1:
            cur_balance, cur_user, add_amount = OpenLotteryTimer._winner_presents(
                mysql_db, luck_token, win_prize_player_id, commodity_pk)
            self.logger.error(
                str(cur_balance) + " " + str(cur_user) + " " + str(add_amount))

        # 推送
        if win_player[0] != 1:
            prize_record = mysql_db.get(
                OpenLotteryTimer.query_prize_sql.format(
                    win_prize_player_id, period_pk))
            # 推送
            self._push_msg(mysql_db, commodity_commodity_name,
                           period_no, period_pk, OpenLotteryTimer.user_sql,
                           win_prize_player_id, prize_record[0])

        # 删除镜像
        CacheUtil.delete_period_mirroring(period_pk)

    def open_lottery(self):
        """[4]开奖 (1s执行一次)"""

        keys = CacheUtil.keys_by('period:mirroring:*')
        for key in keys:
            period_pk = key.split(":")[-1]
            cache_data = CacheUtil.get_period_mirroring(period_pk)

            # 找到镜像,并且镜像的倒计时已经<=0
            if cache_data and CacheUtil.get_pttl_mirroring(period_pk) < 0:
                control_flag = 'open_lottery:setnx:{}'.format(period_pk)
                if CacheUtil.set_nx(control_flag, 1):
                    try:
                        self._open_lottery_commit(cache_data)
                    finally:
                        CacheUtil.del_key(control_flag)

    @db.transaction(is_commit=True)
    def _calculate_result_commit(self, commodity_reward_type,
                                 a_value, target_amounts, ssc_period_no,
                                 period_pk, content, commodity_dh_price_cny,
                                 open_prize_count, commodity_commodity_name,
                                 period_no, v_value, commodity_id):
        mysql_db = db.MysqlDbUtil(self.mysql_cur)
        ssc_no = None
        # 类型是秒开
        if commodity_reward_type == 1:
            luck_token = str((a_value % target_amounts) + 10000001)
        # 类型是B值
        if commodity_reward_type == 2:
            shishicai = mysql_db.get(OpenLotteryTimer.shishicai_sql.format(
                str(ssc_period_no)))
            # 如果未出B值, 则跳过这条周期
            if not shishicai:
                return 'c'

            luck_token = str(
                ((a_value + shishicai[1])
                 % target_amounts) + 10000001)
            v_value = shishicai[1]
            ssc_no = v_value

        # 模糊查询中奖的参与记录
        dpr_obj = mysql_db.get(
            OpenLotteryTimer.dpr_sql.format(period_pk,
                                            '%%%%%s%%%%' % luck_token))
        if not dpr_obj:
            return 'c'

        # #################这里作弊######################
        # 指定中奖人
        appoint_winners = mysql_db.query(
            OpenLotteryTimer.appoint_winner_sql.format(period_pk))
        if appoint_winners:
            candidate_list = [appoint_winners[0][0]]
            # 改变幸运号码
            to_player_id, dpr_id, luck_token = \
                self.open_lottery_business.change_luck_token(
                    mysql_db, period_pk, luck_token,
                    target_amounts, a_value, content,
                    candidate_list, dpr_obj[1], dpr_obj[0],
                    ssc_no)

            # 设置中奖人
            win_prize_player_id = to_player_id
            win_prize_player_dpr_id = dpr_id
        else:
            # if target_amounts >= 3000:

            max_loss_rate = Decimal(
                mysql_db.get(OpenLotteryTimer.conf_sql.format('max_loss_rate'))[
                    3])
            min_loss_rate = Decimal(
                mysql_db.get(OpenLotteryTimer.conf_sql.format('min_loss_rate'))[
                    3])

            candidate_list = \
                self.open_lottery_business.get_candidate_list(
                    mysql_db, commodity_dh_price_cny, period_pk,
                    max_loss_rate, min_loss_rate, luck_token, target_amounts)
            #
            if isinstance(candidate_list, list) and candidate_list:
                # 改变幸运号码
                to_player_id, dpr_id, luck_token = \
                    self.open_lottery_business.change_luck_token(
                        mysql_db, period_pk, luck_token,
                        target_amounts, a_value, content,
                        candidate_list, dpr_obj[1], dpr_obj[0],
                        ssc_no)

                # 设置中奖人
                win_prize_player_id = to_player_id
                win_prize_player_dpr_id = dpr_id
            else:
                # 不启用胜利控制,设置中奖人
                win_prize_player_id = dpr_obj[1]
                win_prize_player_dpr_id = dpr_obj[0]

                # else:
                #     # 设置中奖人
                #     win_prize_player_id = dpr_obj[1]
                #     win_prize_player_dpr_id = dpr_obj[0]

        cache_data = {
            "luck_token": luck_token,
            "open_prize_count": open_prize_count,
            "v_value": v_value,
            "period_pk": period_pk,
            "win_prize_player_id": win_prize_player_id,
            "commodity_dh_price_cny": commodity_dh_price_cny,
            "commodity_pk": commodity_id,
            "commodity_commodity_name": commodity_commodity_name,
            "period_no": period_no,
            "win_prize_player_dpr_id": win_prize_player_dpr_id

        }
        # 计算结果完成之后
        CacheUtil.set_period_mirroring(period_pk, cache_data)
        CacheUtil.incr_open_prize_count()
        CacheUtil.rem_period_from_set(CacheUtil.PERIOD_STATUS_COUNTDOWN,
                                      period_pk)

    @db.get_conn
    def calculate_result(self):
        """[3]计算结果 1.5s"""
        mysql_db = db.MysqlDbUtil(self.mysql_cur)
        keys = CacheUtil.get_period_set_by(CacheUtil.PERIOD_STATUS_COUNTDOWN)
        if len(keys) <= 0:
            return

        result = mysql_db.query(OpenLotteryTimer.period_sql)
        for period_row in result:
            period_pk = period_row[0]
            a_value = period_row[3]
            target_amounts = period_row[1]
            commodity_id = period_row[4]
            period_no = period_row[5]
            ssc_period_no = period_row[6]
            content = period_row[7]

            v_value = 0
            commodity_row = mysql_db.get(
                OpenLotteryTimer.commodity_sql.format(commodity_id))
            commodity_reward_type = commodity_row[1]  # 可从period表拿数据
            commodity_dh_price_cny = commodity_row[2]  # 可从period表拿数据
            commodity_commodity_name = commodity_row[3]  # 可从period表拿数据

            # 开奖计数
            open_prize_count = CacheUtil.get_open_prize_count()
            if open_prize_count:
                open_prize_count = int(open_prize_count)
            else:
                open_prize_count = 0

            # 计算结果倒计时小于等于0,可以计算结果了,并且还没有镜像
            if CacheUtil.get_pttl_calculate_result(period_pk) <= 0 and \
                    (not CacheUtil.get_period_mirroring(period_pk)):
                control_flag = 'mirroring:setnx:{}'.format(period_pk)
                if CacheUtil.set_nx(control_flag, 1):
                    try:
                        self._calculate_result_commit(
                            commodity_reward_type,
                            a_value, target_amounts, ssc_period_no,
                            period_pk, content, commodity_dh_price_cny,
                            open_prize_count, commodity_commodity_name,
                            period_no, v_value, commodity_id)
                    finally:
                        # 删除控制标记
                        CacheUtil.del_key(control_flag)

    @staticmethod
    def _pop_up_window(mysql_db, commodity_commodity_name, period_no,
                       period_pk, win_prize_player_id):
        sql = "SELECT ubp.`nickname`,ubp.`phone`,gp.`is_robot`,ubp.`id` FROM " \
              "`user_profile_basic` AS ubp INNER JOIN `game_player` " \
              "AS gp ON gp.`userprofilebasic_ptr_id`=ubp.`id` WHERE `id`={}"
        prize_record = mysql_db.get(
            OpenLotteryTimer.query_prize_sql.format(
                win_prize_player_id, period_pk))
        user = mysql_db.get(sql.format(win_prize_player_id))
        nickname = user[0]
        phone = user[1]
        is_robot = user[2]
        player_pk = user[3]
        if not nickname:
            nickname = phone[:3] + "****" + phone[:-4]

        headline = CacheUtil.get_headline()
        headline_arr = headline.split(u"|")
        if len(headline_arr) > 10:
            headline_arr.pop(0)
        headline_arr.append(u"恭喜{0}中奖,{1}".format(
            nickname, commodity_commodity_name))

        CacheUtil.set_headline("|".join(headline_arr))

        if not is_robot or int(CacheUtil.robot_phone_is_member(player_pk)):

            dialog_data = {"commodity_name": commodity_commodity_name,
                           "period_no": period_no,
                           "prize_record_pk": prize_record[0],
                           "period_pk": period_pk}
            CacheUtil.dialog_push(win_prize_player_id, dialog_data)

    @staticmethod
    def _insert_msg_data(mysql_db, commodity_commodity_name, period_no,
                         win_prize_player_id):
        title = u"恭喜中奖".encode("utf8")
        content = u"尊敬的用户，恭喜获得 第 {0}期 【{1}】奖励，" \
                  u"快去领奖吧！".encode("utf8")
        insert_msg_data = {
            "title": title,
            "content": content.format(period_no,
                                      commodity_commodity_name.encode(
                                          "utf8")),
            "to_player_id": win_prize_player_id,
            "from_user": "system",
            "status": 2,
            "create_time": "now()"
        }
        mysql_db.insert(insert_msg_data, table_name='messages')

    @staticmethod
    def _insert_prize_data(mysql_db, commodity_dh_price_cny, period_pk,
                           win_prize_player_dpr_id, win_prize_player_id):
        insert_prize_data = {
            "record_id": str(time.time()).replace(".", ""),
            "period_id": period_pk,
            "amounts": commodity_dh_price_cny,
            "participate_id": win_prize_player_dpr_id,
            "player_id": win_prize_player_id,
            "status": 1,  # 未领奖
            "prize_time": "now()",
            "to_recycle_businessman_id": "null",
            "card_id": "null"
        }
        mysql_db.insert(insert_prize_data, table_name='prize_record')

    @staticmethod
    def _update_dpr_data(mysql_db, win_prize_player_dpr_id):
        update_dpr_data = {
            "id": win_prize_player_dpr_id,
            "is_win_prize": 1
        }
        mysql_db.update(update_dpr_data,
                        table_name='duobao_participate_record')

    @staticmethod
    def _update_period_data(mysql_db, luck_token, open_prize_count,
                            period_pk, v_value, win_prize_player_id):

        update_period_data = {
            "id": period_pk,
            "b_value": v_value,
            "luck_token": luck_token,
            "luck_player_id": win_prize_player_id,
            "reward_time": 'now()',
            "status": 6,  # 已开奖
            "open_index": open_prize_count + 1
        }
        mysql_db.update(update_period_data, table_name='period')

    def _push_msg(self, mysql_db, commodity_commodity_name, period_no,
                  period_pk, user_sql, win_prize_player_id, prize_record_pk):
        try:
            win_game_player = mysql_db.get(
                user_sql.format(win_prize_player_id))
            data = {
                "period_no": period_no,
                "period_id": period_pk,
                "luck_player_id": win_prize_player_id,
                "commodity_name": commodity_commodity_name,
                "prize_record_pk": prize_record_pk
            }
            string = u"{}期".format(period_no) \
                     + u" " + commodity_commodity_name
            android_alert_data = string
            ios_alert_data = u"恭喜中奖\n" + string
            self.jpush_obj.push_to_user(json.dumps(data),
                                        android_alert_data,
                                        ios_alert_data,
                                        u"恭喜中奖",
                                        win_game_player[0])
        except:
            self.logger.error(traceback.format_exc())

    @staticmethod
    def _save_trend_map(mysql_db, period_pk, win_prize_player_dpr_id):
        """缓存走势图"""
        sql = """SELECT p.`id`,c.`snatch_treasure_amounts`,p.`commodity_id`,
    p.`period_no` FROM `period` AS p INNER JOIN `commodity` AS c ON
    c.`id`=p.`commodity_id` WHERE p.`id`={}""".format(period_pk)
        result = mysql_db.get(sql)
        snatch_treasure_amounts = result[1]
        commodity_id = result[2]
        period_no = result[3]

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

        # 缓存数据
        cache_data = CacheUtil.get_cache_trend_map(commodity_id)
        if cache_data:
            sql = """SELECT `residue` FROM `duobao_participate_record`
                  WHERE `id`={}""".format(win_prize_player_dpr_id)
            result = mysql_db.get(sql)
            residue = result[0]

            x_axis_data = cache_data["x_axis_data"]
            x_axis_data.append(period_no)
            trend_map_data = cache_data["trend_map_data"]
            trend_map_data.append({"period_no": period_no,
                                   "residue_ren_ci": residue})
            if len(x_axis_data) > 20:
                x_axis = x_axis_data[1:]
                trend_map = trend_map_data[1:]
        else:
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

    @staticmethod
    def _winner_presents(mysql_db, luck_token, win_prize_player_id,
                         commodity_pk):
        """中奖者赠送"""
        # conf_value : [{"commodity_pk": 12, "8": 388, "88":3888}]
        luck_token = str(luck_token)
        conf_sql = "SELECT `conf_value` " \
                   "FROM `common_param_conf` WHERE `conf_key`='TAIL_NUMBER'"
        result = mysql_db.get(conf_sql)
        d = json.loads(result[0])
        current_balance = 0
        add_amount = 0
        cur_user = 0
        for row in d:
            if commodity_pk == row["commodity_pk"]:
                amount = None
                try:
                    amount = row[luck_token[-2:]]
                except KeyError:
                    try:
                        amount = row[luck_token[-1]]
                    except KeyError:
                        pass
                if amount:
                    # 查询钱包
                    sql = "SELECT `id`,`balance` FROM `wallet` WHERE " \
                          "`user_id`={} AND `unit`=1 FOR UPDATE" \
                          "".format(win_prize_player_id)
                    wallet = mysql_db.get(sql)
                    wallet_id = wallet[0]
                    balance = wallet[1]

                    current_balance = balance
                    add_amount = amount
                    cur_user = win_prize_player_id

                    balance += Decimal(str(amount))
                    data = {
                        "balance": balance,
                        "id": wallet_id
                    }
                    mysql_db.update(data, table_name='wallet')
        return current_balance, cur_user, add_amount
