# coding:utf-8
import json, time
from decimal import Decimal
from collections import defaultdict

# django 包
import django_filters
from django.db import transaction
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db.models import Q, Sum, Count
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import connection

# rest framework 包
from rest_framework import generics, filters
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

# 项目
from financial.models import PrizeRecord
from shopping_user.models import GamePlayer
from shopping_settings.models import CommodityType, BuyChannel, Banner
from resources.models import Imgs
from inventory.models import CardInventories
from models import Commodity, DuoBaoParticipateRecord, Period, \
    TokenRecord, ShiShiCai, Order, Administrator, AppointWinner, \
    RecommendCommodity
from paginations import LargeResultsSetPagination

from resources.serializers import ImagesSerializer
from serializers import CommoditySerializer, PeriodSerializer, \
    DprSerializer, TrendMapSerializer, HomepageSerializer, \
    AppointWinnerSerializer

from shopping_settings.serializers import BannerSerializer, \
    CommodityTypeSerializer

from shopping_user.permissions import IsAdministratorPermission, IsGamePlayer
from shopping_user.business import change_wallet

from utils.AppError import AppError
from utils.framework import post_require_check, get_require_check
from utils import code_set
from utils.cache_util import CacheUtil, Cache, lock_instance
from utils import utils
import logging
from tasks import allocation_token

logger = logging.getLogger(__name__)


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'commoditytypes': reverse('commoditytypes', request=request,
                                  format=format),
        'commoditys': reverse('commoditys', request=request,
                              format=format)
    })


# ################################### BACKEND ###############################

class CountdownAndParticipating(generics.ListAPIView):
    """倒计时和参与中的周期 backend"""

    permission_classes = (IsAdministratorPermission,)

    @get_require_check([])
    def get(self, request, *args, **kwargs):
        phone = request.query_params.get('phone', None)
        if not phone:
            raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)
        l = [code_set.PeriodStatusCode.COUNTDOWNING[0],
             code_set.PeriodStatusCode.WATING_B_V[0],
             code_set.PeriodStatusCode.PARTICIPATING[0]]
        try:
            player = GamePlayer.objects.filter(phone=phone)
        except ObjectDoesNotExist:
            raise AppError(*code_set.SubErrorCode.NOT_EXIST_PLAYER)
        periodids = DuoBaoParticipateRecord.objects.filter(
            Q(period__status__in=l) & Q(player=player)
        ).values_list('period_id', flat=True)
        periodids = list(set(periodids))

        data = []
        queryset = Period.objects.filter(id__in=periodids)
        for row in queryset:
            d = defaultdict()
            d["pk"] = row.id
            d["period_no"] = row.period_no
            d["commodity_name"] = row.commodity.commodity_name
            d["target_amounts"] = row.target_amounts
            d["participate_amounts"] = \
                DuoBaoParticipateRecord.objects.filter(
                    player=player, period=row).aggregate(
                    Sum('participate_amounts')).values()[0]
            data.append(d)
        return data


class QueryParticipatePlayer(generics.ListAPIView):
    """查询参与玩家 backend"""

    permission_classes = (IsAdministratorPermission,)

    @get_require_check([])
    def get(self, request, *args, **kwargs):
        period_id = int(request.data["period_id"])
        l = [code_set.PeriodStatusCode.PARTICIPATING[0],
             code_set.PeriodStatusCode.COUNTDOWNING[0]]
        try:
            period = Period.objects.get(Q(id=period_id) & Q(status__in=l))
        except ObjectDoesNotExist:
            raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)
        r = DuoBaoParticipateRecord.objects.filter(period=period)
        return DprSerializer(r, many=True).data


class AppointWinnerFilter(django_filters.FilterSet):
    phone = django_filters.CharFilter(name='player__phone')
    admin__username = django_filters.CharFilter(name='admin__username')

    class Meta:
        model = AppointWinner
        fields = []


class AppointWinnerView(generics.ListCreateAPIView):
    """指定中奖人 backend"""
    queryset = AppointWinner.objects.all()
    serializer_class = AppointWinnerSerializer
    permission_classes = (IsAdministratorPermission,)
    pagination_class = LargeResultsSetPagination
    ordering_fields = ('id',)

    filter_backends = (
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,)
    filter_class = AppointWinnerFilter

    @get_require_check([])
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs).data

    @post_require_check([])
    def post(self, request, *args, **kwargs):
        user = request.user
        phone = int(request.data["phone"])
        period_id = int(request.data["period_id"])
        l = [code_set.PeriodStatusCode.PARTICIPATING[0],
             code_set.PeriodStatusCode.WATING_B_V[0],
             code_set.PeriodStatusCode.COUNTDOWNING[0]]
        try:
            player = GamePlayer.objects.get(phone=phone)
        except ObjectDoesNotExist:
            raise AppError(*code_set.SubErrorCode.NOT_EXIST_PLAYER)
        try:
            period = Period.objects.get(id=period_id, status__in=l)
        except ObjectDoesNotExist:
            raise AppError(*code_set.SubErrorCode.NOT_MODIFY)
        calculate_countdown = CacheUtil.get_pttl_calculate_result(period_id)
        if period.status == code_set.PeriodStatusCode.COUNTDOWNING[0] or \
                period.status == code_set.PeriodStatusCode.WATING_B_V[
            0]:
            if (not calculate_countdown) or int(calculate_countdown) < 5000:
                raise AppError(*code_set.SubErrorCode.NOT_MODIFY)

        dprs = DuoBaoParticipateRecord.objects.filter(
            Q(period=period) & Q(player=player))
        if not len(dprs):
            raise AppError(*code_set.SubErrorCode.PLAYER_NOT_BUY)
        try:
            appoint_winner = AppointWinner.objects.get(period=period)
        except ObjectDoesNotExist:
            appoint_winner = AppointWinner()
            appoint_winner.period = period
        appoint_winner.player = player
        appoint_winner.admin = Administrator.objects.get(id=user.id)
        appoint_winner.save()
        return {}


