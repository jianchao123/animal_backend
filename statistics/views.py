# coding:utf-8
from operator import itemgetter, attrgetter
from decimal import Decimal
import datetime as datetime_m
from datetime import datetime, timedelta
from collections import defaultdict
from django.db.models import Q, Sum
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics
from rest_framework import permissions

from snatch_treasure.models import Order
from shopping_user.permissions import IsAdministratorPermission
from shopping_user.models import GamePlayer
from financial.models import ConsumeRecord, DepositRecord, PayType, PrizeRecord
from activitys.models import PresentsRecord
from models import UserEveryDayInfo, PlatformEverydayData, UserEveryMonthInfo
from serializers import UserEveryDayInfoSerializer, \
    PlatformEverydayDataSerializer
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from utils.AppError import AppError
from utils import code_set
from utils import framework
import logging

logger = logging.getLogger(__name__)


class UserConsumeSituation(generics.ListAPIView):
    """用户批次分析"""

    permission_classes = (IsAdministratorPermission,)

    def paginate(self, data, page, limit):
        paginator = Paginator(data, limit)  # Show 25 contacts per page

        try:
            result = paginator.page(page)
        except PageNotAnInteger:
            result = paginator.page(1)
        except EmptyPage:
            result = paginator.page(paginator.num_pages)
        return result, paginator.count

    @framework.get_require_check([])
    def get(self, request, *args, **kwargs):
        """
        condition = 1:给定日期那天消费的前100名用户
        condition = 2:给定日期那天新注册的用户
        condition = 3:总消费前10%
        """
        condition = request.query_params.get("condition", None)
        query_date_str = request.query_params.get("query_date", None)
        page = int(request.query_params["page"])
        limit = int(request.query_params["limit"])

        format_time_str = "%Y-%m-%d %H:%M:%S"
        format_date_str = "%Y-%m-%d"
        if query_date_str:
            end_date = datetime.strptime(query_date_str, format_date_str).date()
            # 如果参数大于今天则报错
            if end_date > datetime_m.date.today():
                raise AppError(*code_set.GlobalErrorCode.PARAM_ERROR)
        else:
            end_date = datetime_m.date.today()
        if not condition:
            condition = "1"

        # 构造标题栏的时间列表
        date_list = []
        for inx in range(7):
            tmp = end_date - timedelta(days=7 - inx)
            date_list.append(tmp.strftime(format_date_str))
        date_list.append(end_date.strftime(format_date_str))

        zero = Decimal(str(0.0))
        # 总数据
        data = {}
        # 用户数据
        user_data = []
        # 给定日期那天消费的前100名用户
        if condition == '1':
            querysets = UserEveryDayInfo.objects.filter(
                Q(cur_date=end_date) & Q(player__is_robot=False)).order_by(
                '-consume_cny')
            querys, _ = self.paginate(querysets, page, limit)
            count = 100
            for row in querys:
                self._user_patch_situation(date_list, row.player,
                                           user_data, zero)

        # 给定日期那天新注册的用户
        if condition == '2':
            start_time_str = end_date.strftime(format_date_str) + " 00:00:00"
            start_time = datetime.strptime(start_time_str, format_time_str)
            end_time_str = end_date.strftime(format_date_str) + " 23:59:59"
            end_time = datetime.strptime(end_time_str, format_time_str)

            querys = UserEveryDayInfo.objects.filter(
                Q(cur_date=end_date) &
                Q(player__create_time__range=[start_time, end_time]) &
                Q(player__is_robot=False)).order_by(
                '-consume_cny')
            count = len(querys)
            querys, _ = self.paginate(querys, page, limit)
            for row in querys:
                self._user_patch_situation(date_list, row.player,
                                           user_data, zero)

        # 总消费前10%
        if condition == '3':
            # 获取当前用户量的10%
            player_count = GamePlayer.objects.filter(is_robot=False).count()
            if player_count < 10:
                end = player_count
            else:
                end = player_count / 10
            count = end
            querys = UserEveryDayInfo.objects.values_list('player').annotate(
                Sum('consume_cny'))[:end]
            # 玩家IDS
            player_ids = []
            querys = sorted(querys, key=itemgetter(1), reverse=True)
            for row in querys:
               player_ids.append(row[0])

            player_ids, _ = self.paginate(player_ids, page, limit)
            for player_pk in player_ids:
                gameplayer = GamePlayer.objects.get(pk=player_pk)
                self._user_patch_situation(date_list,
                                           gameplayer, user_data, zero)

        if condition not in ['1', '2', '3']:
            queryset = GamePlayer.objects.all()
            queryset, count = self.paginate(queryset, page, limit)
            for row in queryset:
                self._user_patch_situation(date_list,
                                           row, user_data, zero)

        # 用户信息数据
        data["user_data"] = user_data
        # 8天统计数据
        data["date_list"] = date_list
        return {
            "count": count,
            "next": None,
            "previous": None,
            "results": data
        }

    def _user_patch_situation(self, date_list, gameplayer, user_data, zero):
        player_dict = defaultdict()
        player_dict["pk"] = gameplayer.pk
        player_dict["uid"] = gameplayer.uid
        player_dict["nickname"] = gameplayer.nickname
        player_dict["phone"] = gameplayer.phone
        # 消费总金额
        aggregate_amount = \
            ConsumeRecord.objects.filter(
                Q(player=gameplayer)).aggregate(Sum('amounts')).values()[0]
        player_dict["aggregate_amount"] = \
            aggregate_amount if aggregate_amount else zero
        last_login_str = ""
        if gameplayer.last_login:
            last_login_str = gameplayer.last_login.strftime("%Y-%m-%d %H:%M:%S")
        # 最后登陆时间
        player_dict["last_login_time"] = last_login_str

        # 8日各种金额
        query_list = [date_list[0], date_list[-1]]
        user_everyday_datas = UserEveryDayInfo.objects.filter(
            Q(player=gameplayer) &
            Q(cur_date__range=query_list))
        user_everyday_datas = UserEveryDayInfoSerializer(
            user_everyday_datas, many=True).data
        tmp_list = []
        for _date in date_list:
            flag = 0
            for user_everyday_data in user_everyday_datas:
                if _date == user_everyday_data["cur_date"]:
                    flag = 1
                    break
            if flag:
                tmp_list.append(user_everyday_data)
            else:
                tmp_list.append({})

        player_dict["user_everyday_data"] = tmp_list
        user_data.append(player_dict)


