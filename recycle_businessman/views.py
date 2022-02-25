# coding:utf-8
import re
import datetime
import django_filters
from decimal import Decimal
from collections import defaultdict
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.contrib.auth.models import Group
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction
from django.conf import settings
from rest_framework import generics
from rest_framework import filters

from shopping_user.models import Wallet, Administrator, \
    UserProfileBasic, GamePlayer
from recycle_businessman.models import RecycleBusinessman
from shopping_settings.models import CommonParamConf, PayType
from financial.models import DepositRecord, AgencyRecord, WithdrawRecord
from statistics.models import RbEveryDayInfo
from models import RecycleRecord, InviteRecord, UserConsignee

from shopping_user.permissions import IsRecycleBusinessman, \
    IsAdministratorPermission, IsAdminOrBusinessman, IsGamePlayer
from statistics.serializers import RbRecycleBusinessmanSerializer
from financial.serializers import AgencyRecordSerializer, WithdrawSerializer
from shopping_user.business import change_wallet

from paginations import LargeResultsSetPagination
from serializers import InviteRecordSerializer, RecycleBusinessmanSerializer, \
    UserConsigneeSerializer

from utils import code_set
from utils import framework
from utils.AppError import AppError
from utils.utils import generate_out_trade_no, generate_qr_code, generate_code
from utils.cache_util import CacheUtil, lock_instance


class RecycleBusinessmanHomepage(generics.ListAPIView):
    """回收商主页"""

    permission_classes = (IsRecycleBusinessman,)

    @framework.get_require_check([])
    def get(self, request, *args, **kwargs):
        user = request.user
        try:
            recycle_businessman = RecycleBusinessman.objects.get(pk=user.pk)
            common_param_conf = CommonParamConf.objects.get(
                conf_key="invite_link")
            wallet = Wallet.objects.get(Q(user_id=recycle_businessman.pk) &
                                        Q(unit=code_set.WalletUnit.CNY[0]))
        except ObjectDoesNotExist:
            raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)
            # 获取余额
        data = defaultdict()
        data["pk"] = recycle_businessman.pk
        data["username"] = recycle_businessman.username
        data["phone"] = recycle_businessman.phone
        data["invite_code"] = recycle_businessman.invite_code
        data["recycle_back_rate"] = recycle_businessman.recycle_back_rate
        data["deposit_back_rate"] = recycle_businessman.deposit_back_rate
        data["invite_back_rate"] = recycle_businessman.invite_back_rate
        data["balance"] = wallet.balance
        data["invite_link"] = common_param_conf.conf_value + "?invite_code=" \
                              + str(recycle_businessman.invite_code)
        data["invite_qr_code"] = recycle_businessman.invite_qr_code

        # 获取回收商每日数据
        rb_everyday_info = RbEveryDayInfo.objects.filter(
            Q(recycle_businessman=recycle_businessman)).order_by("-pk")[:7]

        result = {
            "recycle_businessman_data": data,
            "jqgk": RbRecycleBusinessmanSerializer(rb_everyday_info,
                                                   many=True).data
        }
        return result


