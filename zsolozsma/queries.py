from operator import attrgetter
from datetime import datetime, timedelta
from zsolozsma import models


class ScheduleItem(object):
    event = None
    location = None
    date = None
    time = None

    def __init__(self, event, location, date, time):
        self.location = location
        self.event = event
        self.date = date
        self.time = time


def get_schedule(location=None, fixed_date=None):

    if(fixed_date):
        date = datetime.strptime(fixed_date, '%Y-%M-%d').date()
        dates = [(date, date.weekday())]
        schedule_query = models.CustomEventSchedule.objects.filter(
            date=fixed_date)
    else:
        MAX_DAYS = 7
        today = datetime.today().date()
        end_date = today + timedelta(days=MAX_DAYS)

        dates = [(date, date.weekday())
                 for date in [today + timedelta(days=i) for i in range(MAX_DAYS)]]
        schedule_query = models.CustomEventSchedule.objects.filter(
            date__gte=today, date__lte=end_date)

    if (location):
        events = list(location.event_set.all())
        schedule_query = schedule_query.filter(event__location=location)
    else:
        events = list(models.Event.objects.all())

    event_schedules = list(schedule_query)

    schedule = list()
    for (date, day) in dates:
        for event in events:
            custom_time = next(
                (t for t in event_schedules if t.date == date), None)
            if(custom_time):
                schedule.append(ScheduleItem(
                    event, event.location, date, custom_time.time))
            elif (len(event.times) > day):
                time = event.times[day]
                if (time):
                    schedule.append(ScheduleItem(
                        event, event.location, date, time))

    schedule.sort(key=attrgetter('date', 'time'))

    return schedule
