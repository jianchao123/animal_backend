# coding:utf-8
import json
import hashlib
from datetime import datetime
from decimal import Decimal
from collections import defaultdict
from rest_framework import generics
from django.conf import settings
from django.db.models import Q
from django.http import HttpResponse
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from shopping_user.business import change_wallet

from utils import framework
from utils import utils
from utils.AppError import AppError
from utils import code_set
from utils.cache_util import CacheUtil
from utils.cache_util import lock_pay_func

from shopping_settings.models import PayType, PayChannel, PayAccountsConf, \
    PayMoneyCtl
from financial.models import DepositRecord
from shopping_user.models import GamePlayer
from activitys.models import PresentsRecord
from shopping_user.permissions import IsGamePlayer
from financial.serializers import DepositOrderSerializer
from tasks import deposit_present_notice
import ailifu
import vippay
import a_eight
import logging

logger = logging.getLogger(__name__)


class WxScanCodeDeposit(generics.CreateAPIView):
    """所有通道充值接口"""

    permission_classes = (IsGamePlayer,)

    @framework.post_require_check([])
    def post(self, request, *args, **kwargs):
        user = request.user
        amounts = int(request.data["amounts"])
        if amounts < 1 or amounts > 999999:
            raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)

        # 用户选择的支付通道
        r = CacheUtil.get_user_choice_pay_channel(user.id)
        if not r:
            raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)

        pay_channel_id = int(r)

        try:
            player = GamePlayer.objects.get(pk=user.pk)
        except ObjectDoesNotExist:
            raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)
        pay_channel = PayChannel.objects.get(id=pay_channel_id)
        pay_type = pay_channel.pay_type

        pay_accounts_confs = PayAccountsConf.objects.filter(
            Q(pay_channel=pay_channel) &
            Q(status=code_set.PayAccountsConfStatus.NORMAL[0]))
        if not pay_accounts_confs.count():
            raise AppError(*code_set.SubErrorCode.NOT_ADD_CONFIGURE_ERROR)
        pay_accounts_conf = pay_accounts_confs[0]

        data = {}
        out_trade_no = utils.generate_out_trade_no('DPT')
        if pay_channel.company == "XIXI":
            d = ailifu.xixi_pay(amounts, out_trade_no, pay_accounts_conf)
            data["pay_type"] = "XIXI_PAY"
            data["d"] = d
            data["url"] = settings.XIXI_LINK

        if pay_channel.company == "VIP":
            d, param = vippay.vip_pay(amounts, out_trade_no,
                                      u"牛肉面".encode("utf8"),
                                      pay_channel.code,
                                      pay_accounts_conf.merchant_no)
            data["pay_type"] = "VIP_PAY"
            data["url"] = d
        if pay_channel.company == "A8_PAY":
            d = a_eight.a_eight_pay(amounts, out_trade_no, pay_accounts_conf.merchant_no, pay_accounts_conf.pay_channel.code)
            data["pay_type"] = "A8_PAY"
            data["d"] = d
            data["url"] = settings.A_EIGHT_LINK
        # 增加充值记录
        deposit_record = DepositRecord()
        # 商户号
        deposit_record.commercial_tenant_nos = pay_accounts_conf.merchant_no
        # 实际支付金额
        deposit_record.payment_amount_cny = amounts
        # 自家交易号
        deposit_record.out_trade_no = out_trade_no
        # 充值豆子数量
        deposit_record.amounts = amounts
        deposit_record.units = 1
        deposit_record.to_player = player
        deposit_record.deposit_type = pay_type
        deposit_record.deposit_channel = pay_channel
        deposit_record.channel_rate = pay_channel.rate
        deposit_record.deposit_time = datetime.now()
        deposit_record.status = 0  # 等待付款
        deposit_record.save()
        logger.error("===============prepay=============" + json.dumps(data))

        return data