class ModifyAppShowIndex(generics.CreateAPIView):
    """修改APP展示顺序"""

    permission_classes = (IsAdministratorPermission,)

    @post_require_check([])
    def post(self, request, *args, **kwargs):
        data = request.data["show_data"]

        obj_l = []
        for row in data:
            commodity_id = row["commodity_id"]
            show_index = row["show_index"]
            try:
                commodity = Commodity.objects.get(id=commodity_id)
            except ObjectDoesNotExist:
                raise AppError(*code_set.GlobalErrorCode.PARAM_ERROR)
            obj_l.append({"commodity": commodity, "show_index": show_index})
        for obj in obj_l:
            commodity = obj["commodity"]
            show_index = obj["show_index"]
            commodity.show_index = show_index
            commodity.save()
        return {}


class UploadFileToQiniu(generics.CreateAPIView):
    """上传文件到七牛"""

    permission_classes = (IsAdministratorPermission,)

    @post_require_check([])
    def post(self, request, *args, **kwargs):
        imgs = request.FILES

        current_time = time.time()
        image_file_name = str(current_time).replace(".", "") + ".jpg"
        img_path = settings.TMP_PATH + "/qr_code/" + image_file_name
        with open(img_path, 'wb+') as fd:
            for row in imgs["file"].chunks():
                fd.write(row)

        utils.upload_image("qr_code/" + image_file_name, img_path)
        return {"path": "qr_code/" + image_file_name}


class OrderList(generics.ListAPIView):
    """实时购买列表 (参与记录) backend"""

    permission_classes = (IsAdministratorPermission,)

    @get_require_check(["page", "limit"])
    @transaction.atomic
    def get(self, request, *args, **kwargs):
        page = request.query_params.get("page")
        limit = request.query_params.get("limit")

        uid = request.query_params.get("uid", None)
        phone = request.query_params.get("phone", None)
        period_no = request.query_params.get("period_no", None)

        queryset = DuoBaoParticipateRecord.objects.filter(
            Q(player__is_robot=False)).order_by("-time")
        if period_no:
            queryset = queryset.filter(Q(period__period_no=period_no))
        if uid:
            queryset = queryset.filter(Q(player__uid=uid))
        if phone:
            queryset = queryset.filter(Q(player__phone=phone))

        paginator = Paginator(queryset, limit)
        try:
            queryset = paginator.page(page)
        except PageNotAnInteger:
            queryset = paginator.page(1)
        except EmptyPage:
            queryset = paginator.page(paginator.num_pages)

        zero = Decimal(str(0.0))
        data = []
        for row in queryset:
            period = row.period
            commodity = period.commodity
            player = row.player
            target_amounts = period.target_amounts
            luck_token = None
            if period.status == code_set.PeriodStatusCode.REWARDED[0]:
                luck_token = period.luck_token

            # 总的购买人次
            # participate_amounts = DuoBaoParticipateRecord.objects.filter(
            #     Q(period=period) & Q(player=player)).aggregate(
            #     Sum('participate_amounts')).values()[0]

            # 总的购买次数
            # buy_count = Order.objects.filter(Q(player=player)).count()

            # 当前周期是第几期
            # period_index = 0
            # period_ids = Period.objects.filter(
            #     Q(commodity=commodity)).values_list("pk", flat=True)
            # for x in period_ids:
            #     period_index += 1
            #     if period.pk == x:
            #         break

            d = defaultdict()
            d["pk"] = row.pk
            d["commodity_id"] = commodity.pk
            d["period_id"] = period.pk
            d["commodity_name"] = commodity.commodity_name
            d["snatch_treasure_amounts"] = commodity.snatch_treasure_amounts
            d["period_no"] = period.period_no
            d["period_index"] = commodity.count
            d["nickname"] = player.get_nickname
            d["ip"] = player.ip
            d["ip_address"] = player.ip_address
            d["uid"] = player.uid
            d["phone"] = player.phone
            d["buy_count"] = 0
            d["buy_renci"] = \
                row.participate_amounts if row.participate_amounts else zero
            d["rate"] = round(row.participate_amounts / target_amounts,
                              4) * 100
            d["time"] = row.time.strftime("%Y-%m-%d %H:%M:%S")

            if period.status == code_set.PeriodStatusCode.REWARDED[0]:
                d["period_status"] = u"已结束"
            else:
                d["period_status"] = u"正在进行中"
            if luck_token and str(luck_token) in row.token_str:
                d["_status"] = u"中奖"
            else:
                d["_status"] = u"已支付"
            data.append(d)

        return {
            "count": paginator.count,
            "next": None,
            "previous": None,
            "results": data
        }


