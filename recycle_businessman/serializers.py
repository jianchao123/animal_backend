# coding:utf-8
from rest_framework import serializers
from models import InviteRecord, UserConsignee, RecycleBusinessman


class InviteRecordSerializer(serializers.ModelSerializer):
    recycle_businessman_nickname = serializers.CharField(
        source="recycle_businessman.get_nickname")
    invite_player_nickname = \
        serializers.CharField(source="invite_player.phone")
    invite_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = InviteRecord
        fields = ("pk", "recycle_businessman_id",
                  "recycle_businessman_nickname", "invite_player_id",
                  "invite_player_nickname", "invite_time")


class UserConsigneeSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserConsignee
        fields = ('pk', 'player_id', 'recycle_businessman_id',
                  'consignee_name', "phone", 'flag')


class RecycleBusinessmanSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecycleBusinessman
        fields = \
            ("pk", "uid", "username", "nickname", "sex", "province", "city",
             "country", "headimage", "email", "phone", "status", "create_time",
             "is_recycle", "is_login", "invite_code",
             "invite_qr_code", "deposit_back_rate", "recycle_back_rate",
             "invite_back_rate", "balance_cny")