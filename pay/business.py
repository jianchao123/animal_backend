# coding:utf-8
from decimal import Decimal
from django.db import transaction
from shopping_user.models import Wallet
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned


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


