
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from marketing.models import Page, Feature
from core.saas_models import PricingPlan

def fix_data():
    print("Checking Home Page...")
    page, created = Page.objects.get_or_create(
        slug='home',
        defaults={
            'title': 'ProjectFlow: Work Without Limits',
            'meta_description': 'Plan, execute, and track projects of any size. Easily assign tasks, automate workflows, and collaborate with your team in one place.',
            'is_published': True
        }
    )
    if created:
        print("Created Home Page.")
    else:
        print("Home Page exists.")
        # Ensure description is set if empty
        if not page.meta_description:
            page.meta_description = 'Plan, execute, and track projects of any size. Easily assign tasks, automate workflows, and collaborate with your team in one place.'
            page.save()
            print("Updated Home Page description.")

    print("Checking Pricing Plans...")
    if not PricingPlan.objects.exists():
        PricingPlan.objects.create(name='Basic', price=10, features=['Unlimited Boards', '200+ Templates', 'iOS and Android Apps'])
        PricingPlan.objects.create(name='Standard', price=12, features=['Timeline & Gantt', 'Calendar View', 'Guest Access'])
        PricingPlan.objects.create(name='Pro', price=20, features=['Private Boards', 'Chart View', 'Time Tracking'])
        print("Created Default Plans.")
    else:
        print(f"Found {PricingPlan.objects.count()} plans.")

if __name__ == '__main__':
    fix_data()
