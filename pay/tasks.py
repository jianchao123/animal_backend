# encoding: utf-8
from __future__ import absolute_import
from shopping import celery_app
from utils import miaodi_sms_api
import logging

logger = logging.getLogger(__name__)


@celery_app.task
def deposit_present_notice(phone, amounts, present_amounts):
    """
    充值通知
    """
    resp_code, resp_desc = miaodi_sms_api.send_deposit_success(
        phone, amounts, present_amounts)
    if resp_code != "0000":
        logger.error(resp_desc)