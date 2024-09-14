from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, JsonResponse

from videos.helpers import ask_ai
from .models import Video
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_protect
from moviepy.editor import VideoFileClip
from PIL import Image
import base64
import io
import subprocess
from django import forms

class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField()

def index(request):
    videos = Video.objects.all()

    context = {
        'videos': videos
    }
    return render(request, 'videos.html', context)

def add(request):
    videos = Video.objects.all()
    context = {
        'videos': videos
    }
    return render(request, 'add_video.html', context)

def video(request, video_id):
    video = get_object_or_404(Video, pk=video_id)
    return render(request, 'video.html', context={'video': video})

def upload(request):
    print("upload")
    print(request.POST)
    print(request.FILES)
    form = UploadFileForm(request.POST, request.FILES)
    if form.is_valid():
        video = Video.objects.create(title=request.POST["title"], description=request.POST["description"], video_file=request.FILES["file"])
        video.save()
    else:
        print("not validdd", form.errors)
    return redirect("/videos/1")


from django.views.decorators.http import require_POST
import json
# Return a json response with the chat messages
@require_POST
def add_message(request, video_id):
    video = get_object_or_404(Video, pk=video_id)
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    message = data.get('message', None)
    timestamp = data.get('timestamp', None)
    if message == "" or message is None:
        return JsonResponse({'message': None}, content_type="application/json")
    
    image_base64 = None
    if timestamp != None:
        image = extract_frame_at_timestamp(video.video_file.url, timestamp)
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG") 
        image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

    video.messages.append(
        {
            "role": "user",
            "content": [
                {"type": "text", "text": message, "timestamp": timestamp},
            ]
        })
    response = ask_ai(video.messages, f"data:image/jpeg;base64,{image_base64}")
    video.messages.append(response)
    video.save()
    return JsonResponse({'message': response}, content_type="application/json")

def format_timestamp(timestamp):
    # Timestamp is in seconds ex 273.681453
    hours = int(timestamp // 3600)
    minutes = int((timestamp % 3600) // 60)
    seconds = int(timestamp % 60)
    
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def extract_frame_at_timestamp(video_path, timestamp):
    timestamp_str = format_timestamp(timestamp)
    output_path = 'temp_frame.jpg'
    
    subprocess.run([
        'ffmpeg', '-ss', timestamp_str, '-i', video_path,
        '-frames:v', '1', output_path, '-y'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    image = Image.open(output_path)
    
    return image