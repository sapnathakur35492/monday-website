from django.db import models

class Feature(models.Model):
    """
    Dynamic features for the Features page.
    """
    title = models.CharField(max_length=100)
    description = models.TextField()
    icon_name = models.CharField(max_length=50, help_text="SVG icon identifier (e.g., 'boards', 'automation', 'team')")
    order = models.IntegerField(default=0, help_text="Display order (lower numbers first)")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order', 'id']
    
    def __str__(self):
        return self.title

class Page(models.Model):
    """
    Admin-editable pages for the Marketing Website.
    """
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField(help_text="HTML Content for the page body")
    meta_description = models.CharField(max_length=160, blank=True)
    is_published = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class PricingPlan(models.Model):
    """
    SaaS Plans for display and billing.
    """
    name = models.CharField(max_length=100) # Free, Basic, Pro
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    features = models.JSONField(default=list, help_text="List of features")
    is_active = models.BooleanField(default=True)
    recommended = models.BooleanField(default=False)
    
    # Limits
    user_limit = models.IntegerField(default=1)
    board_limit = models.IntegerField(default=3)
    automation_limit = models.IntegerField(default=100)

    def __str__(self):
        return self.name
