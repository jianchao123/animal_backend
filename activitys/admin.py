from django.contrib import admin
from models import PresentsRecord


@admin.register(PresentsRecord)
class PresentsRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'amounts', 'to_player', 'presents_type',
                    'present_time', 'msg_content')
