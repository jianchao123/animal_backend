# coding:utf-8
"""捕获business.py抛出异常"""

import re, time, requests, json

from collections import defaultdict
from datetime import datetime, timedelta
from decimal import Decimal

# django 包
import django_filters
from django.db import transaction
from django.conf import settings
from django.db.models import Q, Sum
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.contrib.auth.models import Group
from django.contrib import auth

# rest framework 包
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework import filters
from rest_framework import permissions

# models
from models import GamePlayer, Wallet, \
    UserProfileBasic, Administrator, TieBaUserInfo
from snatch_treasure.models import DuoBaoParticipateRecord
from recycle_businessman.models import InviteRecord, RecycleRecord, \
    UserConsignee, RecycleBusinessman
from financial.models import PrizeRecord, DepositRecord
from inventory.models import CardInventories, \
    CardEntryRecord, Card, CardDeliveryRecord
from rest.models import GoodsDeliverRecord
from snatch_treasure.models import UserCard
from shopping_settings.models import ShippingAddress, CommonParamConf
from activitys.models import SunTheOrder

# serializers
from serializers import GamePlayerSerializer, \
    AdministratorSerializer, TiebaSerializer
from resources.serializers import ImagesSerializer

# permissions
from permissions import IsAdministratorPermission, \
    IsGamePlayer, IsAdminOrBusinessman
from paginations import LargeResultsSetPagination

# utils
from utils.utils import generate_code, generate_qr_code, get_qiniu_token
from utils.cache_util import CacheUtil
from utils import code_set
from utils.framework import post_require_check, get_require_check
from utils.AppError import AppError

# tasks
from shopping_user.tasks import send_sms, signup_present

# business
from business import change_wallet, signup_gameplayer, set_login_limit
from financial import business as financial_business

import logging

logger = logging.getLogger(__name__)


# ################################## common ##################################
class GetQiniuToken(APIView):
    @get_require_check(["upload_file_name"])
    def get(self, request):
        """获取七牛上传token"""
        upload_file_name = request.query_params.get("upload_file_name")
        return get_qiniu_token(upload_file_name.encode('utf-8'))


class SendSignInCode(APIView):
    """发送登陆code"""

    @get_require_check(["phone"])
    def get(self, request):
        phone = request.query_params.get("phone")
        r = CacheUtil.get_sms_interval(phone)
        if r:
            raise AppError(*code_set.SubErrorCode.TRY_AGAIN_MINUTE)

        if not phone or not re.match(r"1[3|4|5|7|8][0-9]{9}", phone):
            raise AppError(*code_set.SubErrorCode.PHONE_NUMBER_FORMAT_ERROR)

        code = CacheUtil.get_signin_code(phone)
        # 上一次的验证码已失效,重新生成
        if not code:
            code = generate_code()

        ret = CacheUtil.set_signin_code(phone, code)
        if not ret:
            raise AppError(*code_set.SubErrorCode.MSG_LIMIT_ERROR)
        logger.error(str(code))
        send_sms.apply_async(args=[phone, code],
                             exchange='user',
                             routing_key="sms")
        CacheUtil.set_sms_interval(phone)
        return {}


# #################################### app ###################################

