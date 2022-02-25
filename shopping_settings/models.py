# coding:utf-8
from django.db import models
from shopping_user.models import Administrator, GamePlayer


class CommodityType(models.Model):
    """商品类型"""
    status_tuple = (
        (1, u"启用"),
        (2, u"禁用"),
    )

    type_name = models.CharField(max_length=32, blank=True, null=True,
                                 verbose_name=u"类型名字")
    type_code = models.CharField(max_length=8, blank=True, null=True,
                                 verbose_name=u"类型CODE")
    type_index = models.IntegerField(blank=True, null=True,
                                     unique=True, verbose_name=u"类型顺序")
    status = models.IntegerField(choices=status_tuple, blank=True,
                                 null=True, verbose_name=u"状态")

    def __unicode__(self):
        return u"pk={}, {}".format(str(self.pk), self.type_name)

    class Meta:
        db_table = u"commodity_type"
        verbose_name = u"商品类型"
        verbose_name_plural = verbose_name


class BuyChannel(models.Model):
    """进货渠道"""

    channel_code = models.CharField(max_length=8, blank=True, null=True,
                                    verbose_name=u"code")
    remark = models.CharField(max_length=32, blank=True, null=True,
                              verbose_name=u"备注")

    def __unicode__(self):
        return u"{},{}".format(self.channel_code, self.remark)

    class Meta:
        db_table = u"buy_channel"
        verbose_name = u"进货渠道"
        verbose_name_plural = verbose_name


class Notice(models.Model):
    """公告"""
    status_tuple = (
        (1, u"启用"),
        (2, u"删除"),
    )
    type_tuple = (
        (1, u"常用"),
        (2, u"重要"),
        (3, u"重磅"),
    )
    is_notice = (
        (1, u"是"),
        (0, u"否"),
    )

    title = models.CharField(max_length=54, blank=True, null=True,
                             verbose_name=u"标题")
    content = models.TextField(blank=True, null=True, verbose_name=u"内容")

    notice_type = models.IntegerField(choices=type_tuple, blank=True,
                                      null=True,
                                      default=1, verbose_name=u"类型")
    status = models.IntegerField(choices=status_tuple, blank=True, null=True,
                                 default=1, verbose_name=u"状态")
    index = models.IntegerField(blank=True, null=True, verbose_name=u"顺序")
    administrator = \
        models.ForeignKey(Administrator, related_name=u"notice_admin_set",
                          blank=True, null=True,
                          verbose_name=u"创建人")
    is_notice_businessman = \
        models.IntegerField(choices=is_notice, blank=True,
                            null=True,
                            default=1, verbose_name=u"是否通知回收商")
    create_time = models.DateTimeField(auto_now_add=True, blank=True,
                                       null=True, verbose_name=u"创建时间")

    def __unicode__(self):
        return str(self.title)

    class Meta:
        db_table = u"notice"
        verbose_name = u"公告"
        verbose_name_plural = verbose_name


class Banner(models.Model):
    """banner"""

    status_tuple = (
        (1, u"启用"),
        (2, u"删除"),
    )

    title = models.CharField(max_length=54, blank=True, null=True,
                             verbose_name=u"标题")
    image_path = models.CharField(max_length=128, blank=True, null=True,
                                  verbose_name=u"图片路径")
    link = models.CharField(max_length=128, blank=True, null=True,
                            verbose_name=u"超链接")
    index = models.IntegerField(blank=True, null=True, verbose_name=u"顺序")
    status = models.IntegerField(choices=status_tuple, blank=True, null=True,
                                 default=1, verbose_name=u"状态")
    administrator = \
        models.ForeignKey(Administrator, related_name=u"banner_admin_set",
                          blank=True, null=True,
                          verbose_name=u"创建人")
    create_time = models.DateTimeField(auto_now_add=True, blank=True,
                                       null=True, verbose_name=u"创建时间")

    def __unicode__(self):
        return self.title

    class Meta:
        db_table = u"banner"
        verbose_name = u"banner"
        verbose_name_plural = verbose_name