class DcDepositRecordList(generics.ListAPIView):
    """ 代充记录"""

    permission_classes = (IsAdminOrBusinessman,)

    @framework.get_require_check(["page", "limit"])
    def get(self, request, *args, **kwargs):
        start_time = request.query_params.get("start_time", None)
        end_time = request.query_params.get("end_time", None)
        page = request.query_params.get("page")
        limit = request.query_params.get("limit")
        user = request.user
        if start_time and end_time:
            try:
                start_time = \
                    datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
                end_time = datetime.datetime.strptime(end_time,
                                                      "%Y-%m-%d %H:%M:%S")
            except ValueError:
                raise AppError(*code_set.GlobalErrorCode.PARAM_ERROR)

        try:
            paytype = PayType.objects.get(code=u"DC")
        except ObjectDoesNotExist:
            raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)

        queryset = DepositRecord.objects.filter(
            Q(status=code_set.PayStatus.SUCCESS[0]) &
            Q(deposit_type=paytype)).order_by("-deposit_time")
        if user.is_role(u"回收商"):
            queryset = queryset.filter(Q(from_recycle_businessman_id=user.pk))

        # 参数
        if start_time and end_time:
            queryset = queryset.filter(
                Q(deposit_time__range=(start_time, end_time)))

        # 查询回收商数量
        paginator = Paginator(queryset, limit)
        try:
            queryset = paginator.page(page)
        except PageNotAnInteger:
            queryset = paginator.page(1)
        except EmptyPage:
            queryset = paginator.page(paginator.num_pages)
        data = []
        for row in queryset:
            d = defaultdict()
            d["pk"] = row.pk
            d["out_trade_no"] = row.out_trade_no
            d["businessman_nickname"] = row.from_recycle_businessman.nickname
            d["payment_amount_cny"] = row.payment_amount_cny
            d["to_player_phone"] = row.to_player.phone
            d["deposit_time"] = row.deposit_time.strftime("%Y-%m-%d %H:%M:%S")
            d["status"] = row.status
            data.append(d)
        return {
            "count": paginator.count,
            "next": None,
            "previous": None,
            "pages": paginator.num_pages,
            "data": data
        }


class AgencyRecordFilter(django_filters.FilterSet):
    to_recycle_businessman_phone = \
        django_filters.NumberFilter(name='to_recycle_businessman__phone')
    status = django_filters.NumberFilter(name="status")

    class Meta:
        model = AgencyRecord
        fields = []


class AgencyRecordList(generics.ListCreateAPIView):
    """代理记录"""

    queryset = AgencyRecord.objects.all()
    serializer_class = AgencyRecordSerializer
    permission_classes = (IsAdministratorPermission,)
    filter_backends = (
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,)
    filter_class = AgencyRecordFilter
    pagination_class = LargeResultsSetPagination
    ordering_fields = ('id',)

    @framework.get_require_check([])
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs).data

    @framework.post_require_check([])
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """添加代理记录"""
        amounts = Decimal(str(request.data["amounts"]))
        remark = request.data["remark"]
        to_recycle_businessman = request.data["to_recycle_businessman"]

        if amounts <= Decimal(str(0)):
            raise AppError(
                *code_set.GlobalErrorCode.PARAM_ERROR)
        try:
            businessman = \
                RecycleBusinessman.objects.get(pk=to_recycle_businessman)
        except ObjectDoesNotExist:
            raise AppError(*code_set.GlobalErrorCode.PARAM_ERROR)

        # 增加余额
        if not change_wallet(amounts,
                             unit=code_set.WalletUnit.CNY[0],
                             user_id=businessman.id):
            raise AppError(
                *code_set.SubErrorCode.AMOUNTS_INSUFFICIENT_ERROR)

        agency_record = AgencyRecord()
        agency_record.agency_trade_no = generate_out_trade_no('AGY')
        agency_record.units = code_set.AgencyUnits.CNY[0]
        agency_record.deposit_time = datetime.datetime.now()
        agency_record.status = 2
        agency_record.to_recycle_businessman = businessman
        agency_record.amounts = amounts
        agency_record.remark = remark
        agency_record.phone = businessman.phone
        agency_record.save()
        return {}


