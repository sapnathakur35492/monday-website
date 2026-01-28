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

@register.filter
def clean_username(value):
    """
    Cleans a username by removing trailing numbers for professional display.
    Usage: {{ user.username|clean_username }}
    Examples: "Santosh3" -> "Santosh", "john_doe123" -> "john_doe"
    """
    if not value:
        return ""
    # Remove trailing digits
    import re
    cleaned = re.sub(r'\d+$', '', str(value))
    # Replace underscores with spaces and title case
    cleaned = cleaned.replace('_', ' ').title()
    return cleaned if cleaned else value

