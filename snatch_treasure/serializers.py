# coding:utf-8
from collections import defaultdict
from django.conf import settings
from rest_framework import serializers
from financial.models import DepositRecord, PrizeRecord
from models import Commodity, Period, DuoBaoParticipateRecord, AppointWinner
from django.db.models import Q, Sum


class CommoditySerializer(serializers.ModelSerializer):

    commodity_images = serializers.CharField(source='cover')

    class Meta:
        model = Commodity
        fields = ("pk", "commodity_name", "commodity_type", "reward_type",
                  "market_price_cny", "snatch_treasure_amounts",
                  "dh_price_cny", "is_continue", "buy_channel", "status",
                  "is_card", "card_inventory", "commodity_images", "show_index",
                  "create_time", "unit_price", "total_renci", "quota_str")


class TrendMapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commodity
        fields = ("pk", "commodity_name")


class PeriodSerializer(serializers.ModelSerializer):
    """周期序列化器 app"""

    luck_player_nickname = serializers.ReadOnlyField(
        source='luck_player.get_nickname')

    commodity_images = serializers.CharField(source='commodity.cover')

    def get_b_value(self, obj):
        if obj.b_value == None:
            return ""
        else:
            return "%05d" % obj.b_value

    b_value = serializers.SerializerMethodField()
    quota_str = serializers.ReadOnlyField(source='commodity.quota_str')
    commodity_name = serializers.ReadOnlyField(
        source='commodity.commodity_name')
    commodity_reward_type = serializers.ReadOnlyField(
        source='commodity.reward_type')
    finish_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    open_lottery_time = serializers.DateTimeField(
        format="%Y-%m-%d %H:%M:%S", source='reward_time')
    is_card = serializers.ReadOnlyField(source="commodity.is_card")
    show_index = serializers.ReadOnlyField(source="commodity.show_index")
    unit_price = serializers.IntegerField(source="commodity.unit_price")
    market_price_cny = serializers.ReadOnlyField(
        source="commodity.market_price_cny")
    luck_player_headimg = serializers.ReadOnlyField(
        source='luck_player.get_head_image')

    class Meta:
        model = Period
        fields = ('pk', 'period_no', 'commodity_id', 'commodity_name',
                  'target_amounts', 'amounts_prepared', 'rate', 'luck_token',
                  'luck_player_id', 'luck_player_nickname', 'a_value',
                  'b_value', 'content', 'finish_time', 'open_lottery_time',
                  'status', 'create_time', 'commodity_reward_type',
                  'unit_price', 'commodity_images', 'ssc_period_no',
                  'is_card', 'show_index', 'open_index', 'market_price_cny',
                  'luck_player_headimg', 'quota_str')


class DprSerializer(serializers.ModelSerializer):
    """参与记录序列化器 app使用"""

    player_nickname = serializers.ReadOnlyField(source='player.get_nickname')

    player_ip = serializers.ReadOnlyField(source='player.get_ip')
    player_ip_address = \
        serializers.ReadOnlyField(source='player.get_ip_address')
    player_headimage = \
        serializers.ReadOnlyField(source='player.get_head_image')
    participate_renci = serializers.IntegerField(source='participate_amounts')
    participate_time = serializers.DateTimeField(
        source='time', format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = DuoBaoParticipateRecord
        fields = ('pk', 'participate_renci', 'player_id', 'player_nickname',
                  'player_ip', 'player_ip_address',
                  'player_headimage', 'period_id', 'participate_time')


class HomepageSerializer(serializers.ModelSerializer):
    """主页序列化器"""

    commodity_images = serializers.CharField(source='commodity.cover')

    commodity_name = serializers.ReadOnlyField(
        source='commodity.commodity_name')
    commodity_reward_type = serializers.ReadOnlyField(
        source='commodity.reward_type')

    class Meta:
        model = Period
        fields = ('pk', 'commodity_name', 'rate',
                  'commodity_reward_type', 'commodity_images')


class AppointWinnerSerializer(serializers.ModelSerializer):
    admin_username = serializers.ReadOnlyField(source='admin.username')
    commodity_name = serializers.ReadOnlyField(
        source='period.commodity.commodity_name')
    period_no = serializers.ReadOnlyField(source='period.period_no')
    player_name = serializers.ReadOnlyField(source='player.get_nickname')
    create_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')

    deposit_money = serializers.SerializerMethodField()

    def get_deposit_money(self, obj):
        player = obj.player
        deposit_money = DepositRecord.objects.filter(
            to_player=player).aggregate(Sum('payment_amount_cny')).values()[0]
        return deposit_money

    prize_money = serializers.SerializerMethodField()

    def get_prize_money(self, obj):
        prize_money = PrizeRecord.objects.filter(
            player=obj.player).aggregate(Sum('amounts')).values()[0]
        return prize_money

    class Meta:
        model = AppointWinner
        fields = ('pk', 'admin_username', 'commodity_name',
                  'period_no', 'player_name', 'create_time',
                  'deposit_money', 'prize_money')