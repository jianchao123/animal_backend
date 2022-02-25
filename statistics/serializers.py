# coding:utf-8

from rest_framework import serializers
from models import UserEveryDayInfo, RbEveryDayInfo, PlatformEverydayData


class UserEveryDayInfoSerializer(serializers.ModelSerializer):
    cur_date = serializers.DateField(format="%Y-%m-%d")

    class Meta:
        model = UserEveryDayInfo
        fields = ("pk", "deposit_cny", "bonus",
                  "difference", "presents_b", "cur_date")


class RbRecycleBusinessmanSerializer(serializers.ModelSerializer):
    class Meta:
        model = RbEveryDayInfo
        fields = ("pk", "recycle_businessman", "receive_cny",
                  "dai_chong_cny", "receive_back_profit_cny",
                  "dai_chong_back_profit_cny", "ls_back_profit_cny",
                  "total", "data_date", "status")


class PlatformEverydayDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlatformEverydayData
        fields = '__all__'