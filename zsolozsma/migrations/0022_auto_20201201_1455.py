# Generated by Django 3.0.5 on 2020-12-01 13:55

from django.db import migrations, models


class Migration(migrations.Migration):
    def move_video_urls(apps, schema_editor):
        Broadcast = apps.get_model('zsolozsma', 'Broadcast')
        for broadcast in Broadcast.objects.all():
            if (broadcast.video_only):
                broadcast.video_youtube_channel = broadcast.video_url[
                    len('https://www.youtube.com/embed/live_stream?channel='):]
                broadcast.video_url = None
                broadcast.save()

    dependencies = [
        ('zsolozsma', '0021_liturgy_text_url_pattern'),
    ]

    operations = [
        migrations.AddField(
            model_name='broadcast',
            name='video_youtube_channel',
            field=models.URLField(blank=True,
                                  null=True,
                                  max_length=500,
                                  verbose_name='Videó YouTube csatorna'),
        ),
        migrations.AlterField(
            model_name='broadcast',
            name='video_url',
            field=models.URLField(blank=True,
                                  null=True,
                                  max_length=500,
                                  verbose_name='Videó URL'),
        ),
        migrations.RunPython(move_video_urls),
        migrations.RemoveField(
            model_name='broadcast',
            name='video_only',
        ),
    ]