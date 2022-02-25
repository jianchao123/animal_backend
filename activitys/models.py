# coding:utf-8
from __future__ import unicode_literals

from django.db import models
from shopping_user.models import GamePlayer, Administrator
from snatch_treasure.models import Period


class PresentsRecord(models.Model):
    """赠送记录"""
    presents_type_tuple = (
        (1, u"首充赠送"),
        (2, u"召回赠送"),
        (3, u"注册赠送")
    )

    amounts = models.IntegerField(blank=True,
                                  null=True, verbose_name=u"赠送金额")
    to_player = models.ForeignKey(GamePlayer,
                                  related_name=u"presents_tp_set",
                                  blank=True, null=True,
                                  verbose_name=u"赠送给")
    from_administrator = models.ForeignKey(Administrator,
                                           related_name=u"presents_fa_set",
                                           blank=True, null=True,
                                           verbose_name=u"操作员")
    presents_type = models.IntegerField(choices=presents_type_tuple,
                                        blank=True,
                                        null=True,
                                        default=1, verbose_name=u"类型")
    present_time = models.DateTimeField(auto_now_add=True, blank=True,
                                        null=True, verbose_name=u"赠送时间")
    msg_content = models.CharField(max_length=256, blank=True, null=True,
                                   verbose_name=u"内容")
    remark = models.CharField(max_length=64, blank=True, null=True,
                              verbose_name=u"备注")

    def __unicode__(self):
        return self.to_player.email

    class Meta:
        db_table = u"presents_record"
        verbose_name = u"赠送记录"
        verbose_name_plural = verbose_name


class SunTheOrder(models.Model):
    """晒单"""
    commodity_name = models.CharField(max_length=64, blank=True, null=True,
                                      verbose_name=u"商品名字")
    img_url = models.CharField(max_length=64, blank=True,
                               null=True, verbose_name=u"图片")
    period_no = models.CharField(max_length=32, blank=True,
                                 null=True, verbose_name=u"期号")
    reward_time = models.DateTimeField(blank=True, null=True,
                                       verbose_name=u"开奖时间")
    luck_player_name = models.CharField(max_length=64, blank=True, null=True,
                                        verbose_name=u"幸运玩家昵称")
    luck_player_headimg = models.CharField(
        max_length=64, blank=True, null=True, verbose_name=u"幸运玩家头像")
    luck_player = models.ForeignKey(GamePlayer,
                                    related_name=u"sto_lp_set",
                                    blank=True, null=True,
                                    verbose_name=u"幸运玩家")
    period = models.ForeignKey(Period, unique=True,
                               related_name=u"sto_period_set",
                               blank=True,
                               null=True,
                               verbose_name=u"周期")
    text = models.CharField(max_length=128, blank=True, null=True,
                            verbose_name=u"文本")
    upload_img = models.CharField(max_length=256, blank=True, null=True,
                                  verbose_name=u"文本")
    praise_count = models.IntegerField(blank=True, null=True,
                                       verbose_name=u"点赞数量")

    create_time = models.DateTimeField(auto_now_add=True,
                                       verbose_name=u"创建时间")

    def __unicode__(self):
        return self.commodity_name

    class Meta:
        db_table = u"sun_the_order"
        verbose_name = u"晒单"
        verbose_name_plural = verbose_name


class Praise(models.Model):
    """点赞"""

    sun_the_order = models.ForeignKey(SunTheOrder,
                                      related_name=u"praise_sto_set",
                                      blank=True,
                                      null=True,
                                      verbose_name=u"晒单")
    praise_player = models.ForeignKey(GamePlayer,
                                      related_name=u"praise_pp_set",
                                      blank=True, null=True,
                                      verbose_name=u"点赞玩家")

    def __unicode__(self):
        return str(self.id)

    class Meta:
        db_table = u"praise"
        verbose_name = u"点赞"
        verbose_name_plural = verbose_name