class CommodityList(generics.ListCreateAPIView):
    """商品 backend"""
    permission_classes = (IsAdministratorPermission,)

    @post_require_check(["commodity_name", "commodity_type", "reward_type",
                         "market_price_cny", "snatch_treasure_amounts",
                         "dh_price_cny", "is_continue", "buy_channel",
                         "status", "image_path"])
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        commodity_name = request.data["commodity_name"]
        commodity_type = request.data["commodity_type"]
        reward_type = int(request.data["reward_type"])
        market_price_cny = int(float(request.data["market_price_cny"]))
        snatch_treasure_amounts = int(
            float(request.data["snatch_treasure_amounts"]))
        dh_price_cny = int(float(request.data["dh_price_cny"]))
        is_continue = int(request.data["is_continue"])
        buy_channel = request.data["buy_channel"]
        status = int(request.data["status"])
        image_path = request.data["image_path"]
        is_card = int(request.data["is_card"])
        card_inventory = request.data["card_inventory"]
        quota_str = request.data["quota_str"]
        unit_price = request.data["unit_price"]
        total_renci = request.data["total_renci"]

        if reward_type not in (1, 2) or \
                is_continue not in (1, 0) or \
                status not in (1, 2) or \
                is_card not in (1, 0):
            logger.error("{} {} {} {}".format(reward_type, is_continue, status, is_card))
            raise AppError(*code_set.GlobalErrorCode.PARAM_ERROR)

        if u"，" in quota_str.encode("utf-8"):
            logger.error(u"逗号验证错误")
            raise AppError(*code_set.GlobalErrorCode.PARAM_ERROR)
        if unit_price * total_renci != snatch_treasure_amounts:
            logger.error(u"{} * {} != {}".format(unit_price, total_renci, snatch_treasure_amounts))
            raise AppError(*code_set.GlobalErrorCode.PARAM_ERROR)
        if reward_type == 2:  # B值
            if is_card:
                raise AppError(*code_set.GlobalErrorCode.PARAM_ERROR)
        if market_price_cny != dh_price_cny:
            logger.error(u"{} != {}".format(snatch_treasure_amounts, dh_price_cny))
            raise AppError(*code_set.GlobalErrorCode.PARAM_ERROR)

        try:
            commodity_type = CommodityType.objects.get(pk=commodity_type)
            buy_channel = BuyChannel.objects.get(pk=buy_channel)
            card_inventory = CardInventories.objects.get(pk=card_inventory)
        except (ObjectDoesNotExist,):
            raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)

        commodity = Commodity()
        commodity.commodity_name = commodity_name
        commodity.commodity_type = commodity_type
        commodity.reward_type = int(reward_type)
        commodity.market_price_cny = market_price_cny
        commodity.snatch_treasure_amounts = snatch_treasure_amounts
        commodity.dh_price_cny = dh_price_cny
        commodity.is_continue = int(is_continue)
        commodity.buy_channel = buy_channel
        commodity.status = int(status)
        commodity.is_card = True if is_card else False
        commodity.card_inventory = card_inventory
        commodity.cover = image_path
        commodity.quota_str = quota_str
        commodity.unit_price = unit_price
        commodity.total_renci = total_renci
        commodity.save()

    @get_require_check([])
    def get(self, request, *args, **kwargs):
        status = request.query_params.get("status", None)
        # page = request.query_params.get("page", None)
        # size = 10

        if status and status not in (1, 2):
            raise AppError(*code_set.GlobalErrorCode.PARAM_ERROR)

        queryset = Commodity.objects.filter(
            ~Q(status=10)).order_by("show_index")
        if status:
            queryset = queryset.filter(Q(status=status))
        # 查询回收商数量
        # paginator = Paginator(queryset, size)
        # try:
        #     queryset = paginator.page(page)
        # except PageNotAnInteger:
        #     queryset = paginator.page(1)
        # except EmptyPage:
        #     queryset = paginator.page(paginator.num_pages)

        for row in queryset:
            setattr(row, "image_path", "")
        data = CommoditySerializer(queryset, many=True).data
        for row in data:
            if row["card_inventory"]:
                ci = CardInventories.objects.get(id=row["card_inventory"])
                row["card_inventory_name"] = ci.name
        result = {
            "count": 0,
            "next": None,
            "previous": None,
            "results": data
        }
        return result


class CommodityDetail(generics.RetrieveUpdateAPIView):
    """商品详情 backend"""
    queryset = Commodity.objects.all()
    serializer_class = CommoditySerializer
    permission_classes = (IsAdministratorPermission,)

    @get_require_check([])
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs).data

    @post_require_check([])
    def put(self, request, *args, **kwargs):
        """
        单价 总人次 开奖类型 市场价 兑换价 夺宝价 不能更改
        """
        pk = request.data.get("pk", None)
        commodity_name = request.data.get("commodity_name", None)
        commodity_type = request.data.get("commodity_type", None)
        reward_type = request.data.get("reward_type", None)
        market_price_cny = request.data.get("market_price_cny", None)
        snatch_treasure_amounts = request.data.get("snatch_treasure_amounts",
                                                   None)
        dh_price_cny = request.data.get("dh_price_cny", None)
        is_continue = request.data.get("is_continue", None)
        buy_channel = request.data.get("buy_channel", None)
        status = request.data.get("status", None)
        image_path = request.data.get("image_path", None)
        show_index = request.data.get("show_index", None)
        is_card = request.data.get("is_card", None)
        card_inventory = request.data.get("card_inventory", None)
        quota_str = request.data.get("quota_str", None)
        unit_price = request.data.get("unit_price", None)
        total_renci = request.data.get("total_renci", None)

        if status and int(status) not in (1, 2, 10):
            raise AppError(*code_set.GlobalErrorCode.PARAM_ERROR)
        if is_continue and int(is_continue) not in (1, 0):
            raise AppError(*code_set.GlobalErrorCode.PARAM_ERROR)
        try:
            commodity = Commodity.objects.get(pk=pk)
        except ObjectDoesNotExist:
            raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)

        if commodity_name:
            commodity.commodity_name = commodity_name
        if commodity_type:
            commodity.commodity_type_id = commodity_type

        if is_continue:
            commodity.is_continue = is_continue
        if buy_channel:
            buy_channel = BuyChannel.objects.get(pk=buy_channel)
            commodity.buy_channel = buy_channel
        if show_index:
            commodity.show_index = show_index
        if status:
            commodity.status = status
            # 删除
            if int(status) == 10:
                commodity.is_continue = 0
            if int(status) == 2:
                commodity.is_continue = 0
        if image_path:
            commodity.cover = image_path

        if quota_str:
            commodity.quota_str = quota_str
        commodity.save()

        return {}


