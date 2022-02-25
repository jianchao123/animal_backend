# coding:utf-8
from __future__ import unicode_literals

from django.db import models


class Imgs(models.Model):
    """图片资源"""

    # 模型类的名字
    resource_type_tuple = (
        (1, u"Commodity"),
    )

    image_path = models.TextField(blank=True, null=True,
                                  verbose_name=u"图片路径")
    resource_type = models.IntegerField(choices=resource_type_tuple,
                                        blank=True,
                                        null=True, verbose_name=u"资源类型")
    relation_pk = models.IntegerField(blank=True,
                                      null=True, verbose_name=u"关联的主键")
    info = models.CharField(max_length=128, blank=True, null=True,
                            verbose_name=u"图片信息")

    def __unicode__(self):
        return str(self.image_path)

    class Meta:
        db_table = u"imgs"
        verbose_name = u"图片表"
        verbose_name_plural = verbose_name