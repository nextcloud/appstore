"""nextcloudappstore URL Configuration

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
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views as auth_views

import allauth.urls

from nextcloudappstore.core.views import HomeView, \
     AppDetailView, AppsByCategoryView

urlpatterns = [
    url(r'^$',
        HomeView.as_view(),
        name='home'),
    url(r'^',
        include('allauth.urls')),
    url(r'^category/(?P<id>[-\w]+)$',
        AppsByCategoryView.as_view(),
        name='category_list_category'),
    url(r'^app/(?P<id>[-\w]+)$',
        AppDetailView.as_view(),
        name='app_detail'),
    url(r'^api/v1/',
        include('nextcloudappstore.core.api.v1.urls',
                namespace='api-v1')
        ),
    url(r'^admin/',
        admin.site.urls),
]
