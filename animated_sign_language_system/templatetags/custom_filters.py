from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Returns dictionary item from key."""
    return dictionary.get(key, None)

@register.filter
def has_key(dictionary, key):
    """Checks if key exists in dictionary."""
    return key in dictionary
