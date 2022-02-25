from django.contrib import admin
from models import UserEveryDayInfo, RbEveryDayInfo, PlatformEverydayData, \
    UserEveryMonthInfo


@admin.register(UserEveryDayInfo)
class UserEveryDayInfoAdmin(admin.ModelAdmin):
    list_display = ["player", "deposit_cny", "bonus", "difference",
                    "presents_b", "consume_cny", "cur_date"]


@admin.register(RbEveryDayInfo)
class RbEveryDayInfoAdmin(admin.ModelAdmin):
    list_display = ("pk", "recycle_businessman", "receive_cny", "ls_cny",
                    "dai_chong_cny", "receive_back_profit_cny",
                    "dai_chong_back_profit_cny", "ls_back_profit_cny",
                    "total", "data_date", "settlement_date", "status")


@admin.register(PlatformEverydayData)
class PlatformEverydayDataAdmin(admin.ModelAdmin):
    list_display = (
    'alipay_cny', 'wx_cny', 'dai_chong_cny', 'deposit_total_cny', 'bonus',
    'presents_b', 'data_date', 'update_time', 'status', 'pay_rates',
    'win_prize_entity_price', 'win_prize_virtual_price',
    'deliver_goods_entity_price', 'deliver_goods_virtual_price',
    'recycle_businessman_withdraw_price', 'recycle_commission',
    'ls_commission', 'dc_commission', 'shipment_phone_deposit_cny',
    'shipment_phone_shipment_cny', 'shipment_phone_profit_and_loss',
    'll_profit')


@admin.register(UserEveryMonthInfo)
class UserEveryMonthInfoAdmin(admin.ModelAdmin):
    list_display = ('player', 'consume_money', 'deposit_money', 'bonus',
                    'presents_money', 'snatch_treasure_b', 'order_count',
                    'data_date', 'update_time')