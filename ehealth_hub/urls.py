"""
URL configuration for ehealth_hub project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path, include
from django.conf.urls import handler404
from django.shortcuts import render
from django.conf import settings
from django.urls import re_path
from django.views.static import serve
import os


urlpatterns = [
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('e_admin/', admin.site.urls),
    path('', include('ehealth_app.urls'))
]

# Serve locally generated profile images only in the explicit SQLite test mode.
if os.environ.get('EHEALTH_TEST_MODE') == '1':
    urlpatterns += [re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT})]

# Custom 404 handler
def custom_page_not_found(request, exception):
    return render(request, 'htmls/404.html', status=404)

handler404 = custom_page_not_found
