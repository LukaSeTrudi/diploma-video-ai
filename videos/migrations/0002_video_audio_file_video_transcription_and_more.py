# Generated by Django 5.0.4 on 2024-06-02 18:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='audio_file',
            field=models.FileField(blank=True, null=True, upload_to='media/videos/audio/'),
        ),
        migrations.AddField(
            model_name='video',
            name='transcription',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='video',
            name='thumbnail',
            field=models.ImageField(blank=True, null=True, upload_to='media/thumbnails/'),
        ),
        migrations.AlterField(
            model_name='video',
            name='video_file',
            field=models.FileField(upload_to='media/videos/'),
        ),
    ]
