# coding:utf-8
from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns

from views import CommodityList, CommodityDetail, api_root, Participate, \
    NewDrawLottery, Homepage, CommodityDetailPage, RecentlyWinPrizeRecords, \
    PreviousPeriod, RecentlyParticipateRecords, PrizeRecords, \
    OrderList, WinPrizeOrder, AppOrderRecords, QueryTokens, PopPrizeDialog, \
    CommodityTag, PeriodByTag, UploadFileToQiniu, ModifyAppShowIndex, \
    CountdownAndParticipating, QueryParticipatePlayer, AppointWinnerView, \
    CurrentPeriodParticipates, \
    TrendMap, PeriodQueryByPk, FinishedPeriodQuery, GetPeriodIdByCommodityId, \
    QueryPeriodByRewardType, ParticipateByPeriod, GetHeadLine

urlpatterns = format_suffix_patterns([
    url(r'^$', api_root),
    # ################################# APP #################################
    # 主页
    url(r'^homepage/$', Homepage.as_view(), name='homepage'),
    # 商品分类
    url(r'^commoditytag/$', CommodityTag.as_view(), name='commoditytag'),
    # 分类查询
    url(r'^periodbytag/$', PeriodByTag.as_view(), name='periodbytag'),
    # 商品详情页
    url(r'^commoditydetailpage/$', CommodityDetailPage.as_view(),
        name='commoditydetailpage'),
    # 本期参与记录
    url(r'^currentperiodparticipates/$', CurrentPeriodParticipates.as_view(),
        name='currentperiodparticipates'),
    # 往期揭晓
    url(r'^previousperiod/$', PreviousPeriod.as_view(), name='previousperiod'),
    # 最新揭晓
    url(r'^newdrawlottery/$', NewDrawLottery.as_view(), name="newdrawlottery"),
    # 最近参与记录
    url(r'^recentlyparticipaterecords/$', RecentlyParticipateRecords.as_view(),
        name="recentlyparticipaterecords"),
    # 最近中奖记录
    url(r'^recentlywinprizerecords/$', RecentlyWinPrizeRecords.as_view(),
        name="recentlywinprizerecords"),
    # 订单记录
    url(r'^apporderrecords/$', AppOrderRecords.as_view(),
        name="apporderrecords"),
    # 中奖记录
    url(r'^prizerecords/$', PrizeRecords.as_view(), name="prizerecords"),
    # 购买人次
    url(r'^participate/$', Participate.as_view(), name="participate"),
    # 查询夺宝号
    url(r'^querytokens/$', QueryTokens.as_view(), name='query_tokens'),
    # 消费一个中奖弹出框
    url(r'^popprizedialog/$', PopPrizeDialog.as_view(),
        name='popprizedialog'),
    # 获取一个头条
    url(r'^headline/$', GetHeadLine.as_view(), name='headline'),

    # ################################# BACKEND #############################
    # 商品上移下移
    url(r'^modifyappshowindex/$', ModifyAppShowIndex.as_view(),
        name="modifyappshowindex"),

    # 商品列表
    url(r'^commoditys/$', CommodityList.as_view(),
        name="commoditys"),
    # 商品详情
    url(r'^commodity/(?P<pk>[0-9]+)/$', CommodityDetail.as_view(),
        name="commoditydetail"),
    # 实时购买列表
    url(r'^orderlist/$', OrderList.as_view(), name="orderlist"),
    # 中奖订单列表
    url(r'^winprizeorder/$', WinPrizeOrder.as_view(), name="winprizeorder"),
    # 上传
    url(r'^upload/$', UploadFileToQiniu.as_view(), name="upload"),
    # 查询参与中和倒计时中的周期
    url(r'^countdownandparticipating/$', CountdownAndParticipating.as_view(),
        name="countdownandparticipating"),
    # 查询周期中的参与人
    url(r'^queryparticipateplayer/$', QueryParticipatePlayer.as_view(),
        name="queryparticipateplayer"),
    # 指定中奖人
    url(r'^appointwinnerview/$', AppointWinnerView.as_view(),
        name="appointwinnerview"),
    # 手动给机器人晾单

])
