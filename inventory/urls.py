# coding:utf-8
from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns

from views import CardList, CardDeliveryRecordList, \
    CardInventoriesList, CardEntryRecordList, \
    CardInventory, CardEntryRecordDetail, ImportCard, CardInventoriesDetail

urlpatterns = format_suffix_patterns([
    # ############################## BACKEND ##################################
    # 卡密列表
    url(r'^cards/$', CardList.as_view(), name="cards"),
    # 卡密使用记录
    url(r'^carddeliveryrecords/$', CardDeliveryRecordList.as_view(),
        name="carddeliveryrecords"),
    # 卡密种类记录
    url(r'^cardinventories/$', CardInventoriesList.as_view(),
        name="cardinventories"),
    # 卡密种类详情
    url(r'^cardinventoriesdetail/(?P<pk>[0-9]+)/$',
        CardInventoriesDetail.as_view(),
        name="cardinventoriesdetail"),

    # 卡密入库记录
    url(r'^cardentryrecords/$', CardEntryRecordList.as_view(),
        name="cardentryrecords"),
    # 卡密入库详情
    url(r'^cardentryrecorddetail/(?P<pk>[0-9]+)/$',
        CardEntryRecordDetail.as_view(),
        name="cardentryrecorddetail"),
    # 导入卡密
    url(r'^importcard/$', ImportCard.as_view(), name="importcard"),
    # 卡密库存信息
    url(r'^cardinventoryinfo/$', CardInventory.as_view(),
        name="cardinventoryinfo")
    # #############################  APP  ###############################
])
