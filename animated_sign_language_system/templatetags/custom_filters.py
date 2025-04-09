from django import template
import os
register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Returns dictionary item from key."""
    return dictionary.get(key, None)

@register.filter
def has_key(dictionary, key):
    """Checks if key exists in dictionary."""
    return key in dictionary

@register.filter
def basename(value):
    return os.path.basename(value)
