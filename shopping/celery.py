# coding:utf-8

from __future__ import absolute_import, \
    unicode_literals  # 目的是拒绝隐士引入，celery.py和celery冲突。
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shopping.settings")

# 创建celery应用
app = Celery('shopping')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)