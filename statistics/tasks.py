# encoding: utf-8
from __future__ import absolute_import
from shopping import celery_app
import traceback
import datetime
import json
import logging
from decimal import Decimal
from django.db.models import Q, Sum
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from statistics.models import UserEveryDayInfo, PlatformEverydayData, \
    RbEveryDayInfo, UserEveryMonthInfo
from shopping_user.models import GamePlayer, Wallet
from financial.models import DepositRecord, PrizeRecord, ConsumeRecord, \
    WithdrawRecord, BackProfitRecord
from activitys.models import PresentsRecord
from recycle_businessman.models import RecycleRecord, RecycleBusinessman, \
    InviteRecord
from rest.models import GoodsDeliverRecord
from snatch_treasure.models import Order
from shopping_settings.models import PayType, PayChannel
from shopping_user.business import change_wallet
from utils.utils import DecimalEncoder
from utils.cache_util import CacheUtil
from utils import code_set

logger = logging.getLogger(__name__)


@celery_app.task
def statistics_month_player_data():
    """统计玩家每月数据"""
    cur_date = datetime.date.today()
    year = cur_date.year
    month = cur_date.month - 1
    if not month:
        month = 12
        year -= 1
    date_str = ("%04d" % year) + ("%02d" % month)

    zero = Decimal(str(0.0))
    gameplayers = GamePlayer.objects.filter(is_robot=False)
    for gameplayer in gameplayers:

        # 总消费金额
        consume_cnys = ConsumeRecord.objects.filter(
            Q(player=gameplayer) &
            Q(period__status=code_set.PeriodStatusCode.REWARDED[0]) &
            Q(consume_time__year=year) & Q(consume_time__month=month)
        ).aggregate(Sum('amounts')).values()[0]
        consume_cnys = consume_cnys if consume_cnys else zero

        # 总充值
        deposit_cnys = DepositRecord.objects.filter(
            Q(to_player=gameplayer) &
            Q(status=code_set.PayStatus.SUCCESS[0]) &
            Q(deposit_time__year=year) & Q(deposit_time__month=month)
        ).aggregate(Sum('payment_amount_cny')).values()[0]
        deposit_cnys = deposit_cnys if deposit_cnys else zero

        # 总赠送
        presents = PresentsRecord.objects.filter(
            Q(to_player=gameplayer) &
            Q(present_time__year=year) & Q(present_time__month=month)
        ).aggregate(Sum('amounts')).values()[0]
        presents = presents if presents else zero

        # 总中奖
        prize_set = PrizeRecord.objects.filter(
            Q(player=gameplayer) &
            Q(prize_time__year=year) & Q(prize_time__month=month))
        prize_cnys = prize_set.aggregate(Sum('amounts')).values()[0]
        prize_cnys = prize_cnys if prize_cnys else zero

        # 中奖期数花费的金额
        periodids = [row.period.pk for row in prize_set]
        snatch_treasure_b = ConsumeRecord.objects.filter(
            Q(player=gameplayer) &
            Q(period_id__in=periodids)
        ).aggregate(Sum('amounts')).values()[0]
        snatch_treasure_b = snatch_treasure_b if snatch_treasure_b else zero

        # 订单次数
        order_count = Order.objects.filter(
            Q(player=gameplayer) &
            Q(status=code_set.OrderStatus.ORDERED[0]) &
            Q(create_time__year=year) & Q(create_time__month=month)
        ).count()

        try:
            user_every_month_info = \
                UserEveryMonthInfo.objects.get(data_date=date_str,
                                               player=gameplayer)
        except ObjectDoesNotExist:
            user_every_month_info = UserEveryMonthInfo()
            user_every_month_info.data_date = date_str
            user_every_month_info.player = gameplayer
        user_every_month_info.consume_money = consume_cnys
        user_every_month_info.deposit_money = deposit_cnys
        user_every_month_info.presents_money = presents
        user_every_month_info.bonus = prize_cnys
        user_every_month_info.snatch_treasure_b = snatch_treasure_b
        user_every_month_info.order_count = order_count
        user_every_month_info.update_time = datetime.datetime.now()
        user_every_month_info.save()