class Area(models.Model):
    level_tuple = (
        (0, u"省"),
        (1, u"市"),
        (2, u"区县"),
    )

    pid = models.IntegerField(blank=True, null=True, verbose_name=u"父id")
    shortname = models.CharField(max_length=32, blank=True, null=True,
                                 verbose_name=u"简称")
    name = models.CharField(max_length=32, blank=True, null=True,
                            verbose_name=u"名称")
    merger_name = models.CharField(max_length=128, blank=True, null=True,
                                   verbose_name=u"全称")
    level = models.IntegerField(choices=level_tuple,
                                blank=True, null=True, verbose_name=u"层级")
    pinyin = models.CharField(max_length=256, blank=True, null=True,
                              verbose_name=u"拼音")
    code = models.CharField(max_length=16, blank=True, null=True,
                            verbose_name=u"长途区号")
    zip_code = models.CharField(max_length=16, blank=True, null=True,
                                verbose_name=u"邮编")
    first = models.CharField(max_length=8, blank=True, null=True,
                             verbose_name=u"首字母")
    lng = models.CharField(max_length=32, blank=True, null=True,
                           verbose_name=u"经度")
    lat = models.CharField(max_length=32, blank=True, null=True,
                           verbose_name=u"纬度")

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = u"sh_area"
        verbose_name = u"区域"
        verbose_name_plural = verbose_name


class PayType(models.Model):
    """支付类型"""
    status_tuple = (
        (1, u"使用中"),
        (2, u"禁用中")
    )

    pay_name = models.CharField(max_length=32, blank=True,
                                null=True, verbose_name=u"支付名字")
    code = models.CharField(max_length=32, blank=True,
                            null=True, verbose_name=u"代码")
    pay_rates = models.DecimalField(max_digits=8,
                                    decimal_places=4,
                                    blank=True,
                                    null=True,
                                    verbose_name=u"三方收取费率")
    is_third_party = models.BooleanField(default=False,
                                         verbose_name=u"是否三方充值")
    status = models.IntegerField(choices=status_tuple, default=1,
                                 verbose_name=u"状态")

    def __unicode__(self):
        return u"{},{}".format(self.pay_name, str(self.pay_rates))

    class Meta:
        db_table = u"pay_type"
        verbose_name = u"支付类型"
        verbose_name_plural = verbose_name


class PayChannel(models.Model):
    """支付通道"""

    status_tuple = (
        (1, u"正常"),
        (2, u"异常"),
    )
    code = models.CharField(max_length=16, blank=True, null=True,
                            verbose_name=u"通道编码")
    name = models.CharField(max_length=128, blank=True, null=True,
                            verbose_name=u"通道名字")
    rate = models.DecimalField(max_digits=8,
                               decimal_places=4,
                               blank=True,
                               null=True,
                               verbose_name=u"费率")
    money_str = models.CharField(max_length=64, blank=True, null=True,
                                 verbose_name=u"金额")
    pay_type = models.ForeignKey(PayType, blank=True, null=True,
                                 related_name=u"pac_pt_set",
                                 verbose_name=u"支付类型")
    company = models.CharField(max_length=16, blank=True, null=True,
                               verbose_name=u"三方公司") # 例如:爱立付
    status = models.IntegerField(choices=status_tuple, default=1,
                                 verbose_name=u"状态")

    def __unicode__(self):
        return u"{}".format(self.pk)

    class Meta:
        db_table = u"pay_channel"
        verbose_name = u"支付通道"
        verbose_name_plural = verbose_name


class PayAccountsConf(models.Model):
    """支付账户配置"""
    status_tuple = (
        (1, u"正常"),
        (2, u"异常"),
        (3, u"封停中")
    )
    pay_channel = models.ForeignKey(PayChannel, related_name=u"pac_pc_set",
                                    blank=True, null=True,
                                    verbose_name=u"支付通道")
    merchant_no = models.CharField(max_length=32, blank=True, null=True,
                                   verbose_name=u"商户号")
    status = models.IntegerField(choices=status_tuple, default=1,
                                 verbose_name=u"状态")
    is_use = models.BooleanField(default=True, verbose_name=u"是否使用中")
    remark = models.TextField(blank=True, null=True, verbose_name=u"备注")
    operator = models.ForeignKey(Administrator, blank=True, null=True,
                                 verbose_name=u"操作员")

    def __unicode__(self):
        return u"{}".format(self.pk)

    class Meta:
        db_table = u"pay_accounts_conf"
        verbose_name = u"支付帐号配置"
        verbose_name_plural = verbose_name


