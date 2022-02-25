# coding:utf-8
from __future__ import unicode_literals

from django.db import models

from shopping_user.models import GamePlayer, Administrator
from recycle_businessman.models import RecycleBusinessman
from shopping_settings.models import PayType, PayChannel
from snatch_treasure.models import Period, DuoBaoParticipateRecord
from inventory.models import Card


class DepositRecord(models.Model):
    """
    充值记录
    """
    status_tuple = (
        (0, u"等待付款"),
        (1, u"充值成功"),
        (2, u"已退费"),
        (10, u"删除"),
    )
    units_tuple = (
        (1, u"cny"),
    )

    trade_no = models.CharField(max_length=128, blank=True, null=True,
                                verbose_name=u"三方交易号")
    discount_amount_cny = models.DecimalField(max_digits=16, decimal_places=6,
                                              blank=True,
                                              null=True, verbose_name=u"优惠金额")
    commercial_tenant_nos = models.CharField(max_length=32, blank=True,
                                             null=True,
                                             verbose_name=u"商户号")

    from_recycle_businessman = \
        models.ForeignKey(RecycleBusinessman, blank=True,
                          null=True,
                          related_name=u"dr_rb_set",
                          verbose_name=u"代充的回收商")

    # 实际支付金额
    payment_amount_cny = models.DecimalField(max_digits=16, decimal_places=6,
                                             blank=True,
                                             null=True, verbose_name=u"实际支付金额")

    is_ret = models.BooleanField(default=False, verbose_name=u"是否已返利")

    # 公有
    out_trade_no = models.CharField(max_length=128, blank=True, null=True,
                                    verbose_name=u"自家交易号")
    amounts = models.IntegerField(blank=True,
                                  null=True, verbose_name=u"充值金额")
    units = models.IntegerField(choices=units_tuple, blank=True,
                                null=True,
                                verbose_name=u"单位(支付币种)")
    to_player = models.ForeignKey(GamePlayer, related_name=u"dr_tp_set",
                                  verbose_name=u"充值用户")
    deposit_type = models.ForeignKey(PayType, blank=True, null=True,
                                     verbose_name=u"充值类型")
    deposit_channel = models.ForeignKey(PayChannel, blank=True, null=True,
                                        verbose_name=u"支付通道")
    channel_rate = models.DecimalField(max_digits=8,
                                       decimal_places=4,
                                       blank=True,
                                       null=True,
                                       verbose_name=u"通道费率")
    deposit_time = models.DateTimeField(auto_now_add=True, blank=True,
                                        null=True, verbose_name=u"充值时间")
    status = models.IntegerField(choices=status_tuple, blank=True, null=True,
                                 verbose_name=u"状态")
    remark = models.CharField(max_length=1024, blank=True, null=True,
                              verbose_name=u"备注")

    def __unicode__(self):
        return u"自家交易号=[{}]".format(self.out_trade_no)

    class Meta:
        db_table = u"deposit_record"
        verbose_name = u"充值记录"
        verbose_name_plural = verbose_name


class ConsumeRecord(models.Model):
    """消费记录"""

    status_tuple = (
        (1, u"消费成功"),
        (10, u"删除"),
    )
    period = models.ForeignKey(Period, blank=True, null=True,
                               verbose_name=u"周期id")
    amounts = models.DecimalField(max_digits=32, decimal_places=16, blank=True,
                                  null=True, verbose_name=u"消费金额")
    renci = models.IntegerField(default=1, verbose_name=u"人次")

    participate = models.ForeignKey(DuoBaoParticipateRecord,
                                    related_name=u"cr_participate_set",
                                    blank=True, null=True,
                                    verbose_name=u"消费的参与记录")

    player = models.ForeignKey(GamePlayer, related_name=u"cr_player_set",
                               blank=True, null=True, verbose_name=u"玩家")
    status = models.IntegerField(choices=status_tuple, blank=True, null=True,
                                 verbose_name=u"状态")
    consume_time = models.DateTimeField(auto_now_add=True, blank=True,
                                        null=True, verbose_name=u"消费时间")

    def __unicode__(self):
        return u"{}[{}]".format(self.player.phone, str(self.amounts))

    class Meta:
        db_table = u"consume_record"
        verbose_name = u"消费记录"
        verbose_name_plural = verbose_name


class PrizeRecord(models.Model):
    """中奖记录"""

    status_tuple = (
        (1, u"未领奖"),
        (2, u"已领奖"),
        (9, u"卡密库存不足"),
    )
    accept_prize_type_tuple = (
        (1, u"兑换欢乐豆"),
        (2, u"转到收货人"),
        (3, u"领取奖品"),
    )
    record_id = models.CharField(max_length=32, blank=True, null=True,
                                 verbose_name=u"记录id")

    period = models.ForeignKey(Period, blank=True, null=True,
                               related_name=u"pr_period_set",
                               verbose_name=u"周期id")
    amounts = models.DecimalField(max_digits=32, decimal_places=16, blank=True,
                                  null=True, verbose_name=u"中奖金额")
    accept_prize_type = models.IntegerField(choices=accept_prize_type_tuple,
                                            blank=True,
                                            null=True,
                                            verbose_name=u"领奖方式")
    to_recycle_businessman = models.ForeignKey(RecycleBusinessman, blank=True,
                                               null=True,
                                               related_name=u"pr_trb_set",
                                               verbose_name=u"转到回收商")
    card = models.ForeignKey(Card, blank=True,
                             null=True,
                             related_name=u"pr_card_set",
                             verbose_name=u"用户领取的卡")
    accept_prize_time = models.DateTimeField(blank=True,
                                             null=True,
                                             verbose_name=u"领奖时间")

    participate = models.ForeignKey(DuoBaoParticipateRecord,
                                    related_name=u"pr_participate_set",
                                    blank=True, null=True,
                                    verbose_name=u"中奖的参与记录")

    player = models.ForeignKey(GamePlayer, related_name=u"pr_tp_set",
                               blank=True, null=True, verbose_name=u"玩家")
    status = models.IntegerField(choices=status_tuple, blank=True, null=True,
                                 verbose_name=u"状态")
    prize_time = models.DateTimeField(auto_now_add=True, blank=True, null=True,
                                      verbose_name=u"中奖时间")

    def __unicode__(self):
        return u"pk={},{},[{}]".format(str(self.pk), self.player.phone,
                                       str(self.amounts))

    class Meta:
        db_table = u"prize_record"
        verbose_name = u"获奖记录"
        verbose_name_plural = verbose_name


