from django.contrib import admin
from models import PrizeRecord, ConsumeRecord, DepositRecord, \
    AgencyRecord, BackProfitRecord, WithdrawRecord


@admin.register(PrizeRecord)
class PrizeRecordAdmin(admin.ModelAdmin):
    list_display = \
        ("pk", "period", "amounts", "accept_prize_type",
         "to_recycle_businessman",
         "player", "status")
    search_fields = ['player__phone']


@admin.register(ConsumeRecord)
class ConsumeRecordAdmin(admin.ModelAdmin):
    list_display = ("pk", "period", "amounts", "participate",
                    "player", "status", "consume_time")
    search_fields = ('period__id',)


@admin.register(DepositRecord)
class DepositRecordAdmin(admin.ModelAdmin):
    list_display = (
        "pk", "trade_no", "discount_amount_cny", "commercial_tenant_nos",
        "from_recycle_businessman", "payment_amount_cny", "is_ret",
        "out_trade_no",
        "amounts", "to_player", "deposit_type", "deposit_time", "status",
        "remark")
    list_filter = ['deposit_type']
    search_fields = ['id']


@admin.register(AgencyRecord)
class AgencyRecordAdmin(admin.ModelAdmin):
    pass


@admin.register(BackProfitRecord)
class BackProfitRecordAdmin(admin.ModelAdmin):
    list_display = ("pk", "amounts", "back_profit_type",
                    "to_recycle_businessman", "back_profit_date",
                    "settlement_date", "relation_ids", "status")


@admin.register(WithdrawRecord)
class WithdrawRecordAdmin(admin.ModelAdmin):
    list_display = ("pk", "out_trade_no", "amounts", "units", "apply_for_time",
                    "transfer_time", "arrive_time", "status", "remark",
                    "to_recycle_businessman", "admin")

    search_fields = ['id']