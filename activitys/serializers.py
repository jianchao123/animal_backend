# coding:utf-8
from django.contrib.auth.models import AnonymousUser
from rest_framework import serializers
from models import PresentsRecord, SunTheOrder
from shopping_user.models import GamePlayer
from activitys.models import Praise


class PresentsRecordSerializer(serializers.ModelSerializer):

    player_name = serializers.SerializerMethodField()

    def get_player_name(self, obj):
        if obj.to_player.nickname:
            v = obj.to_player.nickname
        else:
            v = obj.to_player.phone
        v += " [{}]".format(obj.to_player.phone)
        return v

    present_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = PresentsRecord
        fields = ('id', 'amounts', 'to_player', 'player_name', 'present_time')


class SunTheOrderSerializer(serializers.ModelSerializer):
    """晒单"""

    reward_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S",
                                            read_only=True)
    commodity_pk = serializers.ReadOnlyField(source='period.commodtiy.id')

    is_praise = serializers.SerializerMethodField()

    def get_is_praise(self, obj):
        request = self.__dict__["_context"]["request"]
        if request.user.is_authenticated():
            game_player = GamePlayer.objects.get(pk=request.user.pk)
            praise = Praise.objects.filter(praise_player=game_player,
                                           sun_the_order=obj).first()
            if praise:
                return True
            else:
                return False
        else:
            return False

    praise_count = serializers.SerializerMethodField()

    def get_praise_count(self, obj):
        count = Praise.objects.filter(sun_the_order=obj).count()
        return count

    def create(self, validated_data):
        request = self.__dict__["_context"]["request"]
        if request.user.is_authenticated():
            if validated_data["luck_player"].pk != request.user.id:
                raise serializers.ValidationError("qwe")
            return SunTheOrder.objects.create(**validated_data)
        else:
            raise serializers.ValidationError("error")

    class Meta:
        model = SunTheOrder
        fields = ('id', 'commodity_name', 'img_url', 'period_no', 'praise_count',
                  'reward_time', 'luck_player_name', 'luck_player', 'period',
                  'text', 'upload_img', 'praise_count', 'create_time',
                  'is_praise', 'luck_player_headimg', 'commodity_pk')


class PraiseSerializer(serializers.ModelSerializer):
    """点赞"""

    class Meta:
        model = Praise
        fields = ('id', 'sun_the_order', 'praise_player')