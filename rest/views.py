# coding:utf-8
import django_filters
from rest_framework import filters
from rest_framework import generics

from models import GoodsDeliverRecord
from utils import framework
from shopping_user.permissions import IsAdministratorPermission
from serializers import GoodsDeliverListSerializer
from shopping_user.paginations import LargeResultsSetPagination


class DeliveryGoodsFilter(django_filters.FilterSet):
    status = django_filters.NumberFilter(name="status")

    class Meta:
        model = GoodsDeliverRecord
        fields = []


class DeliveryGoodsList(generics.ListAPIView):
    """实物发货列表"""
    queryset = GoodsDeliverRecord.objects.all()
    serializer_class = GoodsDeliverListSerializer
    permission_classes = (IsAdministratorPermission,)
    filter_backends = (
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter)
    filter_class = DeliveryGoodsFilter
    pagination_class = LargeResultsSetPagination

    @framework.get_require_check([])
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs).data


class DeliveryGoodsDetail(generics.RetrieveUpdateAPIView):
    """实物发货列表详情"""

    queryset = GoodsDeliverRecord.objects.all()
    serializer_class = GoodsDeliverListSerializer
    permission_classes = (IsAdministratorPermission,)

    @framework.get_require_check([])
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs).data

    @framework.get_require_check([])
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs).data

    @framework.post_require_check([])
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs).data