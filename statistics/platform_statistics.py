# encoding: utf-8
from __future__ import absolute_import
import traceback
import datetime
from decimal import Decimal

import logging
from django.db.models import Q, Sum
from django.core.exceptions import ObjectDoesNotExist
from statistics.models import PlatformEverydayData
from financial.models import DepositRecord, PrizeRecord, \
    WithdrawRecord, BackProfitRecord
from activitys.models import PresentsRecord
from rest.models import GoodsDeliverRecord
from shopping_settings.models import PayType
from shopping_user.models import Wallet, GamePlayer
from utils import code_set

logger = logging.getLogger(__name__)


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
        Q(arrive_time__year=today_year) & Q(
            arrive_time__month=today_month) & Q(
            arrive_time__day=today_day)).aggregate(
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


def statistics_platform_data(today):
    try:
        zero = Decimal(str(0.0))
        today_year = today.year
        today_month = today.month
        today_day = today.day

        try:
            alipay_type = PayType.objects.get(code="ALIPAY")
            mkpay_type = PayType.objects.get(code="DC")
            wxpay_type = PayType.objects.get(code="WXPAY")
        except ObjectDoesNotExist:
            return
        try:
            platform_everyday_data = PlatformEverydayData. \
                objects.get(Q(data_date=today))
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
        platform_everyday_data.data_date = today
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


        # try:
        #     platform_everyday_data = PlatformEverydayData. \
        #         objects.get(Q(data_date=today))
        # except ObjectDoesNotExist:
        #     platform_everyday_data = PlatformEverydayData()
        # # 微信充值记录
        # wx_deposit_records = DepositRecord.objects.filter(
        #     Q(deposit_time__year=today_year) &
        #     Q(deposit_time__month=today_month) &
        #     Q(deposit_time__day=today_day) &
        #     Q(status=code_set.PayStatus.SUCCESS[0]) &
        #     Q(deposit_type=wxpay_type))
        # wx_cny = wx_deposit_records.aggregate(
        #     Sum('payment_amount_cny')).values()[0]
        # wx_deposit_count = wx_deposit_records.count()
        #
        # # 支付宝充值记录
        # ali_deposit_records = DepositRecord.objects.filter(
        #     Q(deposit_time__year=today_year) &
        #     Q(deposit_time__month=today_month) &
        #     Q(deposit_time__day=today_day) &
        #     Q(status=code_set.PayStatus.SUCCESS[0]) &
        #     Q(deposit_type=alipay_type))
        # alipay_cny = ali_deposit_records \
        #     .aggregate(Sum('payment_amount_cny')).values()[0]
        # alipay_deposit_count = ali_deposit_records.count()
        #
        # # 代充记录
        # deposit_records = DepositRecord.objects.filter(
        #     Q(deposit_time__year=today_year) &
        #     Q(deposit_time__month=today_month) &
        #     Q(deposit_time__day=today_day) & Q(
        #         deposit_type=mkpay_type))
        # dai_chong_cny = deposit_records \
        #     .aggregate(Sum('payment_amount_cny')).values()[0]
        # dai_chong_deposit_count = deposit_records.count()
        #
        # # 充值总金额
        # total_money = DepositRecord.objects.filter(
        #     Q(deposit_time__year=today_year) &
        #     Q(deposit_time__month=today_month) &
        #     Q(deposit_time__day=today_day) &
        #     Q(status=code_set.PayStatus.SUCCESS[0])).aggregate(
        #     Sum('payment_amount_cny')).values()[0]
        #
        # # 赠送总金额
        # presents_b = PresentsRecord.objects.filter(
        #     Q(present_time__year=today_year) &
        #     Q(present_time__month=today_month) &
        #     Q(present_time__day=today_day)).aggregate(
        #     Sum('amounts')).values()[0]
        #
        # shipment_phone_deposit_money, shipment_phone_shipment_money, shipment_phone_balance = _shipment_phones_data(
        #     today_year, today_month, today_day, zero)
        # profit_and_loss = shipment_phone_shipment_money - shipment_phone_deposit_money
        # platform_everyday_data.shipment_phone_deposit_cny = shipment_phone_deposit_money  # 出卡号充值金额
        # platform_everyday_data.shipment_phone_shipment_cny = shipment_phone_shipment_money  # 出卡号出货金额
        # platform_everyday_data.shipment_phone_profit_and_loss = profit_and_loss  # 出卡号盈利
        #
        # alipay_cny = alipay_cny if alipay_cny else zero
        # wx_cny = wx_cny if wx_cny else zero
        # dai_chong_cny = dai_chong_cny if dai_chong_cny else zero
        # presents_b = presents_b if presents_b else zero
        # total_money = total_money if total_money else zero
        #
        # # 今日支付宝充值金额
        # platform_everyday_data.alipay_cny = alipay_cny
        # # 支付宝充值次数
        # platform_everyday_data.alipay_deposit_count = alipay_deposit_count
        #
        # # 今日微信充值金额
        # platform_everyday_data.wx_cny = wx_cny
        # # 今日微信充值次数
        # platform_everyday_data.wx_deposit_count = wx_deposit_count
        #
        # # 今日代充金额
        # platform_everyday_data.dai_chong_cny = dai_chong_cny
        # # 代充次数
        # platform_everyday_data.dai_chong_deposit_count = dai_chong_deposit_count
        #
        # # 充值总金额
        # platform_everyday_data.deposit_total_cny = total_money
        # # 中奖总金额
        # platform_everyday_data.bonus = \
        #     _win_prize_price(today_year, today_month,
        #                      today_day, money_type='all')
        # # 赠送总金额
        # platform_everyday_data.presents_b = presents_b
        #
        # # 数据日期
        # platform_everyday_data.data_date = today
        # # 已结算状态
        # platform_everyday_data.status = code_set.SettlementStatus.SETTLED[0]
        #
        # # 三方充值收取的费用和费率
        # payrates_cny, pay_rates = _pay_rates(
        #     alipay_cny, wx_cny, today_year, today_month, today_day,
        #     wx_deposit_records, ali_deposit_records)
        # # 三方充值收取的费率
        # platform_everyday_data.pay_rates = pay_rates
        # platform_everyday_data.win_prize_entity_price = \
        #     _win_prize_price(today_year, today_month,
        #                      today_day, money_type='entity')
        # virtual_price = \
        #     _win_prize_price(today_year, today_month,
        #                      today_day, money_type='virtual')
        # platform_everyday_data.win_prize_virtual_price = virtual_price
        #
        # # 实物发货金额
        # platform_everyday_data.deliver_goods_entity_price = \
        #     _entity_deliver_good_money(today_year, today_month, today_day)
        # # 虚拟发货金额
        # platform_everyday_data.deliver_goods_virtual_price = virtual_price
        # # 卡商提现金额
        # platform_everyday_data.recycle_businessman_withdraw_price = \
        #     _withdraw_price(today_year, today_month, today_day)
        # # 卡商收货佣金
        # platform_everyday_data.recycle_commission = \
        #     _commission(today_year, today_month, today_day, back_profit_type=
        #     code_set.BackProfitType.recycle_back_profit[0])
        # # 卡商代充佣金
        # platform_everyday_data.dc_commission = \
        #     _commission(today_year, today_month, today_day, back_profit_type=
        #     code_set.BackProfitType.dc_back_profit[0])
        # # 卡商流水佣金
        # platform_everyday_data.ls_commission = \
        #     _commission(today_year, today_month, today_day, back_profit_type
        #     =code_set.BackProfitType.ls_back_profit[0])
        #
        # # 理论利润
        # ll_profit = (total_money - platform_everyday_data.shipment_phone_deposit_cny) - (platform_everyday_data.bonus - platform_everyday_data.shipment_phone_shipment_cny) - platform_everyday_data.recycle_commission - platform_everyday_data.dc_commission - \
        #             platform_everyday_data.ls_commission - payrates_cny
        # platform_everyday_data.ll_profit = ll_profit
        #
        # # 利润率
        # platform_everyday_data.profit_rate = Decimal(
        #     str(round(ll_profit / total_money, 4))) if total_money else zero
        # # 实际利润
        # platform_everyday_data.real_profit = ll_profit
        # platform_everyday_data.save()
    except:
        logger.error(traceback.format_exc())


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