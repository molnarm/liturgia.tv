# Generated by Django 3.0.5 on 2020-04-26 12:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('zsolozsma', '0004_auto_20200426_1428'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='hash',
            field=models.CharField(max_length=8, unique=True, verbose_name='URL hash'),
        ),
    ]