class PayMoneyCtl(models.Model):
    """支付金额控制器"""

    status_tuple = (
        (1, u"显示"),
        (2, u"屏蔽"),
    )
    min = models.IntegerField(default=0,
                              verbose_name=u"最小金额")
    max = models.IntegerField(default=0,
                              verbose_name=u"最大金额")

    history_min = models.IntegerField(default=0,
                                      verbose_name=u"历史最小金额")
    history_max = models.IntegerField(default=0,
                                      verbose_name=u"历史最大金额")
    pay_channel = models.ForeignKey(PayChannel, related_name=u"pmc_pc_set",
                                    blank=True, null=True,
                                    verbose_name=u"支付通道")
    status = models.IntegerField(choices=status_tuple, default=1,
                                 verbose_name=u"状态")
    operator = models.ForeignKey(Administrator, blank=True, null=True,
                                 verbose_name=u"操作员")

    def __unicode__(self):
        return u"{}".format(self.pk)

    class Meta:
        db_table = u"pay_money_ctl"
        verbose_name = u"支付金额控制器"
        verbose_name_plural = verbose_name


class CommonParamConf(models.Model):
    """公共配置"""

    conf_name = models.CharField(max_length=32, blank=True,
                                 null=True, verbose_name=u"配置名字")
    conf_key = models.CharField(max_length=32, blank=True,
                                null=True, verbose_name=u"key")
    conf_value = models.CharField(max_length=384, blank=True,
                                  null=True, verbose_name=u"value")

    def __unicode__(self):
        return u"{}".format(self.pk)

    class Meta:
        db_table = u"common_param_conf"
        verbose_name = u"公共配置"
        verbose_name_plural = verbose_name


class ShippingAddress(models.Model):
    """配送地址"""
    player = models.ForeignKey(GamePlayer, related_name=u"address_player_set",
                               blank=True, null=True,
                               verbose_name=u"玩家")
    recipents_name = models.CharField(max_length=16, blank=True,
                                      null=True,
                                      verbose_name=u"收件人名字")
    recipents_phone = models.CharField(max_length=16, blank=True,
                                       null=True,
                                       verbose_name=u"收件人号码")
    province = models.ForeignKey(Area, blank=True, null=True,
                                 related_name=u"sa_province_set",
                                 verbose_name=u"省")
    city = models.ForeignKey(Area, blank=True, null=True,
                             related_name=u"sa_city_set", verbose_name=u"市")
    area = models.ForeignKey(Area, blank=True, null=True,
                             related_name=u"sa_area_set", verbose_name=u"区")
    recipents_address = models.CharField(max_length=128, blank=True,
                                         null=True,
                                         verbose_name=u"收件人地址")
    is_default = models.BooleanField(default=False, verbose_name=u"是否默认")

    def __unicode__(self):
        return u"pk={}, {}, {}".format(str(self.pk), self.recipents_name,
                                       self.recipents_address)

    class Meta:
        db_table = u"shipping_address"
        verbose_name = u"配送地址"
        verbose_name_plural = verbose_name


class SectionMoneyRecord(models.Model):
    """充值流水区间记录"""

    section_mix = models.IntegerField(default=0, verbose_name=u"区间最小金额")
    section_max = models.IntegerField(default=0, verbose_name=u"区间最大金额")
    present_amounts = models.IntegerField(default=0, verbose_name=u"赠送数量")
    text = models.TextField(default="", verbose_name=u"号码文本")

    def __unicode__(self):
        return str(self.id)

    class Meta:
        db_table = u"section_money_record"
        verbose_name = u"充值流水金额区间"
        verbose_name_plural = verbose_name


class FeesUseRecord(models.Model):
    """费用使用记录"""
    text = models.TextField(verbose_name=u"费用记录")
    use_time = models.DateTimeField(verbose_name=u"费用使用时间")
    create_time = models.DateTimeField(auto_now_add=True,
                                       verbose_name=u"创建世界")

    def __unicode__(self):
        return str(self.id)

    class Meta:
        db_table = u"fees_use_record"
        verbose_name = u"费用使用记录"
        verbose_name_plural = verbose_name