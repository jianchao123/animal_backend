from django.contrib import admin
from models import Imgs


@admin.register(Imgs)
class ImgsAdmin(admin.ModelAdmin):
    list_display = ("pk", "image_path", "resource_type", "relation_pk", "info")


