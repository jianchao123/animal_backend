# coding:utf-8
import datetime
from financial.models import DepositRecord
from utils.utils import generate_out_trade_no
from utils import code_set
from shopping_settings.models import PayType


def insert_deposit_record(gameplayer, amounts, recyclebusinessman):
    # 充值记录
    deposit_record = DepositRecord()
    deposit_record.out_trade_no = \
        generate_out_trade_no(
            code_set.OutTradeNoPrefix.RECYCEL_BUSINESSMAN)
    deposit_record.amounts = amounts
    deposit_record.units = 1
    deposit_record.to_player = gameplayer
    deposit_record.deposit_type = PayType.objects.get(code=u"DC")
    deposit_record.deposit_time = datetime.datetime.now()
    deposit_record.status = code_set.PayStatus.SUCCESS[0]
    deposit_record.from_recycle_businessman = recyclebusinessman
    deposit_record.payment_amount_cny = amounts
    deposit_record.save()