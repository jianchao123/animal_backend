from django.contrib import admin
from models import RecycleRecord, InviteRecord, UserConsignee, \
    RecycleBusinessman


@admin.register(RecycleRecord)
class RecycleRecordAdmin(admin.ModelAdmin):
    list_display = (
    'pk', 'recycle_period_no', 'recycle_price', 'recycle_trade_no', 'period',
    'recycle_businessman', 'commodity', 'recycle_time', 'is_ret')


@admin.register(InviteRecord)
class InviteRecordAdmin(admin.ModelAdmin):
    list_display = ("pk", "recycle_businessman",
                    "invite_player", "invite_time")


@admin.register(UserConsignee)
class UserConsigneeAdmin(admin.ModelAdmin):
    list_display = ("pk", "player", "recycle_businessman", "consignee_name",
                    "phone", "flag")


@admin.register(RecycleBusinessman)
class RecycleBusinessmanAdmin(admin.ModelAdmin):
    list_display = (
        "pk", "is_recycle",
        "is_login", "invite_code", "deposit_back_rate", "recycle_back_rate",
        "invite_back_rate")