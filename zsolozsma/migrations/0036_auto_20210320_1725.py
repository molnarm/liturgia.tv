# Generated by Django 3.1.7 on 2021-03-20 16:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('zsolozsma', '0035_auto_20210320_1624'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='eventschedule',
            options={'verbose_name': 'Esemény', 'verbose_name_plural': 'Események'},
        ),
        migrations.AlterField(
            model_name='eventschedule',
            name='day_of_week',
            field=models.IntegerField(choices=[(0, 'Hétfő'), (1, 'Kedd'), (2, 'Szerda'), (3, 'Csütörtök'), (4, 'Péntek'), (5, 'Szombat'), (6, 'Vasárnap')], verbose_name='Hét napja'),
        ),
        migrations.AlterField(
            model_name='eventschedule',
            name='name',
            field=models.CharField(blank=True, help_text='Ha más, mint az esemény szokásos neve.', max_length=100, null=True, verbose_name='Név'),
        ),
        migrations.AlterField(
            model_name='eventschedule',
            name='time',
            field=models.TimeField(verbose_name='Kezdés ideje'),
        ),
    ]
