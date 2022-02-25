from django.contrib import admin
from models import CommodityType, BuyChannel, Banner, PayType, \
    PayAccountsConf, PayMoneyCtl, ShippingAddress, CommonParamConf, PayChannel


@admin.register(CommodityType)
class CommodityTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(BuyChannel)
class BuyChannelAdmin(admin.ModelAdmin):
    pass


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ("pk", "title", "image_path", "link", "status")


@admin.register(PayType)
class PayTypeAdmin(admin.ModelAdmin):
    list_display = ("pk", "pay_name", "pay_rates")


@admin.register(PayChannel)
class PayChannelAdmin(admin.ModelAdmin):
    list_display = ("pk", "code", "name", "rate", "money_str",
                    "pay_type", "company")


@admin.register(PayAccountsConf)
class PayAccountsConfAdmin(admin.ModelAdmin):
    list_display = ("pk", "pay_channel", "merchant_no", "status",
                    "is_use", "remark", "operator")


@admin.register(PayMoneyCtl)
class PayMoneyCtlAdmin(admin.ModelAdmin):
    list_display = ("pk", "min", "max", "history_min",
                    "history_max", "pay_channel", "status", "operator")


@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = (
        "pk", "player", "recipents_name", "recipents_phone",
        "recipents_address",
        "is_default")


@admin.register(CommonParamConf)
class CommonParamConfAdmin(admin.ModelAdmin):
    list_display = ("pk", "conf_name", "conf_key", "conf_value")