@celery_app.task
def statistics_player_data():
    """统计玩家数据 (每5分钟执行一次)"""
    zero = Decimal(str(0.0))
    cur_date = datetime.date.today()
    year = cur_date.year
    month = cur_date.month

    gameplayers = GamePlayer.objects.filter(is_robot=False)
    for gameplayer in gameplayers:
        # 账户余额
        wallet = Wallet.objects.get(Q(user_id=gameplayer.pk) &
                                    Q(unit=code_set.WalletUnit.B[0]))

        # 当月消费金额
        consume_cnys = ConsumeRecord.objects.filter(
            Q(player=gameplayer) &
            Q(period__status=code_set.PeriodStatusCode.REWARDED[0]) &
            Q(consume_time__year=year) &
            Q(consume_time__month=month)
        ).aggregate(Sum('amounts')).values()[0]
        consume_cnys = consume_cnys if consume_cnys else zero
        # 往月消费金额
        before_month_data = UserEveryMonthInfo.objects.filter(
            player=gameplayer)
        before_consume_cnys = before_month_data.aggregate(
            Sum('consume_money')).values()[0]
        before_consume_cnys = before_consume_cnys if before_consume_cnys else zero
        consume_cnys += before_consume_cnys

        # 总充值
        deposit_cnys = DepositRecord.objects.filter(
            Q(to_player=gameplayer) &
            Q(status=code_set.PayStatus.SUCCESS[0])).aggregate(
            Sum('payment_amount_cny')).values()[0]
        deposit_cnys = deposit_cnys if deposit_cnys else zero

        # 总赠送
        presents = PresentsRecord.objects.filter(
            Q(to_player=gameplayer)
        ).aggregate(Sum('amounts')).values()[0]
        presents = presents if presents else zero

        # 订单次数
        before_order_count = before_month_data.aggregate(
            Sum('order_count')).values()[0]
        before_order_count = before_order_count if before_order_count else 0
        order_count = Order.objects.filter(
            Q(player=gameplayer) &
            Q(status=code_set.OrderStatus.ORDERED[0]) &
            Q(create_time__year=year) & Q(create_time__month=month)
        ).count()
        order_count = order_count if order_count else 0
        order_count += before_order_count

        prize_set = PrizeRecord.objects.filter(Q(player=gameplayer))
        # 中奖次数
        prize_count = prize_set.count()
        # 中奖总金额
        prize_cnys = Decimal(str(0.0))
        # 中奖期数的商品市场总额
        market_price_cny = Decimal(str(0.0))

        periodids = []
        for row in prize_set:
            prize_cnys += row.amounts
            periodids.append(row.period.pk)
            market_price_cny += row.period.commodity.market_price_cny

        before_snatch_treasure_b = before_month_data.aggregate(
            Sum('snatch_treasure_b')).values()[0]
        before_snatch_treasure_b = before_snatch_treasure_b if \
            before_snatch_treasure_b else zero

        # 中奖期数花费的金额
        duobao_cnys = ConsumeRecord.objects.filter(
            Q(period_id__in=periodids) & Q(player=gameplayer) &
            Q(status=code_set.ConsumeStatusCode.CONSUME_SUCCESS[0]) &
            Q(consume_time__year=year) & Q(consume_time__month=month)
        ).aggregate(Sum('amounts')).values()[0]
        duobao_cnys = duobao_cnys if duobao_cnys else zero
        duobao_cnys += before_snatch_treasure_b

        gameplayer.has_been_spending_b = consume_cnys
        gameplayer.deposit_cny = deposit_cnys
        gameplayer.presents_b = presents
        gameplayer.participate_count = order_count
        gameplayer.win_prize_count = prize_count
        # 夺宝的期数所花费的总金额
        gameplayer.snatch_treasure_b = duobao_cnys
        gameplayer.market_price_cny = market_price_cny
        gameplayer.win_prize_amounts = prize_cnys
        # 亏损金额
        loss_amounts = consume_cnys - prize_cnys
        gameplayer.loss_amounts = deposit_cnys - prize_cnys - wallet.balance
        # （充值金额-中奖金额-账户余额）除以充值金额
        gameplayer.loss_rate = \
            round((deposit_cnys - prize_cnys - wallet.balance) / deposit_cnys,
                  3) if deposit_cnys else zero
        gameplayer.save()