class AppSignIn(APIView):
    """app登陆"""

    @post_require_check([])
    def post(self, request):
        phone = request.data.get("phone")
        password = request.data.get("password", None)
        code = request.data.get("code", None)

        r = CacheUtil.get_pwd_err_count(phone)
        if r and int(r) > 4:
            raise AppError(*code_set.SubErrorCode.PHONE_LIMIT_THE_LOGIN)

        # password 和 code必须要有一个
        if not password and not code:
            raise AppError(*code_set.GlobalErrorCode.PARAM_ERROR)

        try:
            user_profile_basic = UserProfileBasic.objects.get(phone=phone)
            # 不是玩家和卡商不能使用此接口
            if user_profile_basic.is_role(u"管理员"):
                raise AppError(
                    *code_set.SubErrorCode.BUSINESS_NUMBER_NOT_LOGIN)
            # 在黑名单中
            if not user_profile_basic.is_active:
                raise AppError(*code_set.SubErrorCode.IN_BLACKLIST_ERROR)
        except ObjectDoesNotExist:
            # 如果是密码登陆,还不存在的用户,直接报错
            if password:
                raise AppError(*code_set.SubErrorCode.MISSING_PHONE_ERROR)
            elif code:
                # 该用户不存在且是code登陆, 且code是正确的, 就直接添加该用户
                code_dup = CacheUtil.get_signin_code(phone)
                if not code_dup:
                    raise AppError(*code_set.SubErrorCode.SIGNUP_INVALID_ERROR)
                if code_dup and int(code_dup) != int(code):
                    raise AppError(*code_set.SubErrorCode.SIGNUP_INVALID_ERROR)
                # 都满足的情况下
                new_player = signup_gameplayer(password, phone)
                signup_present.apply_async(
                    args=[phone], exchange='user',
                    routing_key="signup_present")

                user_profile_basic = \
                    UserProfileBasic.objects.get(pk=new_player.pk)
            else:
                raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)

        # 密码登陆
        if password:
            # 验证密码
            user_profile_basic = \
                auth.authenticate(username=user_profile_basic.username,
                                  password=password)
            # 密码错误
            if not user_profile_basic:
                set_login_limit(phone)
                raise AppError(*code_set.SubErrorCode.PWD_INCORRECT_ERROR)

        # 验证码登陆
        elif code:
            # 验证码错误
            code_dup = CacheUtil.get_signin_code(phone)
            if not code_dup or int(code_dup) != int(code):
                set_login_limit(phone)
                raise AppError(*code_set.SubErrorCode.SIGNUP_INVALID_ERROR)
            # 获取用户
            user_profile_basic = UserProfileBasic.objects.get(phone=phone)
        else:
            raise AppError(*code_set.SubErrorCode.PWD_INCORRECT_ERROR)

        # 查询是否已经登陆
        print user_profile_basic.get_session_auth_hash()

        # 登陆
        auth.login(request, user_profile_basic)
        user_info = defaultdict()
        if user_profile_basic.is_role(u"玩家"):
            try:
                gameplayer = GamePlayer.objects.get(pk=user_profile_basic.pk)
                if not gameplayer.is_robot:
                    self._get_ip(gameplayer, request)
                    gameplayer.last_login = datetime.now()
                    gameplayer.save()

                # 返回的用户信息
                user_info["pk"] = gameplayer.pk
                user_info["uid"] = gameplayer.uid
                user_info["headimage"] = gameplayer.get_head_image
                user_info["nickname"] = gameplayer.get_nickname
                user_info["phone"] = gameplayer.phone

                wallet = Wallet.objects.get(Q(user_id=user_profile_basic.pk) &
                                            Q(unit=code_set.WalletUnit.B[
                                                0]))
                user_info["balance"] = wallet.balance
                user_info["role"] = u"玩家"

            except ObjectDoesNotExist:
                raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)
        elif user_profile_basic.is_role(u"回收商"):
            recycle_businessman = RecycleBusinessman.objects.get(
                Q(pk=user_profile_basic.pk))
            user_info["nickname"] = recycle_businessman.nickname
            user_info['pk'] = recycle_businessman.pk
            user_info['username'] = recycle_businessman.username
            user_info["role"] = u"回收商"

        user_info["csrftoken"] = request.META["CSRF_COOKIE"]
        user_info["sessionid"] = \
            request.session.session_key if request.session.session_key else None
        return user_info

    def _get_ip(self, gameplayer, request):
        if request.META.has_key('HTTP_X_FORWARDED_FOR'):
            ip = request.META['HTTP_X_FORWARDED_FOR']
        else:
            ip = request.META['REMOTE_ADDR']
        if "," in ip:
            ip = ip.split(",")[0]
        logger.error("ip_address={}".format(str(ip)))
        gameplayer.ip = ip
        # ip归属地查询,聚合数据
        res = requests.get(
            "http://apis.juhe.cn/ip/ip2addr?"
            "ip={}&dtype=json&key={}".format(ip,
                                             settings.JUHE_DATA_KEY))
        if res.content:
            content = json.loads(res.content)
            logger.error("ip_address={}".format(str(content)))
            if int(content["resultcode"]) == 200:
                ip_address = content["result"]["area"] + " " + \
                             content["result"]["location"]
                gameplayer.ip_address = ip_address


