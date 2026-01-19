from django.shortcuts import render, get_object_or_404
from core.saas_models import PricingPlan
from .models import Page, Feature # Re-enabling imports as landing_page uses Page

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
    # Fetch all plans, assuming is_active doesn't exist yet on the new model or add it? 
    # checking saas_models.py... I didn't add is_active to PricingPlan in step 330.
    # So I will just fetch all.
    plans = PricingPlan.objects.all().order_by('price')
    return render(request, 'marketing/pricing.html', {'plans': plans})

def about(request):
    return render(request, 'marketing/about.html')

def contact(request):
    return render(request, 'marketing/contact.html')
