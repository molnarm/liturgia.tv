from django.test import TestCase
from zsolozsma import queries
from zsolozsma.models import *
from datetime import datetime, timedelta
from django.utils import timezone


class ScheduleTests(TestCase):
    def setUp(self):
        self.city1 = City.objects.create(name='City 1')
        self.city2 = City.objects.create(name='City 2')

        self.location1 = Location.objects.create(name='Church A',
                                                 city=self.city1)
        self.location2 = Location.objects.create(name='Church B',
                                                 city=self.city1,
                                                 miserend_id=42)
        self.location3 = Location.objects.create(name='Church A',
                                                 city=self.city2)

        self.denomination1 = Denomination.objects.create(name='Denomination 1')
        self.denomination2 = Denomination.objects.create(name='Denomination 2')

        self.liturgy1 = Liturgy.objects.create(name='Liturgy 1',
                                               denomination=self.denomination1)
        self.liturgy2 = Liturgy.objects.create(name='Liturgy 2',
                                               denomination=self.denomination2)

        for location in Location.objects.all():
            for liturgy in Liturgy.objects.all():
                Event.objects.create(location=location,
                                     liturgy=liturgy,
                                     name=location.name + ' ' + liturgy.name)

        self.now = datetime.now()
        self.today = self.now.date()
        self.later = (self.now + timedelta(hours=1)).time()

        for event in Event.objects.all():
            EventSchedule.objects.create(event=event,
                                         day_of_week=self.today.weekday(),
                                         time=self.later)

    def test_query_city_filter(self):
        schedule = queries.get_schedule(city_slug='city-1')

        self.__assert_schedule([('Church A Liturgy 1', 'City 1'),
                                ('Church A Liturgy 2', 'City 1'),
                                ('Church B Liturgy 1', 'City 1'),
                                ('Church B Liturgy 2', 'City 1')], schedule)

    def test_query_location_filter(self):
        schedule = queries.get_schedule(location_slug='church-a')

        self.__assert_schedule([('Church A Liturgy 1', 'City 1'),
                                ('Church A Liturgy 2', 'City 1'),
                                ('Church A Liturgy 1', 'City 2'),
                                ('Church A Liturgy 2', 'City 2')], schedule)

    def test_query_city_location_filter(self):
        schedule = queries.get_schedule(city_slug='city-1',
                                        location_slug='church-a')

        self.__assert_schedule([('Church A Liturgy 1', 'City 1'),
                                ('Church A Liturgy 2', 'City 1')], schedule)

    def test_query_denomination_filter(self):
        schedule = queries.get_schedule(denomination_slug='denomination-1')

        self.__assert_schedule([('Church A Liturgy 1', 'City 1'),
                                ('Church B Liturgy 1', 'City 1'),
                                ('Church A Liturgy 1', 'City 2')], schedule)

    def test_query_denomination_city_filter(self):
        schedule = queries.get_schedule(denomination_slug='denomination-1',
                                        city_slug='city-2')

        self.__assert_schedule([('Church A Liturgy 1', 'City 2')], schedule)

    def test_liturgy_filter(self):
        schedule = queries.get_schedule(liturgy_slug='liturgy-2')

        self.__assert_schedule([('Church A Liturgy 2', 'City 1'),
                                ('Church B Liturgy 2', 'City 1'),
                                ('Church A Liturgy 2', 'City 2')], schedule)

    def test_miserend_filter(self):
        schedule = queries.get_schedule(miserend_id=42)

        self.__assert_schedule([('Church B Liturgy 1', 'City 1'),
                                ('Church B Liturgy 2', 'City 1')], schedule)

    def test_validity(self):
        schedule11 = EventSchedule.objects.get(event__location=self.location1,
                                               event__liturgy=self.liturgy1)
        schedule11.valid_from = self.today + timedelta(days=1)
        schedule11.save()
        schedule12 = EventSchedule.objects.get(event__location=self.location1,
                                               event__liturgy=self.liturgy2)
        schedule12.valid_to = self.today + timedelta(days=-1)
        schedule12.save()

        schedule = queries.get_schedule()

        self.__assert_schedule([('Church B Liturgy 1', 'City 1'),
                                ('Church B Liturgy 2', 'City 1'),
                                ('Church A Liturgy 1', 'City 2'),
                                ('Church A Liturgy 2', 'City 2')], schedule)

    def test_is_active(self):
        self.location1.is_active = False
        self.location1.save()
        event21 = Event.objects.get(location=self.location2,
                                    liturgy=self.liturgy1)
        event21.is_active = False
        event21.save()

        schedule = queries.get_schedule()

        self.__assert_schedule([('Church B Liturgy 2', 'City 1'),
                                ('Church A Liturgy 1', 'City 2'),
                                ('Church A Liturgy 2', 'City 2')], schedule)

    def test_duration(self):
        self.liturgy1.duration = 50
        self.liturgy1.save()
        event11 = Event.objects.get(location=self.location1,
                                    liturgy=self.liturgy1)
        event11.duration = 40
        event11.save()

        schedule = queries.get_schedule(city_slug='city-1')

        expected = [('Church A Liturgy 1', 'City 1', 40),
                    ('Church A Liturgy 2', 'City 1', 60),
                    ('Church B Liturgy 1', 'City 1', 50),
                    ('Church B Liturgy 2', 'City 1', 60)]
        for expected_item, actual_item in zip(expected, schedule):
            self.assertEqual(expected_item,
                             (actual_item.name, actual_item.city_name,
                              actual_item.duration))

    def __assert_schedule(self, expected, schedule):
        self.assertEqual(len(expected), len(schedule))

        for expected_item, actual_item in zip(expected, schedule):
            self.assertEqual(expected_item,
                             (actual_item.name, actual_item.city_name))
