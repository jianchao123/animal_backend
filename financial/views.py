# coding:utf-8
import time
import datetime
import json
from decimal import Decimal
from collections import defaultdict

from rest_framework import generics
from django.db.models import Q, Sum
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from utils import framework
from utils.AppError import AppError
from utils import code_set
from utils.utils import generate_out_trade_no
from models import DepositRecord, PrizeRecord
from shopping_settings.models import PayType
from recycle_businessman.models import RecycleRecord, RecycleBusinessman
from statistics.models import PlatformEverydayData
from activitys.models import PresentsRecord
from shopping_user.models import GamePlayer, Wallet, Administrator
from inventory.models import Card, CardDeliveryRecord
from snatch_treasure.models import UserCard

from shopping_user.permissions import IsAdministratorPermission, \
    IsRecycleBusinessman
from shopping_user.business import change_wallet
from serializers import DepositOrderSerializer
import business


# ################################# backend ###############################


class DepositRecordList(generics.ListCreateAPIView):
    """充值列表 backend"""

    permission_classes = (IsAdministratorPermission,)

    @framework.get_require_check([])
    def get(self, request, *args, **kwargs):
        pay_type_pk = request.query_params.get("pay_type_pk", None)
        player_phone = request.query_params.get("player_phone", None)
        page = request.query_params.get("page")
        limit = request.query_params.get("limit")

        queryset = DepositRecord.objects.filter(
            Q(status=code_set.PayStatus.SUCCESS[0]))
        # 参数
        if pay_type_pk:
            try:
                paytype = PayType.objects.get(pk=pay_type_pk)
                queryset = queryset.filter(deposit_type=paytype)
            except ObjectDoesNotExist:
                paytype = PayType.objects.filter(
                    code__in=['DC', 'ALIPAY', 'WXPAY'])
                queryset = queryset.filter(deposit_type__in=paytype)

        if player_phone:
            game_player = GamePlayer.objects.filter(
                phone__contains=player_phone)
            queryset = queryset.filter(Q(to_player__in=game_player))

        queryset = queryset.order_by("-deposit_time")
        # 查询回收商数量
        paginator = Paginator(queryset, limit)
        try:
            queryset = paginator.page(page)
        except PageNotAnInteger:
            queryset = paginator.page(1)
        except EmptyPage:
            queryset = paginator.page(paginator.num_pages)

        data = {
            "count": paginator.count,
            "next": None,
            "previous": None,
            "data": DepositOrderSerializer(queryset, many=True).data
        }
        return data


# 暂未使用
# class AdministratorDeposit(generics.CreateAPIView):
#     """管理员充值"""
#
#     permission_classes = (IsAdministratorPermission,)
#
#     @framework.post_require_check(["player_id", "amounts", "remark"])
#     @transaction.atomic
#     def post(self, request, *args, **kwargs):
#         """结算台充值"""
#         player_id = request.data.get("player_id")
#         amounts = request.data.get("amounts")
#         remark = request.data.get("remark")
#
#         if float(amounts) < 10 or float(amounts) > 10000:
#             raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)
#
#         recycle_businessman = None
#         try:
#             administrator = Administrator.objects.get(pk=request.user.pk)
#             gameplayer = GamePlayer.objects.get(pk=player_id)
#             Wallet.objects.get(
#                 Q(user_id=gameplayer.pk) & Q(unit=code_set.WalletUnit.B[0]))
#             invite_records = gameplayer.ir_ip_set.all()
#             if invite_records:
#                 recycle_businessman = invite_records[0].recycle_businessman
#         except ObjectDoesNotExist:
#             raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)
#
#         if not change_wallet(amounts=amounts, unit=code_set.WalletUnit.B[0],
#                              user_id=gameplayer.pk):
#             raise AppError(*code_set.SubErrorCode.NOT_SUFFICIENT_FUNDS_ERROR)
#
#         # 充值记录
#         amounts = Decimal(str(amounts))
#         deposit_record = DepositRecord()
#         deposit_record.out_trade_no = \
#             generate_out_trade_no(code_set.OutTradeNoPrefix.ADMIN)
#         deposit_record.amounts = amounts
#         deposit_record.payment_amount_cny = amounts
#         deposit_record.units = 1
#         deposit_record.to_player = gameplayer
#         deposit_record.deposit_type = PayType.objects.get(pay_name=u"管理员充值")
#         deposit_record.deposit_time = datetime.datetime.now()
#         deposit_record.status = code_set.PayStatus.SUCCESS[0]
#         deposit_record.administrator = administrator
#
#         if recycle_businessman:
#             # 流水返利
#             deposit_record.recycle_businessman_profit = \
#                 amounts * recycle_businessman.invite_back_rate
#         deposit_record.remark = remark
#         deposit_record.save()
#         return {}