class WinPrizeOrder(generics.ListAPIView):
    """中奖订单 backend"""

    permission_classes = (IsAdministratorPermission,)

    @get_require_check([])
    def get(self, request, *args, **kwargs):
        page = request.query_params.get("page")
        limit = request.query_params.get("limit")

        uid = request.query_params.get("uid", None)
        phone = request.query_params.get("phone", None)
        period_no = request.query_params.get("period_no", None)

        queryset = Period.objects.filter(
            Q(status=code_set.PeriodStatusCode.REWARDED[0]) &
            Q(luck_player__is_robot=False))
        if period_no:
            queryset = queryset.filter(Q(period_no=period_no))
        if uid:
            queryset = queryset.filter(Q(luck_player__uid=uid))
        if phone:
            queryset = queryset.filter(Q(luck_player__phone=phone))
        queryset = queryset.order_by("-reward_time")
        paginator = Paginator(queryset, limit)
        try:
            queryset = paginator.page(page)
        except PageNotAnInteger:
            queryset = paginator.page(1)
        except EmptyPage:
            queryset = paginator.page(paginator.num_pages)

        zero = Decimal(str(0.0))
        data = []
        for period in queryset:
            commodity = period.commodity
            player = period.luck_player

            # 总的购买人次
            participate_amounts = DuoBaoParticipateRecord.objects.filter(
                Q(period=period) & Q(player=player)).aggregate(
                Sum('participate_amounts')).values()[0]

            # 当前周期是第几期
            period_index = 0
            period_ids = Period.objects.filter(
                Q(commodity=commodity)).values_list("pk", flat=True)
            for x in period_ids:
                period_index += 1
                if period.pk == x:
                    break

            d = defaultdict()
            d["pk"] = period.pk
            d["commodity_id"] = commodity.pk
            d["commodity_name"] = commodity.commodity_name
            d["commodity_type"] = commodity.commodity_type.type_name
            d["commodity_buy_channel"] = commodity.buy_channel.remark
            d["snatch_treasure_amounts"] = commodity.snatch_treasure_amounts
            d["period_no"] = period.period_no
            d["period_index"] = period_index
            d["nickname"] = player.get_nickname
            d["phone"] = player.phone
            d["ip"] = player.ip
            d["ip_address"] = player.ip_address
            d["buy_renci"] = \
                participate_amounts if participate_amounts else zero
            d["luck_token"] = period.luck_token
            d["reward_time"] = period.reward_time.strftime("%Y-%m-%d %H:%M:%S")

            if period.status == code_set.PeriodStatusCode.REWARDED[0]:
                d["period_status"] = u"已结束"
            else:
                d["period_status"] = u"正在进行中"

            # 是否领奖
            prize_record = PrizeRecord.objects.get(period=period)
            if prize_record.status == \
                    code_set.PrizeStatusCode.ACCEPT_PRIZED[0]:
                d["is_accept_prize"] = u"已领奖"
            else:
                d["is_accept_prize"] = u"未领奖"
            data.append(d)

        return {
            "count": paginator.count,
            "next": None,
            "previous": None,
            "results": data
        }


# ################################# APP ######################################


def _get_player_tokens(player_id, period_id):
    """获取用户夺宝号"""
    dprs = DuoBaoParticipateRecord.objects.filter(
        Q(player_id=player_id) & Q(period_id=period_id))
    arr = []
    for row in dprs:
        arr.append(row.token_str)
    return ','.join(arr)


class Homepage(generics.ListAPIView):
    """主页 mobile"""

    @get_require_check([])
    def get(self, request, *args, **kwargs):
        PARTICIPATING = code_set.PeriodStatusCode.PARTICIPATING[0]

        query_params = request.query_params
        order_type = int(query_params['order_type'])
        last_pk = query_params.get('last_pk', None)

        if order_type not in [1, 2, 3, 4, 5, 6]:
            raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)

        if last_pk:
            last_pk = int(last_pk)
            if last_pk < 0 or last_pk > 999999999:
                raise AppError(*code_set.GlobalErrorCode.PARAM_ERROR)

        banners = Cache.get_cache_banner()
        # 推荐商品
        recommend_commodity_data = []
        recommend_commodities = RecommendCommodity.objects.filter(status=1)
        for row in recommend_commodities:
            commodity = row.commodity
            recommend_commodity_data.append({
                "name": row.name,
                "commodity_id": commodity.pk,
                "commodity_images": commodity.cover,
                "location": row.location,
                "status": row.status,
            })

        commodities = []
        # 在售商品
        queryset = Period.objects.filter(status=PARTICIPATING)
        if last_pk:
            queryset = queryset.filter(pk__lt=last_pk)
        # 推荐
        if order_type == 1:
            queryset = queryset.order_by('commodity__show_index')
        # 最快
        if order_type == 2:
            queryset = queryset.order_by('-rate')
        # 最新
        if order_type == 3:
            queryset = queryset.order_by('-create_time')
        # 低价
        if order_type == 4:
            queryset = queryset.order_by('commodity__unit_price')
        # 高价
        if order_type == 5:
            queryset = queryset.order_by('-commodity__unit_price')

        if last_pk:
            paginator = Paginator(queryset, 10)
            queryset = paginator.page(1)

        for row in queryset:
            commodity = row.commodity

            d = defaultdict()
            d["period_pk"] = row.pk
            d["commodity_name"] = commodity.commodity_name
            d["commodity_reward_type"] = commodity.reward_type
            d["commodity_images"] = commodity.cover
            d["rate"] = row.rate
            d["total_renci"] = commodity.total_renci
            d["residue_renci"] = row.target_amounts - row.amounts_prepared
            commodities.append(d)

        data = {
            "banner": banners,
            "headline": "",
            "recommend": recommend_commodity_data,
            "commodities": commodities
        }
        return data


class CommodityTag(generics.ListAPIView):
    """商品分类"""

    @get_require_check([])
    def get(self, request, *args, **kwargs):
        commodity_types = CommodityType.objects.filter(
            Q(status=1)).order_by('-type_index')
        return CommodityTypeSerializer(commodity_types, many=True).data


class PeriodByTag(generics.ListAPIView):
    """根据分类查询周期"""

    @get_require_check([])
    def get(self, request, *args, **kwargs):
        tag_id = request.query_params.get('tag_id')
        PARTICIPATING = code_set.PeriodStatusCode.PARTICIPATING[0]
        data = []
        periods = Period.objects.select_related(
            'commodity').filter(status=PARTICIPATING,
                                commodity__commodity_type__id=tag_id)
        for row in periods:
            d = defaultdict()
            d["period_pk"] = row.pk
            d["rate"] = row.rate
            d["commodity_name"] = row.commodity.commodity_name
            d["commodity_images"] = row.commodity.cover
            data.append(d)
        return data


