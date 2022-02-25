# coding:utf-8
from django.db import models

from inventory.models import CardInventories
from shopping_settings.models import CommodityType, Administrator, BuyChannel
from shopping_user.models import GamePlayer


class Commodity(models.Model):
    """商品"""
    # 是否展示给玩家, 下架会修改is_continue为0
    status_tuple = (
        (1, u"上架"),
        (2, u"下架"),
        (10, u"删除"),
    )
    reward_type_tuple = (
        (1, u"秒开"),
        (2, u"B值"),
    )
    # 是否开始新的周期
    is_continue_tuple = (
        (1, u"是"),
        (0, u"否"),
    )

    commodity_name = models.CharField(max_length=128, blank=True, null=True,
                                      verbose_name=u"商品名称")
    commodity_type = models.ForeignKey(CommodityType,
                                       related_name=u"commodity_ct_set",
                                       blank=True, null=True,
                                       verbose_name=u"商品类型")
    reward_type = models.IntegerField(choices=reward_type_tuple, blank=True,
                                      null=True, verbose_name=u"开奖类型")
    market_price_cny = models.DecimalField(max_digits=32, decimal_places=16,
                                           blank=True,
                                           null=True, verbose_name=u"市场价")
    snatch_treasure_amounts = models.IntegerField(blank=True,
                                                  null=True,
                                                  verbose_name=u"夺宝价")
    dh_price_cny = models.DecimalField(max_digits=32,
                                       decimal_places=16,
                                       blank=True,
                                       null=True, verbose_name=u"兑换价")
    unit_price = models.IntegerField(
        blank=True, null=True, default=1, verbose_name=u"单价")
    total_renci = models.IntegerField(
        blank=True, null=True, verbose_name=u"总需人次")

    is_continue = models.IntegerField(choices=is_continue_tuple, blank=True,
                                      null=True, verbose_name=u"是否续期")

    quota_str = models.CharField(max_length=128, blank=True, null=True,
                                 verbose_name=u"定额串")

    buy_channel = models.ForeignKey(BuyChannel,
                                    related_name=u"commodity_bc_set",
                                    blank=True, null=True,
                                    verbose_name=u"进货渠道")

    status = models.IntegerField(choices=status_tuple, blank=True, null=True,
                                 verbose_name=u"状态")

    count = models.IntegerField(blank=True, null=True, verbose_name=u"已开期数")

    show_index = models.IntegerField(blank=True, null=True,
                                     verbose_name=u"app上显示的顺序")

    create_administrator = \
        models.ForeignKey(Administrator,
                          related_name=u"commodity_admin_set",
                          blank=True, null=True,
                          verbose_name=u"创建人")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name=u"创建时间")
    is_card = models.BooleanField(default=False, verbose_name=u"是否卡密")
    card_inventory = models.ForeignKey(CardInventories,
                                       related_name=u"commodity_ci_set",
                                       blank=True, null=True,
                                       verbose_name=u"所属库存")
    cover = models.CharField(max_length=1024, default=None, verbose_name=u"封面")

    def __unicode__(self):
        return self.commodity_name

    class Meta:
        db_table = u"commodity"
        verbose_name = u"商品"
        verbose_name_plural = verbose_name