class UserInformation(generics.ListAPIView):
    """用户信息 app"""

    @get_require_check([])
    def get(self, request, *args, **kwargs):
        player_pk = request.query_params.get("player_pk", None)
        user = request.user
        print user.is_authenticated(), player_pk
        # 未登陆且未传参
        if not user.is_authenticated() and not player_pk:
            raise AppError(*code_set.GlobalErrorCode.PARAM_ERROR)

        if player_pk:
            player_id = player_pk
        else:
            player_id = user.pk
        try:
            player = GamePlayer.objects.get(pk=player_id)
        except ObjectDoesNotExist:
            raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)
        # 公共返回值
        data = {
            "pk": player.pk,
            "nickname": player.get_nickname,
            "uid": player.uid,
            "headimage": player.get_head_image,
            "sex": player.sex
        }
        # 已经登陆且查询的是自己
        if user.is_authenticated() and not player_pk:
            wallet = Wallet.objects.get(Q(user_id=player.pk) &
                                        Q(unit=code_set.WalletUnit.B[0]))
            data["balance"] = int(wallet.balance)
            data["ip"] = player.ip
            data["ip_address"] = player.ip_address
        else:
            data["phone"] = player.get_phone
            data["ip"] = player.get_ip
            data["ip_address"] = player.get_ip_address
        return data


class SendSignUpCode(APIView):
    """发送注册code"""

    @get_require_check(["phone"])
    def get(self, request):
        phone = request.query_params.get("phone")

        if not phone or not re.match(r"1[3|4|5|6|7|8|9][0-9]{9}", phone):
            raise AppError(*code_set.SubErrorCode.PHONE_NUMBER_FORMAT_ERROR)

        r = CacheUtil.get_sms_interval(phone)
        if r:
            raise AppError(*code_set.SubErrorCode.TRY_AGAIN_MINUTE)

        # 检查手机是否注册
        try:
            GamePlayer.objects.get(phone=phone)
            raise AppError(*code_set.SubErrorCode.PHONE_NUMBER_REGISTERED)
        except ObjectDoesNotExist:
            pass

        code = CacheUtil.get_signup_code(phone)
        # 上一次的验证码已失效
        if not code:
            code = generate_code()

        # 设置并发送短信
        ret = CacheUtil.set_signup_code(phone, code)
        if not ret:
            raise AppError(*code_set.SubErrorCode.MSG_LIMIT_ERROR)
        logger.error("code={} ".format(code))
        send_sms.apply_async(args=[phone, code],
                             exchange='user',
                             routing_key="sms")
        CacheUtil.set_sms_interval(phone)
        return {}


class SignUpGamePlayer(APIView):
    """
    注册玩家
    """

    @post_require_check(["phone", "password", "code"])
    @transaction.atomic
    def post(self, request):
        phone = request.data.get("phone")
        password = request.data.get("password")
        code = request.data.get("code")
        invite_code = request.data.get("invite_code", None)
        logger.error("phone={} ".format(phone))
        code_dup = CacheUtil.get_signup_code(phone)
        if not code_dup or int(code) != int(code_dup):
            raise AppError(*code_set.SubErrorCode.SIGNUP_INVALID_ERROR)

        try:
            UserProfileBasic.objects.get(phone=phone)
            raise AppError(*code_set.SubErrorCode.PHONE_NUMBER_REGISTERED)
        except ObjectDoesNotExist:
            pass

        signup_gameplayer(password, phone, invite_code)
        signup_present.apply_async(
            args=[phone], exchange='user', routing_key="signup_present")
        return {}


