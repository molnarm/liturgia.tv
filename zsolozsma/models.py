from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField
from django.utils.text import slugify


class Location(models.Model):
    """Helyszín"""

    name = models.CharField('Rövid név', max_length=100, blank=False)
    fullname = models.CharField(
        'Teljes név', max_length=300, blank=False, unique=True)
    slug = models.CharField('URL részlet', max_length=50,
                            blank=False, unique=True)
    homepage = models.URLField('Honlap', blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Location, self).save(*args, **kwargs)

    def __str__(self):
        return "%s (%s)" % (self.name, self.fullname)


class Liturgy(models.Model):
    """Szertartás"""

    name = models.CharField('Név', max_length=100, blank=False, unique=True)
    description = models.TextField('Leírás', max_length=500, blank=True)
    slug = models.CharField('URL részlet', max_length=50,
                            blank=False, unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Liturgy, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Event(models.Model):
    """Közvetített esemény (adott szertartás egy adott helyen)"""

    location = models.ForeignKey(
        "Location", verbose_name='Helyszín', on_delete=models.CASCADE, blank=False)
    liturgy = models.ForeignKey(
        "Liturgy", verbose_name='Szertartás', on_delete=models.CASCADE, blank=False)
    name = models.CharField('Név', max_length=100, blank=False)
    slug = models.SlugField('URL részlet', max_length=100, blank=False)
    description = models.TextField('Leírás', max_length=500, blank=True)
    youtube_channel = models.CharField(
        'YouTube csatorna ID', max_length=20, blank=True)
    video_url = models.URLField(
        'URL a közvetítéshez', max_length=500, blank=True)

    times = ArrayField(base_field=models.TimeField('Kezdés ideje', auto_now=False,
                                                   auto_now_add=False, null=True, blank=True), verbose_name='Kezdési időpontok', blank=False, default=list)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Event, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class CustomEventSchedule(models.Model):
    """Közvetített esemény egy példánya (alkalom)"""

    event = models.ForeignKey(
        "Event", verbose_name='Esemény', on_delete=models.CASCADE, blank=False)
    date = models.DateField('Dátum (egyedi alkalomnál)',
                            auto_now=False, auto_now_add=False, null=True, blank=True)
    time = models.TimeField('Kezdés ideje', auto_now=False,
                            auto_now_add=False, blank=True)
    text_url = models.URLField('Egyedi szöveg URL', max_length=500, blank=True)

    def __str__(self):
        return "%s %s" % (self.date, self.time)


class LiturgyText(models.Model):
    """Egy szertartás szövegei"""

    liturgy = models.ForeignKey(
        "Liturgy", verbose_name="Szertartás", on_delete=models.CASCADE, blank=False)
    date = models.DateField("Dátum", auto_now=False,
                            auto_now_add=False, blank=False)
    text_url = models.URLField('Szöveg URL', max_length=500, blank=True)


class CachedBroadcast(models.Model):
    """Egy alkalom tárolt adatai"""

    event = models.ForeignKey(
        "Event", verbose_name='Esemény', on_delete=models.CASCADE, blank=False)
    date = models.DateField(auto_now=False, auto_now_add=False, blank=False)
    video_url = models.URLField(max_length=500, blank=False)
    text_url = models.URLField(max_length=500, blank=True)