class CommodityDetailPage(generics.ListAPIView):
    """商品详情页 app"""

    @get_require_check([])
    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            user_pk = user.pk
        commodity_pk = request.query_params.get("commodity_pk", None)
        period_pk = request.query_params.get("period_pk", None)

        if not commodity_pk and not period_pk:
            raise AppError(*code_set.GlobalErrorCode.PARAM_ERROR)
        try:
            if period_pk:
                period = Period.objects.get(pk=period_pk)
                commodity = period.commodity
            elif commodity_pk:
                commodity = Commodity.objects.get(id=commodity_pk)
                period = Period.objects.get(
                    Q(commodity=commodity) &
                    Q(status=code_set.PeriodStatusCode.PARTICIPATING[0]))

        except ObjectDoesNotExist:
            raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)

        # 商品数据
        commodity_data = CommoditySerializer(commodity).data
        commodity_pk = commodity_data["pk"]

        commodity_detail_data = PeriodSerializer(period).data
        commodity_detail_data["commodity_images"] = \
            commodity_data["commodity_images"]

        # 后期数据
        period_pk = period.pk
        period_status = period.status

        luck_player_data = defaultdict()
        # 中奖用户数据
        if period_status == code_set.PeriodStatusCode.REWARDED[0]:
            luck_player = period.luck_player
            luck_player_pk = period.luck_player.pk
            open_lottery_time = period.reward_time
            luck_token = period.luck_token

            luck_player_data["pk"] = luck_player.pk
            luck_player_data["headimage"] = luck_player.get_head_image
            luck_player_data["nickname"] = luck_player.get_nickname
            participate_amounts = DuoBaoParticipateRecord.objects.filter(
                Q(period=period) & Q(player=luck_player)).aggregate(
                Sum('participate_amounts')).values()[0]
            luck_player_data["participate_amounts"] = participate_amounts
            luck_player_data["reward_time"] = open_lottery_time.strftime(
                "%m-%d %H:%M")
            luck_player_data["luck_token"] = luck_token
            luck_player_data["ip"] = luck_player.get_ip
            luck_player_data["ip_address"] = luck_player.get_ip_address

        content = json.loads(period.content)
        # 往期走势
        trend_map_data = Cache.get_cache_trend_map(commodity_pk)

        # 荣誉榜
        honor_list_data = content["honor_list"] if "honor_list" \
                                                   in content else []

        # 当前登陆用户是否参与,是否中奖
        if "playerids" in content:
            playerids_d = content["playerids"]
            playerids = map(int, playerids_d.keys())
        else:
            playerids_d = {}
            playerids = []
        notice = 6
        if user.is_authenticated:
            if period_status == code_set.PeriodStatusCode.REWARDED[0]:
                if user_pk == luck_player_pk:
                    notice = 5  # 已开奖 已中奖
                if user_pk in playerids and user_pk != luck_player_pk:
                    notice = 4  # 已开奖 已参与 未中奖
                if user_pk not in playerids:
                    notice = 6  # 已开奖 未参与 跳到最新一期
            elif period_status == code_set.PeriodStatusCode.PARTICIPATING[0]:
                if user_pk in playerids:
                    notice = 2  # 未开奖 已参与
                else:
                    notice = 1  # 未开奖 未参与 弹出底部参与框
            elif period_status in [code_set.PeriodStatusCode.COUNTDOWNING[0],
                                   code_set.PeriodStatusCode.WATING_B_V[0]]:
                notice = 3  # 开奖中
        else:
            notice = 7  # 未登录都是7
        commodity_detail_data["countdown_millisecond"] = \
            CacheUtil.get_pttl_expire(period_pk)

        data = {
            "commodity_detail_data": commodity_detail_data,
            "honor_list_data": honor_list_data,
            "luck_player_data": luck_player_data,
            "trend_map_data": trend_map_data,
            "notice": notice,
            "my_amounts": 0
        }

        # 当前登陆用户的购买量
        if user.is_authenticated:
            my_amounts = 0
            if str(user_pk) in playerids_d:
                my_amounts += playerids_d[str(user_pk)]
            data["my_amounts"] = my_amounts

        return data


class CurrentPeriodParticipates(generics.ListAPIView):
    """本期参与记录"""

    @get_require_check([])
    def get(self, request, *args, **kwargs):
        period_pk = int(request.query_params["period_pk"])
        participates = DuoBaoParticipateRecord.objects.filter(
            period_id=period_pk).order_by("-id")
        return DprSerializer(participates, many=True).data


class PreviousPeriod(generics.ListAPIView):
    """往期揭晓 app"""

    @get_require_check(["commodity_pk"])
    def get(self, request, *args, **kwargs):
        commodity_pk = int(request.query_params["commodity_pk"])
        last_pk = int(request.query_params["last_pk"])

        if last_pk < 0 or last_pk > 999999999:
            raise AppError(*code_set.GlobalErrorCode.PARAM_ERROR)

        queryset = Period.objects.filter(
            Q(status=code_set.PeriodStatusCode.REWARDED[0]) &
            Q(commodity=commodity_pk))
        if last_pk:
            queryset = queryset.filter(Q(pk__lt=last_pk))
        queryset = queryset.order_by('-pk')
        paginator = Paginator(queryset, 10)
        queryset = paginator.page(1)

        data = []
        for row in queryset:
            luck_player = row.luck_player
            order = Order.objects.get(period=row, player=luck_player)

            d = defaultdict()
            d["period_pk"] = row.pk
            d["period_no"] = row.period_no
            d["open_lottery_time"] = row.reward_time.strftime(
                "%Y-%m-%d %H:%M:%S")
            d["luck_player_nickname"] = luck_player.get_nickname
            d["luck_token"] = row.luck_token
            d["participate_renci"] = order.total_renci
            d["luck_player_headimage"] = luck_player.get_head_image
            d["luck_player_id"] = luck_player.pk
            data.append(d)
        return data


class NewDrawLottery(generics.ListAPIView):
    """最新揭晓 mobile"""

    @get_require_check([])
    def get(self, request, *args, **kwargs):
        last_pk = int(request.query_params.get("last_pk"))

        if last_pk < 0 or last_pk > 999999999:
            raise AppError(*code_set.GlobalErrorCode.PARAM_ERROR)

        l = [code_set.PeriodStatusCode.WATING_B_V[0],
             code_set.PeriodStatusCode.COUNTDOWNING[0],
             code_set.PeriodStatusCode.REWARDING[0],
             code_set.PeriodStatusCode.REWARDED[0]]

        queryset = Period.objects.select_related(
            'commodity', 'luck_player').filter(
            status__in=l, pk__lt=last_pk).order_by('-open_index')

        paginator = Paginator(queryset, 10)
        queryset = paginator.page(1)

        data = []
        for row in queryset:
            period_pk = row.id
            commodity = row.commodity
            period_status = row.status
            luck_player = row.luck_player
            reward_type = commodity.reward_type

            d = defaultdict()
            d["period_pk"] = row.id
            d["commodity_name"] = commodity.commodity_name
            d["commodity_images"] = commodity.cover
            d["commodity_reward_type"] = reward_type
            d["period_status"] = period_status
            d["open_index"] = row.open_index
            d["market_price_cny"] = commodity.market_price_cny

            if period_status == code_set.PeriodStatusCode.REWARDED[0]:
                #order = Order.objects.get(period=row, player=luck_player)
                d["luck_player_nickname"] = luck_player.get_nickname
                d["luck_player_pk"] = luck_player.pk
                d["open_lottery_time"] = row.reward_time.strftime("%m-%d %H:%M")
                d["luck_player_headimage"] = luck_player.get_head_image
                d["participate_renci"] = 0 # TODO

            if reward_type == code_set.CommodityRewardCode.MIAOKAI[0] \
                    and period_status == code_set.PeriodStatusCode.COUNTDOWNING[
                0]:
                d["countdown_millisecond"] = \
                    CacheUtil.get_pttl_expire(row.id)
            if reward_type == code_set.CommodityRewardCode.B_VALUE[0]:
                # d["b_value_millisecond"] = CacheUtil.get_pttl_expire(period_pk)
                d["countdown_millisecond"] = CacheUtil.get_pttl_expire(
                    period_pk)
            data.append(d)
        return data


