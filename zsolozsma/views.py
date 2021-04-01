import re
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseGone, JsonResponse
from django.urls import reverse
from zsolozsma import models
from zsolozsma import queries
from datetime import datetime
from django.conf import settings

API_PARAMETER = 'json'


def home(request):
    schedule = queries.get_schedule()

    if (API_PARAMETER in request.GET):
        return __JsonSchedule__(request, schedule)

    return render(request, "zsolozsma/home.html", {
        'message': settings.MESSAGE,
        'schedule': schedule
    })


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

    return render(request, 'zsolozsma/search.html', {
        'locations': locations,
        'liturgies': liturgies
    })


def info(request):
    return render(request, 'zsolozsma/info.html')


def location(request, city, location):
    location_object = get_object_or_404(
        models.Location.objects.select_related('city'),
        city__slug=city,
        slug=location)

    schedule = queries.get_schedule(city_slug=city, location_slug=location)

    if (API_PARAMETER in request.GET):
        return __JsonSchedule__(request, schedule)

    return render(
        request, 'zsolozsma/location.html', {
            'location': location_object,
            'schedule': schedule,
            'editor': {
                'model': models.Location._meta,
                'id': location_object.pk
            }
        })


def liturgy(request, liturgy):
    liturgy_object = get_object_or_404(models.Liturgy, slug=liturgy)

    schedule = queries.get_schedule(liturgy_slug=liturgy)

    if (API_PARAMETER in request.GET):
        return __JsonSchedule__(request, schedule)

    return render(
        request, 'zsolozsma/liturgy.html', {
            'liturgy': liturgy_object,
            'schedule': schedule,
            'editor': {
                'model': models.Liturgy._meta,
                'id': liturgy_object.pk
            }
        })


def city(request, city):
    city_object = get_object_or_404(models.City, slug=city)
    schedule = queries.get_schedule(city_slug=city)

    if (API_PARAMETER in request.GET):
        return __JsonSchedule__(request, schedule)

    return render(
        request, 'zsolozsma/city.html', {
            'city': city_object,
            'schedule': schedule,
            'editor': {
                'model': models.City._meta,
                'id': city_object.pk
            }
        })


def denomination(request, denomination, city=None):
    denomination_object = get_object_or_404(models.Denomination,
                                            slug=denomination)

    schedule = queries.get_schedule(city_slug=city,
                                    denomination_slug=denomination)

    if (API_PARAMETER in request.GET):
        return __JsonSchedule__(request, schedule)

    return render(
        request, 'zsolozsma/denomination.html', {
            'denomination': denomination_object,
            'schedule': schedule,
            'editor': {
                'model': models.Denomination._meta,
                'id': denomination_object.pk
            }
        })


def miserend(request, id):
    location_object = get_object_or_404(models.Location, miserend_id=id)

    schedule = queries.get_schedule(miserend_id=id)

    if (API_PARAMETER in request.GET):
        return __JsonSchedule__(request, schedule)

    return render(
        request, 'zsolozsma/location.html', {
            'location': location_object,
            'schedule': schedule,
            'editor': {
                'model': models.Location._meta,
                'id': location_object.pk
            }
        })


def liturgytext(request, liturgy):
    liturgy_object = get_object_or_404(models.Liturgy, slug=liturgy)

    if (liturgy_object.text):
        return render(
            request, 'zsolozsma/liturgytext.html', {
                'liturgy': liturgy_object,
                'editor': {
                    'model': models.Liturgy._meta,
                    'id': liturgy_object.pk
                }
            })

    return Http404('Nincs ilyen szöveg.')


def broadcast(request, hash, date):
    schedule_object = get_object_or_404(
        models.EventSchedule.objects.select_related('location',
                                                    'location__city',
                                                    'liturgy'),
        hash=hash)
    date = datetime.strptime(date, '%Y-%m-%d').date()

    broadcast = queries.get_broadcast(schedule_object, date)
    state = queries.get_broadcast_status(schedule_object, date)

    if (broadcast):
        if (state == queries.BroadcastState.Past):
            return HttpResponseGone("Ez a közvetítés már nem elérhető.")
        elif (state == queries.BroadcastState.Live
              or state == queries.BroadcastState.Recent
              or 'mutasd' in request.GET):
            return render(request, 'zsolozsma/broadcast_current.html',
                          {'broadcast': broadcast})
        else:
            return render(request, 'zsolozsma/broadcast_future.html', {
                'broadcast': broadcast,
                'state': state
            })

    raise Http404("Nincs ilyen közvetítés!")


def __JsonSchedule__(request, schedule):
    return JsonResponse(list(
        map(
            lambda s: {
                'date':
                s.date,
                'time':
                s.time,
                'city':
                s.city_name,
                'location':
                s.location_name,
                'name':
                s.name,
                'state':
                s.state.value,
                'duration':
                s.duration,
                'url':
                request.build_absolute_uri(
                    reverse('broadcast', args=[s.schedule_hash, s.date]))
            }, schedule)),
                        safe=False)
