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

    # Esemény adatlapja, közvetítések
    re_path(r'^esemeny/(?P<event>[\w-]+)/$', views.event, name='event'),
    re_path(r'^esemeny/(?P<event>[\w-]+)/(?P<date>\d{4}-\d{2}-\d{2})/$', views.event, name='event-date'),
    re_path(r'^esemeny/(?P<event>[\w-]+)/(?P<location>[\w-]+)/$', views.event, name='event-location'),

    # Hely adatlapja, közvetítések
    re_path(r'^(?:hely/)?(?P<location>[\w-]+)/$', views.location, name='location'),
    re_path(r'^(?:hely/)?(?P<location>[\w-]+)/(?P<date>\d{4}-\d{2}-\d{2})/$', views.location, name='location-date'),
    re_path(r'^(?:hely/)?(?P<location>[\w-]+)/(?P<event>[\w-]+)/$', views.location, name='location-event'),
]