class RecentlyParticipateRecords(generics.ListAPIView):
    """最近参与记录 mobile"""

    @get_require_check([])
    def get(self, request, *args, **kwargs):
        player_pk = int(request.query_params["player_pk"])

        try:
            player = GamePlayer.objects.get(pk=player_pk)
        except ObjectDoesNotExist:
            raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)

        participate_records = []
        dprs = DuoBaoParticipateRecord.objects.filter(
            player=player).order_by('-pk')[:10]
        for row in dprs:
            period = row.period
            commodity = period.commodity
            luck_player = period.luck_player
            d = defaultdict()
            d["participate_pk"] = row.pk
            d["commodity_name"] = commodity.commodity_name
            d["commodity_images"] = commodity.cover
            d["period_no"] = period.period_no
            d["participate_renci"] = row.participate_amounts
            # 已开奖
            if period.status == 6:
                d["open_lottery_time"] = \
                    period.reward_time.strftime('%m-%d %H:%M')
                d["luck_token"] = period.luck_token
                d["luck_player_nickname"] = luck_player.get_nickname
                if luck_player.pk == player_pk:
                    d["is_win_prize"] = True
                else:
                    d["is_win_prize"] = False
            participate_records.append(d)
        return participate_records


class RecentlyWinPrizeRecords(generics.ListAPIView):
    """最近中奖记录"""

    @get_require_check([])
    def get(self, request, *args, **kwargs):
        player_pk = int(request.query_params["player_pk"])

        try:
            player = GamePlayer.objects.get(pk=player_pk)
        except ObjectDoesNotExist:
            raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)

        prize_records = []
        prizes = PrizeRecord.objects.filter(
            player=player).order_by('-pk')[:10]
        for row in prizes:
            period = row.period
            commodity = period.commodity

            order = Order.objects.get(period=period, player=player)
            d = defaultdict()
            d["participate_pk"] = row.pk
            d["commodity_name"] = commodity.commodity_name
            d["commodity_images"] = commodity.cover
            d["period_no"] = period.period_no
            d["participate_renci"] = order.total_renci
            d["open_lottery_time"] = period.reward_time
            d["luck_token"] = period.luck_token

            prize_records.append(d)
        return prize_records


class AppOrderRecords(generics.ListAPIView):
    """订单记录 mobile[我的-->订单记录]"""

    permission_classes = (IsGamePlayer,)

    @get_require_check(['last_pk'])
    def get(self, request, *args, **kwargs):
        last_pk = int(request.query_params.get('last_pk'))
        status = request.query_params['status']

        user = request.user
        if last_pk < 0 or last_pk > 999999999:
            raise AppError(*code_set.GlobalErrorCode.PARAM_ERROR)
        status_list = [code_set.PeriodStatusCode.PARTICIPATING[0],
                       code_set.PeriodStatusCode.REWARDED[0]]
        if status not in ['P', 'K', 'Y']:
            raise AppError(*code_set.GlobalErrorCode.PARAM_ERROR)

        try:
            cur_player = GamePlayer.objects.get(pk=user.pk)
        except ObjectDoesNotExist:
            raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)

        order_records = []

        orders = Order.objects.filter(Q(player=cur_player) &
                                      Q(pk__lt=last_pk))
        # 拼购中 根据第一次order创建时间排序
        if status == 'P':
            orders = orders.filter(Q(period__status__in=[1, 2])
                                   ).order_by('-create_time')
        # 开奖中 根据筹备完成时间排序
        elif status == 'K':
            orders = orders.filter(Q(period__status__in=[3, 4, 5])
                                   ).order_by('-period__finish_time')
        # 已揭晓 根据揭晓时间排序
        elif status == 'Y':
            orders = orders.filter(Q(period__status=6)
                                   ).order_by('-period__reward_time')
        paginator = Paginator(orders, 10)
        orders = paginator.page(1)

        for order in orders:
            period = order.period
            commodity = period.commodity
            period_pk = period.pk
            commodity_pk = commodity.pk
            commodity_name = commodity.commodity_name

            d = defaultdict()
            d["order_pk"] = order.pk
            d["commodity_id"] = commodity_pk
            d["commodity_name"] = commodity_name
            d["commodity_images"] = commodity.cover

            d["period_id"] = period_pk
            d["period_no"] = period.period_no
            d["participate_renci"] = order.total_renci
            d["is_win_prize"] = False
            d["luck_token"] = period.luck_token
            d["period_numbers"] = "%07d" % commodity.count
            d["rate"] = round(period.rate, 2) * 100
            d["token_str"] = _get_player_tokens(cur_player.pk, period.pk)

            # 已开奖
            if period.status == code_set.PeriodStatusCode.REWARDED[0]:
                luck_player = period.luck_player
                luck_player_order = Order.objects.get(
                    player=luck_player, period=period)
                d["luck_player_id"] = luck_player.pk
                d["luck_player_headimage"] = luck_player.get_head_image
                d["luck_player_nickname"] = luck_player.get_nickname
                d["luck_player_participate_renci"] = \
                    luck_player_order.total_renci
                d["reward_time"] = \
                    period.reward_time.strftime("%Y-%m-%d %H:%M:%S")
                if luck_player.pk == cur_player.pk:
                    d["is_win_prize"] = True
                else:
                    d["is_win_prize"] = False
            order_records.append(d)

        return order_records


