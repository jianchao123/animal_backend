# encoding: utf-8
from __future__ import absolute_import
import random, time, json
import datetime as datetime_m
from datetime import datetime, timedelta
from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.db import transaction
from shopping import celery_app
from financial.models import ConsumeRecord
from snatch_treasure.models import Period, DuoBaoParticipateRecord, \
    Order, ShiShiCai
from shopping_user.models import GamePlayer
from snatch_treasure.serializers import DprSerializer
from utils.cache_util import lock_nonblock, CacheUtil, Cache
from utils import utils
from utils import code_set
import logging

logger = logging.getLogger(__name__)


def _format_dpr_time(cur_time):
    """格式化参与时间"""
    hour = "%02d" % cur_time.hour
    minute = "%02d" % cur_time.minute
    second = "%02d" % cur_time.second
    millisecond = "%03d" % (cur_time.microsecond / 1000)

    dpr_time_str = str(hour) + ":" + str(minute) + ":" + str(second) \
                   + "." + str(millisecond)
    dpr_time_int = int(
        str(hour) + str(minute) + str(second) + str(millisecond))
    return dpr_time_str, dpr_time_int


def _fifty_time(cur_player, current_time):
    """
    50条时间
    :param cur_player:
    :param current_time:
    :return:
    """
    a_value = 0
    a_time_list = []

    # 49条参与的时间
    dprs = DuoBaoParticipateRecord.objects.order_by("-pk")[:49]
    for dpr in dprs:
        dpr_time_str, dpr_time_int = _format_dpr_time(dpr.time)
        a_value += dpr_time_int
        l = [dpr_time_str, dpr_time_int, dpr.player.get_nickname]
        a_time_list.append(l)
    # 玩家当前参与的时间
    dpr_time_str, dpr_time_int = _format_dpr_time(current_time)
    a_time_list.append(
        [dpr_time_str, dpr_time_int, cur_player.get_nickname])
    a_value += dpr_time_int
    return a_time_list, a_value


def _get_waiting_scc_period(shishicai):
    if shishicai:
        ssc_period_no = str(shishicai.ssc_period_no)
        prefix = ssc_period_no[:8]
        today_open_count = ssc_period_no[-3:]
        if int(today_open_count) < 59:
            return prefix + ('%03d' % (int(today_open_count) + 1))
        else:
            cur_date = datetime.strptime(prefix, "%Y%m%d")
            cur_date += timedelta(days=1)
            return cur_date.strftime("%Y%m%d") + "001"
    else:
        logger.error(u"没有时时彩记录")


@celery_app.task
def allocation_token(period_id):
    """分配token """
    d = CacheUtil.pop_period_queue(period_id)
    allocation_token_sync(d["amounts"], d["player_id"],
                          d["spend"], d["unit_price"], period_id=period_id)


@lock_nonblock
@transaction.atomic
def allocation_token_sync(amounts, player_id, spend, unit_price, period_id=None):
    """同步分配token"""
    spend = Decimal(str(spend))
    start_time = time.time()
    game_player = GamePlayer.objects.get(id=player_id)
    period = Period.objects.select_for_update().get(id=period_id)

    current_time = datetime.now()
    # 更新订单记录
    try:
        order = Order.objects.get(Q(period=period) & Q(player=game_player))
    except ObjectDoesNotExist:
        order = Order()
        order.order_no = utils.generate_out_trade_no('odr')
        order.player = game_player
        order.period = period
        order.count = 0
        order.unit_price = unit_price
        order.total_renci = 0
        order.total_fees = Decimal(str(0.0))
    order.count += 1
    order.total_renci += amounts
    order.total_fees += spend
    order.save()

    period.amounts_prepared += amounts
    period.rate = round(Decimal(str(period.amounts_prepared)) / Decimal(
        str(period.target_amounts)), 2)

    # 添加参与记录
    dpr_obj = DuoBaoParticipateRecord()
    dpr_obj.participate_amounts = amounts   # 人次
    dpr_obj.player = game_player
    dpr_obj.period = period
    dpr_obj.time = current_time
    dpr_obj.residue = period.target_amounts - period.amounts_prepared + amounts

    # TOKEN
    residue_token_str = period.residue_token_str
    token_nos = []
    residue_token_no = residue_token_str.split(",")
    for _ in xrange(amounts):
        random.seed()
        token_no = random.choice(residue_token_no)
        token_nos.append(token_no)
        residue_token_no.remove(token_no)
    # 保存参与记录token
    dpr_obj.token_str = ",".join(token_nos)
    dpr_obj.save()

    # 增加消费记录
    consume_obj = ConsumeRecord()
    consume_obj.period = period
    consume_obj.amounts = spend   # 消费金额
    consume_obj.renci = amounts                 # 人次
    consume_obj.participate = dpr_obj
    consume_obj.player = game_player
    consume_obj.status = code_set.ConsumeStatusCode.CONSUME_SUCCESS[0]
    consume_obj.save()

    period.residue_token_str = ",".join(residue_token_no)

    # 将参与时间加入redis
    if int(CacheUtil.get_fifty_len()) < 50:
        # 取50条时间放进去
        dprs = DuoBaoParticipateRecord.objects.order_by("-pk")[:50]
        for dpr in dprs:
            dpr_time_str, dpr_time_int = _format_dpr_time(dpr.time)
            l = [dpr_time_str, dpr_time_int, dpr.player.get_nickname]
            CacheUtil.right_push_fifty(l)
    else:
        dpr_time_str, dpr_time_int = _format_dpr_time(current_time)
        l = [dpr_time_str, dpr_time_int, game_player.get_nickname.encode('utf-8')]
        CacheUtil.right_push_fifty(l)

    participates = \
        DuoBaoParticipateRecord.objects.filter(period=period)

    participate_record_data = \
        DprSerializer(participates, many=True).data

    # 缓存荣誉榜
    honor_list_data = []
    data = {}
    if participate_record_data:
        participate_record_data = \
            sorted(participate_record_data,
                   key=lambda o: o['pk'])

        for row in participate_record_data:
            if row["player_id"] in data:
                data[row["player_id"]]["participate_renci"] += \
                    row["participate_renci"]
            else:
                data[row["player_id"]] = \
                    {"pk": row["pk"],
                     "participate_renci": row["participate_renci"],
                     "player_id": row["player_id"],
                     "player_nickname": row["player_nickname"],
                     "player_headimage": row["player_headimage"]}

        t = [v for k, v in data.items()]
        t = sorted(t, key=lambda o: o['participate_renci'], reverse=True)
        try:
            honor_list_data.append(t[0])
        except IndexError:
            pass
        try:
            honor_list_data.append(t[1])
        except IndexError:
            pass
        try:
            honor_list_data.append(t[2])
        except IndexError:
            pass
    content = json.loads(period.content)
    content["honor_list"] = honor_list_data

    playerids = {}
    for k in data:
        playerids[k] = data[k]["participate_renci"]
    content["playerids"] = playerids
    period.content = json.dumps(content)
    period.save()
    end_time = time.time()
    #logger.error("============" + str(end_time - start_time))

