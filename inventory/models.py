# coding:utf-8
from __future__ import unicode_literals

from django.db import models

from shopping_user.models import Administrator, GamePlayer


class CardInventories(models.Model):
    """卡密库存"""
    status_tuple = (
        (1, u"启用"),
        (2, u"禁用"),
        (3, u"删除")
    )

    name = models.CharField(max_length=128, blank=True, null=True,
                            verbose_name=u"卡名字")
    code = models.CharField(max_length=16, blank=True, null=True,
                            verbose_name=u"code")
    market_price_cny = models.DecimalField(max_digits=32, decimal_places=16,
                                           blank=True,
                                           null=True,
                                           verbose_name=u"市场价(面值)")
    volumes = models.IntegerField(blank=True, null=True, verbose_name=u"数量")

    warning_volumes = models.IntegerField(blank=True,
                                          null=True, verbose_name=u"警告数量")
    update_time = models.DateTimeField(auto_now_add=True, blank=True,
                                       null=True, verbose_name=u"更新时间")
    status = models.IntegerField(choices=status_tuple, default=1,
                                 blank=True, null=True, verbose_name=u"状态")

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = u"card_inventories"
        verbose_name = u"卡密库存"
        verbose_name_plural = verbose_name


class CardEntryRecord(models.Model):
    """卡密入库记录表"""

    # 20180930195059 时间
    batch_no = models.CharField(max_length=32, blank=True, null=True,
                                verbose_name=u"批次号")
    card_inventory = models.ForeignKey(CardInventories,
                                       related_name=u"cer_ci_set",
                                       blank=True, null=True,
                                       verbose_name=u"关联的卡库存")
    volumes = models.IntegerField(blank=True, null=True, verbose_name=u"数量")
    entry_time = models.DateTimeField(blank=True,
                                      null=True, verbose_name=u"入库时间")
    entry_admin = models.ForeignKey(Administrator,
                                    related_name=u"cer_admin_set",
                                    blank=True, null=True,
                                    verbose_name=u"入库管理员")

    def __unicode__(self):
        return u"pk={}, {}, {}".format(str(self.pk), self.card_inventory.name,
                                       str(self.volumes))

    class Meta:
        db_table = u"card_entry_record"
        verbose_name = u"卡密入库记录表"
        verbose_name_plural = verbose_name


class Card(models.Model):
    """卡密表"""
    status = (
        (1, u"有效"),
        (2, u"已使用")
    )

    card_entry_no = models.ForeignKey(CardEntryRecord,
                                      related_name=u"card_cen_set",
                                      blank=True, null=True,
                                      verbose_name=u"入库记录ID")
    card_inventory = models.ForeignKey(CardInventories,
                                       related_name=u"card_ci_set",
                                       blank=True, null=True,
                                       verbose_name=u"所属库存")
    card_number = models.CharField(max_length=128, blank=True, null=True,
                                   verbose_name=u"卡号")
    card_pwd = models.CharField(max_length=128, blank=True, null=True,
                                verbose_name=u"密码")
    batch_no = models.CharField(max_length=32, blank=True, null=True,
                                verbose_name=u"批次号")
    status = models.IntegerField(choices=status, blank=True, null=True,
                                 verbose_name=u"状态")

    def __unicode__(self):
        return str(self.id)

    class Meta:
        db_table = u"card"
        verbose_name = u"卡密"
        verbose_name_plural = verbose_name


class CardDeliveryRecord(models.Model):
    """卡密出库记录表"""

    card_inventory = models.ForeignKey(CardInventories,
                                       related_name=u"cdr_ci_set",
                                       blank=True, null=True,
                                       verbose_name=u"关联的卡库存")
    volumes = models.IntegerField(blank=True, null=True, verbose_name=u"数量")
    delivery_time = models.DateTimeField(auto_now_add=True, blank=True,
                                         null=True, verbose_name=u"出库时间")

    to_player = models.ForeignKey(GamePlayer, related_name=u"cdr_tp_set",
                                  blank=True,
                                  null=True,
                                  verbose_name=u"玩家")
    reason = models.CharField(max_length=256, blank=True, null=True,
                              verbose_name=u"出库原因")

    def __unicode__(self):
        return u"{}, {}".format(self.card_inventory.name, str(self.volumes))

    class Meta:
        db_table = u"card_delivery_record"
        verbose_name = u"卡密出库记录表"
        verbose_name_plural = verbose_name
