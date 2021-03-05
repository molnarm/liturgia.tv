from django.contrib import admin
import zsolozsma.models
from django.utils import timezone
from django.db.models.functions import Concat


class EventScheduleInline(admin.TabularInline):
    model = zsolozsma.models.EventSchedule
    readonly_fields = ('hash', )


@admin.register(zsolozsma.models.Event)
class EventAdmin(admin.ModelAdmin):
    model = zsolozsma.models.Event
    inlines = [
        EventScheduleInline,
    ]

    def location_name(self, event):
        return event.location.city.name + ', ' + event.location.name

    location_name.short_description = 'Helyszín'
    location_name.admin_order_field = Concat('location__city__name',
                                             'location__name')

    def liturgy_name(self, event):
        return event.liturgy.name

    liturgy_name.short_description = 'Szertartás'
    liturgy_name.admin_order_field = 'liturgy__name'

    list_display = ('pk', 'location_name', 'liturgy_name')
    list_display_links = ('pk', )
    ordering = ['location__city__name', 'location__name', 'liturgy__name']
    list_filter = ('liturgy__denomination', 'location__city')


class EventInline(admin.TabularInline):
    model = zsolozsma.models.Event


@admin.register(zsolozsma.models.City)
class CityAdmin(admin.ModelAdmin):
    readonly_fields = ('slug', )
    ordering = ['name']


@admin.register(zsolozsma.models.Location)
class LocationAdmin(admin.ModelAdmin):
    readonly_fields = ('slug', )
    inlines = [
        EventInline,
    ]

    def city_name(self, location):
        return location.city.name

    city_name.short_description = 'Település'
    city_name.admin_order_field = 'city__name'

    list_display = ('city_name', 'name')
    list_display_links = ('name', )
    ordering = ['city__name', 'name']
    list_filter = ('city', )


class LiturgyTextInline(admin.TabularInline):
    model = zsolozsma.models.LiturgyText
    extra = 30

    def get_queryset(self, request):
        today = timezone.localtime().date()
        qs = super().get_queryset(request)
        return qs.filter(date__gte=today)


@admin.register(zsolozsma.models.Liturgy)
class LiturgyAdmin(admin.ModelAdmin):
    readonly_fields = ('slug', )
    inlines = [
        LiturgyTextInline,
    ]

    def denomination_name(self, liturgy):
        return liturgy.denomination.name

    denomination_name.short_description = 'Felekezet/rítus'
    denomination_name.admin_order_field = 'denomination__name'

    list_display = ('denomination_name', 'name')
    list_display_links = ('name', )
    ordering = ['denomination__name', 'name']
    list_filter = ('denomination', )


class LiturgyInline(admin.TabularInline):
    model = zsolozsma.models.Liturgy


@admin.register(zsolozsma.models.Denomination)
class DenominationAdmin(admin.ModelAdmin):
    readonly_fields = ('slug', )
    inlines = [
        LiturgyInline,
    ]
    ordering = ['name']


@admin.register(zsolozsma.models.Broadcast)
class BroadcastAdmin(admin.ModelAdmin):
    readonly_fields = ('schedule', 'date')

    def location_name(self, broadcast):
        return broadcast.schedule.event.location.city.name + ', ' + broadcast.schedule.event.location.name

    location_name.short_description = 'Helyszín'
    location_name.admin_order_field = Concat(
        'schedule__event__location__city__name',
        'schedule__event__location__name')

    def liturgy_name(self, broadcast):
        return broadcast.schedule.event.liturgy.name

    liturgy_name.short_description = 'Szertartás'
    liturgy_name.admin_order_field = 'schedule__event__liturgy__name'

    def datetime(self, broadcast):
        return str(broadcast.date) + ' ' + str(broadcast.schedule.time)

    datetime.short_description = 'Időpont'
    datetime.admin_order_field = Concat('date', 'schedule__time')

    def hash(self, broadcast):
        return broadcast.schedule.hash

    list_display = ('hash', 'datetime', 'location_name', 'liturgy_name')
    list_display_links = ('datetime', )
    ordering = [
        'date', 'schedule__time', 'schedule__event__location__city__name',
        'schedule__event__location__name'
    ]
