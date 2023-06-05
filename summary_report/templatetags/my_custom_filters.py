from django import template
from datetime import datetime

register = template.Library()

@register.filter(name='uppercase_ampm')
def uppercase_ampm(time):
    return datetime.strftime(time, "%I:%M %p").upper()