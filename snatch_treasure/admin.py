# coding:utf-8

from django.contrib import admin
from models import Commodity, Period, TokenRecord, RecommendCommodity, \
    DuoBaoParticipateRecord, ShiShiCai, UserCard, Order, AppointWinner


@admin.register(Commodity)
class CommodityAdmin(admin.ModelAdmin):
    list_display = ("pk", "commodity_name", "commodity_type", "reward_type",
                    "market_price_cny", "snatch_treasure_amounts",
                    "unit_price", "total_renci",
                    "dh_price_cny", "is_continue", "buy_channel", "status",
                    "count", "show_index", "is_card", "cover", "unit_price")


@admin.register(Period)
class PeriodAdmin(admin.ModelAdmin):
    list_display = (
        "pk", "period_no", "commodity", "target_amounts", "amounts_prepared",
        "rate", "luck_token", "luck_player", "a_value", "b_value",
        "ssc_period_no",
        "finish_time", "reward_time", "status", "open_index")
    search_fields = ("period_no",)
    list_filter = ("status",)


@admin.register(TokenRecord)
class TokenRecordAdmin(admin.ModelAdmin):
    pass


@admin.register(DuoBaoParticipateRecord)
class DuoBaoParticipateRecordAdmin(admin.ModelAdmin):
    list_display = ("pk", "participate_amounts", "player", "period",
                    "time", "residue", "is_win_prize")
    search_fields = ('period__id',)


@admin.register(ShiShiCai)
class ShiShiCaiAdmin(admin.ModelAdmin):
    list_display = ["number", "ssc_period_no", "open_time", "next_open_time"]


@admin.register(UserCard)
class UserCardAdmin(admin.ModelAdmin):
    list_display = ("pk", "player", "card_number", "card_pwd", "source")


@admin.register(Order)
class Order(admin.ModelAdmin):
    list_display = ("pk", "order_no", "player", "period", "count",
                    "status", "create_time")


@admin.register(AppointWinner)
class AppointWinner(admin.ModelAdmin):
    list_display = ("pk", "admin", "player", "period", "create_time")


@admin.register(RecommendCommodity)
class RecommendCommodity(admin.ModelAdmin):
    list_display = ("pk", "name", "commodity", "location", "status")
