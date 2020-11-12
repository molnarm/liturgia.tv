from django.contrib import admin
import zsolozsma.models


class EventScheduleInline(admin.TabularInline):
    model = zsolozsma.models.EventSchedule
    readonly_fields = ('hash', )


@admin.register(zsolozsma.models.Event)
class EventAdmin(admin.ModelAdmin):
    model = zsolozsma.models.Event
    inlines = [
        EventScheduleInline,
    ]
    ordering = ['location__name', 'liturgy']
    list_display = ('location', 'liturgy')


class EventInline(admin.TabularInline):
    model = zsolozsma.models.Event


@admin.register(zsolozsma.models.City)
class CityAdmin(admin.ModelAdmin):
    readonly_fields = ('slug', )
    ordering = ['name']
    list_display = ('name', 'diocese')


class CityInline(admin.TabularInline):
    model = zsolozsma.models.City


@admin.register(zsolozsma.models.Diocese)
class DioceseAdmin(admin.ModelAdmin):
    readonly_fields = ('slug', )
    inlines = [
        CityInline,
    ]
    ordering = ['name']


@admin.register(zsolozsma.models.Location)
class LocationAdmin(admin.ModelAdmin):
    readonly_fields = ('slug', )
    inlines = [
        EventInline,
    ]
    ordering = ['name']
    list_display = ('name', 'city')


class LiturgyTextInline(admin.TabularInline):
    model = zsolozsma.models.LiturgyText


@admin.register(zsolozsma.models.Liturgy)
class LiturgyAdmin(admin.ModelAdmin):
    readonly_fields = ('slug', )
    inlines = [
        LiturgyTextInline,
    ]
    ordering = ['name']


@admin.register(zsolozsma.models.Broadcast)
class BroadcastAdmin(admin.ModelAdmin):
    pass
