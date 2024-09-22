
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from machineapp import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("screen/", include("screen_app.urls")),
    path('account/', include('user_app.urls')),
    path('', views.home, name='home'),
    path('user/logout/', views.user_logout, name='user_logout'),
    path('machine/login/', views.machine_login, name='machine_login'),
    path('machine/logout/', views.machine_logout, name='machine_logout'),
    path('skill-logout/', views.skill_based_user_logout, name='skill_based_user_logout'),
]
