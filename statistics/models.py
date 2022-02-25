# coding:utf-8
from django.db import models

from shopping_user.models import GamePlayer
from recycle_businessman.models import RecycleBusinessman


class UserEveryDayInfo(models.Model):
    """用户每日数据"""
    player = models.ForeignKey(GamePlayer, related_name=u"uei_player_set",
                               verbose_name=u"玩家")
    consume_cny = models.DecimalField(max_digits=16, decimal_places=6,
                                      blank=True, null=True,
                                      verbose_name=u"消费金额")
    deposit_cny = models.DecimalField(max_digits=16, decimal_places=6,
                                      blank=True, null=True,
                                      verbose_name=u"充值金额")
    bonus = models.DecimalField(max_digits=16, decimal_places=6,
                                blank=True, null=True,
                                verbose_name=u"中奖金额")
    # 今日充值金额和中奖金额的差额
    difference = models.DecimalField(max_digits=16, decimal_places=6,
                                     blank=True, null=True,
                                     verbose_name=u"差额")
    presents_b = models.IntegerField(blank=True, null=True,
                                     verbose_name=u"当日赠送")
    cur_date = models.DateField(auto_now_add=True, blank=True,
                                null=True, verbose_name=u"时间")
    update_time = models.DateTimeField(auto_now=True, blank=True, null=True,
                                       verbose_name=u"更新时间")

    def __unicode__(self):
        return u"用户={}, id=[{}]". \
            format(self.player.phone,
                   self.player.nickname)

    class Meta:
        db_table = u"user_everyday_info"
        verbose_name = u"用户每日数据"
        verbose_name_plural = verbose_name


class UserEveryMonthInfo(models.Model):
    """用户每月数据"""
    player = models.ForeignKey(GamePlayer, related_name=u"uem_player_set",
                               verbose_name=u"玩家")
    consume_money = models.DecimalField(max_digits=8, decimal_places=1,
                                        blank=True, null=True,
                                        verbose_name=u"消费金额")
    deposit_money = models.DecimalField(max_digits=8, decimal_places=1,
                                        blank=True, null=True,
                                        verbose_name=u"充值金额")
    bonus = models.DecimalField(max_digits=8, decimal_places=1,
                                blank=True, null=True,
                                verbose_name=u"中奖金额")
    presents_money = models.DecimalField(max_digits=8, decimal_places=1,
                                         blank=True, null=True,
                                         verbose_name=u"赠送金额")
    snatch_treasure_b = models.DecimalField(max_digits=8,
                                            decimal_places=1,
                                            blank=True, null=True,
                                            verbose_name=u"夺宝价")
    order_count = models.IntegerField(blank=True, null=True,
                                      verbose_name=u"下单次数")

    data_date = models.CharField(max_length=32, verbose_name=u"数据日期")
    update_time = models.DateTimeField(auto_now=True, blank=True, null=True,
                                       verbose_name=u"更新时间")

    def __unicode__(self):
        return str(self.id)

    class Meta:
        db_table = u"user_everymonth_info"
        verbose_name = u"用户每月数据"
        verbose_name_plural = verbose_name


class RbEveryDayInfo(models.Model):
    """回收商每日数据 第二日计算前一日的数据,每天执行一次"""
    status_tuple = (
        (1, u"已结算"),
        (2, u"未结算"),
    )

    recycle_businessman = models.ForeignKey(RecycleBusinessman,
                                            blank=True, null=True,
                                            related_name=u"rs_rb_set",
                                            verbose_name=u"回收商")
    receive_cny = models.DecimalField(max_digits=16, decimal_places=6,
                                      blank=True, null=True,
                                      verbose_name=u"收货金额")
    ls_cny = models.DecimalField(max_digits=16, decimal_places=6,
                                 blank=True, null=True,
                                 verbose_name=u"关联用户流水")
    dai_chong_cny = models.DecimalField(max_digits=16, decimal_places=6,
                                        blank=True, null=True,
                                        verbose_name=u"代充金额")
    receive_back_profit_cny = models.DecimalField(max_digits=16,
                                                  decimal_places=6,
                                                  blank=True, null=True,
                                                  verbose_name=u"收货返利")
    dai_chong_back_profit_cny = models.DecimalField(max_digits=16,
                                                    decimal_places=6,
                                                    blank=True, null=True,
                                                    verbose_name=u"代充返利")
    ls_back_profit_cny = models.DecimalField(max_digits=16,
                                             decimal_places=6,
                                             blank=True, null=True,
                                             verbose_name=u"流水返利")

    total = models.DecimalField(max_digits=16, decimal_places=6,
                                blank=True, null=True,
                                verbose_name=u"汇总")
    data_date = models.DateField(blank=True,
                                 null=True, verbose_name=u"数据日期")

    settlement_date = models.DateField(blank=True,
                                       null=True, verbose_name=u"结算日期")
    status = models.IntegerField(choices=status_tuple, blank=True, null=True,
                                 verbose_name=u"状态")

    def __unicode__(self):
        return u"回收商={}, id=[{}]". \
            format(self.recycle_businessman.phone,
                   self.recycle_businessman.pk)

    class Meta:
        db_table = u"rb_everyday_info"
        verbose_name = u"回收商每日数据"
        verbose_name_plural = verbose_name