class RecycleBusinessDeposit(generics.CreateAPIView):
    """代充"""

    permission_classes = (IsRecycleBusinessman,)

    @framework.post_require_check(["phone", "amounts"])
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """结算台充值"""
        phone = request.data.get("phone")
        amounts = int(request.data.get("amounts"))
        if amounts < 1 or amounts > 999999:
            raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)

        try:
            gameplayer = GamePlayer.objects.get(phone=phone)
        except ObjectDoesNotExist:
            raise AppError(*code_set.SubErrorCode.MISSING_PHONE_ERROR)
        try:
            recyclebusinessman = \
                RecycleBusinessman.objects.get(pk=request.user.pk)
            Wallet.objects.get(
                Q(user_id=gameplayer.pk) & Q(unit=code_set.WalletUnit.B[0]))
            Wallet.objects.get(
                Q(user_id=recyclebusinessman.pk) &
                Q(unit=code_set.WalletUnit.CNY[0]))
        except ObjectDoesNotExist:
            raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)

        # 减少回收商余额
        if not change_wallet(amounts=-amounts, unit=code_set.WalletUnit.CNY[0],
                             user_id=recyclebusinessman.pk):
            raise AppError(*code_set.SubErrorCode.AMOUNTS_INSUFFICIENT_ERROR)

        # 是否首充,增加赠送的豆子
        present_amounts = Decimal(str(0.0))
        if not DepositRecord.objects.filter(
                        Q(to_player=gameplayer) &
                        Q(status=code_set.PayStatus.SUCCESS[0])).count():
            present_amounts += amounts / 10 * 1
            # 增加赠送记录
            present_record = PresentsRecord()
            present_record.amounts = present_amounts
            present_record.to_player = gameplayer
            present_record.presents_type = code_set.PresentStatus.FIRST_DEPOSIT[0]
            present_record.msg_content = \
                u"动物世界赠送您{}豆子,快去消费吧!".format(present_amounts)
            present_record.save()

        # 增加用户余额
        if not change_wallet(amounts=amounts + present_amounts,
                             unit=code_set.WalletUnit.B[0],
                             user_id=gameplayer.pk):
            raise AppError(*code_set.SubErrorCode.NOT_SUFFICIENT_FUNDS_ERROR)

        # 代充记录
        business.insert_deposit_record(gameplayer, amounts, recyclebusinessman)
        return {}


class PrizeRecords(generics.ListAPIView):
    """奖金记录 backend"""

    permission_classes = (IsAdministratorPermission,)

    @framework.get_require_check(["page", "limit"])
    def get(self, request, *args, **kwargs):
        prize_record_id = request.query_params.get("prize_record_id", None)
        record_id = request.query_params.get("record_id", None)
        phone = request.query_params.get("phone", None)
        card = request.query_params.get("card", None)
        status = request.query_params.get("status", None)
        page = int(request.query_params.get("page"))
        limit = int(request.query_params.get("limit"))

        queryset = PrizeRecord.objects.filter(
            Q(period__commodity__is_card=True) & Q(player__is_robot=False))
        if record_id:
            queryset = queryset.filter(Q(record_id=record_id))
        if phone:
            queryset = queryset.filter(Q(player__phone=phone))
        if card:
            queryset = queryset.filter(
                Q(card__card_number=card) | Q(card__card_pwd=card))
        if prize_record_id:
            queryset = queryset.filter(Q(pk=prize_record_id))
        if status:
            queryset = queryset.filter(Q(status=int(status)))

        paginator = Paginator(queryset, limit)
        try:
            queryset = paginator.page(page)
        except PageNotAnInteger:
            queryset = paginator.page(1)
        except EmptyPage:
            queryset = paginator.page(paginator.num_pages)

        data = []
        for row in queryset:
            player = row.player
            period = row.period
            commodity = period.commodity
            d = defaultdict()
            d["pk"] = row.pk
            d["uid"] = player.uid
            d["player_nickname"] = player.get_nickname
            d["player_id"] = player.pk
            d["player_phone"] = player.phone
            if row.status == \
                    code_set.PrizeStatusCode.CARD_INVENTORIES_INSUFFICIENT[0]:
                d["to_phone_number"] = u"卡密不足"
                d["accept_type"] = row.accept_prize_type
            if row.status == code_set.PrizeStatusCode.ACCEPT_PRIZED[0]:
                if row.accept_prize_type == code_set.AcceptPrizeType.DHHLD[0]:
                    d["to_phone_number"] = player.phone
                if row.accept_prize_type == code_set.AcceptPrizeType.ZDSHR[0]:
                    d["to_phone_number"] = row.to_recycle_businessman.phone
                if row.accept_prize_type == code_set.AcceptPrizeType.LQJP[0]:
                    d["to_phone_number"] = u"领取卡密"
                d["accept_type"] = row.accept_prize_type
            if row.status == code_set.PrizeStatusCode.NOT_ACCEPT_PRIZE[0]:
                d["to_phone_number"] = u"用户未领奖"
                d["accept_type"] = ""
            d["commodity_id"] = commodity.pk

            period_index = 0
            period_ids = []
            for t in commodity.period_c_set.all():
                period_ids.append(t.pk)

            for x in period_ids:
                period_index += 1
                if period.pk == x:
                    break
            d["period_index"] = period_index
            d["commodity_name"] = commodity.commodity_name
            d["reward_time"] = period.reward_time.strftime("%Y-%m-%d %H:%M:%S")
            d["record_id"] = row.record_id
            d["prize_time"] = row.prize_time.strftime("%Y-%m-%d %H:%M:%S")
            d["status"] = row.status
            data.append(d)

        return {
            "count": paginator.count,
            "next": None,
            "previous": None,
            "results": data
        }


