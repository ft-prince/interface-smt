from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from machineapp import views
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.views import serve

admin.site.site_header = 'InterfaceAuto  Admin Panel'
admin.site.site_title = 'Company Portal'
admin.site.index_title = 'Welcome to Administration'

urlpatterns = [
    path("admin/", admin.site.urls),
    path("screen/", include("screen_app.urls")),
    path('account/', include('user_app.urls')),
    path('station/',include('station_app.urls')),
    path('', views.home, name='home'),
    path('user/logout/', views.user_logout, name='user_logout'),
    path('machine/login/', views.machine_login, name='machine_login'),
    path('machine/logout/', views.machine_logout, name='machine_logout'),
    path('skill-logout/', views.skill_based_user_logout, name='skill_based_user_logout'),
    path('api/check-machine-status/', views.check_machine_status, name='check_machine_status'),
    path('machine-checklist-config/', views.machine_checklist_config, name='machine_checklist_config'),
    path('switch-machine/<int:machine_id>/', views.switch_machine, name='switch_machine'),
    path('debug-machine-login/', views.debug_machine_login, name='debug_machine_login'),

    # Service Worker path
    path('sw.js', serve, kwargs={'path': 'sw.js'}, name='sw.js'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)