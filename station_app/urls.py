from django.urls import path
from . import views

urlpatterns = [
    path('<int:station_id>/media/', views.get_station_media, name='station_media'),
    path('<int:station_id>/slider/', views.station_media_slider, name='station_media_slider'),

]