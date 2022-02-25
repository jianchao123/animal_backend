from rest_framework import serializers
from models import GamePlayer, Administrator, TieBaUserInfo


class GamePlayerSerializer(serializers.ModelSerializer):

    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    last_login = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = GamePlayer
        fields = \
            ("pk", "uid", "username", "nickname", "sex", "province", "city",
             "country", "get_head_image", "last_login",
             "headimage", "email", "phone", "status", "create_time",
             "is_active", "ip", "ip_address",
             "balance_b", "has_been_spending_b", "deposit_cny",
             "presents_b", "participate_count", "win_prize_count",
             "snatch_treasure_b", "market_price_cny")


class AdministratorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Administrator
        fields = \
            ("pk", "uid", "username", "nickname", "sex", "province", "city",
             "country", "headimage", "email", "phone", "status", "create_time")


class TiebaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TieBaUserInfo
        fields = '__all__'