class AcceptPrize(generics.CreateAPIView):
    """
    领奖
        从中奖记录表将数据提取出来, 不可使用商品表, 商品表数据会被随时更改的
    """

    permission_classes = (IsGamePlayer,)

    @post_require_check(["prize_record_pk", "accept_prize_type"])
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        accept_prize_type = int(request.data["accept_prize_type"])
        prize_record_pk = int(request.data["prize_record_pk"])
        # 回收号 或者 兑换号
        phone = request.data.get("phone", None)
        shipping_address_pk = request.data.get("shipping_address_pk", None)
        shipping_address_pk = int(shipping_address_pk) if shipping_address_pk else None

        user = request.user
        ret_data = {}
        if accept_prize_type not in (1, 2, 3):
            raise AppError(*code_set.GlobalErrorCode.PARAM_ERROR)

        try:
            prize_record = PrizeRecord.objects.select_for_update().get(
                pk=prize_record_pk)
            game_player = GamePlayer.objects.get(pk=user.pk)
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)
        # 不是这个玩家的,状态不是未领奖的
        if prize_record.player.id != game_player.id or prize_record.status != \
                code_set.PrizeStatusCode.NOT_ACCEPT_PRIZE[0]:
            raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)
        if game_player.is_robot:
            raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)
        period = prize_record.period
        commodity = period.commodity

        # 用户选择的兑换豆
        # if accept_prize_type == 1:
        #     try:
        #         user_consignee = UserConsignee.objects.get(
        #             Q(player=game_player) & Q(flag=2))
        #     except ObjectDoesNotExist:
        #         raise AppError(
        #             *code_set.SubErrorCode.RECYCLE_PHONE_MISSING_ERROR)
        #     try:
        #         businessman = RecycleBusinessman.objects.get(
        #             Q(dh_phone=user_consignee.phone))
        #     except ObjectDoesNotExist:
        #         raise AppError(
        #             *code_set.SubErrorCode.RECYCLE_PHONE_MISSING_ERROR)
        #     # 直接给用户增加余额
        #     result_code = change_wallet(prize_record.amounts, unit=1,
        #                                 user_id=user.pk)
        #     if not result_code:
        #         raise AppError(
        #             *code_set.SubErrorCode.NOT_SUFFICIENT_FUNDS_ERROR)
        #     # 增加收货记录
        #     self._add_recycle_record(businessman, period, user_consignee.phone,
        #                              prize_record)
        #     # 增加代充记录
        #     financial_business.insert_deposit_record(
        #         game_player, prize_record.amounts, businessman)
        #
        #     prize_record.to_recycle_businessman = businessman
        #     # 领奖方式
        #     prize_record.accept_prize_type = \
        #         code_set.AcceptPrizeType.DHHLD[0]

        # 转到收货人
        if accept_prize_type == 2:
            try:
                businessman = RecycleBusinessman.objects.get(phone=phone)
            except ObjectDoesNotExist:
                raise AppError(
                    *code_set.SubErrorCode.RECYCLE_PHONE_MISSING_ERROR)
            # 添加回收记录
            self._add_recycle_record(businessman, period, phone, prize_record)

            # 回收商
            prize_record.to_recycle_businessman = businessman

            # # 兑换号码
            # if businessman.dh_phone == phone:
            #     # 直接给用户增加余额 (流程相当于先给回收商充值,然后给回收商给用户充值,这里简化了步骤)
            #     result_code = change_wallet(prize_record.amounts, unit=1,
            #                                 user_id=user.pk)
            #     if not result_code:
            #         raise AppError(
            #             *code_set.SubErrorCode.NOT_SUFFICIENT_FUNDS_ERROR)
            #     # 领奖方式
            #     prize_record.accept_prize_type = \
            #         code_set.AcceptPrizeType.DHHLD[0]
            #
            #     # 增加代充记录
            #     financial_business.insert_deposit_record(
            #         game_player, prize_record.amounts, businessman)

            # 收货号码
            if businessman.phone == phone:
                # 给回收商增加余额
                if not change_wallet(prize_record.amounts,
                                     unit=2, user_id=businessman.pk):
                    raise AppError(
                        *code_set.SubErrorCode.RECYCLE_PHONE_USED_ERROR)

                # 领奖方式
                prize_record.accept_prize_type = \
                    code_set.AcceptPrizeType.ZDSHR[0]

        # 领取奖品
        elif accept_prize_type == 3:
            prize_record.accept_prize_type = code_set.AcceptPrizeType.LQJP[0]
            is_card = commodity.is_card
            # 卡密
            if is_card:
                # 从库存获取一张card
                card_inventory = period.commodity.card_inventory

                # 卡密库存不足
                if card_inventory.volumes < 1:
                    prize_record.status = \
                        code_set.PrizeStatusCode.CARD_INVENTORIES_INSUFFICIENT[
                            0]
                    prize_record.accept_prize_time = datetime.now()
                    prize_record.save()
                    d = defaultdict()
                    return {"code": 1,
                            "notice": u"卡密库存余量不足,请联系客服"}
                else:
                    card_inventory.volumes -= 1
                    card_inventory.update_time = datetime.now()
                    card_inventory.save()

                    card = Card.objects.filter(
                        Q(card_inventory=card_inventory) &
                        Q(status=code_set.CardStatusCode.VALID[0]))[0]
                    card.status = code_set.CardStatusCode.USED[0]
                    card.save()

                    # 增加出库记录
                    card_delivery_record = CardDeliveryRecord()
                    card_delivery_record.card_inventory = card_inventory
                    card_delivery_record.volumes = 1
                    card_delivery_record.delivery_time = datetime.now()
                    card_delivery_record.to_player = game_player
                    card_delivery_record.reason = json.dumps(
                        {"period_id": period.pk, "reason": u"中奖"})
                    card_delivery_record.save()

                    # 为用户增加一张卡密
                    user_card = UserCard()
                    user_card.player = game_player
                    user_card.card_number = 1
                    user_card.card_number = card.card_number
                    user_card.card_pwd = card.card_pwd
                    user_card.source = period
                    user_card.save()

                    prize_record.card = card
                    ret_data["code"] = 1
                    ret_data["notice"] = \
                        u"卡券号{},请进入卡号卡密查看".format(card.card_number)
            # 实物
            else:
                try:
                    shipping_address = \
                        ShippingAddress.objects.get(
                            Q(pk=shipping_address_pk) & Q(player=game_player))
                except ObjectDoesNotExist:
                    raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)
                string = "{} {} {} ".format(
                    shipping_address.province.name.encode("utf8"),
                    shipping_address.city.name.encode("utf8"),
                    shipping_address.area.name.encode("utf8"))

                # 添加发货数据
                goods_deliver_record = GoodsDeliverRecord()
                goods_deliver_record.to_player = game_player
                goods_deliver_record.commodity = commodity
                goods_deliver_record.period = period
                goods_deliver_record.recipents_name = \
                    shipping_address.recipents_name
                goods_deliver_record.recipents_phone = \
                    shipping_address.recipents_phone
                goods_deliver_record.recipents_address = \
                    string + shipping_address.recipents_address.encode("utf8")
                goods_deliver_record.quantity = 1
                goods_deliver_record.status = 1
                goods_deliver_record.save()
                # 更新数据
        prize_record.status = code_set.PrizeStatusCode.ACCEPT_PRIZED[0]
        prize_record.accept_prize_time = datetime.now()
        prize_record.save()
        ret_data["prize_record_pk"] = prize_record.id
        return ret_data

    def _add_recycle_record(self, businessman, period, phone, prize_record):
        # 添加收货记录
        recycle_record = RecycleRecord()
        recycle_record.recycle_period_no = period.period_no
        recycle_record.recycle_price = prize_record.amounts
        recycle_record.recycle_trade_no = \
            "RR" + str(int(time.time())) + \
            str(phone) + period.period_no
        recycle_record.period = period
        recycle_record.recycle_businessman = businessman
        recycle_record.commodity = period.commodity
        recycle_record.recycle_time = datetime.now()
        recycle_record.save()


