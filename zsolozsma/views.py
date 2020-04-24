import re
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from zsolozsma import models
from zsolozsma import queries


def home(request):
    schedule = queries.get_schedule()

    return render(request, "zsolozsma/home.html", { 'schedule': schedule })


def calendar(request):
    raise Http404("Calendar does not exist")


def info(request):
    raise Http404("Info does not exist")


def location(request, slug, date=None):
    location = get_object_or_404(models.Location, slug=slug)
    schedule = queries.get_schedule(location, date)

    return render(request, 'zsolozsma/location.html', { 'location': location, 'schedule': schedule })

def event(request, location, date, event):
    raise Http404("Event does not exist")
