# coding:utf-8
from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from views import RecycleBusinessDeposit, \
    DepositRecordList, PrizeRecords, PrizeRecordEdit

urlpatterns = format_suffix_patterns([

    # ################################# backend ###############################
    # 代充
    url(r'^dcdeposit/$', RecycleBusinessDeposit.as_view(),
        name="recyclebusiness"),
    # 充值列表
    url(r'^depositlist/$', DepositRecordList.as_view(),
        name="depositlist"),
    # 虚拟订单
    url(r'^virtualorders/$', PrizeRecords.as_view(), name="virtualorders"),
    url(r'^virtualorderedit/$', PrizeRecordEdit.as_view(),
        name="virtualorderedit")
])