class PlatformEverydayData(models.Model):
    """平台每日数据"""

    status_tuple = (
        (1, u"已结算"),
        (2, u"未结算"),
    )
    alipay_cny = models.DecimalField(max_digits=16, decimal_places=6,
                                     blank=True, null=True,
                                     verbose_name=u"支付宝充值金额")
    wx_cny = models.DecimalField(max_digits=16, decimal_places=6,
                                 blank=True, null=True, default=0.0,
                                 verbose_name=u"微信充值金额")
    # 代充
    dai_chong_cny = models.DecimalField(max_digits=16, decimal_places=6,
                                        blank=True, null=True,
                                        verbose_name=u"代充金额")
    # app充值,代充
    deposit_total_cny = models.DecimalField(max_digits=16, decimal_places=6,
                                            blank=True, null=True,
                                            verbose_name=u"充值总金额")
    bonus = models.DecimalField(max_digits=16, decimal_places=6,
                                blank=True, null=True,
                                verbose_name=u"中奖金额")
    presents_b = models.IntegerField(blank=True, null=True,
                                     verbose_name=u"当日赠送")
    alipay_deposit_count = models.IntegerField(blank=True, null=True,
                                               verbose_name=u"支付宝充值笔数")
    wx_deposit_count = models.IntegerField(blank=True, null=True,
                                           verbose_name=u"微信充值笔数")

    dai_chong_deposit_count = models.IntegerField(blank=True, null=True,
                                                  verbose_name=u"代充笔数")
    shipment_phone_deposit_cny = models.DecimalField(max_digits=16,
                                                     decimal_places=1,
                                                     blank=True, null=True,
                                                     verbose_name=u"出卡号充值总额")
    shipment_phone_shipment_cny = models.DecimalField(max_digits=16,
                                                      decimal_places=1,
                                                      blank=True, null=True,
                                                      verbose_name=u"出卡号出货总额")
    shipment_phone_profit_and_loss = models.DecimalField(max_digits=16,
                                                         decimal_places=1,
                                                         blank=True, null=True,
                                                         verbose_name=u"出卡号盈利总额(截止当天)")

    data_date = models.DateField(blank=True,
                                 null=True, verbose_name=u"数据日期")

    update_time = models.DateTimeField(auto_now=True,
                                       blank=True, null=True,
                                       verbose_name=u"更新时间")

    status = models.IntegerField(choices=status_tuple, blank=True, null=True,
                                 verbose_name=u"状态")

    # 支付费率
    pay_rates = models.DecimalField(max_digits=16, decimal_places=6,
                                    blank=True, null=True,
                                    verbose_name=u"三方费率")
    # 中奖金额
    win_prize_entity_price = models.DecimalField(max_digits=16,
                                                 decimal_places=6,
                                                 blank=True, null=True,
                                                 verbose_name=u"实物中奖金额")
    win_prize_virtual_price = models.DecimalField(max_digits=16,
                                                  decimal_places=6,
                                                  blank=True, null=True,
                                                  verbose_name=u"虚拟中奖金额")
    # 发货金额
    deliver_goods_entity_price = models.DecimalField(max_digits=16,
                                                     decimal_places=6,
                                                     blank=True, null=True,
                                                     verbose_name=u"实物发货金额")
    deliver_goods_virtual_price = models.DecimalField(max_digits=16,
                                                      decimal_places=6,
                                                      blank=True, null=True,
                                                      verbose_name=u"虚拟发货金额")
    # 回收商
    recycle_businessman_withdraw_price = \
        models.DecimalField(max_digits=16,
                            decimal_places=6,
                            blank=True,
                            null=True,
                            verbose_name=u"回收商提现金额")

    # 佣金
    recycle_commission = \
        models.DecimalField(max_digits=16,
                            decimal_places=6,
                            blank=True,
                            null=True,
                            verbose_name=u"收卡佣金")
    ls_commission = \
        models.DecimalField(max_digits=16,
                            decimal_places=6,
                            blank=True,
                            null=True,
                            verbose_name=u"流水佣金")
    dc_commission = \
        models.DecimalField(max_digits=16,
                            decimal_places=6,
                            blank=True,
                            null=True,
                            verbose_name=u"代充佣金")

    # (充值-中奖-佣金-费率)
    ll_profit = \
        models.DecimalField(max_digits=16,
                            decimal_places=6,
                            blank=True,
                            null=True,
                            verbose_name=u"理论利润")
    # 理论利润 / 充值
    profit_rate = \
        models.DecimalField(max_digits=16,
                            decimal_places=6,
                            blank=True,
                            null=True,
                            verbose_name=u"利润率")
    real_profit = \
        models.DecimalField(max_digits=16,
                            decimal_places=6,
                            blank=True,
                            null=True,
                            verbose_name=u"实际利润")

    def __unicode__(self):
        return str(self.pk)

    class Meta:
        db_table = u"platform_everyday_data"
        verbose_name = u"平台每日数据"
        verbose_name_plural = verbose_name