class FinancialSheets(generics.ListAPIView):
    """财务表"""

    permission_classes = (IsAdministratorPermission,)

    @framework.get_require_check(["page", "limit"])
    def get(self, request, *args, **kwargs):

        page = request.query_params.get("page")
        limit = request.query_params.get("limit")

        queryset = PlatformEverydayData.objects.order_by('-pk')
        paginator = Paginator(queryset, limit)
        try:
            queryset = paginator.page(page)
        except PageNotAnInteger:
            queryset = paginator.page(1)
        except EmptyPage:
            queryset = paginator.page(paginator.num_pages)
        financials = PlatformEverydayDataSerializer(queryset, many=True).data
        for row in financials:
            row["alipay_cny"] = float(row["alipay_cny"])  # 支付宝充值金额
            row["wx_cny"] = float(row["wx_cny"])  # 微信充值金额
            row["dai_chong_cny"] = float(row["dai_chong_cny"])  # 代充金额
            row["deposit_total_cny"] = float(row["deposit_total_cny"])  # 充值总金额
            row["bonus"] = float(row["bonus"])  # 中奖金额
            row["presents_b"] = float(row["presents_b"])  # 赠送金额
            row["pay_rates"] = float(row["pay_rates"])  # 支付费率
            row["win_prize_entity_price"] = float(row["win_prize_entity_price"])  # 实物中奖金额
            row["win_prize_virtual_price"] = float(row["win_prize_virtual_price"])  # 虚拟中奖金额
            row["deliver_goods_entity_price"] = float(row["deliver_goods_entity_price"])  # 实物发货金额
            row["deliver_goods_virtual_price"] = float(row["deliver_goods_virtual_price"])  # 虚拟发货金额
            row["recycle_businessman_withdraw_price"] = float(row["recycle_businessman_withdraw_price"])  # 卡商提现金额
            row["recycle_commission"] = float(row["recycle_commission"])  # 收货佣金
            row["ls_commission"] = float(row["ls_commission"])  # 流水佣金
            row["dc_commission"] = float(row["dc_commission"])  # 代充佣金
            row["ll_profit"] = float(row["ll_profit"])  # 理论利润
            row["profit_rate"] = float(row["profit_rate"])  # 利润率
            row["real_profit"] = float(row["real_profit"])  # 实际利润

        data = {
            "count": paginator.count,
            "next": None,
            "previous": None,
            "results": financials
        }

        return data


