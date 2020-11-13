from django.urls import path, re_path
from zsolozsma import views

urlpatterns = [
    # Kezdőlap
    path("", views.home, name="home"),

    # Keresés
    path("kereses/", views.search, name="search"),

    # Információk
    path("info/", views.info, name="info"),

    # Szertartás adatlapja, közvetítések
    path('szertartas/<slug:liturgy>/', views.liturgy, name='liturgy'),
    re_path(r'^szertartas/(?P<liturgy>[\w-]+)/(?P<date>\d{4}-\d{2}-\d{2})/$', views.liturgy, name='liturgy-date'),
    re_path(r'^szertartas/(?P<liturgy>[\w-]+)/(?P<location>[\w-]+)/$', views.liturgy, name='liturgy-location'),

    # Helyszín adatlapja, közvetítések
    re_path(r'^helyszin/(?P<location>[\w-]+)/$', views.location, name='location'),
    re_path(r'^helyszin/(?P<location>[\w-]+)/(?P<date>\d{4}-\d{2}-\d{2})/$', views.location, name='location-date'),
    
    # Város
    re_path(r'^varos/(?P<city>[\w-]+)/$', views.city, name='city'),

    # Egyházmegye
    re_path(r'^egyhazmegye/(?P<diocese>[\w-]+)/$', views.diocese, name='diocese'),

    # Közvetítés
    re_path(r'^kozvetites/(?P<hash>[\w]+)/(?P<date>\d{4}-\d{2}-\d{2})/$', views.broadcast, name='broadcast'),
]
