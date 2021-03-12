from django.test import TestCase
from zsolozsma import queries
from zsolozsma.models import *
from datetime import datetime, timedelta
from django.utils import timezone


class BroadcastTests(TestCase):
    def test_states(self):
        event = Event(name='test', duration=50)
        now = datetime.now()
        day = now.date().weekday()
        schedules = [
            EventSchedule(event=event, day_of_week=day, time=t)
            for t in [(now + timedelta(minutes=d)).time() for d in
                      [60, 16, 14, 1, 0, -1, -49, -51, -64, -66, -120]]
        ]

        states = [
            queries.get_broadcast_status(s, now.date()) for s in schedules
        ]

        self.assertListEqual([
            queries.BroadcastState.Future, queries.BroadcastState.Future,
            queries.BroadcastState.Upcoming, queries.BroadcastState.Upcoming,
            queries.BroadcastState.Live, queries.BroadcastState.Live,
            queries.BroadcastState.Live, queries.BroadcastState.Recent,
            queries.BroadcastState.Recent, queries.BroadcastState.Past,
            queries.BroadcastState.Past
        ], states)

    def test_text(self):
        now = datetime.now()
        city = City.objects.create(name='city')
        location = Location.objects.create(name='location', city=city)

        liturgy1 = Liturgy.objects.create(
            name='liturgy1', text_url_pattern='https://textpattern')
        LiturgyText.objects.create(liturgy=liturgy1,
                                   text_url='https://liturgytext',
                                   date=now.date())
        liturgy2 = Liturgy.objects.create(
            name='liturgy2', text_url_pattern='https://textpattern')
        liturgy3 = Liturgy.objects.create(name='liturgy3')

        event1 = Event.objects.create(location=location,
                                      liturgy=liturgy1,
                                      text_url='https://eventtext')
        event2 = Event.objects.create(location=location, liturgy=liturgy1)
        event3 = Event.objects.create(location=location, liturgy=liturgy2)
        event4 = Event.objects.create(location=location, liturgy=liturgy3)

        schedule1 = EventSchedule.objects.create(
            event=event1, time=now.time(), text_url='https://scheduletext')
        schedule2 = EventSchedule.objects.create(event=event1, time=now.time())
        schedule3 = EventSchedule.objects.create(event=event2, time=now.time())
        schedule4 = EventSchedule.objects.create(event=event3, time=now.time())
        schedule5 = EventSchedule.objects.create(event=event4, time=now.time())

        # Text is retrieved from the most specific source available for the broadcast:
        # 1. The text url in the schedule item
        broadcast = queries.get_broadcast(schedule1, now.date())
        self.assertEqual('https://scheduletext', broadcast.text_url)
        self.assertTrue(broadcast.has_text)

        # 2. The text url in the event
        broadcast = queries.get_broadcast(schedule2, now.date())
        self.assertEqual('https://eventtext', broadcast.text_url)
        self.assertTrue(broadcast.has_text)

        # 3. The text url in the liturgy for the given date
        broadcast = queries.get_broadcast(schedule3, now.date())
        self.assertEqual('https://liturgytext', broadcast.text_url)
        self.assertTrue(broadcast.has_text)

        # 4. The text pattern in the liturgy for the given date
        broadcast = queries.get_broadcast(schedule4, now.date())
        self.assertEqual('https://textpattern', broadcast.text_url)
        # TODO check pattern
        self.assertTrue(broadcast.has_text)

        # (5. Nothing)
        broadcast = queries.get_broadcast(schedule5, now.date())
        self.assertEqual('', broadcast.text_url)
        self.assertFalse(broadcast.has_text)

    def test_video(self):
        now = datetime.now()
        city = City.objects.create(name='city')
        liturgy = Liturgy.objects.create(name='liturgy')

        location1 = Location.objects.create(name='location1',
                                            city=city,
                                            video_url='https://locationurl',
                                            youtube_channel='locationchannel')
        location2 = Location.objects.create(name='location2',
                                            city=city,
                                            video_url='https://locationurl')
        location3 = Location.objects.create(name='location3', city=city)

        event1 = Event.objects.create(location=location1,
                                      liturgy=liturgy,
                                      video_url='https://eventurl',
                                      youtube_channel='eventchannel')
        event2 = Event.objects.create(location=location1,
                                      liturgy=liturgy,
                                      video_url='https://eventurl')
        event3 = Event.objects.create(location=location1, liturgy=liturgy)
        event4 = Event.objects.create(location=location2, liturgy=liturgy)
        event5 = Event.objects.create(location=location3, liturgy=liturgy)

        schedule1 = EventSchedule.objects.create(
            event=event1,
            time=now.time(),
            video_url='https://scheduleurl',
            youtube_channel='schedulechannel')
        schedule2 = EventSchedule.objects.create(
            event=event1, time=now.time(), video_url='https://scheduleurl')
        schedule3 = EventSchedule.objects.create(
            event=event1, time=now.time())
        schedule4 = EventSchedule.objects.create(event=event2, time=now.time())
        schedule5 = EventSchedule.objects.create(event=event3, time=now.time())
        schedule6 = EventSchedule.objects.create(event=event4, time=now.time())
        schedule7 = EventSchedule.objects.create(event=event5, time=now.time())

        # Video is retrieved from the most specific source available for the broadcast:
        # 1. The YouTube channel of the schedule item
        broadcast = queries.get_broadcast(schedule1, now.date())
        self.assertIn('schedulechannel', broadcast.video_embed_url)
        self.assertTrue(broadcast.video_only)

        # 2. The video url in the schedule item
        broadcast = queries.get_broadcast(schedule2, now.date())
        self.assertEqual('https://scheduleurl', broadcast.video_embed_url)
        self.assertFalse(broadcast.video_only)

        # 3. The YouTube channel of the event
        broadcast = queries.get_broadcast(schedule3, now.date())
        self.assertIn('eventchannel', broadcast.video_embed_url)
        self.assertTrue(broadcast.video_only)

        # 4. The video url in the event
        broadcast = queries.get_broadcast(schedule4, now.date())
        self.assertEqual('https://eventurl', broadcast.video_embed_url)
        self.assertFalse(broadcast.video_only)

        # 5. The YouTube channel of the location
        broadcast = queries.get_broadcast(schedule5, now.date())
        self.assertIn('locationchannel', broadcast.video_embed_url)
        self.assertTrue(broadcast.video_only)

        # 6. The video url of the location
        broadcast = queries.get_broadcast(schedule6, now.date())
        self.assertEqual('https://locationurl', broadcast.video_embed_url)
        self.assertFalse(broadcast.video_only)

        # (7. Nothing)
        broadcast = queries.get_broadcast(schedule7, now.date())
        self.assertEqual('', broadcast.video_embed_url)