@celery_app.task
def statistics_player_everyday_data():
    """统计玩家每日数据 (每40分钟执行一次)"""
    try:
        cur_time = datetime.datetime.now()
        day = cur_time.day
        month = cur_time.month
        year = cur_time.year
        today = datetime.date.today()

        zero = Decimal(str(0.0))
        gameplayers = GamePlayer.objects.filter(is_robot=False)
        for gameplayer in gameplayers:
            try:
                user_everyday_info = UserEveryDayInfo.objects.get(
                    Q(player=gameplayer) & Q(cur_date=today))
            except ObjectDoesNotExist:
                user_everyday_info = UserEveryDayInfo()

            # 充值金额
            deposit_cny = DepositRecord.objects.filter(
                Q(to_player=gameplayer) & Q(deposit_time__year=year) &
                Q(deposit_time__month=month) &
                Q(deposit_time__day=day) &
                Q(status=code_set.PayStatus.SUCCESS[0])).aggregate(
                Sum('payment_amount_cny')).values()[0]
            # 中奖金额
            bonus = PrizeRecord.objects.filter(
                Q(player=gameplayer) & Q(prize_time__year=year) & Q(
                    prize_time__month=month) & Q(
                    prize_time__day=day)).aggregate(
                Sum('amounts')).values()[0]
            # 赠送金额
            presents_b = PresentsRecord.objects.filter(
                Q(to_player=gameplayer) & Q(present_time__year=year) & Q(
                    present_time__month=month) & Q(
                    present_time__day=day)).aggregate(
                Sum('amounts')).values()[
                0]
            # 消费金额
            consume_cny = ConsumeRecord.objects.filter(
                Q(player=gameplayer) & Q(consume_time__year=year) &
                Q(consume_time__month=month) &
                Q(consume_time__day=day) &
                Q(status=code_set.ConsumeStatusCode.CONSUME_SUCCESS[0])
            ).aggregate(Sum('amounts')).values()[0]

            deposit_cny = deposit_cny if deposit_cny else zero
            bonus = bonus if bonus else zero
            presents_b = presents_b if presents_b else zero
            consume_cny = consume_cny if consume_cny else zero
            user_everyday_info.player = gameplayer
            user_everyday_info.deposit_cny = deposit_cny
            user_everyday_info.bonus = bonus
            user_everyday_info.difference = deposit_cny - bonus
            user_everyday_info.presents_b = presents_b
            user_everyday_info.cur_date = today
            user_everyday_info.consume_cny = consume_cny
            user_everyday_info.update_time = datetime.datetime.now()
            user_everyday_info.save()
    except:
        logger.error(traceback.format_exc())
    return True


# ################################ 回收商昨日数据 #############################


def _calculate_back_profit(recycle_records, dc_deposit_records,
                           relation_player_deposits, businessman):
    """
    计算返利
    :param recycle_records: 该回收商昨日的所有收货记录
    :param dc_deposit_records: 该回收商昨日的所有代充记录
    :param relation_player_deposits: 该回收商关联用户的昨日充值记录
    :param businessman: 回收商
    :return:
    """
    # 计算昨日收货总金额
    receive_record_ids = []
    receive_total_cny = Decimal(str(0.0))
    for recycle_record in recycle_records:
        receive_total_cny += recycle_record.recycle_price
        receive_record_ids.append(recycle_record.pk)

    # 计算昨日代充总金额
    dc_deposit_record_ids = []
    dai_chong_total_cny = Decimal(str(0.0))
    for deposit_record in dc_deposit_records:
        dai_chong_total_cny += deposit_record.payment_amount_cny
        dc_deposit_record_ids.append(deposit_record.pk)

    # 计算昨日该回收商关联用户的总充值流水
    ls_deposit_records_ids = []
    ls_total_cny = Decimal(str(0.0))
    for row in relation_player_deposits:
        ls_total_cny += row.payment_amount_cny
        ls_deposit_records_ids.append(row.pk)

    # 计算收货返利
    receive_back_profit_cny = receive_total_cny * businessman.recycle_back_rate
    # 计算代充返利
    dai_chong_back_profit_cny = \
        dai_chong_total_cny * businessman.deposit_back_rate
    # 计算关联用户充值流水返利(邀请返点)
    ls_back_profit_cny = ls_total_cny * businessman.invite_back_rate

    # 保存相关数据
    receive_record_content = {"ids": receive_record_ids,
                              "recycle_back_rate": businessman.recycle_back_rate}
    dc_deposit_record_content = \
        {"ids": dc_deposit_record_ids,
         "dc_deposit_bakc_rate": businessman.deposit_back_rate}
    ls_deposit_records_content = {"ids": ls_deposit_records_ids,
                                  "invite_back_rate": businessman.invite_back_rate}

    return receive_back_profit_cny, dai_chong_back_profit_cny, \
           ls_back_profit_cny, receive_record_content, \
           dc_deposit_record_content, ls_deposit_records_content, \
           receive_total_cny, dai_chong_total_cny, ls_total_cny


