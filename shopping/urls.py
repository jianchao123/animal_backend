"""shopping URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^activitys/', include('activitys.urls')),
    url(r'^settings/', include('shopping_settings.urls')),
    url(r'^user/', include('shopping_user.urls')),
    url(r'^snatchtreasure/', include('snatch_treasure.urls')),
    url(r'^inventory/', include('inventory.urls')),
    url(r'^statistics/', include('statistics.urls')),
    url(r'^financial/', include('financial.urls')),
    url(r'^businessman/', include('recycle_businessman.urls')),
    url(r'^rest/', include('rest.urls')),
    url(r'^pay/', include('pay.urls')),
    url(r'^api-auth/',
        include('rest_framework.urls', namespace="rest_framework")),
]
