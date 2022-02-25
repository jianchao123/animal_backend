from django.contrib import admin
from models import GoodsDeliverRecord


@admin.register(GoodsDeliverRecord)
class GoodsDeliverRecordAdmin(admin.ModelAdmin):
    list_display = (
    "pk", "to_player", "commodity", "period", "express_company",
    "express_number", "status")
