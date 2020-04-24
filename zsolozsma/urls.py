from django.urls import path, re_path
from zsolozsma import views

urlpatterns = [
    path("", views.home, name="home"),
    path("calendar/", views.calendar, name="calendar"),
    path("info/", views.info, name="info"),
    path('<slug:slug>/', views.location, name='location'),
    re_path(r'^(?P<slug>[\w-]+)/(?P<date>\d{4}-\d{2}-\d{2})/$', views.location, name='location'),
    re_path(r'^(?P<location>[\w-]+)/(?P<date>\d{4}-\d{2}-\d{2})/(?P<event>[\w-]+)/$', views.event, name='event')
]
