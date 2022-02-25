# coding:utf-8
from rest_framework import serializers
from models import DepositRecord, ConsumeRecord, PrizeRecord, \
    AgencyRecord, WithdrawRecord


class DepositOrderSerializer(serializers.ModelSerializer):
    """充值订单序列化器"""

    gameplayer_nickname = serializers.ReadOnlyField(
        source="to_player.get_nickname")

    phone = serializers.ReadOnlyField(source='to_player.phone')

    # def get_deposit_type_describe(self, obj):
    #     for k, v in DepositRecord.deposit_tuple:
    #         if obj.deposit_type == k:
    #             return v
    #     return ""
    #
    # deposit_type_describe = serializers.SerializerMethodField()
    #
    def get_business_name(self, obj):
        if obj.from_recycle_businessman:
            return obj.from_recycle_businessman.nickname
        else:
            return ""

    business_name = serializers.SerializerMethodField()

    class Meta:
        model = DepositRecord
        fields = ("pk", "out_trade_no", "discount_amount_cny",
                  "payment_amount_cny", "phone", "business_name",
                  "discount_amount_cny", "amounts", "gameplayer_nickname",
                  "deposit_type", "status")


class AgencyRecordSerializer(serializers.ModelSerializer):
    """代理记录"""
    agency_trade_no = serializers.ReadOnlyField(read_only=True)
    units = serializers.ReadOnlyField(read_only=True)
    status = serializers.ReadOnlyField(read_only=True)
    deposit_time = serializers.DateTimeField(read_only=True,
                                             format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = AgencyRecord
        fields = ("pk", "agency_trade_no", "amounts", "units",
                  "deposit_time", "status", "remark", "to_recycle_businessman")


class WithdrawSerializer(serializers.ModelSerializer):
    """提现记录"""
    apply_for_time = serializers.DateTimeField(read_only=True,
                                               format="%Y-%m-%d %H:%M:%S")
    transfer_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    arrive_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    to_businessman_nickname = \
        serializers.CharField(read_only=True,
                              source='to_recycle_businessman.nickname')
    to_businessman_pk = \
        serializers.IntegerField(read_only=True,
                                 source='to_recycle_businessman.pk')
    admin_username = serializers.CharField(read_only=True,
                                           source="admin.username")

    class Meta:
        model = WithdrawRecord
        fields = ("pk", "out_trade_no", "amounts", "units", "apply_for_time",
                  "transfer_time", "arrive_time", "status", "remark",
                  "to_businessman_nickname", "to_businessman_pk", "admin_id",
                  "admin_username")
