# coding:utf-8
from rest_framework import serializers
from models import GoodsDeliverRecord


class GoodsDeliverListSerializer(serializers.ModelSerializer):
    gameplayer_nickname = serializers.ReadOnlyField(
        source="to_player.get_nickname")
    commodity_name = serializers.ReadOnlyField(
        source="commodity.commodity_name")
    deliver_goods_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    arrive_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    period_no = serializers.ReadOnlyField(source="period.period_no")

    class Meta:
        model = GoodsDeliverRecord
        fields = \
            ("pk", "to_player_id", "gameplayer_nickname", "commodity_id",
             "commodity_name", "period_id", "period_no",
             "recipents_name", "recipents_phone", "recipents_address",
             "deliver_goods_channel", "quantity", "real_price_cny",
             "delivery_expense", "express_company", "express_number", "link",
             "deliver_goods_time", "arrive_time", "status", "remark")
