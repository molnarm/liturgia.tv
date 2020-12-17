from django.test import TestCase
from zsolozsma import queries
from zsolozsma.models import *
from datetime import datetime, timedelta
from django.utils import timezone

class QueryTests(TestCase):
    def setup(self):
        TestData.setup()

    def test_query_city_filter(self):
        pass

    def test_query_location_filter(self):
        pass

    def test_query_city_location_filter(self):
        pass

    def test_query_denomination_filter(self):
        pass

    def test_query_denomination_city_filter(self):
        pass

    def test_liturgy_filter(self):
        pass

    def test_validity(self):
        pass

    def test_is_active(self):
        pass

    def test_style(self):
        pass