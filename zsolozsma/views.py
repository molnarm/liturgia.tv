import re
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseGone
from zsolozsma import models
from zsolozsma import queries
from datetime import datetime


def home(request):
    schedule = queries.get_schedule()

    return render(request, "zsolozsma/home.html", {'schedule': schedule})


def search(request):
    locations = models.Location.objects\
        .filter(is_active=True)\
        .select_related('city__name', 'city__slug')\
        .order_by('city__name', 'name')\
        .values_list('city__name', 'name', 'city__slug', 'slug')
    liturgies = models.Liturgy.objects.all()\
        .select_related('denomination__name')\
        .order_by('denomination__name', 'name')\
        .values_list('denomination__name', 'name', 'slug')

    return render(request, 'zsolozsma/search.html', {'locations': locations, 'liturgies': liturgies})


def info(request):
    return render(request, 'zsolozsma/info.html')


def location(request, city, location):
    location_object = get_object_or_404(models.Location, city__slug=city, slug=location)

    schedule = queries.get_schedule(city_slug=city, location_slug=location)

    return render(request, 'zsolozsma/location.html', {'location': location_object, 'schedule': schedule})


def liturgy(request, liturgy):
    liturgy_object = get_object_or_404(models.Liturgy, slug=liturgy)

    schedule = queries.get_schedule(liturgy_slug=liturgy)

    return render(request, 'zsolozsma/liturgy.html', {'liturgy': liturgy_object, 'schedule': schedule})

def city(request, city):
    city_object = get_object_or_404(models.City, slug=city)
    schedule = queries.get_schedule(city_slug=city)

    return render(request, 'zsolozsma/city.html', { 'city': city_object, 'schedule': schedule })

def broadcast(request, hash, date):
    schedule_object = get_object_or_404(models.EventSchedule, hash=hash)
    date = datetime.strptime(date, '%Y-%m-%d').date()

    broadcast = queries.get_broadcast(schedule_object, date)
    state = queries.get_broadcast_status(schedule_object, date)

    if(broadcast):
        if(state == queries.BroadcastState.Past):
            return HttpResponseGone("Ez a közvetítés már nem elérhető.")
        elif(state == queries.BroadcastState.Live or state == queries.BroadcastState.Recent or 'mutasd' in request.GET):
            return render(request, 'zsolozsma/broadcast_current.html', {'broadcast': broadcast })
        else:
            return render(request, 'zsolozsma/broadcast_future.html', {'broadcast': broadcast, 'state': state })

    raise Http404("Nincs ilyen közvetítés!")