from django.contrib import admin
from models import GamePlayer, \
    Administrator, UserProfileBasic, Wallet, Messages


@admin.register(GamePlayer)
class GamePlayerAdmin(admin.ModelAdmin):
    list_display = (
        "pk", "uid", "username", "email", "phone", "nickname", "balance_b",
        "has_been_spending_b", 'create_time',
        "deposit_cny", "presents_b", "participate_count", "win_prize_count",
        "snatch_treasure_b", "market_price_cny", "ip_address")
    search_fields = ['phone', 'uid']


@admin.register(Administrator)
class AdministratorAdmin(admin.ModelAdmin):
    list_display = ("pk", "username", "email", "phone")


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "balance", "unit", "last_update_time")
    search_fields = ['user__id']


@admin.register(UserProfileBasic)
class UserProfileBasicAdmin(admin.ModelAdmin):
    pass


@admin.register(Messages)
class MessagesAdmin(admin.ModelAdmin):
    list_display = ("pk", "title", "content", "to_player")