class Period(models.Model):
    """
    周期
    """
    status_tuple = (
        (1, u"筹备中"),
        (2, u"筹备完成"),
        (3, u"等待B值中"),
        (4, u"倒计时中"),
        (5, u"开奖中"),
        (6, u"已开奖"),
    )

    # 夺宝价 兑换价 市场价 单价
    period_no = models.CharField(max_length=16, blank=True, null=True,
                                 verbose_name=u"周期号")
    commodity = models.ForeignKey(Commodity,
                                  related_name=u"period_c_set",
                                  blank=True, null=True, verbose_name=u"商品")
    target_amounts = models.IntegerField(blank=True, null=True,
                                         verbose_name=u"目标人次")
    amounts_prepared = models.IntegerField(blank=True, null=True,
                                           verbose_name=u"已备人次")
    rate = models.DecimalField(max_digits=8,
                               decimal_places=2,
                               blank=True,
                               null=True, verbose_name=u"已备份数占比")
    luck_token = models.CharField(max_length=32, blank=True, null=True,
                                  verbose_name=u"幸运夺宝号")
    luck_player = models.ForeignKey(GamePlayer,
                                    related_name=u"period_lp_set",
                                    blank=True, null=True,
                                    verbose_name=u"幸运玩家")
    a_value = models.BigIntegerField(blank=True, null=True, verbose_name=u"A值")
    b_value = models.BigIntegerField(blank=True, null=True, verbose_name=u"B值")
    ssc_period_no = models.BigIntegerField(blank=True, default=0,
                                           null=True, verbose_name=u"时时彩期次")

    finish_time = models.DateTimeField(blank=True, null=True,
                                       verbose_name=u"筹备完成时间")
    reward_time = models.DateTimeField(blank=True, null=True,
                                       verbose_name=u"开奖时间")
    status = models.IntegerField(choices=status_tuple, blank=True, null=True,
                                 default=0, verbose_name=u"状态")
    create_administrator = models.ForeignKey(Administrator,
                                             related_name=u"period_ca_set",
                                             blank=True, null=True,
                                             verbose_name=u"操作员")
    create_time = models.DateTimeField(auto_now_add=True, blank=True,
                                       null=True, verbose_name=u"创建时间")
    content = models.TextField(blank=True, null=True,
                               verbose_name=u"内容")
    token_str = models.TextField(blank=True, null=True,
                                 verbose_name=u"周期的所有token")
    residue_token_str = models.TextField(blank=True, null=True,
                                         verbose_name=u"剩余Token")
    open_index = models.IntegerField(blank=True, null=True, default=-1,
                                     verbose_name=u"开奖顺序")

    def __unicode__(self):
        return u"PK={},商品=[{}], 周期=[{}]". \
            format(str(self.pk),
                   self.commodity.commodity_name, self.period_no)

    class Meta:
        db_table = u"period"
        verbose_name = u"周期"
        verbose_name_plural = verbose_name


class Order(models.Model):
    """订单 [一个订单对应一种商品]"""

    # 当周期还在参与中, 状态都在下单中.
    status_tuple = (
        (1, u"下单中"),
        (2, u"下单完成"),
    )

    order_no = models.CharField(max_length=64, blank=True, null=True,
                                verbose_name=u"订单号")
    player = models.ForeignKey(GamePlayer, related_name=u"order_player_set",
                               blank=True, null=True,
                               verbose_name=u"下单玩家")
    period = models.ForeignKey(Period, related_name=u"order_period_set",
                               blank=True,
                               null=True,
                               verbose_name=u"下单的周期")
    count = models.IntegerField(blank=True, null=True,
                                verbose_name=u"参与次数")
    unit_price = models.IntegerField(
        blank=True, null=True, default=1, verbose_name=u"单价")
    total_renci = models.IntegerField(blank=True, null=True,
                                      verbose_name=u"总购人次")
    total_fees = models.DecimalField(max_digits=8,
                                     decimal_places=2, blank=True, null=True,
                                     verbose_name=u"总花费")
    status = models.IntegerField(choices=status_tuple, blank=True, null=True,
                                 default=1, verbose_name=u"状态")
    create_time = models.DateTimeField(auto_now_add=True, blank=True,
                                       null=True, verbose_name=u"创建时间")

    def __unicode__(self):
        return u"order_no={}".format(self.order_no)

    class Meta:
        db_table = u"order"
        verbose_name = u"订单"
        verbose_name_plural = verbose_name


class DuoBaoParticipateRecord(models.Model):
    """夺宝参与记录表"""
    order = models.ForeignKey(Order, related_name=u"dpr_order_set",
                              blank=True,
                              null=True,
                              verbose_name=u"所属订单")

    participate_amounts = models.IntegerField(
        blank=True, null=True, verbose_name=u"购买的人次")

    player = models.ForeignKey(GamePlayer, related_name=u"dpr_player_set",
                               blank=True, null=True,
                               verbose_name=u"玩家")
    period = models.ForeignKey(Period, related_name=u"dpr_period_set",
                               blank=True,
                               null=True,
                               verbose_name=u"参与的周期")
    time = models.DateTimeField(blank=True, null=True, verbose_name=u"参与时间")
    token_str = models.TextField(blank=True, null=True,
                                 verbose_name=u"该次的夺宝号")
    residue = models.IntegerField(blank=True, null=True,
                                  verbose_name=u"剩余人次")
    is_win_prize = models.BooleanField(default=False,
                                       verbose_name=u"当前参与是否中奖")

    def __unicode__(self):
        return u"周期=[{}]".format(str(self.period.period_no))

    class Meta:
        db_table = u"duobao_participate_record"
        verbose_name = u"夺宝参与记录表"
        verbose_name_plural = verbose_name


