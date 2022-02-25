# coding:utf-8
from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns

from views import RecycleBusinessmanHomepage, DcDepositRecordList, \
    AgencyRecordList, RecycleRecordList, RecycleStatistics, \
    RecycleBusinessmanList, RecycleBusinessmanDetail, UserConsignees, \
    UpdateUserConsignees, BusinessmanApplyForWithdraw, \
    AuditApplyForRecord, WithdrawRecordList, BusinessmanRecyclePrice, \
    BusinessmanModifyPwd, InviteRecordList

urlpatterns = format_suffix_patterns([
    # ################################# APP #################################
    # 收货人列表
    url(r'^userconsignees/$', UserConsignees.as_view(),
        name="userconsignees"),
    # 更新收货人
    url(r'^updateuserconsignees/$', UpdateUserConsignees.as_view(),
        name="updateuserconsignees"),

    # ################################# BACKEND #############################
    # 回收商主页
    url(r'^homepage/$', RecycleBusinessmanHomepage.as_view(),
        name="homepage"),
    # 代充记录
    url(r'^dcdeposit/$', DcDepositRecordList.as_view(),
        name="dcdeposit"),
    # 代理记录列表
    url(r'^agencyrecordlist/$', AgencyRecordList.as_view(),
        name="agencyrecordlist"),
    # 回收记录列表
    url('^recyclerecordlist/$', RecycleRecordList.as_view(),
        name="recyclerecordlist"),
    # 回收统计
    url('^recyclestatistics/$', RecycleStatistics.as_view(),
        name="recyclestatistics"),
    # 回收商列表
    url(r'^recyclebusinessmanlist/$', RecycleBusinessmanList.as_view(),
        name="recyclebusinessmanlist"),
    # 回收商详情
    url(r'^recyclebusinessmandetail/(?P<pk>[0-9]+)/$',
        RecycleBusinessmanDetail.as_view(),
        name="recyclebusinessmandetail"),
    # 申请提现
    url(r'^applyforwithdraw/$', BusinessmanApplyForWithdraw.as_view(),
        name='applyforwithdraw'),
    # 审核申请
    url(r'^auditapplyforrecord/$', AuditApplyForRecord.as_view(),
        name="auditapplyforrecord"),
    # 提现列表
    url('^withdrawlist/$', WithdrawRecordList.as_view(), name='withdrawlist'),
    # 回收商每日回收金额
    url(r'^everydayrecycleprice/$', BusinessmanRecyclePrice.as_view(),
        name='everydayrecycleprice'),
    # 回收商修改自己的密码
    url(r'^modifypwd/$', BusinessmanModifyPwd.as_view(), name='modifypwd'),
    # 邀请记录
    url(r'^inviterecordlist/$', InviteRecordList.as_view(),
        name='inviterecordlist'),

])
