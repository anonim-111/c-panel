"""
URL configuration for core project.

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
from django.conf import settings
from django.contrib import admin
from django.shortcuts import render
from django.urls import path, re_path
from django.views.static import serve

from psytracks.views import PsychiatristAutocomplete, InspectorAutocomplete
from users.views import dashboard_view, statistics_view
from utils.views import district_patient_stats, mahalla_patient_stats

def custom_permission_denied_view(request, exception=None):
    return render(request, "403.html", status=403)

def custom_page_not_found_view(request, exception=None):
    return render(request, "404.html", status=404)

handler403 = custom_permission_denied_view
handler404 = custom_page_not_found_view

def get_admin_urls(urls):
    def get_urls():
        my_urls = [
            path("", admin.site.admin_view(dashboard_view), name="dashboard"),
            path("statistics/", admin.site.admin_view(statistics_view), name="statistics"),
        ]
        return my_urls + urls
    return get_urls

admin.site.get_urls = get_admin_urls(admin.site.get_urls())

urlpatterns = [
    path('inspector-autocomplete/', InspectorAutocomplete.as_view(), name='inspector-autocomplete'),
    path('psychiatrist-autocomplete/', PsychiatristAutocomplete.as_view(), name='psychiatrist-autocomplete'),
    path("admin/district_patient_stats/", district_patient_stats, name="district_patient_stats"),
    path("admin/mahalla_patient_stats/<int:district_id>/", mahalla_patient_stats, name="mahalla_patient_stats"),
    re_path(r'^media/(?P<path>.*)$', serve,
            {'document_root': settings.MEDIA_ROOT}),
    path('', admin.site.urls),
]