class AcceptPrizeInfo(generics.ListAPIView):
    """领奖信息"""

    permission_classes = (IsGamePlayer,)

    @get_require_check(["prize_record_pk"])
    def get(self, request, *args, **kwargs):
        user = request.user
        prize_record_pk = request.query_params.get("prize_record_pk")
        try:
            player = GamePlayer.objects.get(pk=user.pk)
            prize_record = PrizeRecord.objects.get(
                Q(pk=prize_record_pk) & Q(player=player))
        except ObjectDoesNotExist:
            raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)

        zero = Decimal(str(0.0))
        period = prize_record.period
        ren_ci = DuoBaoParticipateRecord.objects.filter(
            Q(period=period) & Q(player=player)).aggregate(
            Sum('participate_amounts')).values()[0]

        img_l = []
        cover = period.commodity.cover
        for img_row in cover.split(","):
            img_l.append({"image_path": img_row})

        data = {
            "commodity_name": period.commodity.commodity_name,
            "commodity_market_price_cny": period.commodity.market_price_cny,
            "period_pk": period.id,
            "game_player_pk": player.id,
            "luck_player_name": player.get_nickname,
            "luck_player_headimg": player.get_head_image,
            "period_no": period.period_no,
            "luck_token": period.luck_token,
            "participate_amounts": ren_ci if ren_ci else zero,
            "time": period.reward_time.strftime("%Y-%m-%d %H:%M:%S"),
            "commodity_image": img_l,
            "is_card": period.commodity.is_card,
            "accept_prize_type": prize_record.accept_prize_type
        }

        l = [code_set.PrizeStatusCode.ACCEPT_PRIZED[0],
             code_set.PrizeStatusCode.CARD_INVENTORIES_INSUFFICIENT[0]]
        # 卡密不足,算已经领取
        if prize_record.status in l:
            data["is_accept_prize"] = True
        elif prize_record.status == code_set.PrizeStatusCode.NOT_ACCEPT_PRIZE[
            0]:
            data["is_accept_prize"] = False
        # 是否卡券库存不足
        if prize_record.status == \
                code_set.PrizeStatusCode.CARD_INVENTORIES_INSUFFICIENT[0]:
            data["is_insufficient"] = True
        else:
            data["is_insufficient"] = False

        # 判断领奖方式,返回不同的数据
        if prize_record.accept_prize_type == \
                code_set.AcceptPrizeType.DHHLD[0]:
            # 兑换数量
            data["conversion_amounts"] = prize_record.amounts
            data["to_dh_phone"] = \
                prize_record.to_recycle_businessman.dh_phone
        elif prize_record.accept_prize_type == \
                code_set.AcceptPrizeType.ZDSHR[
                    0]:
            # 转让到的收货人号码
            data["to_recycle_phone"] = \
                prize_record.to_recycle_businessman.phone
            data["amounts"] = prize_record.amounts
        elif prize_record.accept_prize_type == \
                code_set.AcceptPrizeType.LQJP[0]:
            if period.commodity.is_card:
                if prize_record.status == \
                        code_set.PrizeStatusCode.CARD_INVENTORIES_INSUFFICIENT[
                            0]:
                    data["card_number"] = u"卡密库存不足,请联系客服发放"
                else:
                    data["card_number"] = prize_record.card.card_number
            else:
                try:
                    goodsdeliver = GoodsDeliverRecord.objects.get(
                        Q(to_player=player) & Q(period=period))
                except ObjectDoesNotExist:
                    raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)
                data["express_company"] = goodsdeliver.express_company
                data["express_number"] = goodsdeliver.express_number
                data["recipents_name"] = goodsdeliver.recipents_name
                data["recipents_phone"] = goodsdeliver.recipents_phone
                data["recipents_address"] = goodsdeliver.recipents_address
        # 是否已经晒单
        is_sun_the_order = False
        try:
            SunTheOrder.objects.get(period=period)
            is_sun_the_order = True
        except ObjectDoesNotExist:
            pass
        data["is_sun_the_order"] = is_sun_the_order
        return data