class WithdrawRecordList(generics.ListAPIView):
    """提现列表"""

    permission_classes = (IsAdminOrBusinessman,)

    @framework.get_require_check([])
    @transaction.atomic
    def get(self, request, *args, **kwargs):
        page = request.query_params.get("page")
        limit = request.query_params.get("limit")
        status = request.query_params.get("status", None)

        user = request.user

        if status and status not in (1, 2, 3, 4):
            raise AppError(*code_set.GlobalErrorCode.PARAM_ERROR)

        queryset = WithdrawRecord.objects.order_by("-apply_for_time")
        if status:
            queryset = queryset.filter(Q(status=status))

        if user.is_role(u"回收商"):
            businessman = RecycleBusinessman.objects.get(pk=user.pk)
            queryset = queryset.filter(Q(to_recycle_businessman=businessman))

        paginator = Paginator(queryset, limit)
        try:
            queryset = paginator.page(page)
        except PageNotAnInteger:
            queryset = paginator.page(1)
        except EmptyPage:
            queryset = paginator.page(paginator.num_pages)
        data = WithdrawSerializer(queryset, many=True).data
        return {
            "pages": paginator.num_pages,
            "count": paginator.count,
            "next": None,
            "previous": None,
            "data": data
        }


class AuditApplyForRecord(generics.CreateAPIView):
    """审核申请记录 backend"""

    permission_classes = (IsAdministratorPermission,)

    @framework.post_require_check(["withdraw_record_pk", "is_pass",
                                   "remark"])
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        withdraw_record_pk = request.data["withdraw_record_pk"]
        is_pass = request.data["is_pass"]
        remark = request.data["remark"]
        transfer_time = request.data.get("transfer_time", None)
        user = request.user

        # 检查参数
        if is_pass not in [1, 0]:
            raise AppError(*code_set.GlobalErrorCode.PARAM_ERROR)
        if transfer_time:
            try:
                transfer_time = \
                    datetime.datetime.strptime(transfer_time,
                                               "%Y-%m-%d %H:%M:%S")
            except ValueError:
                raise AppError(*code_set.GlobalErrorCode.PARAM_ERROR)
        else:
            transfer_time = datetime.datetime.now()

        try:
            admin = Administrator.objects.get(pk=user.pk)
            withdraw_record = WithdrawRecord.objects.get(pk=withdraw_record_pk)
        except ObjectDoesNotExist:
            raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)

        if is_pass:
            withdraw_record.status = 2  # 体现成功
        else:
            # 增加余额
            if not change_wallet(withdraw_record.amounts,
                                 unit=code_set.WalletUnit.CNY[0],
                                 user_id=withdraw_record.to_recycle_businessman.id):
                raise AppError(
                    *code_set.SubErrorCode.AMOUNTS_INSUFFICIENT_ERROR)
            withdraw_record.status = 3  # 不通过
        withdraw_record.remark = remark
        withdraw_record.admin = admin
        withdraw_record.transfer_time = transfer_time
        withdraw_record.save()
        return {}


class BusinessmanApplyForWithdraw(generics.CreateAPIView):
    """回收商申请提现 backend"""

    permission_classes = (IsRecycleBusinessman,)

    @framework.post_require_check(["amounts"])
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        amounts = int(request.data["amounts"])
        user = request.user
        if amounts < 1 or amounts > 20000:
            raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)
        try:
            businessman = \
                RecycleBusinessman.objects.get(pk=user.pk)
            wallet = Wallet.objects.select_for_update().get(
                user=user, unit=code_set.WalletUnit.CNY[0])
        except ObjectDoesNotExist:
            raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)

        # 存款不足
        if wallet.balance < Decimal(str(amounts)):
            raise AppError(*code_set.SubErrorCode.NOT_SUFFICIENT_FUNDS_ERROR)

        # 修改余额
        r = change_wallet(-amounts, unit=code_set.WalletUnit.CNY[0],
                          user_id=businessman.pk)
        if not r:
            raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)

        # 生成交易号
        withdraw_record = WithdrawRecord()
        withdraw_record.out_trade_no = generate_out_trade_no("WD")
        withdraw_record.amounts = amounts
        withdraw_record.units = code_set.AgencyUnits.CNY[0]
        withdraw_record.status = code_set.AgencyStatus.AUDITING[0]
        withdraw_record.to_recycle_businessman = businessman
        withdraw_record.save()
        return {}


