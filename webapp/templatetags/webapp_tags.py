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

@register.filter
def make_list(value):
    """
    Converts a comma-separated string into a list.
    Usage: {{ "A,B,C"|make_list }}
    """
    if not value:
        return []
    return [x.strip() for x in value.split(',')]

@register.filter
def make_list_comma(value):
    """
    Converts a comma-separated string into a list.
    Usage: {{ "A,B,C"|make_list_comma }}
    """
    if not value:
        return []
    return [x.strip() for x in value.split(',')]
