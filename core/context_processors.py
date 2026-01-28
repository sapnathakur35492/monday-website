from core.models import FooterLink

def footer_links(request):
    """
    Injects footer links into the context, organized by section.
    Matches the variable names expected by base.html:
    footer_products, footer_solutions, footer_resources, footer_company
    """
    links = FooterLink.objects.filter(is_active=True).order_by('section', 'order')
    
    return {
        'footer_products': [l for l in links if l.section == 'products'],
        'footer_solutions': [l for l in links if l.section == 'solutions'],
        'footer_resources': [l for l in links if l.section == 'resources'],
        'footer_company': [l for l in links if l.section == 'company'],
    }

def notifications_processor(request):
    """
    Injects user notifications into the context.
    """
    if request.user.is_authenticated:
        # Placeholder: Implement actual notification logic later if needed
        # notifications = request.user.notifications.filter(read=False)
        return {'notifications': [], 'unread_notifications_count': 0}
    return {'notifications': [], 'unread_notifications_count': 0}

def global_settings(request):
    """
    Injects global settings into the context.
    """
    from django.conf import settings
    return {
        'DEBUG': settings.DEBUG,
        'SITE_NAME': 'ProjectFlow',
        # Add other global settings here if needed
    }