class AgencyRecord(models.Model):
    """
    代理记录 (管理员为回收商充值的记录)
    """

    status_tuple = (
        (1, u"待定"),
        (2, u"充值成功")
    )

    units_tuple = (
        (1, u"cny"),
    )

    agency_trade_no = models.CharField(max_length=128, blank=True, null=True,
                                       verbose_name=u"代理交易号")

    amounts = models.DecimalField(max_digits=10, decimal_places=2, blank=True,
                                  null=True, verbose_name=u"代理金额")
    units = models.IntegerField(choices=units_tuple, blank=True,
                                null=True,
                                verbose_name=u"充值货币类型")
    deposit_time = models.DateTimeField(blank=True,
                                        null=True, verbose_name=u"充值时间")
    status = models.IntegerField(choices=status_tuple, blank=True, null=True,
                                 verbose_name=u"状态")
    remark = models.CharField(max_length=128, blank=True, null=True,
                              verbose_name=u"备注")
    to_recycle_businessman = \
        models.ForeignKey(RecycleBusinessman, blank=True,
                          null=True,
                          related_name=u"ar_trb_set",
                          verbose_name=u"回收商")

    def __unicode__(self):
        return u"充值交易号=[{}]".format(self.agency_trade_no)

    class Meta:
        db_table = u"agency_record"
        verbose_name = u"代理记录"
        verbose_name_plural = verbose_name


class BackProfitRecord(models.Model):
    """返利记录表"""
    back_profit_type_tuple = (
        (1, u"代充返利"),
        (2, u"收货返利"),
        (3, u"流水返利"),
    )
    status_tuple = (
        (0, u"未返利"),
        (1, u"已返利"),
        (2, u"返利失败")
    )

    amounts = models.DecimalField(max_digits=16, decimal_places=6, blank=True,
                                  null=True, verbose_name=u"返利金额")
    back_profit_type = models.IntegerField(choices=back_profit_type_tuple,
                                           blank=True,
                                           null=True,
                                           verbose_name=u"状态")
    to_recycle_businessman = \
        models.ForeignKey(RecycleBusinessman, blank=True,
                          null=True,
                          related_name=u"bpr_trb_set",
                          verbose_name=u"回收商")
    back_profit_date = models.DateField(blank=True,
                                        null=True,
                                        verbose_name=u"返利日期")
    settlement_date = models.DateField(blank=True,
                                       null=True, verbose_name=u"结算日期")
    # 代充返利(代充类型)：充值记录id  收货返利:回收记录id   流水返利(所有充值类型):充值记录id
    relation_ids = models.TextField(blank=True, null=True,
                                    verbose_name=u"关联id")
    status = models.IntegerField(choices=status_tuple, blank=True, null=True,
                                 verbose_name=u"状态")

    def __unicode__(self):
        return u"{}".format(self.pk)

    class Meta:
        db_table = u"back_profit_record"
        verbose_name = u"返利记录"
        verbose_name_plural = verbose_name


class WithdrawRecord(models.Model):
    """提现记录 (卡商提现记录)"""

    status_tuple = (
        (1, u"审核中"),
        (2, u"提现成功"),
        (3, u"审核不通过"),
        (10, u"删除"),
    )

    units_tuple = (
        (1, u"cny"),
    )

    out_trade_no = models.CharField(max_length=128, blank=True,
                                    null=True,
                                    verbose_name=u"自己交易号")

    amounts = models.DecimalField(max_digits=10, decimal_places=2,
                                  blank=True,
                                  null=True, verbose_name=u"提现金额")
    units = models.IntegerField(choices=units_tuple, blank=True,
                                null=True,
                                verbose_name=u"提现货币类型")
    apply_for_time = models.DateTimeField(auto_now_add=True, blank=True,
                                          null=True, verbose_name=u"申请时间")
    transfer_time = models.DateTimeField(blank=True,
                                         null=True, verbose_name=u"转帐时间")
    arrive_time = models.DateTimeField(blank=True,
                                       null=True, verbose_name=u"到帐时间")

    status = models.IntegerField(choices=status_tuple, blank=True,
                                 null=True,
                                 verbose_name=u"状态")
    remark = models.CharField(max_length=128, blank=True, null=True,
                              verbose_name=u"备注")
    to_recycle_businessman = \
        models.ForeignKey(RecycleBusinessman, blank=True,
                          null=True,
                          related_name=u"wr_trb_set",
                          verbose_name=u"回收商")
    admin = models.ForeignKey(Administrator, blank=True, null=True,
                              related_name=u"withdraw_admin_set",
                              verbose_name=u"审核人")

    def __unicode__(self):
        return u"自己交易号=[{}]".format(self.out_trade_no)

    class Meta:
        db_table = u"withdraw_record"
        verbose_name = u"提现记录"
        verbose_name_plural = verbose_name
