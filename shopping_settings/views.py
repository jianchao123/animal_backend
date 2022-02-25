# coding:utf-8

# django 包
import django_filters
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist

# rest framework 包
from rest_framework import generics, filters
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from models import CommodityType, BuyChannel, Notice, Banner, Area, PayType, \
    PayMoneyCtl, PayAccountsConf, CommonParamConf, ShippingAddress, \
    PayChannel, SectionMoneyRecord, FeesUseRecord

from serializers import CommodityTypeSerializer, BuyChannelSerializer, \
    NoticeSerializer, BannerSerializer, AreaSerializer, PayTypeSerializer, \
    PayAccountsConfSerializer, PayMoneyCtlSerializer, \
    CommonParamConfSerializer, ShippingAddressSerializer, \
    PayChannelSerializer, SectionMoneyRecordSerializer, FeesUseRecordSerializer
from shopping_user.permissions import IsAdministratorPermission, IsGamePlayer
from paginations import LargeResultsSetPagination, StandardResultsSetPagination

from utils.framework import post_require_check, get_require_check
from utils import code_set
from utils import framework
from utils.AppError import AppError
import logging
logger = logging.getLogger(__name__)


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'commoditytypes': reverse('commoditytypes', request=request,
                                  format=format),
        'buychannels': reverse('buychannels', request=request, format=format),
        'notices': reverse('notices', request=request, format=format),
        'banners': reverse('banners', request=request, format=format),
    })


class CommodityTypeList(generics.ListCreateAPIView):
    queryset = CommodityType.objects.all()
    serializer_class = CommodityTypeSerializer
    permission_classes = (IsAdministratorPermission,)
    pagination_class = LargeResultsSetPagination

    @get_require_check([])
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs).data

    @post_require_check([])
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs).data


class CommodityTypeDetail(generics.RetrieveUpdateAPIView):
    queryset = CommodityType.objects.all()
    serializer_class = CommodityTypeSerializer
    permission_classes = (IsAdministratorPermission,)

    @get_require_check([])
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs).data

    @post_require_check([])
    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs).data

    @post_require_check([])
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs).data


class BuyChannelList(generics.ListCreateAPIView):
    queryset = BuyChannel.objects.all()
    serializer_class = BuyChannelSerializer
    permission_classes = (IsAdministratorPermission,)
    pagination_class = LargeResultsSetPagination

    @get_require_check([])
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs).data

    @post_require_check([])
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs).data


class BuyChannelDetail(generics.RetrieveUpdateAPIView):
    queryset = BuyChannel.objects.all()
    serializer_class = BuyChannelSerializer
    permission_classes = (IsAdministratorPermission,)

    @get_require_check([])
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs).data

    @post_require_check([])
    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs).data

    @post_require_check([])
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs).data


class NoticeList(generics.ListCreateAPIView):
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer
    permission_classes = (IsAdministratorPermission,)
    pagination_class = LargeResultsSetPagination

    @get_require_check([])
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs).data

    @post_require_check([])
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs).data


class NoticeDetail(generics.RetrieveUpdateAPIView):
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer
    permission_classes = (IsAdministratorPermission,)

    @get_require_check([])
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs).data

    @post_require_check([])
    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs).data

    @post_require_check([])
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs).data


class BannerList(generics.ListCreateAPIView):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
    permission_classes = (IsAdministratorPermission,)
    pagination_class = LargeResultsSetPagination

    @get_require_check([])
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs).data

    @post_require_check([])
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs).data


class BannerDetail(generics.RetrieveUpdateAPIView):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
    permission_classes = (IsAdministratorPermission,)

    @get_require_check([])
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs).data

    @post_require_check([])
    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs).data

    @post_require_check([])
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs).data


class AreaFilter(django_filters.FilterSet):
    pid = django_filters.NumberFilter(
        name="pid")
    level = django_filters.NumberFilter(
        name="level")

    class Meta:
        model = Area
        fields = []


class AreaList(generics.ListAPIView):
    queryset = Area.objects.all()
    serializer_class = AreaSerializer
    filter_backends = (
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,)
    filter_class = AreaFilter
    pagination_class = StandardResultsSetPagination

    @get_require_check([])
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs).data


class PayTypeList(generics.ListCreateAPIView):
    """支付类型"""
    queryset = PayType.objects.all()
    serializer_class = PayTypeSerializer
    permission_classes = (IsAdministratorPermission,)
    filter_backends = (
    django_filters.rest_framework.DjangoFilterBackend, filters.OrderingFilter)

    @get_require_check([])
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs).data

    @post_require_check([])
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs).data


class PayTypeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = PayType.objects.all()
    serializer_class = PayTypeSerializer
    permission_classes = (IsAdministratorPermission,)

    @get_require_check([])
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs).data

    @post_require_check([])
    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs).data

    @post_require_check([])
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs).data

    @post_require_check([])
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs).data


class PayChannelList(generics.ListCreateAPIView):
    """支付通道"""

    queryset = PayChannel.objects.all()
    serializer_class = PayChannelSerializer
    permission_classes = (IsAdministratorPermission,)

    @get_require_check([])
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs).data

    @post_require_check([])
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs).data


class PayChannelDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = PayChannel.objects.all()
    serializer_class = PayChannelSerializer
    permission_classes = (IsAdministratorPermission,)

    @get_require_check([])
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs).data

    @post_require_check([])
    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs).data

    @post_require_check([])
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs).data

    @post_require_check([])
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs).data


class PayAccountsConfList(generics.ListCreateAPIView):
    """支付账户配置"""
    queryset = PayAccountsConf.objects.all()
    serializer_class = PayAccountsConfSerializer
    permission_classes = (IsAdministratorPermission,)

    @get_require_check([])
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs).data

    @post_require_check([])
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs).data


class PayAccountsConfDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = PayAccountsConf.objects.all()
    serializer_class = PayAccountsConfSerializer
    permission_classes = (IsAdministratorPermission,)

    @get_require_check([])
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs).data

    @post_require_check([])
    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs).data

    @post_require_check([])
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs).data

    @post_require_check([])
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs).data


class PayMoneyCtlList(generics.ListCreateAPIView):
    """支付金额控制"""
    queryset = PayMoneyCtl.objects.all()
    serializer_class = PayMoneyCtlSerializer
    permission_classes = (IsAdministratorPermission,)

    @get_require_check([])
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs).data

    @post_require_check([])
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs).data


class PayMoneyCtlDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = PayMoneyCtl.objects.all()
    serializer_class = PayMoneyCtlSerializer
    permission_classes = (IsAdministratorPermission,)

    @get_require_check([])
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs).data

    @post_require_check([])
    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs).data

    @post_require_check([])
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs).data

    @post_require_check([])
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs).data


class CommonParamConfList(generics.ListCreateAPIView):
    """公共参数配置"""

    queryset = CommonParamConf.objects.all()
    serializer_class = CommonParamConfSerializer
    permission_classes = (IsAdministratorPermission,)

    @get_require_check([])
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs).data

    @post_require_check([])
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs).data


class CommonParamConfDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = CommonParamConf.objects.all()
    serializer_class = CommonParamConfSerializer
    permission_classes = (IsAdministratorPermission,)

    @get_require_check([])
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs).data

    @post_require_check([])
    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs).data

    @post_require_check([])
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs).data

    @post_require_check([])
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs).data


class ShippingAddresses(generics.ListCreateAPIView):
    """用户收货地址 app"""

    queryset = ShippingAddress.objects.all()
    serializer_class = ShippingAddressSerializer
    permission_classes = (IsGamePlayer,)

    @get_require_check([])
    def get(self, request, *args, **kwargs):
        shippingaddresses = \
            ShippingAddress.objects.filter(Q(player_id=request.user.pk))
        return ShippingAddressSerializer(shippingaddresses, many=True).data

    @post_require_check([])
    def post(self, request, *args, **kwargs):
        if request.data["recipents_address"].find('script') != -1 or \
            request.data["recipents_phone"].find('script') != -1 or \
                request.data["recipents_name"].find('script') != -1:
            raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)
        user = request.user
        if request.data["is_default"]:
            ShippingAddress.objects.filter(Q(player__pk=user.pk)).update(
                is_default=False)
        return self.create(request, *args, **kwargs).data


class ShippingAddressDetail(generics.RetrieveUpdateAPIView):
    """用户收货地址详情 app"""

    queryset = ShippingAddress.objects.all()
    serializer_class = ShippingAddressSerializer
    permission_classes = (IsGamePlayer,)

    @get_require_check([])
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs).data

    @post_require_check([])
    def patch(self, request, *args, **kwargs):
        user = request.user
        if request.data["recipents_address"].find('script') != -1 or \
            request.data["recipents_phone"].find('script') != -1 or \
                request.data["recipents_name"].find('script') != -1:
            raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)
        if request.data["is_default"]:
            ShippingAddress.objects.filter(Q(player__pk=user.pk)).update(
                is_default=False)
        return self.partial_update(request, *args, **kwargs).data


class BasicConf(generics.ListAPIView):
    """移动端基础配置"""

    @get_require_check([])
    def get(self, request, *args, **kwargs):
        # 域名
        try:
            common_param_conf = \
                CommonParamConf.objects.get(Q(conf_key="domain"))
            domain = common_param_conf.conf_value
            common_param_conf = \
                CommonParamConf.objects.get(Q(conf_key="pay_page_url"))
            pay_page_url = common_param_conf.conf_value
            common_param_conf = CommonParamConf.objects.get(
                Q(conf_key="ios_download_link"))
            ios_download_link = common_param_conf.conf_value
            common_param_conf = CommonParamConf.objects.get(
                Q(conf_key="android_download_link"))
            android_download_link = common_param_conf.conf_value
        except ObjectDoesNotExist:
            domain = ""

        # 是否显示充值
        try:
            common_param_conf = \
                CommonParamConf.objects.get(Q(conf_key="is_show_deposit"))
            is_show_deposit = common_param_conf.conf_value
        except ObjectDoesNotExist:
            is_show_deposit = 0

        data = {
            "domain": domain,
            "pay_page_url": pay_page_url,
            "is_show_deposit": is_show_deposit,
            "ios_download_link": ios_download_link,
            "android_download_link": android_download_link
        }
        return data


class SectionMoneyRecordView(generics.ListCreateAPIView):
    """金额区间"""

    queryset = SectionMoneyRecord.objects.all()
    serializer_class = SectionMoneyRecordSerializer
    permission_classes = (IsAdministratorPermission,)

    @get_require_check([])
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs).data

    @post_require_check([])
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs).data


class SectionMoneyRecordDetailView(generics.RetrieveUpdateDestroyAPIView):

    queryset = SectionMoneyRecord.objects.all()
    serializer_class = SectionMoneyRecordSerializer
    permission_classes = (IsAdministratorPermission,)

    @get_require_check([])
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs).data

    @post_require_check([])
    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs).data

    @post_require_check([])
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs).data

    @post_require_check([])
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs).data


class FeesUseRecordView(generics.ListCreateAPIView):
    """费用记录
    page 1
    limit 10 limit只能为10
    """

    queryset = FeesUseRecord.objects.all()
    serializer_class = FeesUseRecordSerializer
    permission_classes = (IsAdministratorPermission,)
    pagination_class = LargeResultsSetPagination

    @get_require_check([])
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs).data

    @post_require_check([])
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs).data