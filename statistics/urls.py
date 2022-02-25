# coding:utf-8

# coding:utf-8
from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from views import UserConsumeSituation, FinancialSheets, DepositStatistics, \
    TestStatistics

urlpatterns = format_suffix_patterns([
    # ################################# backend ###############################
    # 用户批次分析
    url(r'^userconsumesituation/$', UserConsumeSituation.as_view(),
        name="userconsumesituation"),
    # 财务表
    url(r'^financialsheets/$', FinancialSheets.as_view(),
        name="financialsheets"),
    # 充值统计
    url(r'^depositstatistics/$', DepositStatistics.as_view(),
        name="depositstatistics"),
    # Test
    url(r'^teststatistics/$', TestStatistics.as_view(), name="teststatistics")

])
