# Generated by Django 3.0.5 on 2020-04-24 13:39

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Liturgy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Név')),
                ('description', models.TextField(blank=True, max_length=500, verbose_name='Leírás')),
                ('slug', models.CharField(max_length=50, unique=True, verbose_name='URL részlet')),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Rövid név')),
                ('fullname', models.CharField(max_length=300, unique=True, verbose_name='Teljes név')),
                ('slug', models.CharField(max_length=50, unique=True, verbose_name='URL részlet')),
                ('homepage', models.URLField(blank=True, verbose_name='Honlap')),
            ],
        ),
        migrations.CreateModel(
            name='LiturgyText',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='Dátum')),
                ('text_url', models.URLField(blank=True, max_length=500, verbose_name='Szöveg URL')),
                ('liturgy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='zsolozsma.Liturgy', verbose_name='Szertartás')),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Név')),
                ('slug', models.SlugField(max_length=100, verbose_name='URL részlet')),
                ('description', models.TextField(blank=True, max_length=500, verbose_name='Leírás')),
                ('youtube_channel', models.CharField(blank=True, max_length=20, verbose_name='YouTube csatorna ID')),
                ('video_url', models.URLField(blank=True, max_length=500, verbose_name='URL a közvetítéshez')),
                ('times', django.contrib.postgres.fields.ArrayField(base_field=models.TimeField(blank=True, null=True, verbose_name='Kezdés ideje'), default=list, size=None, verbose_name='Kezdési időpontok')),
                ('liturgy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='zsolozsma.Liturgy', verbose_name='Szertartás')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='zsolozsma.Location', verbose_name='Helyszín')),
            ],
        ),
        migrations.CreateModel(
            name='CustomEventSchedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(blank=True, null=True, verbose_name='Dátum (egyedi alkalomnál)')),
                ('time', models.TimeField(blank=True, verbose_name='Kezdés ideje')),
                ('text_url', models.URLField(blank=True, max_length=500, verbose_name='Egyedi szöveg URL')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='zsolozsma.Event', verbose_name='Esemény')),
            ],
        ),
        migrations.CreateModel(
            name='CachedBroadcast',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('video_url', models.URLField(max_length=500)),
                ('text_url', models.URLField(blank=True, max_length=500)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='zsolozsma.Event', verbose_name='Esemény')),
            ],
        ),
    ]
