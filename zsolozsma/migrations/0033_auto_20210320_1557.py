# Generated by Django 3.1.7 on 2021-03-20 14:57

from django.db import migrations, models
import django.db.models.deletion

# select
# 	s.id,
# 	s.hash,
# 	e.location_id,
# 	e.liturgy_id,
# 	e.name,
# 	e.duration,
# 	COALESCE(s.youtube_channel,e.youtube_channel) AS youtube_channel,
# 	COALESCE(s.video_url,e.video_url) AS video_url,
# 	COALESCE(s.text_url,e.text_url) AS text_url,
# 	s.day_of_week,
# 	s.time	
# from zsolozsma_eventschedule s
# inner join zsolozsma_event e on e.id = s.event_id
# order by s.id


class Migration(migrations.Migration):

    dependencies = [
        ('zsolozsma', '0032_eventschedule_is_extraordinary'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventschedule',
            name='duration',
            field=models.IntegerField(blank=True, help_text='Csak akkor kell kitölteni, ha eltér a szokásostól.', null=True, verbose_name='Időtartam (perc)'),
        ),
        migrations.AddField(
            model_name='eventschedule',
            name='liturgy',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='zsolozsma.liturgy', verbose_name='Szertartás'),
        ),
        migrations.AddField(
            model_name='eventschedule',
            name='location',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='zsolozsma.location', verbose_name='Helyszín'),
        ),
        migrations.AddField(
            model_name='eventschedule',
            name='name',
            field=models.CharField(blank=True, help_text='A szertartás neve az adott helyen, ez fog megjelenni a listákban.', max_length=100, verbose_name='Név'),
        ),
    ]