@celery_app.task
def statistics_rb_everyday_data():
    """回收商每日数据 凌晨00:01分开始执行(结算昨天的回收商返利)"""
    try:
        pay_type = PayType.objects.get(code=u"DC")
        zero = Decimal(str(0.0))
        today = datetime.date.today()

        # 昨天
        yesterday = today - datetime.timedelta(days=1)
        day = yesterday.day
        month = yesterday.month
        year = yesterday.year

        recycle_businessmans = RecycleBusinessman.objects.all()
        for recycle_businessman in recycle_businessmans:
            # 1.该回收商昨天的收货记录
            recycle_records = RecycleRecord.objects.filter(
                Q(recycle_time__year=year) & Q(recycle_time__month=month) &
                Q(recycle_time__day=day) &
                Q(recycle_businessman=recycle_businessman))

            # 2.该回收商昨天的代充记录
            dc_deposit_records = DepositRecord.objects.filter(
                Q(from_recycle_businessman=recycle_businessman) &
                Q(deposit_time__year=year) & Q(deposit_time__month=month) &
                Q(deposit_time__day=day) & Q(deposit_type=pay_type) &
                Q(status=code_set.PayStatus.SUCCESS[0]))

            # 3.该回收商邀请的用户的昨日充值流水
            playerids = InviteRecord.objects.filter(
                Q(recycle_businessman=recycle_businessman)).values_list(
                'invite_player', flat=True)
            playerids = [row for row in playerids]
            relation_player_deposits = \
                DepositRecord.objects.filter(
                    Q(deposit_time__year=year) &
                    Q(deposit_time__month=month) &
                    Q(deposit_time__day=day) &
                    Q(to_player_id__in=playerids) &
                    Q(status=code_set.PayStatus.SUCCESS[0]))

            # 结算返利
            receive_back_profit_cny, dai_chong_back_profit_cny, \
            ls_back_profit_cny, receive_total_cny, dai_chong_total_cny, \
            ls_total_cny = settlement_back_profit(
                recycle_businessman, today, yesterday, recycle_records,
                dc_deposit_records, relation_player_deposits)

            # 更新昨日数据
            try:
                rb_everyday_info = RbEveryDayInfo.objects.get(
                    Q(data_date=yesterday) &
                    Q(recycle_businessman=recycle_businessman) &
                    Q(status=code_set.SettlementStatus.NO_SETTLED[0]))
            except ObjectDoesNotExist:
                rb_everyday_info = RbEveryDayInfo()
                rb_everyday_info.recycle_businessman = recycle_businessman
                rb_everyday_info.data_date = yesterday

            rb_everyday_info.ls_cny = ls_total_cny
            rb_everyday_info.receive_cny = receive_total_cny
            rb_everyday_info.dai_chong_cny = dai_chong_total_cny
            # 返利
            rb_everyday_info.receive_back_profit_cny = receive_back_profit_cny
            rb_everyday_info.dai_chong_back_profit_cny = dai_chong_back_profit_cny
            rb_everyday_info.ls_back_profit_cny = ls_back_profit_cny
            # 总共利润
            rb_everyday_info.total = \
                receive_back_profit_cny + dai_chong_back_profit_cny + \
                ls_back_profit_cny
            rb_everyday_info.settlement_date = today
            rb_everyday_info.status = code_set.SettlementStatus.SETTLED[0]
            rb_everyday_info.save()

            # 初始化今日数据
            try:
                RbEveryDayInfo.objects.get(
                    Q(data_date=today) &
                    Q(recycle_businessman=recycle_businessman) &
                    Q(status=code_set.SettlementStatus.NO_SETTLED[0]))
            except ObjectDoesNotExist:
                rb_everyday_info = RbEveryDayInfo()
                rb_everyday_info.recycle_businessman = recycle_businessman
                rb_everyday_info.receive_cny = zero
                rb_everyday_info.dai_chong_cny = zero
                rb_everyday_info.receive_back_profit_cny = zero
                rb_everyday_info.dai_chong_back_profit_cny = zero
                rb_everyday_info.total = zero
                rb_everyday_info.data_date = today
                rb_everyday_info.status = code_set.SettlementStatus.NO_SETTLED[
                    0]
                rb_everyday_info.save()
    except:
        logger.error(traceback.format_exc())
    return True