class DepositStatistics(generics.ListAPIView):
    """充值统计"""

    permission_classes = (IsAdministratorPermission,)

    @framework.get_require_check([])
    def get(self, request, *args, **kwargs):
        zero = Decimal(str(0.0))

        today = datetime_m.date.today()
        start = (datetime.now() - datetime_m.timedelta(days=7)).date()
        end = today

        # 获取7天数据
        records = PlatformEverydayData.objects.filter(
            Q(data_date__range=[start, end])).order_by('-pk')
        records = [row for row in records]

        # 今日数据
        today_data = {
            "total_amounts": 0,
            "dai_chong_amounts": 0,
            "total_count": 0,
            "dai_chong_count": 0,
            "present_amounts": 0
        }
        if records:
            today_record = records[0]
            total_count = DepositRecord.objects.filter(
                Q(deposit_time__year=today.year) &
                Q(deposit_time__month=today.month) &
                Q(deposit_time__day=today.day)).count()
            dai_chong_count = DepositRecord.objects.filter(
                Q(deposit_time__year=today.year) &
                Q(deposit_time__month=today.month) &
                Q(deposit_time__day=today.day)).count()
            present_amounts = PresentsRecord.objects.filter(
                Q(present_time__year=today.year) & Q(
                    present_time__month=today.month) & Q(
                    present_time__day=today.day)).aggregate(
                Sum('amounts')).values()[0]
            today_data["total_amounts"] = \
                today_record.dai_chong_cny + today_record.alipay_cny
            today_data["dai_chong_amounts"] = today_record.dai_chong_cny
            today_data["total_count"] = total_count
            today_data["dai_chong_count"] = dai_chong_count
            today_data["present_amounts"] = \
                present_amounts if present_amounts else zero

        # 两日数据
        numbers = len(records)
        date1 = (today - datetime_m.timedelta(days=1)).strftime("%Y-%m-%d")
        date2 = (today - datetime_m.timedelta(days=2)).strftime("%Y-%m-%d")
        amounts1 = 0
        amounts2 = 0
        print records
        if numbers >= 2:
            print records[-2].data_date.strftime("%Y-%m-%d")
            amounts1 = records[-2].dai_chong_cny + records[-2].alipay_cny
        if numbers >= 3:
            print records[-3].data_date.strftime("%Y-%m-%d")
            amounts2 = records[-3].dai_chong_cny + records[-3].alipay_cny

        two_days_data = [{"date": date1,
                          "amounts": amounts1},
                         {"date": date2,
                          "amounts": amounts2}]

        # 近七天平均流水
        jqtpjls = zero
        for record in records:
            jqtpjls += record.dai_chong_cny
        numbers = Decimal(str(numbers))
        if numbers:
            jqtpjls = jqtpjls / numbers
        else:
            jqtpjls = 0
        jqtpjls = jqtpjls if jqtpjls else zero

        # 今日三方支付接口
        wx_pay = PayType.objects.get(code='WXPAY')

        yest = today - timedelta(days=1)
        year = yest.year
        month = yest.month
        day = yest.day
        third_pay = DepositRecord.objects.filter(
            Q(deposit_type=wx_pay) & Q(deposit_time__year=year) &
            Q(deposit_time__month=month) & Q(deposit_time__day=day) &
            Q(status=code_set.PayStatus.SUCCESS[0])
        ).aggregate(Sum('amounts')).values()[0]

        tt = DepositRecord.objects.filter(
            Q(deposit_type=wx_pay) &
            Q(status=code_set.PayStatus.SUCCESS[0])
        ).aggregate(Sum('amounts')).values()[0]

        data = {
            "jqtpjls": jqtpjls,  # 近期七天平均流水
            "two_days_data": two_days_data,  # 两日数据
            "today_data": today_data,  # 今日数据
            "third_pay": third_pay if third_pay else zero,
            "tt": tt
        }
        return data


