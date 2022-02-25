# coding:utf-8
from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns

from views import DeliveryGoodsList, DeliveryGoodsDetail

urlpatterns = format_suffix_patterns([
    url(r'^deliverygoodslist/$', DeliveryGoodsList.as_view(),
        name="deliverygoodslist"),

    url(r'^deliverygoods/(?P<pk>[0-9]+)/$', DeliveryGoodsDetail.as_view(),
        name="deliverygoods"),
])
