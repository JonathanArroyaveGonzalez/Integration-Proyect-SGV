"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include

from wmsAdapterV2.urls import wms_endpoints_v2
from wmsBase.urls import wms_base_endpoints
from wmsAdapter.urls import wms_endpoints
from contapyme.urls import contapyme_endpoints

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^wms/', include(wms_endpoints)),
    re_path(r'^wms/adapter/v2/', include(wms_endpoints_v2)),
    re_path(r'^wms/base/v2/', include(wms_base_endpoints)),
    re_path(r'^contapyme/', include(contapyme_endpoints)),
]