@transaction.atomic
def settlement_back_profit(businessman, today, yesterday,
                           recycle_records, dc_deposit_records,
                           relation_player_deposits):
    """结算返利"""
    # 结算昨日返利数据
    receive_back_profit_cny, dai_chong_back_profit_cny, \
    ls_back_profit_cny, receive_record_content, \
    dc_deposit_record_content, ls_deposit_records_content, \
    receive_total_cny, dai_chong_total_cny, ls_total_cny = \
        _calculate_back_profit(recycle_records,
                               dc_deposit_records,
                               relation_player_deposits, businessman)
    # 添加返利记录
    try:
        BackProfitRecord.objects.get(
            Q(back_profit_date=yesterday) &
            Q(to_recycle_businessman=businessman) &
            Q(back_profit_type=code_set.BackProfitType.ls_back_profit[0]))
    except ObjectDoesNotExist:
        # >流水
        back_profit_record = BackProfitRecord()
        back_profit_record.amounts = ls_back_profit_cny
        back_profit_record.back_profit_type = \
            code_set.BackProfitType.ls_back_profit[0]
        back_profit_record.to_recycle_businessman = businessman
        back_profit_record.back_profit_date = yesterday
        back_profit_record.settlement_date = today
        back_profit_record.relation_ids = \
            json.dumps(ls_deposit_records_content, cls=DecimalEncoder)
        back_profit_record.status = code_set.BackProfitStatus.BACKED[0]
        back_profit_record.save()

    try:
        BackProfitRecord.objects.get(
            Q(back_profit_date=yesterday) &
            Q(to_recycle_businessman=businessman) &
            Q(back_profit_type=code_set.BackProfitType.dc_back_profit[0]))
    except ObjectDoesNotExist:
        # >代充
        back_profit_record = BackProfitRecord()
        back_profit_record.amounts = dai_chong_back_profit_cny
        back_profit_record.back_profit_type = \
            code_set.BackProfitType.dc_back_profit[0]
        back_profit_record.to_recycle_businessman = businessman
        back_profit_record.back_profit_date = yesterday
        back_profit_record.settlement_date = today
        back_profit_record.relation_ids = \
            json.dumps(dc_deposit_record_content, cls=DecimalEncoder)
        back_profit_record.status = code_set.BackProfitStatus.BACKED[0]
        back_profit_record.save()
    try:
        BackProfitRecord.objects.get(
            Q(back_profit_date=yesterday) &
            Q(to_recycle_businessman=businessman) &
            Q(back_profit_type=code_set.BackProfitType.recycle_back_profit[0]))
    except ObjectDoesNotExist:
        # >收货
        back_profit_record = BackProfitRecord()
        back_profit_record.amounts = receive_back_profit_cny
        back_profit_record.back_profit_type = \
            code_set.BackProfitType.recycle_back_profit[0]
        back_profit_record.to_recycle_businessman = businessman
        back_profit_record.back_profit_date = yesterday
        back_profit_record.settlement_date = today
        back_profit_record.relation_ids = \
            json.dumps(receive_record_content, cls=DecimalEncoder)
        back_profit_record.status = code_set.BackProfitStatus.BACKED[0]
        back_profit_record.save()

        # 修改余额成功
        change_cny = receive_back_profit_cny + \
                     dai_chong_back_profit_cny + ls_back_profit_cny
        if change_cny:
            if change_wallet(change_cny,
                             unit=code_set.WalletUnit.CNY[0],
                             user_id=businessman.pk):
                # 标记为已返利 (代充记录会被重复标记)
                recycle_records.update(is_ret=True)
                dc_deposit_records.update(is_ret=True)
                relation_player_deposits.update(is_ret=True)

    return receive_back_profit_cny, dai_chong_back_profit_cny, \
           ls_back_profit_cny, receive_total_cny, \
           dai_chong_total_cny, ls_total_cny


@celery_app.task
def calcul_business_today_data():
    """计算卡商今日数据"""
    try:
        pay_type = PayType.objects.get(code=u"DC")
        zero = Decimal(str(0.0))
        today = datetime.date.today()

        day = today.day
        month = today.month
        year = today.year

        recycle_businessmans = RecycleBusinessman.objects.all()
        for recycle_businessman in recycle_businessmans:
            # 1.该回收商今天的收货记录
            recycle_records = RecycleRecord.objects.filter(
                Q(recycle_time__year=year) & Q(recycle_time__month=month) &
                Q(recycle_time__day=day) &
                Q(recycle_businessman=recycle_businessman))

            # 2.该回收商今天的代充记录
            dc_deposit_records = DepositRecord.objects.filter(
                Q(from_recycle_businessman=recycle_businessman) &
                Q(deposit_time__year=year) & Q(deposit_time__month=month) &
                Q(deposit_time__day=day) & Q(deposit_type=pay_type) &
                Q(status=code_set.PayStatus.SUCCESS[0]))

            # 3.该回收商邀请的用户的今日充值流水
            playerids = InviteRecord.objects.filter(
                Q(recycle_businessman=recycle_businessman)).values_list(
                'invite_player', flat=True)
            playerids = [row for row in playerids]
            relation_player_deposits = \
                DepositRecord.objects.filter(
                    Q(deposit_time__year=year) &
                    Q(deposit_time__month=month) &
                    Q(deposit_time__day=day) &
                    Q(to_player_id__in=playerids) &
                    Q(status=code_set.PayStatus.SUCCESS[0]))

            # 结算返利
            receive_record_ids = []
            receive_total_cny = Decimal(str(0.0))
            for recycle_record in recycle_records:
                receive_total_cny += recycle_record.recycle_price
                receive_record_ids.append(recycle_record.pk)

            # 计算昨日代充总金额
            dc_deposit_record_ids = []
            dai_chong_total_cny = Decimal(str(0.0))
            for deposit_record in dc_deposit_records:
                dai_chong_total_cny += deposit_record.payment_amount_cny
                dc_deposit_record_ids.append(deposit_record.pk)

            # 计算昨日该回收商关联用户的总充值流水
            ls_deposit_records_ids = []
            ls_total_cny = Decimal(str(0.0))
            for row in relation_player_deposits:
                ls_total_cny += row.payment_amount_cny
                ls_deposit_records_ids.append(row.pk)

            # 计算收货返利
            receive_back_profit_cny = receive_total_cny * recycle_businessman.recycle_back_rate
            # 计算代充返利
            dai_chong_back_profit_cny = \
                dai_chong_total_cny * recycle_businessman.deposit_back_rate
            # 计算关联用户充值流水返利(邀请返点)
            ls_back_profit_cny = ls_total_cny * recycle_businessman.invite_back_rate

            # 更新今日数据
            try:
                rb_everyday_info = RbEveryDayInfo.objects.get(
                    Q(data_date=today) &
                    Q(recycle_businessman=recycle_businessman) &
                    Q(status=code_set.SettlementStatus.NO_SETTLED[0]))
            except ObjectDoesNotExist:
                rb_everyday_info = RbEveryDayInfo()
                rb_everyday_info.recycle_businessman = recycle_businessman
                rb_everyday_info.data_date = today

            rb_everyday_info.receive_cny = receive_total_cny
            rb_everyday_info.dai_chong_cny = dai_chong_total_cny
            # 返利
            rb_everyday_info.receive_back_profit_cny = receive_back_profit_cny
            rb_everyday_info.dai_chong_back_profit_cny = dai_chong_back_profit_cny
            rb_everyday_info.ls_back_profit_cny = ls_back_profit_cny
            # 总共利润
            rb_everyday_info.total = \
                receive_back_profit_cny + dai_chong_back_profit_cny + \
                ls_back_profit_cny
            rb_everyday_info.settlement_date = today
            rb_everyday_info.status = code_set.SettlementStatus.NO_SETTLED[0]
            rb_everyday_info.save()

    except:
        logger.error(traceback.format_exc())
    return True


