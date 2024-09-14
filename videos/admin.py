from django.contrib import admin

# Register your models here.
from .models import Video

# Register your models here.
@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_at')  # Display these fields in the admin list view
    search_fields = ('title',)  # Enable search by title in the admin interface
    list_filter = ('uploaded_at',)  # Add a filter by upload date in the admin interface
