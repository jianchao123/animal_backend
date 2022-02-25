from django.contrib import admin
from models import CardInventories, CardDeliveryRecord, Card, \
    CardEntryRecord


@admin.register(CardDeliveryRecord)
class CardDeliveryRecordAdmin(admin.ModelAdmin):
    pass


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ("pk", "card_number", "batch_no", "status")


@admin.register(CardInventories)
class CardInventoriesAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "code", "market_price_cny",
                    "volumes", "warning_volumes",
                    "update_time", "status")


@admin.register(CardEntryRecord)
class CardEntryRecordAdmin(admin.ModelAdmin):
    list_display = \
        ("pk", "batch_no", "card_inventory", "volumes", "entry_time",
         "entry_admin")
