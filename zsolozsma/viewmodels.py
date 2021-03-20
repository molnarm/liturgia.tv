from datetime import datetime
from django.utils import timezone
from zsolozsma import queries, youtube


class BroadcastItem(object):
    def __init__(self, schedule, broadcast):
        self.event_name = schedule.name or schedule.liturgy.name
        self.city_name = schedule.location.city.name
        self.location_name = schedule.location.name
        self.liturgy_name = schedule.liturgy.name

        self.starttime = datetime.combine(broadcast.date, schedule.time)
        self.starttime_label = timezone.get_current_timezone().localize(
            self.starttime)

        self.has_text = bool(broadcast.text_url)
        self.text_url = broadcast.text_url
        self.text_iframe = broadcast.text_iframe

        is_16_9 = broadcast.video_youtube_channel or broadcast.video_is_facebook(
        )

        self.video_embed_url = broadcast.get_video_embed_url()
        self.video_link_url = youtube.get_link(
            broadcast.video_youtube_channel
        ) if broadcast.video_youtube_channel else broadcast.video_url
        self.video_embedded = broadcast.video_iframe or is_16_9
        self.video_16_9 = is_16_9
        self.video_facebook = broadcast.video_is_facebook()


class ScheduleItem(object):
    name = None
    schedule_hash = None
    date = None
    time = None
    city_slug = None
    city_name = None
    location_slug = None
    location_name = None
    duration = None

    state = None
    style = None

    def __init__(self, schedule, date):
        location = schedule.location
        city = location.city

        self.name = schedule.name or schedule.liturgy.name
        self.schedule_hash = schedule.hash
        self.date = date
        self.time = schedule.time
        self.city_slug = city.slug
        self.city_name = city.name
        self.location_slug = location.slug
        self.location_name = location.name
        self.duration = schedule.duration or schedule.liturgy.duration

        self.state = queries.get_broadcast_status(schedule, date)
        self.style = self.__get_style()

    def __get_style(self):
        if (self.state == queries.BroadcastState.Live):
            return 'live'
        elif (self.state == queries.BroadcastState.Upcoming
              or self.state == queries.BroadcastState.Recent):
            return 'highlight'
        else:
            return 'disabled'