class PrizeRecordEdit(generics.CreateAPIView):
    """奖金记录编辑 backend
    若用户领取卡密失败,管理员可帮他转到回收商或继续发放或兑换豆子
    """

    permission_classes = (IsAdministratorPermission,)

    @framework.post_require_check(["accept_type", "prize_record_id"])
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """
        accept_type 1:继续发放
        accept_type 2:转到回收商
        """
        phone = request.data.get("phone", None)
        prize_record_id = request.data.get("prize_record_id")
        accept_type = int(request.data.get('accept_type'))

        try:
            prize_record = PrizeRecord.objects.get(Q(pk=prize_record_id) & Q(
                status=code_set.PrizeStatusCode.CARD_INVENTORIES_INSUFFICIENT[
                    0]))
        except ObjectDoesNotExist:
            raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)
        if not prize_record.period.commodity.is_card:
            raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)

        if accept_type not in (1, 2):
            raise AppError(*code_set.GlobalErrorCode.PARAM_ERROR)
        if accept_type == 2 and not phone:
            raise AppError(*code_set.GlobalErrorCode.PARAM_ERROR)

        if phone:
            try:
                businessman = \
                    RecycleBusinessman.objects.get(Q(phone=phone))
            except ObjectDoesNotExist:
                # 未找到回收商
                raise AppError(
                    *code_set.SubErrorCode.NOT_FOUND_RECYCLE_BUSINESSMAN_ERROR)

        period = prize_record.period
        player = prize_record.player
        if accept_type == 1:
            # 从库存获取一张card
            card_inventory = period.commodity.card_inventory

            # 卡密库存不足
            if card_inventory.volumes < 1:
                raise AppError(
                    *code_set.SubErrorCode._CARD_INVENTORIES_INSUFFICIENT_ERROR)
            else:
                card_inventory.volumes -= 1
                card_inventory.update_time = datetime.datetime.now()
                card_inventory.save()

                card = Card.objects.filter(
                    Q(card_inventory=card_inventory) &
                    Q(status=code_set.CardStatusCode.VALID[0]))[0]
                card.status = code_set.CardStatusCode.USED[0]
                card.save()

                # 增加出库记录
                card_delivery_record = CardDeliveryRecord()
                card_delivery_record.card_inventory = card_inventory
                card_delivery_record.volumes = 1
                card_delivery_record.delivery_time = datetime.datetime.now()
                card_delivery_record.to_player = player
                card_delivery_record.reason = json.dumps(
                    {"period_id": period.pk, "reason": u"中奖"})
                card_delivery_record.save()

                # 为用户增加一张卡密
                user_card = UserCard()
                user_card.player = player
                user_card.card_number = 1
                user_card.card_number = card.card_number
                user_card.card_pwd = card.card_pwd
                user_card.source = period
                user_card.save()

                # 更新获奖记录
                prize_record.card = card

        elif accept_type == 2:

            prize_record.to_recycle_businessman = businessman
            if businessman.phone == phone:
                # 给回收商增加余额
                if not change_wallet(prize_record.amounts,
                                     unit=code_set.WalletUnit.CNY[0],
                                     user_id=businessman.pk):
                    raise AppError(
                        *code_set.SubErrorCode.RECYCLE_PHONE_USED_ERROR)
                # 添加回收记录
                self._add_recycle_record(businessman, period, phone,
                                         prize_record)

                # 获奖记录更新
                prize_record.accept_prize_type = \
                    code_set.AcceptPrizeType.ZDSHR[0]

            # elif businessman.dh_phone == phone:
            #     # 直接给用户增加余额
            #     if not change_wallet(prize_record.amounts,
            #                          unit=code_set.WalletUnit.B[0],
            #                          user_id=player.pk):
            #         raise AppError(
            #             *code_set.SubErrorCode.NOT_SUFFICIENT_FUNDS_ERROR)
            #
            #     # 添加回收记录
            #     self._add_recycle_record(businessman, period, phone,
            #                              prize_record)
            #
            #     # 获奖记录更新
            #     prize_record.accept_prize_type = \
            #         code_set.AcceptPrizeType.DHHLD[0]

        prize_record.status = code_set.PrizeStatusCode.ACCEPT_PRIZED[0]
        prize_record.accept_prize_time = datetime.datetime.now()
        prize_record.save()
        return {}

    def _add_recycle_record(self, businessman, period, phone, prize_record):
        # 添加收货记录
        recycle_record = RecycleRecord()
        recycle_record.recycle_period_no = period.period_no
        recycle_record.recycle_price = prize_record.amounts
        recycle_record.recycle_trade_no = \
            "RR" + str(int(time.time())) + \
            str(phone) + period.period_no
        recycle_record.period = period
        recycle_record.recycle_businessman = businessman
        recycle_record.commodity = period.commodity
        recycle_record.recycle_time = datetime.datetime.now()
        recycle_record.save()
