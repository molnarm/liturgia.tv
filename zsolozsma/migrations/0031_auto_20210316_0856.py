# Generated by Django 3.1.7 on 2021-03-16 07:56

from django.db import migrations
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('zsolozsma', '0030_auto_20210316_0817'),
    ]

    operations = [
        migrations.AlterField(
            model_name='liturgy',
            name='description',
            field=tinymce.models.HTMLField(blank=True, verbose_name='Leírás'),
        ),
    ]