class RecycleRecordList(generics.ListAPIView):
    """回收记录列表"""

    permission_classes = (IsAdminOrBusinessman,)

    @framework.get_require_check(["page", "limit"])
    def get(self, request, *args, **kwargs):
        user = request.user
        page = request.query_params.get("page")
        limit = request.query_params.get("limit")

        queryset = RecycleRecord.objects.order_by("-recycle_time")
        if user.is_role(u"回收商"):
            queryset = queryset.filter(
                Q(recycle_businessman_id=user.pk))

        paginator = Paginator(queryset, limit)
        try:
            queryset = paginator.page(page)
        except PageNotAnInteger:
            queryset = paginator.page(1)
        except EmptyPage:
            queryset = paginator.page(paginator.num_pages)

        data = []
        for row in queryset:
            businessman = row.recycle_businessman
            commodity = row.commodity
            period = row.period
            luck_player = period.luck_player

            d = defaultdict()
            d["pk"] = row.pk
            d["recycle_trade_no"] = row.recycle_trade_no
            d["recycle_businessman_id"] = businessman.id
            d["recycle_businessman_nickname"] = businessman.get_nickname
            d["recycle_period_no"] = row.recycle_period_no
            d["commodity_id"] = commodity.id
            d["commodity_name"] = commodity.commodity_name
            d["recycle_price"] = row.recycle_price
            d["luck_player_nickname"] = luck_player.get_nickname
            d["phone"] = luck_player.phone
            d["recycle_time"] = \
                row.recycle_time.strftime("%Y-%m-%d %H:%M:%S")
            data.append(d)

        return {
            "pages": paginator.num_pages,
            "count": paginator.count,
            "next": None,
            "previous": None,
            "data": data
        }


class RecycleStatistics(generics.ListAPIView):
    """回收统计列表"""

    permission_classes = (IsAdministratorPermission,)

    @framework.get_require_check([])
    def get(self, request, *args, **kwargs):

        today = datetime.date.today()
        start = today - datetime.timedelta(days=10)
        end = today - datetime.timedelta(days=1)

        date_list = []
        for inx in range(10):
            tmp = today - datetime.timedelta(days=inx + 1)
            date_list.append(tmp.strftime('%Y-%m-%d'))

        businessmans = RecycleBusinessman.objects.all()
        data = {}
        rb_data = []
        for businessman in businessmans:
            result = RbEveryDayInfo.objects.filter(
                Q(data_date__range=(start, end)) &
                Q(recycle_businessman=businessman)). \
                order_by("-data_date").values_list("receive_cny", flat=True)
            result = [row for row in result]
            if len(result) < 10:
                diff = 10 - len(result)
                for _ in range(diff):
                    result.append(0)

            rb_data.append({
                "pk": businessman.pk,
                "nickname": businessman.nickname,
                "data": result
            })
        data["data"] = rb_data
        data["date_list"] = date_list
        return data


class InviteRecordList(generics.ListCreateAPIView):
    """邀请记录列表"""

    permission_classes = (IsAdminOrBusinessman,)

    @framework.get_require_check(["page", "limit"])
    def get(self, request, *args, **kwargs):
        page = request.query_params["page"]
        limit = request.query_params["limit"]

        user = request.user
        queryset = InviteRecord.objects.all()
        if user.is_role(u"回收商"):
            queryset = queryset.filter(Q(recycle_businessman_id=user.pk))
        queryset = queryset.order_by("-invite_time")
        paginator = Paginator(queryset, limit)
        try:
            queryset = paginator.page(page)
        except PageNotAnInteger:
            queryset = paginator.page(1)
        except EmptyPage:
            queryset = paginator.page(paginator.num_pages)
        return {
            "pages": paginator.num_pages,
            "count": paginator.count,
            "next": None,
            "previous": None,
            "data": InviteRecordSerializer(queryset, many=True).data
        }

    @framework.post_require_check(["player_pk", "business_pk"])
    def post(self, request, *args, **kwargs):
        user = request.user
        player_pk = int(request.data["player_pk"])
        business_pk = int(request.data["business_pk"])

        if user.is_role(u"管理员"):
            try:
                player = GamePlayer.objects.get(id=player_pk)
                business = RecycleBusinessman.objects.get(id=business_pk)
            except ObjectDoesNotExist:
                raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)

            if InviteRecord.objects.filter(
                Q(invite_player=player) &
                            Q(recycle_businessman=business)).count():
                raise AppError(*code_set.SubErrorCode.IS_BINDING)

            inviterecord = InviteRecord()
            inviterecord.invite_player = player
            inviterecord.recycle_businessman = business
            inviterecord.save()
        else:
            raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)
        return {}


