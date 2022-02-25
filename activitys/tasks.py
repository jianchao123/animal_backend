# encoding: utf-8
from __future__ import absolute_import
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from activitys.models import PresentsRecord
from shopping_user.models import Administrator
from shopping_user.models import GamePlayer
from shopping_user.business import change_wallet
from financial.models import ConsumeRecord
from shopping import celery_app
from utils import miaodi_sms_api
from utils import code_set
import logging

logger = logging.getLogger(__name__)


@celery_app.task
def present_sms(filtered_phone, amounts, admin_id):
    """赠送短信"""
    real_amounts = amounts
    admin = Administrator.objects.get(id=admin_id)
    presents = []
    phones = []
    for phone in filtered_phone:
        try:
            player = GamePlayer.objects.get(phone=phone)
        except ObjectDoesNotExist:
            continue
        # 获取上次的召回赠送记录
        present = PresentsRecord.objects.filter(
            Q(to_player=player) &
            Q(presents_type=code_set.PresentStatus.SUMMON[0])
        ).order_by('-id').first()
        if present:
            present_time = present.present_time
            count = ConsumeRecord.objects.filter(
                Q(player=player) & Q(consume_time__gt=present_time)).count()
            # 在赠送了之后有消费记录
            if count:
                real_amounts = amounts
            else:
                real_amounts = amounts - present.amounts

        # 赠送量大于0
        if real_amounts > 0:
            present = PresentsRecord()
            present.amounts = real_amounts
            present.to_player = player
            present.from_administrator = admin
            present.presents_type = code_set.PresentStatus.SUMMON[0]
            presents.append(present)
            change_wallet(real_amounts, unit=code_set.WalletUnit.B[0],
                          user_id=player.id)
            phones.append(phone)
    if presents and phones:
        PresentsRecord.objects.bulk_create(presents)
        resp_code, resp_desc = miaodi_sms_api.send_present_notice(
            ",".join(phones), real_amounts)
        if resp_code != "0000":
            logger.error(resp_desc)