# ############################## 平台每日数据 #################################


def _pay_rates(alipay_cny, wx_cny, year, month, day, wx_deposits,
               ali_deposits):
    """
    获取各个三方支付收取的费用

    目前有的三方充值
    1.微信
    2.支付宝
    ：return 三方收取的总手续费和比率
    """
    third_party_total_money = alipay_cny + wx_cny
    # 三方收取的总费用(微信记录)
    sfsqdfy_sum = Decimal(str(0.0))
    for row in wx_deposits:
        sfsqdfy = Decimal(str(round(
            row.channel_rate * row.payment_amount_cny, 4)))
        sfsqdfy_sum += sfsqdfy
    # 三方收取的总费用(支付宝记录)
    for row in ali_deposits:
        sfsqdfy = Decimal(str(round(
            row.channel_rate * row.payment_amount_cny, 4)))
        sfsqdfy_sum += sfsqdfy

    if not third_party_total_money:
        return Decimal(str(0.0)), Decimal(str(0.0))
    return sfsqdfy_sum, Decimal(
        str(round((sfsqdfy_sum / third_party_total_money), 4)))


def _win_prize_price(today_year, today_month, today_day, money_type=None):
    """中奖金额"""
    queryset = PrizeRecord.objects.filter(
        Q(prize_time__year=today_year) & Q(
            prize_time__month=today_month) & Q(
            prize_time__day=today_day) & Q(player__is_robot=False))

    # 中奖金额类型
    if money_type == 'entity':
        queryset = queryset.filter(Q(period__commodity__is_card=False))
    elif money_type == 'virtual':
        queryset = queryset.filter(Q(period__commodity__is_card=True))
    elif money_type == 'all':
        pass
    prize_money = queryset.aggregate(Sum('amounts')).values()[0]
    return prize_money if prize_money else Decimal(str(0.0))


def _entity_deliver_good_money(today_year, today_month, today_day):
    """实物发货金额"""
    zero = Decimal(str('0.0'))
    deliver_good_money = GoodsDeliverRecord.objects.filter(
        Q(deliver_goods_time__year=today_year) &
        Q(deliver_goods_time__month=today_month) &
        Q(deliver_goods_time__day=today_day)).aggregate(
        Sum('real_price_cny')).values()[0]
    return deliver_good_money if deliver_good_money else zero


def _withdraw_price(today_year, today_month, today_day):
    """回收商提现金额"""
    withdraws = WithdrawRecord.objects.filter(
        Q(arrive_time__year=today_year) &
        Q(arrive_time__month=today_month) &
        Q(arrive_time__day=today_day) &
        Q(status=2)).aggregate(
        Sum('amounts')).values()[0]
    return withdraws if withdraws else Decimal(str(0.0))


def _commission(today_year, today_month, today_day, back_profit_type):
    """佣金 直接从BackProfitRecord获取"""
    queryset = BackProfitRecord.objects.filter(
        Q(back_profit_date__year=today_year) & Q(
            back_profit_date__month=today_month) & Q(
            back_profit_date__day=today_day) & Q(
            back_profit_type=back_profit_type))
    commission = queryset.aggregate(Sum('amounts')).values()[0]
    return commission if commission else Decimal(str(0.0))


