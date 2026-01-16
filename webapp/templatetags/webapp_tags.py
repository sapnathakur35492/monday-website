from django import template

register = template.Library()

@register.filter
def get_value(dictionary, key):
    """
    Get value from dictionary using key (converted to string).
    Usage: {{ item.values | get_value:col.id }}
    """
    if not dictionary:
        return ""
    return dictionary.get(str(key), "")
