from operator import attrgetter
from datetime import datetime, timedelta
from zsolozsma import models
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
import urllib.request


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

    video_iframe = None
    video_url = None
    video_content = None

    has_text = False
    text_iframe = None
    text_url = None
    text_content = None


def get_broadcast(event, date):
    broadcast = __get_or_create_broadcast(event, date)

    broadcast_item = BroadcastItem()

    broadcast_item.event_name = event.name
    broadcast_item.location_name = event.location.name
    broadcast_item.liturgy_name = event.liturgy.name

    broadcast_item.has_text = bool(broadcast.text_url)
    broadcast_item.text_url = broadcast.text_url
    broadcast_item.text_iframe = broadcast.text_iframe

    broadcast_item.video_url = broadcast.video_url
    broadcast_item.video_iframe = broadcast.video_iframe

    return broadcast_item


def __get_or_create_broadcast(event, date):
    try:
        broadcast = models.Broadcast.objects.get(event=event, date=date)
    except ObjectDoesNotExist:
        broadcast = models.Broadcast()
        broadcast.event = event
        broadcast.date = date

    if(not broadcast.video_url):
        # TODO YouTube
        video_url = None
        if(event.video_url):
            video_url = event.video_url
        else:
            video_url = event.location.video_url

        if(video_url):
            broadcast.video_url = video_url
            broadcast.video_iframe = __check_iframe_support(video_url)
            broadcast.save()

        if (not broadcast.text_url):
            text_url = None
            if(event.text_url):
                text_url = event.text_url
            else:
                try:
                    liturgy_text = models.LiturgyText.objects.get(
                        liturgy=event.liturgy, date=date)
                    if(liturgy_text):
                        text_url = liturgy_text.text_url
                        broadcast.save()
                except ObjectDoesNotExist:
                    pass

            if (text_url):
                broadcast.text_url = text_url
                broadcast.text_iframe = __check_iframe_support(text_url)
                broadcast.save()

    return broadcast


def __check_iframe_support(url):
    request = urllib.request.Request(url)
    response = urllib.request.urlopen(request)
    frame_header = response.getheader('X-Frame-Options')
    return frame_header is None