def platform_data_by_day(cur_day):
    """
    根据日期计算平台数据
    """
    try:
        zero = Decimal(str(0.0))
        today_year = cur_day.year
        today_month = cur_day.month
        today_day = cur_day.day

        try:
            alipay_type = PayType.objects.get(code="ALIPAY")
            mkpay_type = PayType.objects.get(code="DC")
            wxpay_type = PayType.objects.get(code="WXPAY")
        except ObjectDoesNotExist:
            return
        try:
            platform_everyday_data = PlatformEverydayData. \
                objects.get(Q(data_date=cur_day))
        except ObjectDoesNotExist:
            platform_everyday_data = PlatformEverydayData()
        # 微信充值记录
        wx_deposit_records = DepositRecord.objects.filter(
            Q(deposit_time__year=today_year) &
            Q(deposit_time__month=today_month) &
            Q(deposit_time__day=today_day) &
            Q(status=code_set.PayStatus.SUCCESS[0]) &
            Q(deposit_type=wxpay_type))
        wx_cny = wx_deposit_records.aggregate(
            Sum('payment_amount_cny')).values()[0]
        wx_deposit_count = wx_deposit_records.count()

        # 支付宝充值记录
        ali_deposit_records = DepositRecord.objects.filter(
            Q(deposit_time__year=today_year) &
            Q(deposit_time__month=today_month) &
            Q(deposit_time__day=today_day) &
            Q(status=code_set.PayStatus.SUCCESS[0]) &
            Q(deposit_type=alipay_type))
        alipay_cny = ali_deposit_records \
            .aggregate(Sum('payment_amount_cny')).values()[0]
        alipay_deposit_count = ali_deposit_records.count()

        # 代充记录
        deposit_records = DepositRecord.objects.filter(
            Q(deposit_time__year=today_year) &
            Q(deposit_time__month=today_month) &
            Q(deposit_time__day=today_day) & Q(
                deposit_type=mkpay_type))
        dai_chong_cny = deposit_records \
            .aggregate(Sum('payment_amount_cny')).values()[0]
        dai_chong_deposit_count = deposit_records.count()

        # 充值总金额
        total_money = DepositRecord.objects.filter(
            Q(deposit_time__year=today_year) &
            Q(deposit_time__month=today_month) &
            Q(deposit_time__day=today_day) &
            Q(status=code_set.PayStatus.SUCCESS[0])).aggregate(
            Sum('payment_amount_cny')).values()[0]

        # 赠送总金额
        presents_b = PresentsRecord.objects.filter(
            Q(present_time__year=today_year) &
            Q(present_time__month=today_month) &
            Q(present_time__day=today_day)).aggregate(
            Sum('amounts')).values()[0]

        shipment_phone_deposit_money, shipment_phone_shipment_money, shipment_phone_balance = _shipment_phones_data(today_year, today_month, today_day, zero)
        profit_and_loss = shipment_phone_shipment_money - shipment_phone_deposit_money
        platform_everyday_data.shipment_phone_deposit_cny = shipment_phone_deposit_money        # 出卡号充值金额
        platform_everyday_data.shipment_phone_shipment_cny = shipment_phone_shipment_money      # 出卡号出货金额
        platform_everyday_data.shipment_phone_profit_and_loss = profit_and_loss                 # 出卡号盈利

        alipay_cny = alipay_cny if alipay_cny else zero
        wx_cny = wx_cny if wx_cny else zero
        dai_chong_cny = dai_chong_cny if dai_chong_cny else zero
        presents_b = presents_b if presents_b else zero
        total_money = total_money if total_money else zero

        # 今日支付宝充值金额
        platform_everyday_data.alipay_cny = alipay_cny
        # 支付宝充值次数
        platform_everyday_data.alipay_deposit_count = alipay_deposit_count

        # 今日微信充值金额
        platform_everyday_data.wx_cny = wx_cny
        # 今日微信充值次数
        platform_everyday_data.wx_deposit_count = wx_deposit_count

        # 今日代充金额
        platform_everyday_data.dai_chong_cny = dai_chong_cny
        # 代充次数
        platform_everyday_data.dai_chong_deposit_count = dai_chong_deposit_count

        # 充值总金额
        platform_everyday_data.deposit_total_cny = total_money
        # 中奖总金额
        platform_everyday_data.bonus = \
            _win_prize_price(today_year, today_month,
                             today_day, money_type='all')
        # 赠送总金额
        platform_everyday_data.presents_b = presents_b

        # 数据日期
        platform_everyday_data.data_date = cur_day
        # 已结算状态
        platform_everyday_data.status = code_set.SettlementStatus.SETTLED[0]

        # 三方充值收取的费用和费率
        payrates_cny, pay_rates = _pay_rates(
            alipay_cny, wx_cny, today_year, today_month, today_day,
            wx_deposit_records, ali_deposit_records)
        # 三方充值收取的费率
        platform_everyday_data.pay_rates = pay_rates
        platform_everyday_data.win_prize_entity_price = \
            _win_prize_price(today_year, today_month,
                             today_day, money_type='entity')
        virtual_price = \
            _win_prize_price(today_year, today_month,
                             today_day, money_type='virtual')
        platform_everyday_data.win_prize_virtual_price = virtual_price

        # 实物发货金额
        platform_everyday_data.deliver_goods_entity_price = \
            _entity_deliver_good_money(today_year, today_month, today_day)
        # 虚拟发货金额
        platform_everyday_data.deliver_goods_virtual_price = virtual_price
        # 卡商提现金额
        platform_everyday_data.recycle_businessman_withdraw_price = \
            _withdraw_price(today_year, today_month, today_day)
        # 卡商收货佣金
        platform_everyday_data.recycle_commission = \
            _commission(today_year, today_month, today_day, back_profit_type=
            code_set.BackProfitType.recycle_back_profit[0])
        # 卡商代充佣金
        platform_everyday_data.dc_commission = \
            _commission(today_year, today_month, today_day, back_profit_type=
            code_set.BackProfitType.dc_back_profit[0])
        # 卡商流水佣金
        platform_everyday_data.ls_commission = \
            _commission(today_year, today_month, today_day, back_profit_type
            =code_set.BackProfitType.ls_back_profit[0])

        # 理论利润
        ll_profit = (total_money - platform_everyday_data.shipment_phone_deposit_cny) - (platform_everyday_data.bonus - platform_everyday_data.shipment_phone_shipment_cny) - platform_everyday_data.recycle_commission - platform_everyday_data.dc_commission - \
                    platform_everyday_data.ls_commission - payrates_cny
        platform_everyday_data.ll_profit = ll_profit

        # 利润率
        platform_everyday_data.profit_rate = Decimal(
            str(round(ll_profit / total_money, 4))) if total_money else zero
        # 实际利润
        platform_everyday_data.real_profit = ll_profit
        platform_everyday_data.save()
    except:
        logger.error(traceback.format_exc())


