# myapp/templatetags/custom_filters.py
from django import template
import datetime
from django.utils.timezone import now

register = template.Library()

@register.filter
def format_number(card_number):
    card_number = ''.join(card_number.split()) 
    formatted_number = ' '.join(card_number[i:i+4] for i in range(0, len(card_number), 4))
    return formatted_number


@register.filter
def new_formatter(number):
    number = ''.join(number.split()) 
    new_formatted = ' - '.join(number[i:i+4] for i in range(0, len(number), 4))
    return new_formatted


@register.filter
def hide_number(card_number):
    if len(card_number) > 4:
        return '*' * (len(card_number) - 4) + card_number[-4:]
    return card_number

@register.filter
def time_since(value):
    if not isinstance(value, datetime.datetime):
        # If value is not a datetime, return an empty string
        return ''

    now_time = now()
    
    # If the value is naive, make it aware with current timezone
    if not value.tzinfo:
        value = now_time.tzinfo.localize(value)

    diff = now_time - value

    if diff.total_seconds() < 0:
        return 'just now'

    if diff.days == 0 and diff.seconds < 60:
        seconds = diff.seconds
        return f'{seconds} sec{"s" if seconds != 1 else ""} ago'
    if diff.days == 0 and diff.seconds < 3600:
        minutes = diff.seconds // 60
        return f'{minutes} min{"s" if minutes != 1 else ""} ago'
    if diff.days == 0 and diff.seconds < 86400:
        hours = diff.seconds // 3600
        return f'{hours} hour{"s" if hours != 1 else ""} ago'
    if diff.days < 30:
        days = diff.days
        return f'{days} day{"s" if days != 1 else ""} ago'
    if diff.days < 365:
        months = diff.days // 30
        return f'{months} month{"s" if months != 1 else ""} ago'
    
    years = diff.days // 365
    return f'{years} year{"s" if years != 1 else ""} ago'
