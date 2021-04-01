from django.contrib import admin
import zsolozsma.models
from django.utils import timezone
from django.db.models.functions import Concat
from django.urls import reverse
from django.utils.html import format_html


class LiturgiaTvAdmin(admin.ModelAdmin):
    save_on_top = True


class EventInline(admin.TabularInline):
    model = zsolozsma.models.EventSchedule
    readonly_fields = ('hash', )
    ordering = ('valid_from', 'valid_to', 'day_of_week', 'time')
    fields = ('day_of_week', 'time', 'liturgy', 'name', 'valid_from',
              'valid_to', 'is_extraordinary')
    show_change_link = True
        
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'liturgy':
            kwargs["queryset"] = zsolozsma.models.Liturgy.objects.order_by('name')
        return super(EventInline, self).formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(zsolozsma.models.EventSchedule)
class EventAdmin(LiturgiaTvAdmin):
    def has_add_permission(self, request, obj=None):
        # Eseményt nem lehet magában létrehozni, csak helyszínnél
        return False

    def location_link(self, schedule):
        return format_html(
            '<a href="{}">{}</a>',
            reverse("admin:zsolozsma_location_change",
                    args=(schedule.location.id, )), schedule.location)

    location_link.short_description = 'Helyszín'

    def liturgy_link(self, schedule):
        return format_html(
            '<a href="{}">{}</a>',
            reverse("admin:zsolozsma_liturgy_change",
                    args=(schedule.liturgy.id, )), schedule.liturgy)

    liturgy_link.short_description = 'Szertartás'

    readonly_fields = ('location_link', 'liturgy_link')
    fieldsets = ((None, {
        'fields': ('location_link', 'liturgy_link', 'name', 'day_of_week',
                   'time', 'duration')
    }), ('Időszakos és rendkívüli események', {
        'fields': ('valid_from', 'valid_to', 'is_extraordinary'),
        'classes': ('collapse', )
    }), ('Egyedi közvetítések', {
        'fields': ('youtube_channel', 'video_url', 'text_url'),
        'classes': ('collapse', )
    }))

    def azonosito(self, schedule):
        return schedule.pk

    azonosito.short_description = 'Azonosító'
    azonosito.admin_order_field = 'pk'

    def location_name(self, schedule):
        return schedule.location.city.name + ', ' + schedule.location.name

    location_name.short_description = 'Helyszín'
    location_name.admin_order_field = Concat('location__city__name',
                                             'location__name')

    def liturgy_name(self, schedule):
        return schedule.liturgy.name

    liturgy_name.short_description = 'Szertartás'
    liturgy_name.admin_order_field = 'liturgy__name'

    list_display = ('azonosito', 'location_name', 'liturgy_name',
                    'day_of_week', 'time', 'valid_from', 'valid_to',
                    'is_extraordinary')
    list_display_links = ('azonosito', )
    ordering = [
        'location__city__name', 'location__name', 'day_of_week', 'time',
        'valid_from', 'valid_to'
    ]
    list_filter = ('liturgy__denomination', 'location__city', 'liturgy')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('location', 'location__city', 'liturgy')


@admin.register(zsolozsma.models.City)
class CityAdmin(LiturgiaTvAdmin):
    readonly_fields = ('slug', )
    ordering = ['name']


@admin.register(zsolozsma.models.Location)
class LocationAdmin(LiturgiaTvAdmin):
    readonly_fields = ('slug', )
    inlines = [
        EventInline,
    ]

    def city_name(self, location):
        return location.city.name

    city_name.short_description = 'Település'
    city_name.admin_order_field = 'city__name'

    list_display = ('city_name', 'name', 'last_checked', 'is_active')
    list_display_links = ('name', )
    ordering = ['-is_active', 'city__name', 'name']
    list_filter = ('city', )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('city')


class LiturgyTextInline(admin.TabularInline):
    model = zsolozsma.models.LiturgyText
    extra = 30
    ordering = ('date', )

    def get_queryset(self, request):
        today = timezone.localtime().date()
        qs = super().get_queryset(request)
        return qs.filter(date__gte=today)


@admin.register(zsolozsma.models.Liturgy)
class LiturgyAdmin(LiturgiaTvAdmin):
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

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('denomination')


@admin.register(zsolozsma.models.Denomination)
class DenominationAdmin(LiturgiaTvAdmin):
    readonly_fields = ('slug', )
    ordering = ['name']


@admin.register(zsolozsma.models.Broadcast)
class BroadcastAdmin(LiturgiaTvAdmin):
    def has_add_permission(self, request, obj=None):
        # Közvetítést nem lehet kézzel létrehozni
        return False

    def location_name(self, broadcast):
        return broadcast.schedule.location.city.name + ', ' + broadcast.schedule.location.name

    location_name.short_description = 'Helyszín'
    location_name.admin_order_field = Concat('schedule__location__city__name',
                                             'schedule__location__name')

    def liturgy_name(self, broadcast):
        return broadcast.schedule.liturgy.name

    liturgy_name.short_description = 'Szertartás'
    liturgy_name.admin_order_field = 'schedule__liturgy__name'

    def datetime(self, broadcast):
        return str(broadcast.date) + ' ' + str(broadcast.schedule.time)

    datetime.short_description = 'Időpont'
    datetime.admin_order_field = Concat('date', 'schedule__time')

    def hash(self, broadcast):
        return broadcast.schedule.hash

    readonly_fields = ('hash', 'location_name', 'liturgy_name', 'datetime',
                       'video_url', 'video_youtube_channel', 'video_iframe',
                       'text_url', 'text_iframe')
    fields = readonly_fields

    list_display = ('hash', 'datetime', 'location_name', 'liturgy_name')
    list_display_links = ('datetime', )
    ordering = [
        'date', 'schedule__time', 'schedule__location__city__name',
        'schedule__location__name'
    ]

    def get_queryset(self, request):
        today = timezone.localtime().date()
        qs = super().get_queryset(request)
        return qs.select_related('schedule__location','schedule__location__city', 'schedule__liturgy')\
            .filter(date__gte=today)