class PrizeRecords(generics.ListAPIView):
    """中奖记录 mobile[我的-->中奖记录]"""

    @get_require_check(['last_pk'])
    def get(self, request, *args, **kwargs):
        l = [code_set.PrizeStatusCode.ACCEPT_PRIZED[0],
             code_set.PrizeStatusCode.CARD_INVENTORIES_INSUFFICIENT[0]]

        last_pk = int(request.query_params.get('last_pk'))
        is_accept_prize = request.query_params.get('is_accept_prize', None)
        playerid = request.user.pk

        if last_pk < 0 or last_pk > 999999999:
            raise AppError(*code_set.GlobalErrorCode.PARAM_ERROR)
        if is_accept_prize and int(is_accept_prize) not in (2, 1):
            raise AppError(*code_set.GlobalErrorCode.PARAM_ERROR)
        if is_accept_prize:
            is_accept_prize = int(is_accept_prize)

        queryset = PrizeRecord.objects.filter(
            Q(player_id=playerid) & Q(pk__lt=last_pk))
        if is_accept_prize == 2:
            queryset = queryset.filter(
                ~Q(status=code_set.PrizeStatusCode.NOT_ACCEPT_PRIZE[0]))
        elif is_accept_prize == 1:
            queryset = queryset.filter(
                Q(status=code_set.PrizeStatusCode.NOT_ACCEPT_PRIZE[0]))

        queryset = queryset.order_by('-pk')
        paginator = Paginator(queryset, 10)
        queryset = paginator.page(1)

        data = []
        for row in queryset:
            period = row.period
            commodity = period.commodity
            period_pk = period.pk
            commodity_pk = commodity.pk
            commodity_name = commodity.commodity_name
            order = Order.objects.get(period=period, player_id=playerid)

            d = defaultdict()
            d["prize_record_pk"] = row.pk
            d["commodity_id"] = commodity_pk
            d["commodity_images"] = commodity.cover
            d["commodity_name"] = commodity_name
            d["participate_renci"] = order.total_renci
            d["period_id"] = period_pk
            d["period_no"] = period.period_no
            d["reward_time"] = period.reward_time.strftime("%m-%d %H:%M")
            d["luck_token"] = period.luck_token

            if row.status in l:
                d["is_accept_prize"] = True
            elif row.status == code_set.PrizeStatusCode.NOT_ACCEPT_PRIZE[0]:
                d["is_accept_prize"] = False
            data.append(d)
        return data


class Participate(generics.CreateAPIView):
    """参与夺宝 mobile"""

    permission_classes = (IsGamePlayer,)

    @post_require_check(["period_id", "amounts"])
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """
        period_id 周期id
        amounts 购买的人次
        """
        period_id = int(request.data["period_id"])
        amounts = int(request.data["amounts"])
        if amounts < 1 or amounts > 999999:
            raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)
        user = request.user

        try:
            period = Period.objects.select_for_update().get(pk=period_id)
            # 玩家
            game_player = GamePlayer.objects.get(pk=user.pk)
        except ObjectDoesNotExist:
            raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)
        participate_status = code_set.PeriodStatusCode.PARTICIPATING[0]
        if period.status != participate_status:
            raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)
        # 夺宝货物数量超过剩余量
        if period.amounts_prepared + amounts > period.target_amounts:
            raise AppError(*code_set.SubErrorCode.AMOUNTS_INSUFFICIENT_ERROR)
        amounts_dup = int(CacheUtil.get_period_amounts(period_id))
        # 夺宝货物数量不足
        if amounts_dup - amounts < 0:
            raise AppError(*code_set.SubErrorCode.AMOUNTS_INSUFFICIENT_ERROR)

        # 人次 * 单价
        spend = amounts * period.commodity.unit_price
        result = change_wallet(-spend, unit=1, user_id=user.pk)
        # 存款不足
        if not result:
            raise AppError(*code_set.SubErrorCode.NOT_SUFFICIENT_FUNDS_ERROR)

        d = {"period_id": period_id, "player_id": game_player.id,
             "amounts": amounts, "spend": spend,
             "unit_price": period.commodity.unit_price,
             "residue_amounts": CacheUtil.decr_period_amounts(period_id,
                                                              amounts)}
        CacheUtil.push_period_queue(period_id, d)

        allocation_token.apply_async(
            args=[period_id],
            exchange='snatchtreasure',
            routing_key="allocation_token")
        return {}


class QueryTokens(generics.ListAPIView):
    """查询夺宝号"""

    permission_classes = (IsGamePlayer,)

    @get_require_check([])
    def get(self, request, *args, **kwargs):
        period_id = request.query_params.get("period_id")
        text = request.query_params.get("text", None)
        user = request.user

        try:
            period = Period.objects.get(Q(pk=period_id))
            gameplayer = GamePlayer.objects.get(pk=user.pk)
        except ObjectDoesNotExist:
            raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)
        tokens = _get_player_tokens(gameplayer.pk, period.pk)
        arrs = tokens.split(',')
        if text:
            tmp = []
            # exact_match_list = []
            # for row in arrs:
            #     if row == text:
            #         exact_match_list.append(row)
            for row in arrs:
                index = row.find(text)
                if index != -1:
                    tmp.append((index, row))
            from operator import itemgetter
            tmp = sorted(tmp, key=itemgetter(0))
            fuzzy_match_list = [row[1] for row in tmp]
            return fuzzy_match_list
        else:
            return arrs


class PopPrizeDialog(generics.ListAPIView):
    """弹出一个中奖对话框"""

    permission_classes = (IsGamePlayer,)

    @get_require_check([])
    def get(self, request, *args, **kwargs):
        user = request.user
        return CacheUtil.dialog_pop(user.pk)


class GetHeadLine(generics.ListAPIView):
    """获取一个头条"""

    @get_require_check([])
    def get(self, request, *args, **kwargs):
        headline = CacheUtil.get_headline()
        return {"headline": headline}


######################### 下面的暂时未使用###############


