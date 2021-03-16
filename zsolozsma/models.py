from django.db import models
from django.contrib.postgres.fields import ArrayField
from tinymce.models import HTMLField
from django.utils.text import slugify
import secrets
from zsolozsma import facebook, youtube


class Denomination(models.Model):
    """Felekezet/rítus"""

    name = models.CharField('Név', blank=False, unique=True, max_length=200)
    slug = models.SlugField('URL részlet',
                            max_length=100,
                            blank=False,
                            unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Denomination, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Felekezet/rítus'
        verbose_name_plural = 'Felekezetek/rítusok'


class City(models.Model):
    """Település"""

    name = models.CharField('Név', blank=False, unique=True, max_length=50)
    slug = models.SlugField('URL részlet',
                            max_length=100,
                            blank=False,
                            unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(City, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Település'
        verbose_name_plural = 'Települések'


class Location(models.Model):
    """Helyszín"""

    name = models.CharField('Rövid név', max_length=100, blank=False)
    fullname = models.CharField('Teljes név', max_length=300, blank=False)
    slug = models.SlugField('URL részlet', max_length=50, blank=False)
    city = models.ForeignKey("City",
                             verbose_name='Település',
                             on_delete=models.CASCADE,
                             null=True)
    homepage = models.URLField('Honlap', blank=True)
    youtube_channel = models.CharField('YouTube csatorna ID',
                                       max_length=24,
                                       blank=True)
    video_url = models.URLField('URL a közvetítéshez',
                                max_length=500,
                                blank=True)
    is_active = models.BooleanField(
        'Aktív',
        blank=False,
        default=True,
        help_text='Vedd ki a pipát, ha a helyszínen nincsenek közvetítések.')
    miserend_id = models.IntegerField(
        'miserend.hu ID',
        blank=True,
        null=True,
        help_text=
        'A helyszín azonosítója a miserend.hu-n. Ha megadod, ott is megjelennek a közvetítések.'
    )
    last_checked = models.DateField('Utoljára ellenőrizve',
                                    auto_now=False,
                                    auto_now_add=False,
                                    blank=True,
                                    null=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Location, self).save(*args, **kwargs)

    def __str__(self):
        return "%s, %s" % (self.city.name, self.name)

    class Meta:
        verbose_name = 'Helyszín'
        verbose_name_plural = 'Helyszínek'


class Liturgy(models.Model):
    """Szertartás"""

    name = models.CharField('Név', max_length=100, blank=False, unique=True)
    description = HTMLField('Leírás', blank=True)
    denomination = models.ForeignKey("Denomination",
                                     verbose_name='Felekezet',
                                     on_delete=models.CASCADE,
                                     null=True)
    slug = models.SlugField('URL részlet',
                            max_length=50,
                            blank=False,
                            unique=True)
    duration = models.IntegerField(
        'Időtartam (perc)',
        blank=False,
        null=False,
        default=60,
        help_text='Szokásos időtartam, egyes helyszíneken lehet eltérő.')
    text = HTMLField('Szöveg', blank=True, null=True)
    text_url_pattern = models.CharField(
        'Szöveg URL sablon',
        max_length=300,
        blank=True,
        help_text=
        'Link a szertartás szövegeihez, lehet benne <a href="https://strftime.org/">dátumformátum.</a>'
    )

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Liturgy, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Szertartás'
        verbose_name_plural = 'Szertartások'


class Event(models.Model):
    """Közvetített esemény (adott szertartás egy adott helyen)"""

    name = models.CharField(
        'Név',
        max_length=100,
        blank=False,
        help_text=
        'A szertartás neve az adott helyen, ez fog megjelenni a listákban.')
    location = models.ForeignKey("Location",
                                 verbose_name='Helyszín',
                                 on_delete=models.CASCADE,
                                 blank=False)
    liturgy = models.ForeignKey("Liturgy",
                                verbose_name='Szertartás',
                                on_delete=models.CASCADE,
                                blank=False)
    duration = models.IntegerField(
        'Időtartam (perc)',
        blank=True,
        null=True,
        help_text='Csak akkor kell kitölteni, ha eltér a szokásostól.')

    youtube_channel = models.CharField(
        'Egyedi YouTube csatorna ID',
        max_length=24,
        blank=True,
        help_text=
        'Csak akkor kell kitölteni, ha más, mint a helyszín szokásos csatornája.'
    )
    video_url = models.URLField(
        'Egyedi URL a közvetítéshez',
        max_length=500,
        blank=True,
        help_text=
        'Csak akkor kell kitölteni, ha más, mint a helyszín szokásos közvetítési oldala.'
    )
    text_url = models.URLField(
        'Egyedi szöveg URL',
        max_length=500,
        blank=True,
        help_text=
        'Csak akkor kell kitölteni, ha más, mint a szertartás aznapi szokásos szövege.'
    )

    is_active = models.BooleanField(
        'Aktív',
        blank=False,
        default=True,
        help_text='Vedd ki a pipát, ha az esemény határozatlan ideig szünetel.'
    )

    def __str__(self):
        return "%s %s" % (self.location.name, self.name)

    class Meta:
        verbose_name = 'Esemény'
        verbose_name_plural = 'Események'


class EventSchedule(models.Model):
    event = models.ForeignKey("Event",
                              verbose_name="Esemény",
                              on_delete=models.CASCADE)

    hash = models.CharField('URL hash', max_length=8, unique=True, null=True)

    class Weekdays(models.IntegerChoices):
        hétfő = 0,
        kedd = 1,
        szerda = 2,
        csütörtök = 3,
        péntek = 4,
        szombat = 5,
        vasárnap = 6

    day_of_week = models.IntegerField('Hét napja',
                                      null=True,
                                      blank=True,
                                      choices=Weekdays.choices)
    time = models.TimeField('Kezdés ideje',
                            auto_now=False,
                            auto_now_add=False,
                            null=True,
                            blank=True)

    youtube_channel = models.CharField(
        'Egyedi YouTube csatorna ID',
        max_length=24,
        blank=True,
        help_text='Ha más, mint az esemény szokásos csatornája.')
    video_url = models.URLField(
        'Egyedi URL a közvetítéshez',
        max_length=500,
        blank=True,
        help_text='Ha más, mint a helyszín szokásos közvetítési oldala.')
    text_url = models.URLField(
        'Egyedi szöveg URL',
        max_length=500,
        blank=True,
        help_text='Ha más, mint a szertartás aznapi szokásos szövege.')
    valid_from = models.DateField('Érvényesség kezdete', null=True, blank=True)
    valid_to = models.DateField('Érvényesség vége', null=True, blank=True)

    @property
    def duration(self):
        return self.event.duration or self.event.liturgy.duration

    def __str__(self):
        date_str = EventSchedule.Weekdays(self.day_of_week).name

        return "%s (%s %s)" % (self.event.name, date_str, self.time)

    def save(self, *args, **kwargs):
        if (self.pk is None or self.hash is None):
            self.hash = secrets.token_hex(4)

        super(EventSchedule, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Esemény időpont'
        verbose_name_plural = 'Esemény időpontok'


class LiturgyText(models.Model):
    """Egy szertartás szövegei"""

    liturgy = models.ForeignKey("Liturgy",
                                verbose_name="Szertartás",
                                on_delete=models.CASCADE,
                                blank=False)
    date = models.DateField("Dátum",
                            auto_now=False,
                            auto_now_add=False,
                            blank=False)
    text_url = models.URLField('Szöveg URL', max_length=500, blank=True)

    class Meta:
        verbose_name = 'Szöveg'
        verbose_name_plural = 'Szövegek'


class Broadcast(models.Model):
    schedule = models.ForeignKey("EventSchedule",
                                 verbose_name='Esemény időpont',
                                 null=True,
                                 on_delete=models.CASCADE)
    date = models.DateField('Dátum',
                            auto_now=False,
                            auto_now_add=False,
                            blank=False)
    video_url = models.URLField('Videó URL',
                                max_length=500,
                                blank=True,
                                null=True)
    video_youtube_channel = models.URLField('Videó YouTube csatorna',
                                            max_length=24,
                                            blank=True,
                                            null=True)
    video_iframe = models.BooleanField('Videó beágyazható',
                                       blank=True,
                                       default=True)
    text_url = models.URLField('Szöveg URL', max_length=500, blank=True)
    text_iframe = models.BooleanField('Szöveg beágyazható',
                                      blank=True,
                                      default=True)

    class Meta:
        verbose_name = 'Közvetítés'
        verbose_name_plural = 'Közvetítések'

    def __str__(self):
        event = self.schedule.event
        return "%s %s %s %s" % (event.location.name, event.name, self.date,
                                self.schedule.time)

    def get_video_embed_url(self):
        if (self.video_youtube_channel):
            return youtube.get_embed(self.video_youtube_channel)
        elif self.video_is_facebook():
            return facebook.get_embed_url(self.video_url)
        else:
            return self.video_url

    def video_is_facebook(self):
        return facebook.is_facebook(self.video_url)