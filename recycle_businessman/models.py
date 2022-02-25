# coding:utf-8
from __future__ import unicode_literals

from django.db import models

from snatch_treasure.models import Period
from shopping_user.models import GamePlayer, UserProfileBasic
from snatch_treasure.models import Commodity


class RecycleBusinessman(UserProfileBasic):
    """回收商"""
    is_tuple = (
        (1, u"是"),
        (0, u"否"),
    )

    is_recycle = models.IntegerField(choices=is_tuple, default=1,
                                     blank=True, null=True,
                                     verbose_name=u"是否可以回收")
    is_login = models.IntegerField(choices=is_tuple, default=1,
                                   blank=True, null=True,
                                   verbose_name=u"是否能登陆回收商后台")

    invite_code = models.CharField(max_length=16, blank=True, null=True,
                                   verbose_name=u"邀请码")
    invite_qr_code = models.CharField(max_length=128, blank=True, null=True,
                                      verbose_name=u"邀请二维码")

    deposit_back_rate = models.DecimalField(max_digits=8,
                                            decimal_places=2,
                                            blank=True,
                                            null=True,
                                            verbose_name=u"代充返点")
    recycle_back_rate = models.DecimalField(max_digits=8,
                                            decimal_places=2,
                                            blank=True,
                                            null=True,
                                            verbose_name=u"收货返点")
    invite_back_rate = models.DecimalField(max_digits=8,
                                           decimal_places=2,
                                           blank=True,
                                           null=True,
                                           verbose_name=u"邀请返点(流水)")
    # 可删除
    balance_cny = models.DecimalField(max_digits=16,
                                      decimal_places=6,
                                      blank=True,
                                      null=True,
                                      verbose_name=u"回收商余额")

    @property
    def get_nickname(self):
        if self.nickname:
            return self.nickname
        else:
            return self.phone

    def __unicode__(self):
        return u"{}[{}],[id={}]".format(
            self.phone, self.nickname, self.pk)

    class Meta:
        db_table = u"recycle_businessman"
        verbose_name = u"回收商"
        verbose_name_plural = verbose_name


class RecycleRecord(models.Model):
    """回收记录"""
    recycle_period_no = models.CharField(max_length=32, blank=True, null=True,
                                         verbose_name=u"期号")
    recycle_price = models.DecimalField(max_digits=10, decimal_places=2,
                                        blank=True,
                                        null=True, verbose_name=u"回收价格")

    recycle_trade_no = models.CharField(max_length=128, blank=True, null=True,
                                        verbose_name=u"交易号")
    period = models.ForeignKey(Period, blank=True, null=True,
                               related_name=u"rr_period_set",
                               verbose_name=u"周期")
    recycle_businessman = models.ForeignKey(RecycleBusinessman, blank=True,
                                            null=True,
                                            related_name=u"rr_rb_set",
                                            verbose_name=u"回收商")
    commodity = models.ForeignKey(Commodity,
                                  related_name=u"rr_commodity_set",
                                  blank=True, null=True,
                                  verbose_name=u"商品")
    recycle_time = models.DateTimeField(blank=True, null=True,
                                        auto_now_add=True,
                                        verbose_name=u"回收时间")

    is_ret = models.BooleanField(default=False, verbose_name=u"是否已返利")

    def __unicode__(self):
        return u"回收交易号={}".format(self.recycle_trade_no)

    class Meta:
        db_table = u"recycle_record"
        verbose_name = u"回收记录"
        verbose_name_plural = verbose_name


class InviteRecord(models.Model):
    """邀请记录"""

    recycle_businessman = models.ForeignKey(RecycleBusinessman, blank=True,
                                            null=True,
                                            related_name=u"ir_rb_set",
                                            verbose_name=u"回收商")
    invite_player = models.ForeignKey(GamePlayer, blank=True, null=True,
                                      related_name=u"ir_ip_set",
                                      verbose_name=u"邀请的用户")
    invite_time = models.DateTimeField(blank=True, null=True,
                                       auto_now_add=True,
                                       verbose_name=u"邀请时间")

    def __unicode__(self):
        return u"邀请的用户={}, {}". \
            format(self.invite_player.phone, self.invite_player.pk)

    class Meta:
        db_table = u"invite_record"
        verbose_name = u"邀请记录"
        verbose_name_plural = verbose_name


class UserConsignee(models.Model):
    """玩家的收货人"""
    flag_tuple = (
        (1, u"回收号"),
        (2, u"兑换号")
    )

    player = models.ForeignKey(GamePlayer, related_name=u"uci_player_set",
                               blank=True, null=True,
                               verbose_name=u"玩家")
    recycle_businessman = models.ForeignKey(RecycleBusinessman, blank=True,
                                            null=True,
                                            related_name=u"uci_rb_set",
                                            verbose_name=u"回收商")
    consignee_name = models.CharField(max_length=16, blank=True, null=True,
                                      verbose_name="收货人名字")
    phone = models.CharField(max_length=16, blank=True, null=True,
                             verbose_name=u"号码")
    flag = models.IntegerField(choices=flag_tuple, blank=True, null=True,
                               default=1, verbose_name=u"状态")

    def __unicode__(self):
        return str(self.pk)

    class Meta:
        db_table = u"user_consignee"
        verbose_name = u"玩家的收货人"
        verbose_name_plural = verbose_name
