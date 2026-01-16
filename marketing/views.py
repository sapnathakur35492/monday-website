from django.shortcuts import render, get_object_or_404
from .models import Page, PricingPlan, Feature

def landing_page(request):
    """
    Renders the public landing page with dynamic content.
    """
    page = Page.objects.filter(slug='home', is_published=True).first()
    return render(request, 'marketing/landing.html', {'page': page})

def features(request):
    features_list = Feature.objects.filter(is_active=True)
    return render(request, 'marketing/features.html', {'features': features_list})

def pricing(request):
    plans = PricingPlan.objects.filter(is_active=True).order_by('price')
    return render(request, 'marketing/pricing.html', {'plans': plans})

def about(request):
    return render(request, 'marketing/about.html')

def contact(request):
    return render(request, 'marketing/contact.html')