class RecycleFilter(django_filters.FilterSet):
    phone = \
        django_filters.NumberFilter(name='to_recycle_businessman__phone')

    class Meta:
        model = RecycleBusinessman
        fields = []


class RecycleBusinessmanList(generics.ListCreateAPIView):
    """回收商列表 backend"""

    queryset = RecycleBusinessman.objects.all()
    serializer_class = RecycleBusinessmanSerializer
    permission_classes = (IsAdministratorPermission,)
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_class = RecycleFilter
    pagination_class = LargeResultsSetPagination

    @framework.get_require_check([])
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs).data

    @framework.post_require_check(["recycle_phone", "is_recycle", "is_login"])
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """添加回收商"""
        recycle_phone = request.data["recycle_phone"]
        is_recycle = request.data["is_recycle"]
        is_login = request.data["is_login"]
        nickname = request.data["nickname"]
        password = request.data["password"]

        if (int(is_recycle) not in (1, 0)) or \
                (int(is_login) not in (1, 0)):
            raise AppError(*code_set.GlobalErrorCode.PARAM_ERROR)

        # 1.回收卡号已存在
        try:
            UserProfileBasic.objects.get(phone=recycle_phone)
            raise AppError(*code_set.SubErrorCode.RECYCLE_PHONE_USED_ERROR)
        except ObjectDoesNotExist:
            pass

        # 2.用户名已存在
        username = str(recycle_phone)
        try:
            UserProfileBasic.objects.get(username=username)
            raise AppError(*code_set.SubErrorCode.USERNAME_USED_ERROR)
        except ObjectDoesNotExist:
            pass

        # 3.检查兑换号是否已经存在  (存在玩家表 存在回收商表)
        # try:
        #     GamePlayer.objects.get(phone=dh_phone)
        #     raise AppError(*code_set.SubErrorCode.DH_PHONE_ALREADY_EXIST_ERROR)
        # except ObjectDoesNotExist:
        #     pass
        # if RecycleBusinessman.objects.filter(
        #                 Q(phone=dh_phone) | Q(dh_phone=dh_phone)).count():
        #     raise AppError(*code_set.SubErrorCode.DH_PHONE_ALREADY_EXIST_ERROR)

        invite_code = generate_code()
        invite_qr_code = \
            generate_qr_code(
                settings.INVITE_LINK + "?" + "invite_code=" + invite_code,
                "invitecode")

        recycle_businessman = RecycleBusinessman()
        recycle_businessman.username = username
        recycle_businessman.nickname = nickname
        recycle_businessman.phone = recycle_phone
        recycle_businessman.email = str(recycle_phone) + "@default.com"
        recycle_businessman.set_password(password)
        recycle_businessman.is_recycle = is_recycle
        recycle_businessman.is_login = is_login
        recycle_businessman.invite_code = invite_code
        recycle_businessman.invite_qr_code = invite_qr_code
        recycle_businessman.deposit_back_rate = 0.0
        recycle_businessman.recycle_back_rate = 0.0
        recycle_businessman.invite_back_rate = 0.0
        recycle_businessman.balance_cny = 0.0
        recycle_businessman.save()

        recycle_businessman.uid = "1%05d" % recycle_businessman.pk
        recycle_businessman.save()

        # 添加到回收商组
        group = Group.objects.get(name=u"回收商")
        recycle_businessman.groups.add(group)

        # 初始化钱包
        user_profile_basic = \
            UserProfileBasic.objects.get(pk=recycle_businessman.pk)
        wallet = Wallet()
        wallet.user = user_profile_basic
        wallet.balance = 0.0
        wallet.unit = 2
        wallet.last_update_time = datetime.datetime.now()
        wallet.save()

        return {}


