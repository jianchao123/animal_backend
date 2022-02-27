# coding:utf-8
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, \
    PermissionsMixin
from django.db import models


class UserProfileManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password,
                     is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        now = datetime.now()
        user = self.model(email=email, username=email,
                          is_staff=is_staff, status=1,
                          is_superuser=is_superuser,
                          create_time=now, **extra_fields)

        user.set_password(password)

        # 更新uid
        user.uid = '%08d' % (10000000 + user.id)
        user.save()

        return user

    def create_user(self, email=None, password=None, **extra_fields):
        return self._create_user(email, password, 0, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, 1, True, **extra_fields)


class UserProfileBasic(AbstractBaseUser, PermissionsMixin):
    status_tuple = (
        (1, u"启用"),
        (0, u"禁用"),
    )
    staff_tuple = (
        (1, u"是"),
        (0, u"否"),
    )

    uid = models.CharField(max_length=16, blank=True, null=True,
                           verbose_name=u"uid")
    first_name = models.CharField(max_length=30, blank=True,
                                  verbose_name=u"名字")
    last_name = models.CharField(max_length=30, blank=True, verbose_name=u"姓氏")
    username = models.CharField(max_length=32, blank=True, null=True,
                                unique=True, verbose_name=u"用户名")
    nickname = models.CharField(max_length=32, blank=True, null=True,
                                verbose_name=u"昵称")
    sex = models.IntegerField(blank=True, null=True, verbose_name=u"性别")
    province = models.CharField(max_length=32, blank=True, null=True,
                                verbose_name=u"省")
    city = models.CharField(max_length=32, blank=True, null=True,
                            verbose_name=u"市")
    country = models.CharField(max_length=32, blank=True, null=True,
                               verbose_name=u"国家")
    headimage = models.CharField(max_length=128, blank=True, null=True,
                                 verbose_name=u"头像")
    email = models.CharField(max_length=32, blank=True, null=True, unique=True,
                             verbose_name=u"邮箱")
    phone = models.CharField(max_length=16, blank=True, null=True, unique=True,
                             verbose_name=u"手机")
    is_staff = models.IntegerField(blank=True, null=True, choices=staff_tuple,
                                   verbose_name=u"是否职员")
    is_active = models.BooleanField(default=True, verbose_name=u"是否激活")
    status = models.IntegerField(choices=status_tuple, blank=True, null=True,
                                 default=1, verbose_name=u"状态")
    create_time = models.DateTimeField(blank=True, null=True,
                                       auto_now_add=True,
                                       verbose_name=u"创建时间")

    objects = UserProfileManager()

    # 该字段指定用户的用户名字段
    USERNAME_FIELD = u'username'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = u'user_profile_basic'
        verbose_name = u"用户"
        verbose_name_plural = verbose_name

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        return self.nickname

    def get_short_name(self):
        "Returns the short name for the user."
        return self.nickname

    def is_role(self, role_name):
        """是否拥有该角色"""
        return self.groups.filter(name=role_name).count()

    def __unicode__(self):
        return str(self.pk)


class GamePlayer(UserProfileBasic):
    """游戏玩家"""
    system_tuple = (
        (1, u"IOS"),
        (0, u"ANDROID"),
    )

    ip = models.CharField(max_length=32, blank=True, null=True,
                          verbose_name=u"ip")
    ip_address = models.CharField(max_length=64, blank=True, null=True,
                                  verbose_name=u"ip地址")
    balance_b = models.DecimalField(max_digits=16, decimal_places=6,
                                    blank=True,
                                    null=True,
                                    verbose_name=u"余额")
    has_been_spending_b = models.DecimalField(max_digits=16, decimal_places=6,
                                              blank=True, null=True,
                                              verbose_name=u"已消费")
    deposit_cny = models.DecimalField(max_digits=16, decimal_places=6,
                                      blank=True, null=True,
                                      verbose_name=u"充值金额")
    presents_b = models.DecimalField(max_digits=16, decimal_places=6,
                                     blank=True, null=True,
                                     verbose_name=u"赠送的币")
    participate_count = models.IntegerField(blank=True, null=True,
                                            verbose_name=u"参与次数")
    win_prize_count = models.IntegerField(blank=True, null=True,
                                          verbose_name=u"中奖次数")
    # 该用户所有中奖期数的总费用
    snatch_treasure_b = models.DecimalField(max_digits=16,
                                            decimal_places=6,
                                            blank=True, null=True,
                                            verbose_name=u"夺宝价")
    # 该用户所有中奖期数的总市场价值
    market_price_cny = models.DecimalField(max_digits=16,
                                           decimal_places=6,
                                           blank=True, null=True,
                                           verbose_name=u"市场价")
    # 总中奖金额(兑换价)
    win_prize_amounts = models.DecimalField(max_digits=16,
                                            decimal_places=6,
                                            default=0.0,
                                            blank=True, null=True,
                                            verbose_name=u"总中奖金额")
    # 亏损金额
    loss_amounts = models.DecimalField(max_digits=16,
                                       decimal_places=6,
                                       default=0.0,
                                       blank=True, null=True,
                                       verbose_name=u"亏损金额")
    # 亏损比例
    loss_rate = models.DecimalField(max_digits=16, decimal_places=6,
                                    default=0.0,
                                    blank=True, null=True, verbose_name=u"亏损率")

    system = models.IntegerField(choices=system_tuple,
                                 blank=True, null=True, verbose_name=u"系统")
    is_robot = models.BooleanField(default=False, verbose_name=u"是否机器人")

    @property
    def get_nickname(self):
        if self.nickname:
            return self.nickname
        else:
            return self.phone[:3] + "******" + self.phone[-2:]

    @property
    def get_phone(self):
        return self.phone[:3] + "******" + self.phone[-2:]

    @property
    def get_ip(self):
        if not self.ip:
            return '0.0.0.0'
        ip_arrs = self.ip.split(".")
        return ip_arrs[0] + "." + ip_arrs[1] + "." + ip_arrs[2] + "." + "***"

    @property
    def get_ip_address(self):
        if not self.ip_address:
            return ""
        return self.ip_address

    @property
    def get_head_image(self):
        return settings.STATIC_DOMAIN + self.headimage

    def __unicode__(self):
        return u"{}[{}][id={}]".format(self.phone, self.nickname, self.pk)

    class Meta(UserProfileBasic.Meta):
        db_table = u"game_player"
        verbose_name = u"游戏玩家"
        verbose_name_plural = verbose_name