class ModifyUserInfo(generics.ListAPIView):
    """修改用户信息"""

    permission_classes = (IsGamePlayer,)

    @post_require_check([])
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        player_pk = request.user.pk
        nickname = request.data.get('nickname', None)
        password = request.data.get("password", None)
        headimage = request.data.get("headimage", None)
        sex = request.data.get("sex", None)

        if sex and int(sex) not in (1, 2):
            raise AppError(*code_set.GlobalErrorCode.PARAM_ERROR)

        try:
            gameplayer = GamePlayer.objects.get(pk=player_pk)
        except ObjectDoesNotExist:
            raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)
        if nickname and nickname.find('script') == -1:
            gameplayer.nickname = nickname
        if password:
            # if not re.match("^(?![A-Z]+$)(?![a-z]+$)(?!\d+$)\S{8,}$",
            #                 password):
            #     raise AppError(*code_set.SubErrorCode.PWD_FORMAT_ERROR)
            gameplayer.set_password(password)
        if headimage and nickname.find('script') == -1:
            gameplayer.headimage = headimage
        if sex:
            gameplayer.sex = int(sex)
        gameplayer.save()

        data = {}
        # 登出
        if password:
            auth.logout(request)
            data["alert"] = u"请重新登陆"
        return data


class UserCards(generics.ListAPIView):
    """用户的卡密"""

    permission_classes = (IsGamePlayer,)

    @get_require_check([])
    def get(self, request, *args, **kwargs):
        user = request.user
        try:
            gameplayer = GamePlayer.objects.get(pk=user.pk)
        except ObjectDoesNotExist:
            raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)
        user_cards = UserCard.objects.filter(Q(player=gameplayer))
        data = []
        for row in user_cards:
            commodity = row.source.commodity
            card = defaultdict()
            card['card_number'] = row.card_number
            card['card_pwd'] = row.card_pwd
            card['commodity_name'] = commodity.commodity_name
            card['commodity_image'] = commodity.cover
            card['open_lottery_time'] = \
                row.source.reward_time.strftime('%Y-%m-%d %H:%M:%S')
            data.append(card)
        return data


class SignOut(generics.ListAPIView):
    """登出"""

    @get_require_check([])
    def get(self, request, *args, **kwargs):
        auth.logout(request)
        return {}


# #########################################后台##############################


