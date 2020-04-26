from django.contrib import admin
import zsolozsma.models
import secrets


class EventInline(admin.TabularInline):
    model = zsolozsma.models.Event
    readonly_fields = ('slug', 'hash',)

    def get_changeform_initial_data(self, request):
        hash = secrets.token_hex(4)
        return {'hash': hash}


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
