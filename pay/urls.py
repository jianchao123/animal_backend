
# coding:utf-8
from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from views import WxScanCodeDeposit, AlfNotify, GetPayMoney, VipNotify, AEightPay

urlpatterns = format_suffix_patterns([
    url(r'^alfnotify/$', AlfNotify.as_view(), name="alfnotify"),
    url(r'^vipnotify/$', VipNotify.as_view(), name="vipnotify"),
    url(r'^a_eightnotify/$', AEightPay.as_view(), name="a_eightnotify"),
    url(r'^wxscancodedepost/$', WxScanCodeDeposit.as_view(),
        name="wxscancodedepost"),
    url(r'^getpaymoney/$', GetPayMoney.as_view(), name="getpaymoney")
])


