from operator import attrgetter
from datetime import datetime, timedelta
from zsolozsma import models
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist


class ScheduleItem(object):
    event = None
    date = None
    time = None

    def __init__(self, event,  date, time):
        self.event = event
        self.date = date
        self.time = time


def get_schedule(
        location=None,
        location_slug=None,
        date=None,
        liturgy=None,
        liturgy_slug=None,
        event=None,
        event_slug=None):
    events = models.Event.objects.all()

    if(date):
        weekday = date.weekday()
        dates = [(date, weekday)]
        events = events.filter(Q(date=date) | Q(day_of_week=weekday))
    else:
        MAX_DAYS = 7
        today = datetime.today().date()

        dates = [(date, date.weekday())
                 for date in [today + timedelta(days=i) for i in range(MAX_DAYS)]]

    if (location):
        events = events.filter(location=location)
    elif(location_slug):
        events = events.filter(location_slug=location_slug)

    if(liturgy):
        events = events.filter(liturgy=liturgy)
    elif(liturgy_slug):
        events = events.filter(liturgy_slug=liturgy_slug)

    if(event):
        events = [event]
    elif(event_slug):
        events = events.filter(slug=event_slug)

    schedule = list()
    for (_date, _day) in dates:
        schedule.extend([ScheduleItem(event, _date, event.time)
                         for event in events if event.day_of_week == _day])

    schedule.sort(key=attrgetter('date', 'time'))

    return schedule


class BroadcastItem(object):
    event_name = None
    liturgy_name = None
    video_url = None
    text_url = None


def get_broadcast(event, date):
    broadcast_item = BroadcastItem()

    broadcast_item.event_name = event.name
    broadcast_item.location_name = event.location.name
    broadcast_item.liturgy_name = event.liturgy.name

    if(event.video_url):
        broadcast_item.video_url = event.video_url
    else:
        broadcast_item.video_url = event.location.video_url

    if(event.text_url):
        broadcast_item.text_url = event.text_url
    else:
        try:
            liturgy_text = models.LiturgyText.objects.get(
                liturgy=event.liturgy, date=date)
            if(liturgy_text):
                broadcast_item.text_url = event.liturgy_text.text_url
        except ObjectDoesNotExist:
            pass

    return broadcast_item
