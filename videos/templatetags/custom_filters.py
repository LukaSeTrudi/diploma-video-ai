# myapp/templatetags/custom_filters.py

from django import template

register = template.Library()

@register.filter
def time_format(value):
    try:
        # Convert the value seconds to hh:mm:ss format
        total_seconds = int(float(value))
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
        else:
            return f"{int(minutes):02d}:{int(seconds):02d}"
    except (TypeError, ValueError):
        print("Error")
        return value