class TestStatistics(generics.ListCreateAPIView):
    """测试统计"""

    permission_classes = (permissions.AllowAny,)

    @framework.post_require_check([])
    def post(self, request, *args, **kwargs):
        # ##########################  平台统计 ################################
        from statistics import platform_statistics
        today = datetime.today()
        count = 12

        import datetime as dt
        logger.error("=========================")
        while True:
            tt = today - dt.timedelta(days=count)
            platform_statistics.statistics_platform_data(tt)
            count -= 1
            if count == -1:
                break
        return {}
        # ########################### 玩家月份统计 #############################
        # count = 2
        # cur_date = datetime_m.date.today()
        # year = cur_date.year
        # cur_month = cur_date.month
        # while True:
        #     if not count:
        #         break
        #     month = cur_month - count
        #     if not month:
        #         month = 12
        #         year -= 1
        #     date_str = ("%04d" % year) + ("%02d" % month)
        #
        #     zero = Decimal(str(0.0))
        #     gameplayers = GamePlayer.objects.filter(is_robot=False)
        #     for gameplayer in gameplayers:
        #
        #         # 总消费金额
        #         consume_cnys = ConsumeRecord.objects.filter(
        #             Q(player=gameplayer) &
        #             Q(period__status=code_set.PeriodStatusCode.REWARDED[0]) &
        #             Q(consume_time__year=year) & Q(consume_time__month=month)
        #         ).aggregate(Sum('amounts')).values()[0]
        #         consume_cnys = consume_cnys if consume_cnys else zero
        #
        #         # 总充值
        #         deposit_cnys = DepositRecord.objects.filter(
        #             Q(to_player=gameplayer) &
        #             Q(status=code_set.PayStatus.SUCCESS[0]) &
        #             Q(deposit_time__year=year) & Q(deposit_time__month=month)
        #         ).aggregate(Sum('payment_amount_cny')).values()[0]
        #         deposit_cnys = deposit_cnys if deposit_cnys else zero
        #
        #         # 总赠送
        #         presents = PresentsRecord.objects.filter(
        #             Q(to_player=gameplayer) &
        #             Q(present_time__year=year) & Q(present_time__month=month)
        #         ).aggregate(Sum('amounts')).values()[0]
        #         presents = presents if presents else zero
        #
        #         # 总中奖
        #         prize_set = PrizeRecord.objects.filter(
        #             Q(player=gameplayer) &
        #             Q(prize_time__year=year) & Q(prize_time__month=month))
        #         prize_cnys = prize_set.aggregate(Sum('amounts')).values()[0]
        #         prize_cnys = prize_cnys if prize_cnys else zero
        #
        #         # 中奖期数花费的金额
        #         periodids = [row.period.pk for row in prize_set]
        #         snatch_treasure_b = ConsumeRecord.objects.filter(
        #             Q(player=gameplayer) &
        #             Q(period_id__in=periodids)
        #         ).aggregate(Sum('amounts')).values()[0]
        #         snatch_treasure_b = snatch_treasure_b if snatch_treasure_b else zero
        #
        #         # 订单次数
        #         order_count = Order.objects.filter(
        #             Q(player=gameplayer) &
        #             Q(status=code_set.OrderStatus.ORDERED[0]) &
        #             Q(create_time__year=year) & Q(create_time__month=month)
        #         ).count()
        #
        #         try:
        #             user_every_month_info = \
        #                 UserEveryMonthInfo.objects.get(data_date=date_str,
        #                                                player=gameplayer)
        #         except ObjectDoesNotExist:
        #             user_every_month_info = UserEveryMonthInfo()
        #             user_every_month_info.data_date = date_str
        #             user_every_month_info.player = gameplayer
        #         user_every_month_info.consume_money = consume_cnys
        #         user_every_month_info.deposit_money = deposit_cnys
        #         user_every_month_info.presents_money = presents
        #         user_every_month_info.bonus = prize_cnys
        #         user_every_month_info.snatch_treasure_b = snatch_treasure_b
        #         user_every_month_info.order_count = order_count
        #         user_every_month_info.update_time = datetime.now()
        #         user_every_month_info.save()
        #     count -= 1