class Administrator(UserProfileBasic):
    """管理员"""

    def __unicode__(self):
        return u"管理员名字={}".format(self.username)

    class Meta:
        db_table = u"administrator"
        verbose_name = u"管理员"
        verbose_name_plural = verbose_name


class Wallet(models.Model):
    """
    钱包 (B=玩家角色, CNY=回收商角色)
    """
    unit_tuple = (
        (1, u"B"),
        (2, u"CNY"),
    )

    user = models.OneToOneField(UserProfileBasic,
                                related_name=u"wallet_user_set",
                                unique=True, verbose_name=u"用户")
    balance = models.DecimalField(max_digits=16,
                                  decimal_places=6,
                                  blank=True,
                                  null=True,
                                  verbose_name=u"余额")
    unit = models.IntegerField(choices=unit_tuple, blank=True,
                               null=True,
                               verbose_name=u"单位")
    last_update_time = models.DateTimeField(blank=True, null=True,
                                            auto_now_add=True,
                                            verbose_name=u"最后更新时间")

    def __unicode__(self):
        return str(self.pk)

    class Meta:
        db_table = u"wallet"
        verbose_name = u"钱包"
        verbose_name_plural = verbose_name


class Messages(models.Model):
    status_tuple = (
        (1, u"未发送"),
        (2, u"已发送"),
        (3, u"发送失败"),
        (10, u"删除"),

    )

    title = models.CharField(max_length=64, blank=True, null=True,
                             verbose_name=u"标题")
    content = models.CharField(max_length=128, blank=True, null=True,
                               verbose_name=u"内容")
    to_player = models.ForeignKey(GamePlayer, related_name=u"msg_tp_set",
                                  blank=True, null=True,
                                  verbose_name=u"发送给")
    from_user = models.CharField(max_length=32, blank=True, null=True,
                                 verbose_name=u"发送人")
    status = models.IntegerField(choices=status_tuple, blank=True, null=True,
                                 default=2, verbose_name=u"状态")
    create_time = models.DateTimeField(auto_now_add=True, blank=True,
                                       null=True, verbose_name=u"创建时间")

    def __unicode__(self):
        return self.title

    class Meta:
        db_table = u"messages"
        verbose_name = u"消息"
        verbose_name_plural = verbose_name


class TieBaUserInfo(models.Model):
    nickname = models.CharField(max_length=32, verbose_name=u"昵称")
    headimg = models.CharField(max_length=128, verbose_name=u"头像")
    user = models.ForeignKey(UserProfileBasic, related_name=u"tb_users",
                             blank=True, null=True, verbose_name=u"用户")

    def __unicode__(self):
        return self.nickname

    class Meta:
        db_table = u"tbuser"
        verbose_name = u"贴吧用户"
        verbose_name_plural = verbose_name


class RobotIp(models.Model):
    ip = models.CharField(max_length=32, verbose_name=u"ip")
    address = models.CharField(max_length=32, verbose_name=u"地址")

    def __unicode__(self):
        return self.ip

    class Meta:
        db_table = u"robot_ip"
        verbose_name = u"机器人备用ip"
        verbose_name_plural = verbose_name