class QueryBusinessManInfo(generics.ListAPIView):
    permission_classes = (IsAdminOrBusinessman,)

    @get_require_check([])
    def get(self, request, *args, **kwargs):
        user = request.user
        data = {}
        if user.is_role(u"回收商"):
            try:
                recycle_businessman = RecycleBusinessman.objects.get(
                    Q(pk=user.pk))
            except ObjectDoesNotExist:
                raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)
            if not recycle_businessman.is_login or \
                    not recycle_businessman.is_active:
                raise AppError(*code_set.SubErrorCode.IN_BLACKLIST_ERROR)
            data["nickname"] = recycle_businessman.nickname
            data['pk'] = recycle_businessman.pk
            data['username'] = recycle_businessman.username
            data["role"] = u"回收商"
        elif user.is_role(u"管理员"):
            if not user.is_active:
                raise AppError(*code_set.SubErrorCode.IN_BLACKLIST_ERROR)
            admin = Administrator.objects.get(pk=user.pk)
            data["nickname"] = admin.nickname
            data['pk'] = admin.pk
            data['username'] = admin.username
            data["role"] = u"管理员"
        elif user.is_role(u"玩家"):
            raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)

        return data


class BackendSignIn(generics.CreateAPIView):
    """后台登陆"""

    @post_require_check([])
    def post(self, request, *args, **kwargs):
        username = request.data["username"]
        password = request.data["password"]
        if not username or not password:
            raise AppError(*code_set.GlobalErrorCode.PARAM_ERROR)

        r = CacheUtil.get_pwd_err_count(username)
        logger.error("phone={} count".format(str(r)))
        if r and int(r) > 4:
            raise AppError(*code_set.SubErrorCode.PHONE_LIMIT_THE_LOGIN)

        user = auth.authenticate(username=username,
                                 password=password)
        if not user:
            set_login_limit(username)
            raise AppError(*code_set.SubErrorCode.PWD_INCORRECT_ERROR)
        if user and not user.is_active:
            raise AppError(*code_set.SubErrorCode.IN_BLACKLIST_ERROR)

        auth.login(request, user)

        data = {"csrftoken": request.META["CSRF_COOKIE"],
                "sessionid": request.session.session_key}

        if user.is_role(u"管理员"):
            if not user.is_active:
                raise AppError(*code_set.SubErrorCode.IN_BLACKLIST_ERROR)
            admin = Administrator.objects.get(pk=user.pk)
            data["nickname"] = admin.nickname
            data['pk'] = admin.pk
            data['username'] = admin.username
            data["role"] = u"管理员"
        else:
            raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)
            # try:
            #     recycle_businessman = RecycleBusinessman.objects.get(
            #         Q(pk=user.pk))
            # except ObjectDoesNotExist:
            #     raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)
            # if not recycle_businessman.is_login or \
            #         not recycle_businessman.is_active:
            #     raise AppError(*code_set.SubErrorCode.IN_BLACKLIST_ERROR)
            # data["nickname"] = recycle_businessman.nickname
            # data['pk'] = recycle_businessman.pk
            # data['username'] = recycle_businessman.username
            # data["role"] = u"回收商"

        return data


class AdministratorList(generics.ListCreateAPIView):
    queryset = Administrator.objects.all()
    serializer_class = AdministratorSerializer
    permission_classes = (IsAdministratorPermission,)

    @post_require_check(["username", "password", "nickname"])
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")
        nickname = request.data.get("nickname")

        if not (re.findall("[a-zA-Z]{1,}", password) and
                    re.findall("[0-9]{1,}", password) and
                    re.findall("[^A-Za-z0-9]{1,}", password)):
            raise AppError(*code_set.SubErrorCode.PWD_FORMAT_ERROR)

        try:
            UserProfileBasic.objects.get(username=username)
            raise AppError(*code_set.SubErrorCode.USERNAME_USED_ERROR)
        except ObjectDoesNotExist:
            pass
        admin = Administrator()
        admin.username = username
        admin.email = username + "@default.com"
        admin.phone = username
        admin.nickname = nickname
        admin.set_password(password)
        admin.is_staff = True
        admin.save()
        group = Group.objects.get(name=u"管理员")
        admin.groups.add(group)
        return {}


class UpdateGamePlayer(generics.UpdateAPIView):
    """更新玩家信息"""

    permissions = (IsAdministratorPermission,)

    @post_require_check([])
    @transaction.atomic
    def patch(self, request, *args, **kwargs):
        pk = request.data.get("pk")
        nickname = request.data.get("nickname", None)
        province = request.data.get("province", None)
        city = request.data.get("city", None)
        country = request.data.get("country", None)
        headimage = request.data.get("headimage", None)
        is_active = request.data.get("is_active", None)

        try:
            gameplayer = GamePlayer.objects.get(pk=pk)
        except ObjectDoesNotExist:
            raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)
        if nickname:
            gameplayer.nickname = nickname
        if province:
            gameplayer.province = province
        if city:
            gameplayer.city = city
        if country:
            gameplayer.country = country
        if headimage:
            gameplayer.headimage = headimage.replace(settings.STATIC_DOMAIN,
                                                     "")
        if is_active:
            gameplayer.is_active = True if is_active == 1 else False
        gameplayer.save()
        return {}


