import os
import os
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import datetime, timedelta
from enum import IntEnum
from operator import attrgetter

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone

from zsolozsma import models, viewmodels

SCHEDULE_FUTURE_DAYS = os.getenv('SCHEDULE_FUTURE_DAYS', 3)
TIMEDELTA_TOLERANCE = os.getenv('TIMEDELTA_TOLERANCE', 15)


class BroadcastState(IntEnum):
    Invalid = 0,
    Future = 1,
    Upcoming = 2,
    Live = 3,
    Recent = 4,
    Past = 5


def get_schedule(location_slug=None,
                 liturgy_slug=None,
                 city_slug=None,
                 denomination_slug=None,
                 miserend_id=None,
                 days=SCHEDULE_FUTURE_DAYS):
    today = timezone.localtime().date()
    validity_end = today + timedelta(days=days)
    dates = [(date, date.weekday())
             for date in [today + timedelta(days=i) for i in range(days)]]

    scheduleQuery = models.EventSchedule.objects \
        .select_related('location', 'location__city', 'liturgy') \
        .filter(location__is_active=True) \
        .filter(Q(valid_from__lte=validity_end) | Q(valid_from=None)) \
        .filter(Q(valid_to__gte=today) | Q(valid_to=None)) \
        .filter(day_of_week__in=[d[1] for d in dates])

    if location_slug:
        scheduleQuery = scheduleQuery.filter(location__slug=location_slug)
    if liturgy_slug:
        scheduleQuery = scheduleQuery.filter(liturgy__slug=liturgy_slug)
    if city_slug:
        scheduleQuery = scheduleQuery.filter(location__city__slug=city_slug)
    if denomination_slug:
        scheduleQuery = scheduleQuery.filter(
            liturgy__denomination__slug=denomination_slug)
    if miserend_id:
        scheduleQuery = scheduleQuery.filter(location__miserend_id=miserend_id)

    extraordinary_events = [(item.day_of_week, item.location)
                            for item in scheduleQuery if item.is_extraordinary]

    daily_schedules = defaultdict(list)
    for scheduleItem in scheduleQuery:
        if scheduleItem.is_extraordinary or ((scheduleItem.day_of_week, scheduleItem.location) not in extraordinary_events):
            daily_schedules[scheduleItem.day_of_week].append(scheduleItem)

    schedule = [
        scheduleItem for scheduleItem in [
            viewmodels.ScheduleItem(event, _date) for (_date, _day) in dates
            for event in daily_schedules[_day]
        ] if scheduleItem.state != BroadcastState.Past and scheduleItem.state != BroadcastState.Invalid
    ]

    schedule.sort(key=attrgetter('date', 'time', 'city_name', 'location_name'))

    return schedule


def get_broadcast_status(schedule, date):
    now = timezone.localtime()
    if now.date() < date:
        return BroadcastState.Future

    event_time = datetime.combine(date, schedule.time).replace(tzinfo=timezone.get_current_timezone())

    if schedule.valid_from and schedule.valid_from > date:
        return BroadcastState.Invalid
    if schedule.valid_to and schedule.valid_to < date:
        return BroadcastState.Invalid

    difference = now - event_time
    minutes = difference.total_seconds() / 60

    duration = schedule.duration or schedule.liturgy.duration

    if minutes < -TIMEDELTA_TOLERANCE:
        return BroadcastState.Future  # még több, mint 15 perc a kezdésig
    elif minutes < 0:
        return BroadcastState.Upcoming  # 15 percen belül kezdődik
    elif minutes < duration:
        return BroadcastState.Live  # éppen tart
    elif minutes < duration + TIMEDELTA_TOLERANCE:
        return BroadcastState.Recent  # 15 percen belül ért véget
    else:
        return BroadcastState.Past


def get_broadcast(schedule, date):
    broadcast = __get_or_create_broadcast(schedule, date)

    broadcast_item = viewmodels.BroadcastItem(schedule, broadcast)

    return broadcast_item


def __get_or_create_broadcast(schedule, date):
    try:
        broadcast = models.Broadcast.objects.get(schedule=schedule, date=date)
    except ObjectDoesNotExist:
        broadcast = models.Broadcast()
        broadcast.schedule = schedule
        broadcast.date = date

    if not broadcast.get_video_embed_url():
        if schedule.youtube_channel:
            broadcast.video_youtube_channel = schedule.youtube_channel
        elif schedule.video_url:
            broadcast.video_url = schedule.video_url
        elif schedule.location.youtube_channel:
            broadcast.video_youtube_channel = schedule.location.youtube_channel
        else:
            broadcast.video_url = schedule.location.video_url

        broadcast.video_iframe = __check_iframe_support(
            broadcast.get_video_embed_url())
        broadcast.save()

    if not broadcast.text_url:
        text_url = None
        if schedule.text_url:
            text_url = schedule.text_url
        else:
            try:
                liturgy_text = models.LiturgyText.objects.get(
                    liturgy=schedule.liturgy, date=date)
                if liturgy_text:
                    text_url = liturgy_text.text_url
            except ObjectDoesNotExist:
                if schedule.liturgy.text_url_pattern:
                    try:
                        text_url = date.strftime(
                            schedule.liturgy.text_url_pattern)
                    except ValueError:
                        pass
                elif schedule.liturgy.text:
                    text_url = reverse('liturgy-text',
                                       args=[schedule.liturgy.slug])

        if text_url:
            broadcast.text_url = text_url
            broadcast.text_iframe = __check_iframe_support(text_url)
            broadcast.save()

    return broadcast


def __check_iframe_support(url):
    if not url:
        return False

    try:
        if not urllib.parse.urlparse(url).netloc:
            return True

        request = urllib.request.Request(url)
        response = urllib.request.urlopen(request)
        frame_header = response.getheader('X-Frame-Options')
        return frame_header is None
    except urllib.error.URLError:
        return True