class AlfNotify(generics.CreateAPIView):
    """爱立付 nofity"""

    serializer_class = DepositOrderSerializer

    @lock_pay_func
    @transaction.atomic
    def post(self, request, *args, **kwargs):

        sign = request.data["sign"]
        memberid = request.data["memberid"]
        orderid = request.data["orderid"]
        amount = request.data["amount"]
        transaction_id = request.data["transaction_id"]
        datetime_s = request.data["datetime"]
        returncode = request.data["returncode"]

        d = defaultdict()
        d["memberid"] = memberid
        d["orderid"] = orderid
        d["amount"] = amount
        d["transaction_id"] = transaction_id
        d["datetime"] = datetime_s
        d["returncode"] = returncode
        sign_str = ailifu.signature(d, settings.ALIFU_KEY)
        if sign != sign_str:
            logger.error("{}={}".format(sign, sign_str))
            return HttpResponse("")

        try:
            deposit_record = \
                DepositRecord.objects.select_for_update().get(
                    Q(out_trade_no=orderid))
        except ObjectDoesNotExist:
            logger.error("missing orderid={}".format(orderid))
            return HttpResponse("")
        if sign == sign_str and deposit_record.status == \
                code_set.PayStatus.WAITING[0]:

            player = deposit_record.to_player
            # 是否首充,增加赠送的豆子
            present_amounts = Decimal(str(0.0))
            if not DepositRecord.objects.filter(
                            Q(to_player=player) &
                            Q(status=code_set.PayStatus.SUCCESS[0])).count():
                present_amounts += Decimal(
                    str(int(Decimal(str(amount)) / 10 * 1)))
                # 增加赠送记录
                present_record = PresentsRecord()
                present_record.amounts = present_amounts
                present_record.to_player = player
                present_record.presents_type = \
                    code_set.PresentStatus.FIRST_DEPOSIT[0]
                present_record.msg_content = \
                    u"动物世界赠送您{}豆子,快去消费吧!".format(present_amounts)
                present_record.save()

            # 先保存记录再增加余额

            deposit_record.status = code_set.PayStatus.SUCCESS[0]
            deposit_record.trade_no = transaction_id
            deposit_record.remark = str(request.data)
            deposit_record.deposit_time = datetime.now()
            deposit_record.save()

            deposit_present_notice.apply_async(
                args=[player.phone, str(amount), str(present_amounts)],
                exchange='pay',
                routing_key="pay_success")
            # 余额
            change_wallet(Decimal(str(amount)) + present_amounts,
                          unit=code_set.WalletUnit.B[0],
                          user_id=player.pk)

            # 增加充值成功通知
            # jpush_obj = PushHelper(settings.NOTIFY_APP_KEY,
            #                        settings.NOTIFY_SCRECT_KEY)
            # data = {
            #     "player_id": deposit_record.to_player.pk,
            #     "amounts": amount,
            #     "status": code_set.PayStatus.SUCCESS[0]
            # }
            #
            # string = u"充值成功 ￥{},快去个人中心查看余额吧！".format(amount)
            # android_alert_data = string
            # ios_alert_data = string
            # jpush_obj.push_to_user(json.dumps(data),
            #                        android_alert_data,
            #                        ios_alert_data,
            #                        u"充值成功提醒",
            #                        deposit_record.to_player.uid)

        return HttpResponse("OK")


class GetPayMoney(generics.ListAPIView):
    """获取支付金额"""

    permission_classes = (IsGamePlayer,)

    @framework.get_require_check([])
    def get(self, request, *args, **kwargs):
        user = request.user
        try:
            # 随机获取一条可用的支付通道
            pay_channel = PayChannel.objects.filter(status=1).first()
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            raise AppError(*code_set.SubErrorCode.MONEY_SECTION_ERROR)

        CacheUtil.set_user_choice_pay_channel(user.id, pay_channel.id)
        return pay_channel.money_str.split(",")