@celery_app.task
def statistics_platform_data():
    """统计平台每日数据 (每5s跑一次, 每小时的59分钟的时候执行)"""
    cur_time = datetime.datetime.now()

    if cur_time.minute == 1:
        CacheUtil.delete_control_flag("statistics_platform_data")
    control = CacheUtil.get_control_flag("statistics_platform_data")
    if cur_time.minute != 59 or control:
        return
    CacheUtil.set_control_flag("statistics_platform_data")
    platform_data_by_day(datetime.date.today())
    return True


@celery_app.task
def improve_yesterday_platform_data():
    """完善昨日平台数据"""
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    platform_data_by_day(yesterday)
    return True


def _shipment_phones_data(today_year, today_month, today_day, zero):
    """出卡号数据"""
    from shopping_settings.models import CommonParamConf
    conf = CommonParamConf.objects.get(conf_key='shipment_phones')
    phones = conf.conf_value.split(',')
    # 出卡号充值总额
    deposit_money = DepositRecord.objects.filter(
        Q(deposit_time__year=today_year) &
        Q(deposit_time__month=today_month) &
        Q(deposit_time__day=today_day) &
        Q(to_player__phone__in=phones)).aggregate(
        Sum('payment_amount_cny')).values()[0]
    deposit_money = deposit_money if deposit_money else zero
    # 出卡号充值赠送总额
    present_moeny = PresentsRecord.objects.filter(
        Q(present_time__year=today_year) &
        Q(present_time__month=today_month) &
        Q(present_time__day=today_day) &
        Q(to_player__phone__in=phones)
    ).aggregate(Sum('amounts')).values()[0]
    deposit_money += present_moeny if present_moeny else zero

    # 出卡总额
    shipment_cny = PrizeRecord.objects.filter(
        Q(prize_time__year=today_year) &
        Q(prize_time__month=today_month) &
        Q(prize_time__day=today_day) &
        Q(player__phone__in=phones)).aggregate(
        Sum('amounts')).values()[0]
    shipment_cny = shipment_cny if shipment_cny else zero

    # 出卡号ids
    user_ids = GamePlayer.objects.filter(
        phone__in=phones).values_list('id', flat=True)
    balance = Wallet.objects.filter(user_id__in=user_ids).aggregate(
        Sum('balance')).values()[0]
    balance = balance if balance else zero
    return deposit_money, shipment_cny, balance