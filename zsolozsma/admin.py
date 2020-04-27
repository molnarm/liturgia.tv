from django.contrib import admin
import zsolozsma.models


class EventInline(admin.TabularInline):
    model = zsolozsma.models.Event
    readonly_fields = ('slug', 'hash',)


@admin.register(zsolozsma.models.Location)
class LocationAdmin(admin.ModelAdmin):
    readonly_fields = ('slug',)
    inlines = [EventInline, ]


class LiturgyTextInline(admin.TabularInline):
    model = zsolozsma.models.LiturgyText


@admin.register(zsolozsma.models.Liturgy)
class LiturgyAdmin(admin.ModelAdmin):
    readonly_fields = ('slug',)
    inlines = [LiturgyTextInline, ]


@admin.register(zsolozsma.models.Broadcast)
class BroadcastAdmin(admin.ModelAdmin):
    pass
