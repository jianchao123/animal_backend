# coding:utf-8
from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from views import PresentsRecordList, SunTheOrderList, PraiseCreate, LiangDan

urlpatterns = format_suffix_patterns([
    url(r'^presents/$', PresentsRecordList.as_view(), name="presents"),

    # ###############################  mobile  ##########################
    url(r'^suntheorders/$', SunTheOrderList.as_view(), name="suntheorders"),
    # 手动晾单
    url(r'^liangdan/$', LiangDan.as_view(), name="liangdan"),

    url(r'^praise/$', PraiseCreate.as_view(), name="praise"),
])
