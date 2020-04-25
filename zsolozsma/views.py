import re
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from zsolozsma import models
from zsolozsma import queries
from datetime import datetime


def home(request):
    schedule = queries.get_schedule()

    return render(request, "zsolozsma/home.html", {'schedule': schedule})


def search(request):
    raise Http404("Search does not exist")


def info(request):
    raise Http404("Info does not exist")


def location(request, location, date=None, event=None):
    location_object = get_object_or_404(models.Location, slug=location)
    if(date):
        date = datetime.strptime(date, '%Y-%m-%d').date()

    schedule = queries.get_schedule(
        location=location_object, date=date, event_slug=event)

    return render(request, 'zsolozsma/location.html', {'location': location_object, 'schedule': schedule})


def liturgy(request, liturgy, date=None, event=None):
    liturgy_object = get_object_or_404(models.Liturgy, slug=liturgy)
    if(date):
        date = datetime.strptime(date, '%Y-%m-%d').date()

    schedule = queries.get_schedule(
        liturgy=liturgy_object, date=date, event_slug=event)

    return render(request, 'zsolozsma/liturgy.html', {'liturgy': liturgy_object, 'schedule': schedule})


def event(request, event, date=None, location=None):
    if(date):
        date = datetime.strptime(date, '%Y-%m-%d').date()

    schedule = queries.get_schedule(
        event_slug=event, date=date, location_slug=location)
    if(schedule):
        return render(request, 'zsolozsma/event.html', {'schedule': schedule})

    raise Http404("Nincs ilyen esemény!")
