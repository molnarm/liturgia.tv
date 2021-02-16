from django.urls import path, re_path
from django.views.generic import TemplateView
from zsolozsma import views

urlpatterns = [
    path('service.js', TemplateView.as_view(template_name='zsolozsma/service.js', content_type='application/javascript',), name='service.js'),

    # Kezdőlap
    path("", views.home, name="home"),

    # Keresés
    path("kereses/", views.search, name="search"),

    # Információk
    path("info/", views.info, name="info"),

    # Szertartás adatlapja, közvetítések
    path('szertartas/<slug:liturgy>/', views.liturgy, name='liturgy'),

    # Felekezet/rítus
    path('felekezet/<slug:denomination>/', views.denomination, name='denomination'),
    path('felekezet/<slug:denomination>/<slug:city>/', views.denomination, name='denomination-city'),

    # Miserend.hu
    path('miserend/<int:id>/', views.miserend, name='miserend'),

    # Közvetítés
    re_path(r'^kozvetites/(?P<hash>[\w]+)/(?P<date>\d{4}-\d{2}-\d{2})/$', views.broadcast, name='broadcast'),
    
    # Város
    path('<slug:city>/', views.city, name='city'),
    # Helyszín adatlapja, közvetítések
    path('<slug:city>/<slug:location>/', views.location, name='city-location'),

]
