# coding:utf-8
import django_filters
from django.db.models import ObjectDoesNotExist

from rest_framework import generics
from rest_framework import filters
from rest_framework import permissions

from models import PresentsRecord, SunTheOrder, Praise
from shopping_user.models import GamePlayer
from shopping_user.permissions import IsAdministratorPermission, IsGamePlayer
from serializers import PresentsRecordSerializer, SunTheOrderSerializer, \
    PraiseSerializer
from paginations import LargeResultsSetPagination
from tasks import present_sms

from utils import framework
from utils.AppError import AppError
from utils import code_set
from utils.cache_util import CacheUtil


class PresentsFilter(django_filters.FilterSet):
    presents_type = django_filters.NumberFilter(name='presents_type')

    class Meta:
        model = PresentsRecord
        fields = []


class PresentsRecordList(generics.ListCreateAPIView):
    """赠送记录"""
    serializer_class = PresentsRecordSerializer
    permission_classes = (IsAdministratorPermission,)
    queryset = PresentsRecord.objects.all()
    pagination_class = LargeResultsSetPagination
    ordering_fields = ('present_time',)

    filter_backends = (
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,)
    filter_class = PresentsFilter

    @framework.get_require_check([])
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs).data

    @framework.post_require_check([])
    def post(self, request, *args, **kwargs):
        user = request.user
        phone_str = request.data["phone_str"]
        amounts = int(request.data["amounts"])
        phones = phone_str.split("\n")
        players = GamePlayer.objects.filter(phone__in=phones)
        filtered_phone = []
        for row in players:
            filtered_phone.append(row.phone)

        present_sms.apply_async(args=[filtered_phone, amounts, user.id],
                                exchange='activity',
                                routing_key="presents")
        return {"phones": ",".join(filtered_phone)}


# ################################## mobile ################################


class SunTheOrderFilter(django_filters.FilterSet):
    last_pk = django_filters.NumberFilter(name='id')

    class Meta:
        model = SunTheOrder
        fields = []


class SunTheOrderList(generics.ListCreateAPIView):
    """晒单"""

    serializer_class = SunTheOrderSerializer
    permission_classes = (permissions.AllowAny,)
    queryset = SunTheOrder.objects.all()

    @framework.get_require_check([])
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs).data

    @framework.post_require_check([])
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs).data


class PraiseCreate(generics.CreateAPIView):
    """点赞"""

    serializer_class = PraiseSerializer
    permission_classes = (IsGamePlayer,)
    queryset = Praise.objects.all()

    @framework.post_require_check([])
    def post(self, request, *args, **kwargs):
        user = request.user
        praise_player_pk = user.pk
        sun_the_order_pk = int(request.data["sun_the_order_pk"])

        try:
            praise = Praise.objects.get(sun_the_order_id=sun_the_order_pk,
                                        praise_player_id=praise_player_pk)
            praise.delete()
        except ObjectDoesNotExist:
            Praise.objects.create(sun_the_order_id=sun_the_order_pk,
                                  praise_player_id=praise_player_pk)
        return {}


class LiangDan(generics.ListAPIView):
    """获取机器人登陆密码"""

    @framework.get_require_check([])
    def get(self, request, *args, **kwargs):
        random_number = int(request.query_params["random_number"])
        if random_number == "asd123":
            player = GamePlayer.objects.filter(is_robot=1).order_by('?').first()
            CacheUtil.push_robot_phone_to_set(player.id)
            return {"username": player.phone, "password": "kIhHAWexFy7pU8qM"}
        return {}