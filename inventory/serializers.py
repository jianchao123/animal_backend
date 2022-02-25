# coding:utf-8
from rest_framework import serializers
from models import CardEntryRecord, Card, CardDeliveryRecord, CardInventories


class CardEntryRecordSerializer(serializers.ModelSerializer):
    entry_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S",
                                           required=False)
    card_inventory_name = serializers.ReadOnlyField(
        source='card_inventory.name')
    card_inventory_pk = serializers.ReadOnlyField(
        source='card_inventory.pk')
    entry_admin_username = serializers.ReadOnlyField(
        source='entry_admin.username')
    entry_admin_pk = serializers.ReadOnlyField(
        source='entry_admin.pk')

    class Meta:
        model = CardEntryRecord
        fields = (
            "pk", "batch_no", "card_inventory_name", "card_inventory_pk",
            "volumes", "entry_time", "entry_admin_username", "entry_admin_pk")


class CardSerializer(serializers.ModelSerializer):
    card_inventory_name = serializers.ReadOnlyField(
        source='card_inventory.name')
    card_inventory_pk = serializers.ReadOnlyField(
        source='card_inventory.pk')

    class Meta:
        model = Card
        fields = ("pk", "batch_no", "card_entry_no", "card_inventory_name",
                  "card_inventory_pk", "card_number", "card_pwd", "status")


class CardDeliveryRecordSerializer(serializers.ModelSerializer):
    card_inventory_name = serializers.ReadOnlyField(
        source='card_inventory.name')
    card_inventory_pk = serializers.ReadOnlyField(
        source='card_inventory.pk')
    delivery_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S",
                                              required=False)
    to_player_nickname = serializers.ReadOnlyField(
        source='to_player.nickname')
    to_player_pk = serializers.ReadOnlyField(
        source='to_player.pk')

    class Meta:
        model = CardDeliveryRecord
        fields = (
            "pk", "card_inventory_name", "card_inventory_pk", "volumes",
            "delivery_time", "to_player_nickname", "to_player_pk", "reason")


class CardInventoriesSerializer(serializers.ModelSerializer):
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S",
                                            required=False)

    class Meta:
        model = CardInventories
        fields = ("pk", "name", "code", "market_price_cny", "volumes",
                  "warning_volumes", "update_time")

    def create(self, validated_data):
        validated_data["code"] = "1%04d" % (CardInventories.objects.count() + 1)
        return CardInventories.objects.create(**validated_data)