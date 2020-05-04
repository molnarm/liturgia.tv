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
    locations = models.Location.objects.all().order_by(
        'name').values_list('name', 'slug')
    liturgies = models.Liturgy.objects.all().order_by(
        'name').values_list('name', 'slug')

    return render(request, 'zsolozsma/search.html', {'locations': locations, 'liturgies': liturgies})


def info(request):
    return render(request, 'zsolozsma/info.html')


def location(request, location, date=None):
    location_object = get_object_or_404(models.Location, slug=location)
    if(date):
        date = datetime.strptime(date, '%Y-%m-%d').date()

    schedule = queries.get_schedule(location=location_object, date=date)

    return render(request, 'zsolozsma/location.html', {'location': location_object, 'schedule': schedule})


def liturgy(request, liturgy, date=None):
    liturgy_object = get_object_or_404(models.Liturgy, slug=liturgy)
    if(date):
        date = datetime.strptime(date, '%Y-%m-%d').date()

    schedule = queries.get_schedule(liturgy=liturgy_object, date=date)

    return render(request, 'zsolozsma/liturgy.html', {'liturgy': liturgy_object, 'schedule': schedule})


def broadcast(request, hash, date):
    event_object = get_object_or_404(models.Event, hash=hash)
    date = datetime.strptime(date, '%Y-%m-%d').date()

    broadcast = queries.get_broadcast(event_object, date)

    if(broadcast):
        return render(request, 'zsolozsma/broadcast.html', {'broadcast': broadcast})

    raise Http404("Nincs ilyen közvetítés!")
