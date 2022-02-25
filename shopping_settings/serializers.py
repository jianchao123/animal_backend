# coding:utf-8

from rest_framework import serializers
from models import CommodityType, BuyChannel, Notice, Banner, Area, PayType, \
    PayAccountsConf, PayMoneyCtl, CommonParamConf, ShippingAddress, \
    PayChannel, SectionMoneyRecord, FeesUseRecord
from recycle_businessman.models import RecycleBusinessman
from shopping_user.models import GamePlayer
from django.conf import settings
import logging
from random import randint
from utils import utils

logger = logging.getLogger(__name__)


class CommodityTypeSerializer(serializers.ModelSerializer):
    def get_status_describe(self, obj):
        for k, v in CommodityType.status_tuple:
            if obj.status == k:
                return v
        return 0

    status_describe = serializers.SerializerMethodField()

    class Meta:
        model = CommodityType
        fields = ("pk", "type_name", "type_code", "type_index", "status",
                  "status_describe")


class BuyChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuyChannel
        fields = ("pk", "channel_code", "remark")


class NoticeSerializer(serializers.ModelSerializer):
    def get_status_describe(self, obj):
        for k, v in Notice.status_tuple:
            if obj.status == k:
                return v
        return 0

    status_describe = serializers.SerializerMethodField()

    def get_type_describe(self, obj):
        for k, v in Notice.type_tuple:
            if obj.notice_type == k:
                return v
        return 0

    type_describe = serializers.SerializerMethodField()

    class Meta:
        model = Notice
        fields = ("pk", "title", "content", "notice_type", "status", "index",
                  "administrator_id", "is_notice_businessman", "create_time")


class BannerSerializer(serializers.ModelSerializer):
    def get_imagepath(self, obj):
        return settings.STATIC_DOMAIN + obj.image_path

    imagepath = serializers.SerializerMethodField()

    class Meta:
        model = Banner
        fields = (
            "pk", "title", "imagepath", "image_path", "link", "index",
            "status", "administrator_id", "create_time")

    def update(self, instance, validated_data):
        if "image_path" in validated_data:
            validated_data["image_path"] = \
                validated_data["image_path"].replace(settings.STATIC_DOMAIN, "")
        return super(BannerSerializer, self).update(
            instance, validated_data)


class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ("pk", "pid", "shortname", "name", "merger_name", "level",
                  "pinyin", "code", "zip_code", "first", "lng", "lat")


class PayTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayType
        fields = ("pk", "pay_name", "code", "pay_rates",
                  "is_third_party", "status")


class PayChannelSerializer(serializers.ModelSerializer):

    pay_type_name = serializers.ReadOnlyField(source="pay_type.pay_name")

    class Meta:
        model = PayChannel
        fields = ("pk", "name", "code", "rate", "money_str", "pay_type",
                  "company", "pay_type_name", "status")


class PayAccountsConfSerializer(serializers.ModelSerializer):
    operator = serializers.ReadOnlyField(read_only=True)

    pay_channel_name = serializers.ReadOnlyField(source='pay_channel.name')

    class Meta:
        model = PayAccountsConf
        fields = ("pk", "pay_channel_name",
                  "pay_channel", "merchant_no", "status",
                  "is_use", "remark", "operator")


class PayMoneyCtlSerializer(serializers.ModelSerializer):
    history_min = serializers.ReadOnlyField(read_only=True)
    history_max = serializers.ReadOnlyField(read_only=True)
    operator = serializers.ReadOnlyField(read_only=True)
    pay_channel_name = serializers.ReadOnlyField(source='pay_channel.name')

    class Meta:
        model = PayMoneyCtl
        fields = ("pk", "min", "max", "history_min", "history_max",
                  "pay_channel", "pay_channel_name", "status", "operator")


class CommonParamConfSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommonParamConf
        fields = ("pk", "conf_name", "conf_key", "conf_value")

    def update(self, instance, validated_data):
        """更新所有卡商的二维码"""
        conf_key = validated_data["conf_key"]
        conf_value = validated_data["conf_value"]
        # 邀请链接
        if conf_key == "invite_link":
            businessmans = RecycleBusinessman.objects.all()
            for row in businessmans:
                invite_qr_code = utils.generate_qr_code(
                    conf_value + "?" + "invite_code=" + row.invite_code,
                    str(randint(1, 1000)) + str(randint(1001, 2000)))
                row.invite_qr_code = invite_qr_code
                row.save()
        return super(CommonParamConfSerializer, self).update(
            instance, validated_data)


class ShippingAddressSerializer(serializers.ModelSerializer):
    province_name = serializers.ReadOnlyField(source='province.name')
    city_name = serializers.ReadOnlyField(source='city.name')
    area_name = serializers.ReadOnlyField(source='area.name')

    class Meta:
        model = ShippingAddress
        fields = ("pk", "player_id", "recipents_name", "province",
                  "province_name", "city", "city_name", "area", "area_name",
                  "recipents_phone", "recipents_address", "is_default")

    def create(self, validated_data):
        request = self.__dict__["_context"]["request"]
        user = request.user
        validated_data["player"] = GamePlayer.objects.get(pk=user.pk)
        if not validated_data["is_default"]:
            if not ShippingAddress.objects.filter(player__pk=user.pk).count():
                validated_data["is_default"] = True
        return ShippingAddress.objects.create(**validated_data)

    def update(self, instance, validated_data):
        request = self.__dict__["_context"]["request"]
        user = request.user
        if not validated_data["is_default"]:
            if ShippingAddress.objects.filter(player__pk=user.pk).count() == 1:
                validated_data["is_default"] = True
        return super(ShippingAddressSerializer, self).update(
            instance, validated_data)


class SectionMoneyRecordSerializer(serializers.ModelSerializer):

    class Meta:
        model = SectionMoneyRecord
        fields = ('id', 'section_mix', 'section_max', 'present_amounts', 'text')


class FeesUseRecordSerializer(serializers.ModelSerializer):
    use_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S",
                                            read_only=True)

    class Meta:
        model = FeesUseRecord
        fields = ('id', 'text', 'use_time', 'create_time')