class TokenRecord(models.Model):
    """
    夺宝号
    """

    token_no = models.CharField(max_length=32, blank=True, null=True,
                                verbose_name=u"夺宝号")
    player = models.ForeignKey(GamePlayer, related_name=u"tr_player_set",
                               blank=True, null=True, verbose_name=u"用户")
    period = models.ForeignKey(Period, related_name=u"tr_period_set",
                               blank=True, null=True, verbose_name=u"所属周期")
    participate = models.ForeignKey(DuoBaoParticipateRecord,
                                    related_name=u"tr_participate_set",
                                    blank=True, null=True,
                                    verbose_name=u"参与记录id")

    def __unicode__(self):
        return u"token=[{}]".format(self.token_no)

    class Meta:
        db_table = u"token_record"
        verbose_name = u"夺宝号记录表"
        verbose_name_plural = verbose_name


class ShiShiCai(models.Model):
    """时时彩"""

    number = models.IntegerField(blank=True,
                                 null=True, verbose_name=u"号码")
    ssc_period_no = models.BigIntegerField(blank=True, default=0,
                                           null=True, verbose_name=u"期号")
    open_time = models.DateTimeField(blank=True, null=True,
                                     verbose_name=u"开奖的时间")
    next_open_time = models.DateTimeField(blank=True, null=True,
                                          verbose_name=u"下一次开奖的时间")

    def __unicode__(self):
        return u"number={}, ssc_period_no={}".format(str(self.number),
                                                     self.ssc_period_no)

    class Meta:
        db_table = u"shi_shi_cai"
        verbose_name = u"时时彩"
        verbose_name_plural = verbose_name


class UserCard(models.Model):
    """玩家卡密"""
    player = models.ForeignKey(GamePlayer, related_name=u"uc_player_set",
                               blank=True, null=True,
                               verbose_name=u"玩家")

    card_number = models.CharField(max_length=128, blank=True, null=True,
                                   verbose_name=u"卡号")
    card_pwd = models.CharField(max_length=128, blank=True, null=True,
                                verbose_name=u"密码")
    source = models.ForeignKey(Period, blank=True, null=True,
                               verbose_name=u"来源")

    def __unicode__(self):
        return self.card_number

    class Meta:
        db_table = u"user_card"
        verbose_name = u"用户卡密"
        verbose_name_plural = verbose_name


class AppointWinner(models.Model):
    """指定中奖者"""

    admin = models.ForeignKey(Administrator, related_name=u"aw_admin",
                              blank=True, null=True, verbose_name=u"管理员")
    period = models.ForeignKey(Period, related_name=u"aw_period",
                               blank=True, null=True, verbose_name=u"周期")
    player = models.ForeignKey(GamePlayer, related_name=u"aw_player",
                               blank=True, null=True, verbose_name=u"指定中奖者")
    create_time = models.DateTimeField(auto_now_add=True, blank=True,
                                       null=True, verbose_name=u"创建时间")

    def __unicode__(self):
        return str(self.id)

    class Meta:
        db_table = u"appoint_winner"
        verbose_name = u"指定中奖者"
        verbose_name_plural = verbose_name


class RecommendCommodity(models.Model):
    """推荐商品"""
    location_type = (
        (1, u"精选推荐"),
        (2, u"经典收藏"),
        (3, u"精品推荐"),
        (4, u"美食天地"),
    )
    status_tuple = (
        (1, u"启用"),
        (2, u"禁用"),
    )

    name = models.CharField(max_length=126, blank=True,
                            null=True, verbose_name=u"名字")
    commodity = models.ForeignKey(Commodity,
                                  related_name=u"rc_commodity_set",
                                  blank=True, null=True, verbose_name=u"商品")
    location = models.IntegerField(choices=location_type, blank=True,
                                   null=True, verbose_name=u"推荐位置")
    status = models.IntegerField(choices=status_tuple, blank=True, null=True,
                                 default=1, verbose_name=u"状态")

    def __unicode__(self):
        return str(self.id)

    class Meta:
        db_table = u"recommend_commodity"
        verbose_name = u"推荐位置"
        verbose_name_plural = verbose_name
