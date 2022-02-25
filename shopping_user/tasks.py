# encoding: utf-8
from __future__ import absolute_import
import time
from decimal import Decimal
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from shopping import celery_app
from shopping_user.models import GamePlayer, Wallet
from activitys.models import PresentsRecord
from shopping_settings.models import SectionMoneyRecord
from shopping_user.business import change_wallet
from utils import code_set
from utils import miaodi_sms_api
import logging

logger = logging.getLogger(__name__)


@celery_app.task
def send_sms(phone, code):
    """发送短信 (delay调用) """
    logger.error("============sms=============")
    resp_code, resp_desc = miaodi_sms_api.send_code(phone, code)
    if resp_code != "0000":
        logger.error(resp_desc)
    return True


@celery_app.task
def signup_present(phone):
    """注册赠送"""

    for x in range(10):
        try:
            player = GamePlayer.objects.get(phone=phone)
            break
        except ObjectDoesNotExist:
            time.sleep(0.5)

    queryset = SectionMoneyRecord.objects.filter(
        text__contains=phone).order_by('-section_mix')
    sectionmoneyrecord = queryset.first()
    if sectionmoneyrecord:
        present_amounts = sectionmoneyrecord.present_amounts
        # 增加赠送记录
        present_record = PresentsRecord()
        present_record.amounts = present_amounts
        present_record.to_player = player
        present_record.presents_type = \
            code_set.PresentStatus.SIGNUP[0]
        present_record.msg_content = \
            u"动物世界赠送您{}豆子,快去消费吧!".format(present_amounts)
        present_record.save()

        # 余额
        change_wallet(Decimal(str(present_amounts)),
                      unit=code_set.WalletUnit.B[0],
                      user_id=player.pk)

        resp_code, resp_desc = miaodi_sms_api.send_signup_present_success(phone, present_amounts)
        if resp_code != "0000":
            logger.error(resp_desc)