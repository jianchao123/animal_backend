# coding:utf-8
from django.conf import settings
from rest_framework import serializers
from models import Imgs


class ImagesSerializer(serializers.ModelSerializer):

    def get_image_path(self, obj):
        return settings.STATIC_DOMAIN + obj.image_path

    image_path = serializers.SerializerMethodField()

    class Meta:
        model = Imgs
        fields = ("pk", "image_path", "resource_type", "relation_pk", "info")