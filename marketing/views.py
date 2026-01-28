from django.shortcuts import render, get_object_or_404
from core.saas_models import PricingPlan, PlanFeature
from .models import Page, Feature

def landing_page(request):
    """
    Renders the public landing page with dynamic content.
    """
    page = Page.objects.filter(slug='home', is_published=True).first()
    features = Feature.objects.filter(is_active=True).order_by('order')[:6] # Show top 6 features
    plans = PricingPlan.objects.prefetch_related('features').all().order_by('order') # Show all plans
    
    return render(request, 'marketing/landing.html', {
        'page': page,
        'features': features,
        'plans': plans
    })

def features(request):
    features_list = Feature.objects.filter(is_active=True).order_by('order')
    return render(request, 'marketing/features.html', {'features': features_list})

def pricing(request):
    """
    Pricing page.
    """
    # Fetch all plans with features
    # Fetch all plans with features
    plans = PricingPlan.objects.prefetch_related('features').all().order_by('price')
    
    # Fetch comparison items (Dynamic "Why Choose Us")
    from .models import ComparisonItem
    comparison_items = ComparisonItem.objects.filter(is_active=True).order_by('order')
    
    return render(request, 'marketing/pricing.html', {
        'plans': plans, 
        'comparison_items': comparison_items
    })

def about(request):
    return render(request, 'marketing/about.html')

def contact(request):
    return render(request, 'marketing/contact.html')
