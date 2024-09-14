# Generated by Django 5.0.4 on 2024-06-09 19:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0002_video_audio_file_video_transcription_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='VideoAIChat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('messages', models.JSONField(blank=True, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='video',
            name='chat',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='videos.videoaichat'),
        ),
    ]