class RecycleBusinessmanDetail(generics.RetrieveUpdateAPIView):
    """回收商详情 backend"""

    queryset = RecycleBusinessman.objects.all()
    serializer_class = RecycleBusinessmanSerializer
    permission_classes = (IsAdministratorPermission,)

    @framework.post_require_check([])
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs).data

    @framework.post_require_check(["recycle_businessman_pk"])
    def patch(self, request, *args, **kwargs):
        recycle_businessman_pk = request.data.get("recycle_businessman_pk")
        is_recycle = request.data.get("is_recycle", None)
        is_login = request.data.get("is_login", None)
        nickname = request.data.get("nickname", None)
        password = request.data.get("password", None)
        deposit_back_rate = request.data.get("deposit_back_rate", None)
        recycle_back_rate = request.data.get("recycle_back_rate", None)
        invite_back_rate = request.data.get("invite_back_rate", None)

        if is_recycle and is_recycle not in (1, 0):
            raise AppError(*code_set.GlobalErrorCode.PARAM_ERROR)
        if is_login and is_login not in (1, 0):
            raise AppError(*code_set.GlobalErrorCode.PARAM_ERROR)

        if deposit_back_rate >= 1 or recycle_back_rate >= 1 \
                or invite_back_rate >= 1:
            raise AppError(*code_set.GlobalErrorCode.PARAM_ERROR)
        # 昵称已经存在
        is_exist = RecycleBusinessman.objects.filter(
            Q(nickname=nickname) & ~Q(id=recycle_businessman_pk)).count()
        if is_exist:
            raise AppError(*code_set.SubErrorCode.BUSINESS_NICKNAME_EXIST)

        # 兑换号已经存在
        # is_exist = RecycleBusinessman.objects.filter(
        #     Q(dh_phone=dh_phone) | Q(phone=dh_phone)).filter(
        #     ~Q(id=recycle_businessman_pk)).count()
        # if is_exist:
        #     raise AppError(*code_set.SubErrorCode.DH_PHONE_ALREADY_EXIST_ERROR)

        try:
            recycle_businessman = \
                RecycleBusinessman.objects.get(pk=recycle_businessman_pk)
        except ObjectDoesNotExist:
            raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)

        if password:
            recycle_businessman.set_password(password)

        recycle_businessman.is_recycle = is_recycle
        recycle_businessman.is_login = is_login
        recycle_businessman.nickname = nickname
        recycle_businessman.deposit_back_rate = deposit_back_rate
        recycle_businessman.recycle_back_rate = recycle_back_rate
        recycle_businessman.invite_back_rate = invite_back_rate
        recycle_businessman.save()
        return {}


class BusinessmanRecyclePrice(generics.ListAPIView):
    """回收商每日回收金额"""

    permission_classes = (IsAdministratorPermission,)

    @framework.get_require_check(["businessman_pk"])
    def get(self, request, *args, **kwargs):
        businessman_pk = request.query_params.get("businessman_pk")
        try:
            businessman = RecycleBusinessman.objects.get(pk=businessman_pk)
        except ObjectDoesNotExist:
            raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)

        queryset = RbEveryDayInfo.objects.filter(
            Q(recycle_businessman=businessman))
        data = []
        for row in queryset:
            data.append({
                "price": row.receive_cny,
                "date": row.data_date
            })
        return data


