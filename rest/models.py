# coding:utf-8
from __future__ import unicode_literals

from django.db import models

from shopping_user.models import GamePlayer
from snatch_treasure.models import Commodity, Period


class GoodsDeliverRecord(models.Model):
    """发货记录"""

    channel_tuple = (
        (1, u"京东第三方[手动发货]"),
    )
    status_tuple = (
        (1, u"未下单"),
        (2, u"已下单"),
        (3, u"未发货"),
        (4, u"已发货"),
        (5, u"已确认送到"),
    )

    to_player = models.ForeignKey(GamePlayer, related_name=u"gdr_player_set",
                                  blank=True, null=True,
                                  verbose_name=u"发送给")
    commodity = models.ForeignKey(Commodity,
                                  related_name=u"gdr_commodity_set",
                                  blank=True, null=True,
                                  verbose_name=u"商品")
    period = models.ForeignKey(Period,
                               related_name=u"gdr_period_set",
                               blank=True, null=True,
                               verbose_name=u"周期")

    recipents_name = models.CharField(max_length=16, blank=True,
                                      null=True,
                                      verbose_name=u"收件人名字")
    recipents_phone = models.CharField(max_length=16, blank=True,
                                       null=True,
                                       verbose_name=u"收件人号码")
    recipents_address = models.CharField(max_length=128, blank=True,
                                         null=True,
                                         verbose_name=u"收件人地址")

    deliver_goods_channel = models.IntegerField(choices=channel_tuple,
                                                default=1, blank=True,
                                                null=True,
                                                verbose_name=u"发货渠道")
    quantity = models.IntegerField(blank=True, null=True,
                                   verbose_name=u"数量")
    real_price_cny = models.DecimalField(max_digits=32, decimal_places=16,
                                         blank=True,
                                         null=True, verbose_name=u"实际价格")
    delivery_expense = models.DecimalField(max_digits=32, decimal_places=16,
                                           blank=True,
                                           null=True, verbose_name=u"运费")
    express_company = models.CharField(max_length=32, blank=True, null=True,
                                       verbose_name=u"快递公司")
    express_number = models.CharField(max_length=64, blank=True, null=True,
                                      verbose_name=u"快递单号")
    link = models.CharField(max_length=128, blank=True, null=True,
                            verbose_name=u"下单链接")
    deliver_goods_time = models.DateTimeField(blank=True, null=True,
                                              verbose_name=u"发货时间")
    arrive_time = models.DateTimeField(blank=True, null=True,
                                       verbose_name=u"送达时间")
    status = models.IntegerField(choices=status_tuple, blank=True, null=True,
                                 default=1, verbose_name=u"状态")
    remark = models.CharField(max_length=64, blank=True, null=True,
                              verbose_name=u"备注")

    def __unicode__(self):
        return self.commodity.commodity_name

    class Meta:
        db_table = u"goods_deliver_record"
        verbose_name = u"发货记录"
        verbose_name_plural = verbose_name