class VipNotify(generics.CreateAPIView):
    serializer_class = DepositOrderSerializer

    @lock_pay_func
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        data = request.data
        p_name = data["p_name"]
        p_oid = data["p_oid"]
        p_money = data["p_money"]
        p_code = data["p_code"]
        p_sid = data["p_sid"]
        p_md5 = data["p_md5"]

        sign_str = vippay.signature(p_name, p_oid, p_money)
        logger.error(sign_str, p_md5)
        logger.error(data)
        if sign_str != p_md5:
            return HttpResponse("")

        if sign_str == p_md5 and p_code == '1':
            deposit_record = DepositRecord.objects.select_for_update().get(
                Q(out_trade_no=p_oid))
            if deposit_record.status == code_set.PayStatus.WAITING[0]:
                player = deposit_record.to_player
                # 是否首充,增加赠送的豆子
                present_amounts = Decimal(str(0.0))
                if not DepositRecord.objects.filter(
                                Q(to_player=player) &
                                Q(status=code_set.PayStatus.SUCCESS[
                                    0])).count():
                    present_amounts += Decimal(
                        str(int(Decimal(str(p_money)) / 10 * 1)))
                    # 增加赠送记录
                    present_record = PresentsRecord()
                    present_record.amounts = present_amounts
                    present_record.to_player = player
                    present_record.presents_type = \
                        code_set.PresentStatus.FIRST_DEPOSIT[0]
                    present_record.msg_content = \
                        u"动物世界赠送您{}豆子,快去消费吧!".format(present_amounts)
                    present_record.save()

                # 先保存记录再增加余额
                deposit_record.status = code_set.PayStatus.SUCCESS[0]
                deposit_record.trade_no = p_sid
                deposit_record.remark = str(request.data)
                deposit_record.deposit_time = datetime.now()
                deposit_record.save()
                deposit_present_notice.apply_async(
                    args=[player.phone, str(p_money), str(present_amounts)],
                    exchange='pay',
                    routing_key="pay_success")
                # 余额
                change_wallet(Decimal(str(p_money)) + present_amounts,
                              unit=code_set.WalletUnit.B[0],
                              user_id=player.pk)
        return HttpResponse("success")


class AEightPay(generics.CreateAPIView):
    """A8支付回调"""
    serializer_class = DepositOrderSerializer

    @lock_pay_func
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        data = request.data
        merchant_no = data["merchant_no"]
        order_no = data["order_no"]
        platform_order_no = data["platform_order_no"]
        order_money = data["order_money"]
        pay_time = data["pay_time"]
        sign = data["sign"]

        raw_sign_str = merchant_no + settings.A_EIGHT_KEY + order_no + platform_order_no + str(order_money) + pay_time
        m = hashlib.md5(raw_sign_str.encode('utf-8'))
        sign_str = m.hexdigest()
        if sign_str != sign:
            return HttpResponse("")

        if sign_str == sign:
            order_money = int(order_money) / 100
            deposit_record = DepositRecord.objects.select_for_update().get(
                Q(out_trade_no=order_no))
            if deposit_record.status == code_set.PayStatus.WAITING[0]:
                player = deposit_record.to_player
                # 是否首充,增加赠送的豆子
                present_amounts = Decimal(str(0.0))
                if not DepositRecord.objects.filter(
                                Q(to_player=player) &
                                Q(status=code_set.PayStatus.SUCCESS[
                                    0])).count():
                    present_amounts += Decimal(str(int(Decimal(str(order_money)) / 10 * 1)))
                    # 增加赠送记录
                    present_record = PresentsRecord()
                    present_record.amounts = present_amounts
                    present_record.to_player = player
                    present_record.presents_type = \
                        code_set.PresentStatus.FIRST_DEPOSIT[0]
                    present_record.msg_content = \
                        u"动物世界赠送您{}豆子,快去消费吧!".format(present_amounts)
                    present_record.save()

                # 先保存记录再增加余额
                deposit_record.status = code_set.PayStatus.SUCCESS[0]
                deposit_record.trade_no = platform_order_no
                deposit_record.remark = str(request.data)
                deposit_record.deposit_time = datetime.now()
                deposit_record.save()
                deposit_present_notice.apply_async(
                    args=[player.phone, str(order_money), str(present_amounts)],
                    exchange='pay',
                    routing_key="pay_success")
                # 余额
                change_wallet(Decimal(str(order_money)) + present_amounts,
                              unit=code_set.WalletUnit.B[0],
                              user_id=player.pk)
        return HttpResponse("success")