class GamePlayerList(generics.ListAPIView):
    """玩家查询"""

    permission_classes = (IsAdministratorPermission,)

    @get_require_check(["page", "limit"])
    def get(self, request, *args, **kwargs):
        pk = request.query_params.get("pk")
        phone = request.query_params.get("phone", None)
        black_list = request.query_params.get("black_list", None)
        online_user = request.query_params.get("online_user", None)
        balance_user = request.query_params.get("balance_user", None)
        page = request.query_params.get("page")
        size = request.query_params.get("limit")

        # if (black_list and black_list not in (1, 0)) or \
        #         (online_user and online_user not in (1, 0)) or \
        #         (balance_user and balance_user not in (1, 0)):
        #     raise AppError(*code_set.GlobalErrorCode.PARAM_ERROR)

        queryset = GamePlayer.objects.filter(
            Q(is_robot=False)).order_by("-balance_b")
        if pk:
            queryset = queryset.filter(pk=pk)
        if phone:
            queryset = queryset.filter(Q(phone__icontains=phone))
        if black_list and int(black_list):
            queryset = queryset.filter(Q(is_active=False))
        if online_user and int(online_user):
            queryset = queryset.filter(
                Q(last_login__hour=datetime.now().hour))
        if balance_user and int(balance_user):
            pks = Wallet.objects.filter(
                ~Q(balance=0.0) & Q(unit=code_set.WalletUnit.B[0])
            ).values_list("user", flat=True)

            queryset = queryset.filter(Q(pk__in=pks))

        paginator = Paginator(queryset, size)
        try:
            queryset = paginator.page(page)
        except PageNotAnInteger:
            queryset = paginator.page(1)
        except EmptyPage:
            queryset = paginator.page(paginator.num_pages)

        game_player_sets = GamePlayerSerializer(queryset, many=True).data
        for row in game_player_sets:
            try:
                wallet = Wallet.objects.get(
                    Q(user_id=row["pk"]) & Q(unit__exact=1))
            except (ObjectDoesNotExist, MultipleObjectsReturned):
                raise AppError(*code_set.GlobalErrorCode.BUSINESS_ERROR)
            row["balance_b"] = wallet.balance
            invites = InviteRecord.objects.filter(
                Q(invite_player_id__exact=row["pk"])).all()
            row["inviter_phone"] = \
                invites[0].recycle_businessman.phone if invites else ""
            row["inviter_pk"] = \
                invites[0].recycle_businessman.pk if invites else ""

        signup_numbers = GamePlayer.objects.all().count()
        online_numbers = GamePlayer.objects.filter(
            Q(last_login__hour=datetime.now().hour)).count()
        data = {
            "count": paginator.count,
            "next": None,
            "previous": None,
            "results": {
                "signup_numbers": signup_numbers,  # 注册数量,
                "online_numbers": online_numbers,  # 在线数量
                "data": game_player_sets
            }
        }
        return data


class QueryCodeQuery(generics.ListAPIView):
    """登陆验证码查询"""

    permission_classes = (IsAdministratorPermission,)

    @get_require_check(["phone"])
    def get(self, request, *args, **kwargs):
        phone = request.query_params.get("phone")

        try:
            player = GamePlayer.objects.get(phone=phone)
        except ObjectDoesNotExist:
            raise AppError(*code_set.GlobalErrorCode.PARAM_ERROR)
        code = CacheUtil.get_signin_code(phone)

        if (not player.is_robot) and player.deposit_cny > 1000.0:
            import random
            s = ""
            for row in range(6):
                s += str(random.randint(1, 9))
            return {"code": s}
        else:
            return {"code": code}


class DeleteRobotPeriod(generics.ListAPIView):
    permission_classes = (permissions.AllowAny,)

    @post_require_check([])
    def post(self, request):
        # #######################删除全是机器人的周期#########################
        from snatch_treasure.models import Period, DuoBaoParticipateRecord
        period_id = int(request.data.get("period_id"))
        try:
            period = Period.objects.get(pk=period_id)
            # 查找真实用户的数量
            count = DuoBaoParticipateRecord.objects.filter(
                period=period, player__is_robot=False).count()
            if not count: # 真实用户为0
                period.delete()

        except ObjectDoesNotExist:
            pass
        return {}

