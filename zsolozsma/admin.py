from django.contrib import admin
import zsolozsma.models

admin.site.register(zsolozsma.models.LiturgyText)


@admin.register(zsolozsma.models.Location)
class LocationAdmin(admin.ModelAdmin):
    readonly_fields = ('slug',)


@admin.register(zsolozsma.models.Liturgy)
class LiturgyAdmin(admin.ModelAdmin):
    readonly_fields = ('slug',)


@admin.register(zsolozsma.models.Event)
class EventAdmin(admin.ModelAdmin):
    readonly_fields = ('slug',)