class QueryPeriodByRewardType(generics.ListAPIView):
    """根据开奖类型查询周期"""

    @get_require_check([])
    @transaction.atomic
    def get(self, request, *args, **kwargs):
        order_type = request.query_params.get('order_type', None)
        reward_type = int(request.query_params.get('reward_type'))

        l = [code_set.CommodityRewardCode.B_VALUE[0],
             code_set.CommodityRewardCode.MIAOKAI[0], 3]
        if not order_type:
            order_type = 6
        if reward_type not in l:
            raise AppError(*code_set.GlobalErrorCode.PARAM_ERROR)

        if reward_type == 3:
            periods = PeriodSerializer(_period_query(int(order_type)),
                                       many=True).data
        else:
            periods = PeriodSerializer(
                _by_value_data(reward_type, int(order_type)), many=True).data
        return periods


def _period_query(order_type):
    """
    (最热1 最快2 最新3 高价4 低价5 推荐6)
    :return:
    """
    queryset = Period.objects.filter(
        Q(status=code_set.PeriodStatusCode.PARTICIPATING[0]))
    if order_type == 1:
        queryset = queryset.order_by('-commodity__count')
    if order_type == 2:
        queryset = queryset.order_by('-rate')
    if order_type == 3:
        queryset = queryset.order_by('-create_time')
    if order_type == 4:
        queryset = queryset.order_by('-target_amounts')
    if order_type == 5:
        queryset = queryset.order_by('target_amounts')
    if order_type == 6:
        queryset = queryset.order_by('commodity__show_index')
    return queryset


def _by_value_data(reward_type, order_type):
    """存在b值的数据"""
    commodity_ids = Commodity.objects.filter(
        reward_type=reward_type).values_list(
        'pk', flat=True)
    commodity_ids = [row for row in commodity_ids]

    queryset = Period.objects.filter(
        Q(status=code_set.PeriodStatusCode.PARTICIPATING[0]) &
        Q(commodity__pk__in=commodity_ids))
    if order_type == 1:
        queryset = queryset.order_by('-commodity__count')
    if order_type == 2:
        queryset = queryset.order_by('-rate')
    if order_type == 3:
        queryset = queryset.order_by('-create_time')
    if order_type == 4:
        queryset = queryset.order_by('-target_amounts')
    if order_type == 5:
        queryset = queryset.order_by('target_amounts')
    if order_type == 6:
        queryset = queryset.order_by('commodity__show_index')
    return queryset


class PeriodQueryByPk(generics.ListCreateAPIView):
    """周期查询"""

    @get_require_check(["period_pk"])
    def get(self, request, *args, **kwargs):
        period_pk = int(request.query_params.get("period_pk"))
        period_data = CacheUtil.get_period_data(period_pk)
        if period_data:
            period_data = json.loads(period_data)
        else:
            period = Period.objects.get(pk=period_pk)
            period_data = PeriodSerializer(period).data
            # if period.status == code_set.PeriodStatusCode.COUNTDOWNING[0]:
            #     period_data["countdown_millisecond"] = \
            #         CacheUtil.get_pttl_expire(period_pk)
            if period.status == code_set.PeriodStatusCode.REWARDED[0]:
                CacheUtil.set_period_data(period_pk, period_data)
        return period_data


class FinishedPeriodQuery(generics.ListCreateAPIView):
    """完成的周期查询"""

    @get_require_check(["last_open_index"])
    def get(self, request, *args, **kwargs):
        last_open_index = int(request.query_params.get("last_open_index"))

        if last_open_index < 0 or last_open_index > 999999999:
            raise AppError(*code_set.GlobalErrorCode.PARAM_ERROR)

        queryset = Period.objects.filter(
            Q(status=code_set.PeriodStatusCode.REWARDED[0]))

        queryset = queryset.filter(
            Q(open_index__lt=last_open_index)).order_by('-reward_time')
        paginator = Paginator(queryset, 10)
        queryset = paginator.page(1)

        return PeriodSerializer(queryset, many=True).data


class TrendMap(generics.ListAPIView):
    """走势图"""

    @get_require_check([])
    def get(self, request, *args, **kwargs):
        commodity_pk = request.query_params["commodity_pk"]
        try:
            commodity = Commodity.objects.get(pk=commodity_pk)
        except ObjectDoesNotExist:
            raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)
        # 每部分数量
        part_count = commodity.snatch_treasure_amounts / 5
        y_axis = [0, part_count * 1, part_count * 2, part_count * 3,
                  part_count * 4, part_count * 5 + (
                          commodity.snatch_treasure_amounts % 5)]
        y_axis.reverse()

        periods = Period.objects.filter(Q(commodity=commodity)).order_by('-pk')
        x_axis = []
        for row in periods:
            x_axis.append(row.period_no)

        dpr_records = DuoBaoParticipateRecord.objects.filter(
            Q(period__in=periods) & Q(is_win_prize=True)).order_by(
            '-period_id')
        trend_amp = []
        for row in dpr_records:
            trend_amp.append({
                "period_no": row.period.period_no,
                "residue_ren_ci": row.residue
            })
        commodity_data = TrendMapSerializer(commodity).data
        images = Imgs.objects.filter(
            Q(resource_type=code_set.ImgResourceType.COMMODITY[0]) & Q(
                relation_pk=commodity.pk))
        commodity_data['commodity_images'] = \
            ImagesSerializer(images, many=True).data

        data = {
            "y_axis_data": y_axis,
            "x_axis_data": x_axis,
            "trend_amp_data": trend_amp,
            "commodity_data": commodity_data
        }
        return data


class ParticipateByPeriod(generics.ListAPIView):
    """根据周期查询参与记录"""

    @get_require_check(["period_pk"])
    def get(self, request, *args, **kwargs):
        period_id = int(request.query_params.get('period_pk'))
        participates = DuoBaoParticipateRecord.objects.filter(
            Q(period__id=period_id)).order_by('-time')
        participate_record_data = DprSerializer(participates,
                                                many=True).data
        return participate_record_data


class GetPeriodIdByCommodityId(generics.ListAPIView):
    """获取参与状态中的周期id"""

    @get_require_check([])
    def get(self, request, *args, **kwargs):
        commodity_id = request.query_params.get('commodity_id')
        try:
            period = Period.objects.get(Q(commodity__id=commodity_id) &
                                        Q(status=
                                          code_set.PeriodStatusCode.PARTICIPATING[
                                              0]))
            period_pk = period.pk
        except ObjectDoesNotExist:
            raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)
        return {"period_pk": period_pk}
