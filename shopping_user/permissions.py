# coding:utf-8

from rest_framework import permissions
import logging

logger = logging.getLogger(__name__)

SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')


class IsAdministratorPermission(permissions.BasePermission):
    """是否管理员"""

    def has_permission(self, request, view):
        user = request.user
        if not user.is_staff:
            logger.error(u"{}".format(user.phone))
            logger.error(
                u"不是职员 {}".format(user.is_staff))
            return False
        if not user.groups.filter(name=u"管理员").count():
            logger.error(u"不是管理员 {}".format(user.groups.filter(name=u"管理员").count()))
            return False
        return True

    def has_object_permission(self, request, view, obj):
        """判断用户是否具有单个obj的修改权限"""
        user = request.user
        if not user.is_staff:
            logger.error(
                u"不是职员 {}".format(user.is_staff))
            return False
        if not user.groups.filter(name=u"管理员").count():
            logger.error(
                u"不是管理员 {}".format(user.groups.filter(name=u"管理员").count()))
            return False
        return True


class IsGamePlayer(permissions.BasePermission):
    """是否玩家"""

    def has_permission(self, request, view):
        user = request.user
        if not user.groups.filter(name=u"玩家").count():
            return False
        return True

    def has_object_permission(self, request, view, obj):
        """判断用户是否具有单个obj的修改权限"""
        # if request.method not in SAFE_METHODS:
        #     return False
        user = request.user
        if not user.groups.filter(name=u"玩家").count():
            return False
        return True


class IsRecycleBusinessman(permissions.BasePermission):
    """是否回收商"""

    def has_permission(self, request, view):
        user = request.user
        if not user.groups.filter(name=u"回收商").count():
            return False
        return True

    def has_object_permission(self, request, view, obj):
        """判断用户是否具有单个obj的修改权限"""
        # if request.method not in SAFE_METHODS:
        #     return False
        user = request.user
        if not user.groups.filter(name=u"回收商").count():
            return False

        # 代充
        if hasattr(obj, "from_recycle_businessman"):
            if obj.from_recycle_businessman.pk == user.pk:
                return True
        elif hasattr(obj, "to_recycle_businessman"):
            if obj.to_recycle_businessman.pk == user.pk:    #
                return True
        return False


class IsAdminOrBusinessman(permissions.BasePermission):
    """是否管理员或者回收商
        该权限只能用于读操作
    """

    def has_permission(self, request, view):
        user = request.user
        if user.groups.filter(name=u"管理员").count():
            return True
        if user.groups.filter(name=u"回收商").count():
            return True
        return False

    def has_object_permission(self, request, view, obj):
        """判断用户是否具有单个obj的修改权限"""
        # if request.method not in SAFE_METHODS:
        #     return False
        user = request.user
        if user.groups.filter(name=u"管理员").count():
            return True
        if user.groups.filter(name=u"回收商").count():
            return True
        return False