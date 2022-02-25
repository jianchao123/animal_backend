# coding:utf-8
import json
import random
from datetime import datetime
from datetime import timedelta
from decimal import Decimal


class OpenLotteryBusiness(object):
    """
    开奖业务
    """

    def __init__(self, logger):
        self.logger = logger

    def query_user_consume(self, mysql_db, player_id, period_id):
        sql = "SELECT sum(`amounts`) FROM `consume_record` WHERE " \
              "`player_id` = {} AND `period_id` = {}".format(player_id,
                                                             period_id)
        result = mysql_db.get(sql)
        return result[0]

    def get_candidate_list(self, mysql_db, dh_price_cny, period_id,
                           max_loss_rate, min_loss_rate, luck_token,
                           target_amounts):
        """
        获取候选人
        """
        candidate_list = []
        is_all_real_user = False
        zero = Decimal(str(0.0))

        order_sql = "SELECT `id`,`player_id`,`total_renci` FROM `order` " \
                    "WHERE `period_id` = {} ORDER BY rand()".format(period_id)
        result = mysql_db.query(order_sql)
        # (2.1)单个用户, 无需修改
        if len(result) == 1:
            return -1

        # (2.2)全是机器人, 无需修改, 走正常流程
        player_ids = []
        player_total_renci = {}
        for row in result:
            player_pk = str(row[1])
            player_ids.append(player_pk)
            player_total_renci[player_pk] = row[2]
        user_sql = "SELECT `userprofilebasic_ptr_id` FROM `game_player` " \
                   "WHERE `userprofilebasic_ptr_id` in ({}) AND is_robot = 1"
        robot_result = mysql_db.query(user_sql.format(",".join(player_ids)))
        if len(robot_result) == len(result):
            return -1

        # (2.3)全是真实用户
        user_sql = "SELECT `userprofilebasic_ptr_id`, `has_been_spending_b` " \
                   "FROM `game_player` WHERE `userprofilebasic_ptr_id` " \
                   "in ({}) AND is_robot = 0"
        real_user_result = mysql_db.query(user_sql.format(",".join(player_ids)))
        if len(real_user_result) == len(result):
            is_all_real_user = True

        # 计算亏损率的方式
        # (充值金额 - 中奖金额 - 钱包余额) / 充值金额
        for row in real_user_result:
            game_player_id = row[0]
            cur_consume_amounts = row[1]
            # 判断该用户是否参与了55%以上,如果是,就跟他拼运气
            if str(game_player_id) in player_total_renci:
                if (Decimal(str(player_total_renci[str(game_player_id)])) / Decimal(str(target_amounts))) >= Decimal(str(0.55)):
                    self.logger.error("LuckLuckLuckLuckLuckLuckLuck")
                    return -1

            # 获取充值金额
            r = mysql_db.get("SELECT SUM(`payment_amount_cny`) FROM "
                             "`deposit_record` WHERE `to_player_id`={} AND "
                             "`status`=1".format(game_player_id))
            deposit_cnys = r[0] if r[0] else zero

            # 获取中奖金额
            r = mysql_db.get("SELECT SUM(`amounts`) FROM `prize_record` "
                             "WHERE `player_id`={}".format(game_player_id))
            prize_amounts = r[0] if r[0] else zero

            # 获取钱包余额
            wallet_result = mysql_db.get(
                "SELECT `id`, `user_id`, `balance` FROM `wallet` WHERE"
                "`user_id`={} AND `unit`={}".format(game_player_id, 1))
            wallet_balance = wallet_result[2]

            # 打印信息
            self.logger.error("{} {} {} {}".format(
                deposit_cnys, prize_amounts, wallet_balance, str(r)))

            # 这个用户当前的消费金额
            consume_money = self.query_user_consume(
                mysql_db, game_player_id, period_id)
            if deposit_cnys or consume_money:
                cur_loss_rate = round((deposit_cnys - prize_amounts - wallet_balance) / deposit_cnys, 3) if deposit_cnys else zero
                loss_rate = round((deposit_cnys - (prize_amounts + dh_price_cny) - wallet_balance) / deposit_cnys, 3) if deposit_cnys else zero
                self.logger.error("cur_loss_rate={} loss_rate={}".format(
                    cur_loss_rate, loss_rate))
                # 1.当前亏损比率大于等于max_loss_rate
                # 2.如果给他中奖的亏损比率大于等于min_loss_rate
                # 3.消费金额满1000
                # 4.候选人队列为空
                # 满足以上四个条件,可以加入候选人队列
                if cur_loss_rate > max_loss_rate \
                        and cur_consume_amounts >= 300 \
                        and loss_rate >= min_loss_rate \
                        and (not candidate_list):
                    candidate_list.append(row[0])

        # (3)候选列表为空
        if not candidate_list:
            if is_all_real_user:
                return -1
            else:
                # 根据正常的幸运token随机出一个机器人
                candidate_list.append(
                    self._get_one_robot(mysql_db, period_id, luck_token))
        return candidate_list

    def _get_one_robot(self, mysql_db, period_id, luck_token):
        # 获取所有机器人该期的所有夺宝号
        sql = "SELECT dpr.`token_str` FROM `duobao_participate_record` " \
              "AS dpr INNER JOIN `game_player` AS gp ON gp.`userprofilebasic_ptr_id`=" \
              "dpr.player_id INNER JOIN `period` as p ON p.`id` = " \
              "dpr.`period_id` WHERE gp.`is_robot`=1 AND p.`id` = {}" \
              "".format(period_id)
        robot_tokens = mysql_db.query(sql)
        robot_token_list = []
        for row in robot_tokens:
            robot_token_list.extend(row[0].split(","))
        robot_token_list.append(luck_token)
        robot_token_list = sorted(robot_token_list)
        inx = robot_token_list.index(luck_token)
        if inx:
            front = robot_token_list[inx - 1]
        else:
            front = robot_token_list[1]
        # 根据front这个夺宝号来获取机器人
        dpr_obj = self._get_dpr_record(front, mysql_db, period_id)
        return dpr_obj[1]

    def change_luck_token(self, mysql_db, period_id, luck_token,
                          target_amounts, a_value, content, candidate_list,
                          win_prize_player_id, win_prize_player_dpr_id,
                          ssc_no=None):
        """
        更改幸运夺宝号
        candidate_list 候选人列表
        以下情况不用更换幸运号码:
        1.指定中奖人已经拥有该幸运号码

        return 中奖人id 参与记录id 幸运号码
        """
        luck_token = str(luck_token)

        to_player_id = random.choice(candidate_list)

        # (1)获取该用户该期的夺宝号
        sql = "SELECT dpr.`token_str` FROM `duobao_participate_record` " \
              "AS dpr INNER JOIN `game_player` AS gp ON " \
              "gp.`userprofilebasic_ptr_id`= dpr.player_id " \
              "INNER JOIN `period` as p ON p.`id` = dpr.`period_id` " \
              "WHERE gp.`userprofilebasic_ptr_id`={} AND p.`id` = {}" \
              "".format(to_player_id, period_id)
        tokens = mysql_db.query(sql)
        token_list = []
        for row in tokens:
            token_list.extend(row[0].split(","))

        # (2)指定中奖人已经拥有该幸运夺宝号
        if luck_token in token_list:
            return win_prize_player_id, win_prize_player_dpr_id, luck_token
        else:
            token_list.append(luck_token)
        token_list = sorted(map(int, token_list))
        inx = token_list.index(int(luck_token))
        if inx:
            front = token_list[inx - 1]
        else:
            front = token_list[1]
        difference = int(luck_token) - int(front)  # 3 -3

        if ssc_no:
            changed_token = (a_value - difference + int(ssc_no)) % \
                            target_amounts + 10000001
        else:
            changed_token = (a_value - difference) % \
                            target_amounts + 10000001

        # 修改50个时间的其中一个
        content = json.loads(content)
        a_time_list = content["a_time_list"]

        last_but_one = a_time_list[-2]
        changed_time = datetime.strptime(
            "2000-1-1 " + last_but_one[0], "%Y-%m-%d %H:%M:%S.%f") - \
                       timedelta(milliseconds=difference)
        changed_time_str = changed_time.strftime('%H:%M:%S.%f')[:-3]
        changed_time_str_1 = changed_time_str.replace(
            ":", "").replace(".", "")
        last_but_one = [changed_time_str, int(changed_time_str_1),
                        last_but_one[-1]]
        a_time_list[-2] = last_but_one
        update_data = {
            "id": period_id,
            "content": json.dumps(content, ensure_ascii=False)
        }
        mysql_db.update(update_data, table_name="period")

        dpr_obj = self._get_dpr_record(changed_token, mysql_db, period_id)
        return to_player_id, dpr_obj[0], changed_token

    def _get_dpr_record(self, changed_token, mysql_db, period_id):
        dpr_sql = \
            """
            SELECT `id`, `player_id`,`token_str` FROM `duobao_participate_record`
            WHERE `period_id` = {} AND `token_str` like '{}'
            """
        dpr_obj = mysql_db.get(
            dpr_sql.format(period_id, '%%%%%s%%%%' % changed_token))
        return dpr_obj
