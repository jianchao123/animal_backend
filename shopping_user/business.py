# coding:utf-8
import random, string
from Crypto.Cipher import AES
from decimal import Decimal
from datetime import datetime
from models import Wallet, UserProfileBasic, GamePlayer
from recycle_businessman.models import InviteRecord, RecycleBusinessman
from django.contrib.auth.models import Group
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from utils.AppError import AppError
from utils import code_set
from django.conf import settings
from utils.cache_util import CacheUtil


@transaction.atomic
def change_wallet(amounts, unit=None, user_id=None):
    try:
        wallet = Wallet.objects.select_for_update().get(
            user_id=user_id, unit=unit)
    except (ObjectDoesNotExist, MultipleObjectsReturned):
        return False
    wallet.balance += Decimal(str(amounts))
    if wallet.balance < 0.0:
        return False   # 余额不足
    wallet.save()
    return True


@transaction.atomic
def signup_gameplayer(password, phone, invite_code=None,
                      is_robot=None, nickname=None, headimg=None):
    # 创建玩家信息记录
    player = GamePlayer()
    player.phone = phone
    player.username = str(phone)
    player.email = str(phone) + "@default.com"
    player.headimage = settings.DEFAULT_HEAD_IMG
    player.is_active = True
    player.is_staff = False

    if not password:
        chars = string.ascii_letters + string.digits
        pwd = ''.join([random.choice(chars) for i in range(AES.block_size)])
        player.set_password(pwd)
    else:
        player.set_password(password)
    if is_robot:
        player.is_robot = True
    if nickname:
        player.nickname = nickname
    if headimg:
        player.headimage = headimg

    player.save()
    player.uid = "1%05d" % player.pk
    player.save()
    user_profile_basic = UserProfileBasic.objects.get(pk=player.pk)
    # 添加到玩家组
    group = Group.objects.get(name=u"玩家")
    player.groups.add(group)
    # 初始化钱包
    wallet = Wallet()
    wallet.user = user_profile_basic
    wallet.balance = 0.0
    wallet.unit = code_set.WalletUnit.B[0]
    wallet.last_update_time = datetime.now()
    wallet.save()
    # 添加邀请记录
    if invite_code:
        try:
            recycle_businessman = \
                RecycleBusinessman.objects.get(invite_code=invite_code)
        except ObjectDoesNotExist:
            raise AppError(*code_set.SubErrorCode.INVITE_CODE_ERROR)
        invite_record = InviteRecord()
        invite_record.recycle_businessman = recycle_businessman
        invite_record.invite_player = player
        invite_record.save()
    return player


def set_login_limit(phone):
    """设置登陆限制"""
    r = CacheUtil.get_pwd_err_count(phone)
    if r:
        CacheUtil.incr_pwd_err_count(phone)
    else:
        CacheUtil.set_pwd_err_count(phone)