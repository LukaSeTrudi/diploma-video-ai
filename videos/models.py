from django.db import models

from moviepy.editor import VideoFileClip
import tempfile
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import os
from io import BytesIO
from PIL import Image
import whisper
import json
from videos.helpers import abstract_summary_extraction, key_points_extraction, extract_questions, convert_video_to_mp3, generate_transcription, minimize_json, transcribe_audio, transcribe_audio_api
from django.contrib.auth.models import User

class Video(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    video_file = models.FileField(upload_to='media/videos/')
    audio_file = models.FileField(upload_to='media/videos/audio/', null=True, blank=True)
    transcription = models.JSONField(null=True, blank=True)
    thumbnail = models.ImageField(upload_to='media/thumbnails/', null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploader = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    messages = models.JSONField(null=True, blank=True)

    extracted_data = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Extract audio
        if (self.audio_file is None or self.audio_file == ""):
            with self.video_file.open('rb') as video_file:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video_file:
                    temp_video_file.write(video_file.read())
                    temp_video_file.flush()

                    audio_file_path = convert_video_to_mp3(temp_video_file.name)
                    
                    with open(audio_file_path, 'rb') as audio_file:
                        self.audio_file.save(os.path.basename(audio_file_path), ContentFile(audio_file.read()), save=False)
                    
                    os.remove(temp_video_file.name)
                    os.remove(audio_file_path)
            super().save(*args, **kwargs)

        # Set thumbnail if not set
        if (self.thumbnail == None or self.thumbnail == "") and self.video_file != None:
            
            video_file_content = self.video_file.read()
            
            with tempfile.NamedTemporaryFile(delete=False) as temp_video_file:
                temp_video_file.write(video_file_content)
                temp_video_file.flush()
                
                video = VideoFileClip(temp_video_file.name)
                audio = video.audio
                frame = video.get_frame(0)
                thumbnail_io = BytesIO()
                
                image = Image.fromarray(frame)
                image.save(thumbnail_io, format='JPEG')

                thumbnail_name = os.path.splitext(self.video_file.name)[0] + '_thumbnail.jpg'
                self.thumbnail.save(thumbnail_name, ContentFile(thumbnail_io.getvalue()), save=True)

                os.remove(temp_video_file.name)

        if (self.transcription is None or self.transcription == "") and self.audio_file != None:
            with self.audio_file.open('rb') as audio_file:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_audio_file:
                    temp_audio_file.write(audio_file.read())
                    temp_audio_file.flush()

                    transcription_data = transcribe_audio(temp_audio_file.name)
                    self.transcription = minimize_json(transcription_data)
                    
                    # self.transcription = transcribe_audio_api(temp_audio_file.name) # Uncomment this line to use the API instead of the local model

                    os.remove(temp_audio_file.name)

            super().save(*args, **kwargs)

        if (self.transcription is not None and self.transcription != "") and (self.messages is None or self.messages == ""):
            self.messages = [
                {
                    "role": "system",
                    "content": f"Based on the video transcript: {self.transcription} and any images I send, I will provide concise and brief answers and include timestamps in seconds if relevant."
                }
            ]

        if (self.transcription is not None and self.transcription != "") and (self.extracted_data is None or self.extracted_data == ""):
            self.extracted_data = {
                "abstract": abstract_summary_extraction(self.transcription),
                "key_points": json.loads(key_points_extraction(self.transcription)),
                "questions": json.loads(extract_questions(self.transcription)),
            }
        
        super().save(*args, **kwargs)