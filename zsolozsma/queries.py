from operator import attrgetter
from datetime import datetime, timedelta
from django.utils import timezone
from zsolozsma import models, youtube
from django.core.exceptions import ObjectDoesNotExist
import urllib.request
import os

SCHEDULE_FUTURE_DAYS = os.getenv('SCHEDULE_FUTURE_DAYS', 3)
TIMEDELTA_TOLERANCE = os.getenv('TIMEDELTA_TOLERANCE', 15)


class ScheduleItem(object):
    event = None
    schedule = None
    date = None
    time = None

    enabled = False
    live = False
    shown = False

    def __init__(self, schedule, date, time):
        self.schedule = schedule
        self.event = schedule.event
        self.date = date
        self.time = time

        (self.enabled, self.live, self.shown) = get_broadcast_status(schedule, date)


def get_schedule(
        location=None,
        location_slug=None,
        date=None,
        liturgy=None,
        liturgy_slug=None,
        event=None):
    scheduleQuery = models.EventSchedule.objects.select_related(
        'event', 'event__location').all()

    if(date):
        weekday = date.weekday()
        dates = [(date, weekday)]
        scheduleQuery = scheduleQuery.filter(day_of_week=weekday)
    else:
        today = timezone.localtime().date()

        dates = [(date, date.weekday())
                 for date in [today + timedelta(days=i) for i in range(SCHEDULE_FUTURE_DAYS)]]

    if (location):
        scheduleQuery = scheduleQuery.filter(event__location=location)
    elif(location_slug):
        scheduleQuery = scheduleQuery.filter(event__location_slug=location_slug)

    if(liturgy):
        scheduleQuery = scheduleQuery.filter(event__liturgy=liturgy)
    elif(liturgy_slug):
        scheduleQuery = scheduleQuery.filter(event__liturgy_slug=liturgy_slug)

    if(event):
        scheduleQuery = scheduleQuery.filter(event=event)

    schedule = list()
    for (_date, _day) in dates:
        schedule.extend([i for i in [ScheduleItem(item, _date, item.time)
                                     for item in scheduleQuery if item.day_of_week == _day] if i.shown])

    schedule.sort(key=attrgetter('date', 'time', 'event.name'))

    return schedule


# (enabled, live, shown)
def get_broadcast_status(schedule, date):
    now = timezone.localtime()
    if (now.date() < date):
        return (False, False, True)

    event_time = timezone.get_current_timezone().localize(
        datetime.combine(date, schedule.time))
    difference = now - event_time
    minutes = difference.total_seconds() / 60

    duration = schedule.event.duration or 60

    if (minutes < - TIMEDELTA_TOLERANCE):
        return (False, False, True)  # még több, mint 15 perc a kezdésig
    elif (minutes < 0):
        return (True, False, True)  # 15 percen belül kezdődik
    elif (minutes < duration):
        return (True, True, True)   # éppen tart
    elif (minutes < duration + TIMEDELTA_TOLERANCE):
        return (True, False, True)  # 15 percen belül ért véget
    else:
        return (False, False, False)


class BroadcastItem(object):
    def __init__(self, event, broadcast):
        self.event_name = event.name
        self.location_name = event.location.name
        self.liturgy_name = event.liturgy.name

        self.has_text = bool(broadcast.text_url)
        self.text_url = broadcast.text_url
        self.text_iframe = broadcast.text_iframe

        self.video_url = broadcast.video_url
        self.video_iframe = broadcast.video_iframe
        self.video_only = broadcast.video_only


def get_broadcast(schedule, date):
    now = timezone.localtime()
    if (now.date() < date):
        return None

    broadcast = __get_or_create_broadcast(schedule, date)

    broadcast_item = BroadcastItem(schedule.event, broadcast)

    return broadcast_item


def __get_or_create_broadcast(schedule, date):
    event = schedule.event

    try:
        broadcast = models.Broadcast.objects.get(schedule=schedule, date=date)
    except ObjectDoesNotExist:
        broadcast = models.Broadcast()
        broadcast.schedule = schedule
        broadcast.date = date

    if(not broadcast.video_url):
        video_url = None

        if(schedule.youtube_channel):
            video_url = youtube.get_video(schedule.youtube_channel)
            broadcast.video_only = True
        elif(event.youtube_channel):
            video_url = youtube.get_video(event.youtube_channel)
            broadcast.video_only = True
        elif(schedule.video_url):
            video_url = event.video_url
        elif(event.video_url):
            video_url = event.video_url
        elif(event.location.youtube_channel):
            video_url = youtube.get_video(event.location.youtube_channel)
            broadcast.video_only = True
        else:
            video_url = event.location.video_url

        if(video_url):
            broadcast.video_url = video_url
            broadcast.video_iframe = __check_iframe_support(video_url)
            broadcast.save()

    if (not broadcast.text_url):
        text_url = None
        if(schedule.text_url):
            text_url = schedule.text_url
        elif(event.text_url):
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
