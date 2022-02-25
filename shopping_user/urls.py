# coding:utf-8
from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns

from views import GamePlayerList, SignUpGamePlayer, SendSignUpCode, \
    AdministratorList, AppSignIn, BackendSignIn, \
    AcceptPrize, UserInformation, UserCards, \
    AcceptPrizeInfo, GetQiniuToken, SendSignInCode, ModifyUserInfo, \
    SignOut, UpdateGamePlayer, QueryBusinessManInfo, QueryCodeQuery, \
    DeleteRobotPeriod

urlpatterns = format_suffix_patterns([

    url(r'^getqiniutoken/$', GetQiniuToken.as_view(), name="getqiniutoken"),
    # ################################# APP #################################
    # app登陆
    url(r'^app/signin/$', AppSignIn.as_view(), name="app-signin"),
    # 发送注册验证码
    url(r'^sendsignupcode/$', SendSignUpCode.as_view(),
        name="send-signup-code"),
    # 发送登陆验证码
    url(r'^sendsignincode/$', SendSignInCode.as_view(),
        name="send-signin-code"),
    # 注册玩家
    url(r'^signup/player/$', SignUpGamePlayer.as_view(), name="signup-player"),
    # 领奖
    url(r'^accept/prize/$', AcceptPrize.as_view(), name="accept-prize"),
    # 领奖信息
    url(r'^accept/prize/info/$', AcceptPrizeInfo.as_view(),
        name="accept-prize-info"),
    # 查询玩家
    url(r'^userinformation/$', UserInformation.as_view(),
        name="userinformation"),
    # 用户卡密
    url(r'^usercards/$', UserCards.as_view(),
        name="usercards"),
    # 修改用户信息
    url(r'^update/player/$', ModifyUserInfo.as_view(), name="updateplayer"),
    # 登出
    url(r'^signout/$', SignOut.as_view(), name="signout"),

    # ################################# BACKEND #############################
    # 查询卡商信息
    url(r'^businessman/info/$', QueryBusinessManInfo.as_view(),
        name="businessinfo"),

    # 后台登陆
    url(r'^backend/signin/$', BackendSignIn.as_view(), name="backend-signin"),
    # 查询玩家
    url(r'^players/$', GamePlayerList.as_view(), name="players"),
    # 更新玩家
    url(r"^updategameplayer/$", UpdateGamePlayer.as_view(),
        name="updategameplayer"),
    # 管理员
    url(r'^administrator/$', AdministratorList.as_view(),
        name="administrator"),
    # 查询code
    url(r'^querycode/$', QueryCodeQuery.as_view(), name='querycode'),

    # 删除全是机器人的周期
    url(r'^deleterobotperiod/$', DeleteRobotPeriod.as_view(),
        name="deleterobotperiod"),
])
