# coding:utf-8
from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns

from views import CommodityTypeList, CommodityTypeDetail, \
    BuyChannelList, BuyChannelDetail, NoticeList, AreaList, \
    NoticeDetail, BannerList, BannerDetail, PayTypeList, PayAccountsConfList, \
    PayMoneyCtlList, PayTypeDetail, PayAccountsConfDetail, PayMoneyCtlDetail, \
    CommonParamConfList, CommonParamConfDetail, ShippingAddresses, \
    ShippingAddressDetail, PayChannelList, PayChannelDetail, BasicConf, \
    SectionMoneyRecordView, SectionMoneyRecordDetailView, FeesUseRecordView

urlpatterns = format_suffix_patterns([
    # ################################# APP #################################
    # 地址列表
    url(r'^shipping/address/$', ShippingAddresses.as_view(),
        name="shipping-address"),
    # 地址详情
    url(r'^shipping/address/(?P<pk>[0-9]+)/$', ShippingAddressDetail.as_view(),
        name="shipping-address-detail"),
    url(r'^basicconf/$', BasicConf.as_view(), name="basicconf"),

    # ################################# BACKEND #############################
    # 商品类型
    url(r'^commoditytypes/$', CommodityTypeList.as_view(),
        name="commoditytypes"),
    url(r'^commoditytype/(?P<pk>[0-9]+)/$',
        CommodityTypeDetail.as_view(),
        name="commoditytypedetail"),

    # 购买渠道
    url(r'^buychannels/$', BuyChannelList.as_view(),
        name="buychannels"),
    url(r'^buychannel/(?P<pk>[0-9]+)/$', BuyChannelDetail.as_view(),
        name="buychanneldetail"),

    # 公告
    url(r'^notices/$', NoticeList.as_view(),
        name="notices"),
    url(r'^notice/(?P<pk>[0-9]+)/$', NoticeDetail.as_view(),
        name="noticedetail"),

    # banner
    url(r'^banners/$', BannerList.as_view(),
        name="banners"),
    url(r'^banner/(?P<pk>[0-9]+)/$', BannerDetail.as_view(),
        name="bannerdetail"),
    # 省市区查询
    url(r'^arealist/$', AreaList.as_view(), name="arealist"),

    # 支付类型设置列表
    url(r'^paytypes/$', PayTypeList.as_view(), name="paytype"),
    url(r'^paytype/(?P<pk>[0-9]+)/$', PayTypeDetail.as_view(),
        name="paytype"),
    # 支付通道配置
    url(r'^paychannels/$', PayChannelList.as_view(), name="paychannels"),
    url(r'^paychannel/(?P<pk>[0-9]+)/$', PayChannelDetail.as_view(),
        name="paychannel-detail"),

    # 支付帐号配置
    url(r'^payaccountsconfs/$', PayAccountsConfList.as_view(),
        name="payaccountsconf"),
    url(r'^payaccountsconf/(?P<pk>[0-9]+)/$', PayAccountsConfDetail.as_view(),
        name="payaccountsconf"),
    # 支付金额控制器
    url(r'^paymoneyctls/$', PayMoneyCtlList.as_view(),
        name="paymoneyctl"),
    url(r'^paymoneyctl/(?P<pk>[0-9]+)/$', PayMoneyCtlDetail.as_view(),
        name="paymoneyctl"),
    # 公共参数配置
    url(r'^commonparamconflist/$', CommonParamConfList.as_view(),
        name="commonparamconflist"),
    url(r'^commonparamconfdetail/(?P<pk>[0-9]+)/$',
        CommonParamConfDetail.as_view(),
        name="commonparamconfdetail"),
    # 充值流水金额区间配置
    url(r'^sectionmoneyrecordview/$', SectionMoneyRecordView.as_view(),
        name="sectionmoneyrecordview"),
    url(r'^sectionmoneyrecorddetailview/(?P<pk>[0-9]+)/$',
        SectionMoneyRecordDetailView.as_view(),
        name="sectionmoneyrecorddetailview"),
    url(r'^feesuserecords/$', FeesUseRecordView.as_view(),
        name="feesuserecords")
])