class BusinessmanModifyPwd(generics.ListAPIView):
    """回收商修改自己的密码"""

    permission_classes = (IsRecycleBusinessman,)

    @framework.get_require_check([])
    def get(self, request, *args, **kwargs):
        user = request.user
        password = request.query_params.get("password")
        if not re.match("^(?![A-Z]+$)(?![a-z]+$)(?!\d+$)\S{8,}$",
                        password):
            raise AppError(*code_set.SubErrorCode.PWD_FORMAT_ERROR)
        try:
            businessman = RecycleBusinessman.objects.get(pk=user.pk)
        except ObjectDoesNotExist:
            raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)
        businessman.set_password(password)
        businessman.save()
        return {}

# ##################################  app   ###################################


class UserConsigneeFilter(django_filters.FilterSet):
    player_id = django_filters.NumberFilter(name="player_id")

    class Meta:
        model = UserConsignee
        fields = []


class UserConsignees(generics.ListCreateAPIView):
    """玩家收货人 app"""

    queryset = UserConsignee.objects.all()
    serializer_class = UserConsigneeSerializer
    permission_classes = (IsGamePlayer,)

    @framework.get_require_check([])
    def get(self, request, *args, **kwargs):
        user = request.user
        userconsignee = UserConsignee.objects.filter(Q(player_id=user.pk))
        return UserConsigneeSerializer(userconsignee, many=True).data

    @framework.post_require_check(["phone"])
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        user = request.user
        phone = request.data["phone"]
        consignee_name = request.data["consignee_name"]

        player = GamePlayer.objects.get(pk=user.pk)

        try:
            recycle_businessman = \
                RecycleBusinessman.objects.get(
                    Q(phone=phone))
        except ObjectDoesNotExist:
            raise AppError(
                *code_set.SubErrorCode.NOT_FOUND_RECYCLE_BUSINESSMAN_ERROR)

        # 检查是否添加或更新
        try:
            UserConsignee.objects.get(
                Q(player_id=user.pk) &
                Q(flag=1) &
                Q(recycle_businessman=recycle_businessman))
            raise AppError(
                *code_set.SubErrorCode.RECYCLE_PHONE_ALREADY_EXIST_ERROR)
        except ObjectDoesNotExist:
            pass

        user_consignee = UserConsignee()
        user_consignee.recycle_businessman = recycle_businessman
        user_consignee.player = player
        user_consignee.flag = 1
        if consignee_name.find("script") == -1:
            user_consignee.consignee_name = consignee_name
        user_consignee.phone = phone
        user_consignee.save()
        return {}


class UpdateUserConsignees(generics.UpdateAPIView):
    """更新收货人 app"""

    queryset = UserConsignee.objects.all()
    serializer_class = UserConsigneeSerializer
    permission_classes = (IsGamePlayer,)

    @framework.post_require_check([])
    def post(self, request, *args, **kwargs):
        user = request.user
        phone = request.data["phone"]
        consignee_name = request.data["consignee_name"]
        user_consignee_pk = request.data["user_consignee_pk"]

        # 没有找到要更新的数据
        try:
            user_consignee = UserConsignee.objects.get(
                Q(player_id=user.pk) & Q(pk=user_consignee_pk))
        except ObjectDoesNotExist:
            raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)

        # 获取回收商, 判断这次添加的是回收号还是兑换号
        try:
            recycle_businessman = \
                RecycleBusinessman.objects.get(
                    Q(phone=phone))
        except ObjectDoesNotExist:
            raise AppError(
                *code_set.SubErrorCode.NOT_FOUND_RECYCLE_BUSINESSMAN_ERROR)
        if recycle_businessman.phone == phone:
            flag = 1

        # 修改的号码类型和添加的不一致
        if user_consignee.flag != flag:
            raise AppError(*code_set.SubErrorCode.FLAG_DIFFERENT_ERROR)

        user_consignee.recycle_businessman = recycle_businessman
        user_consignee.consignee_name = consignee_name
        user_consignee.phone = phone
        user_consignee.save()
        return {}
