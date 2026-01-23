from django.db import models
from .models import User, Organization

class PricingPlan(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, null=True, help_text="Unique identifier for URL/API")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='USD')
    interval = models.CharField(max_length=20, default='month', choices=[('month', 'Monthly'), ('year', 'Yearly')])
    
    description = models.TextField(blank=True, help_text="Short tagline for the plan")
    button_text = models.CharField(max_length=50, default="Get Started")
    
    # Limits
    max_users = models.IntegerField(default=5, help_text="Max users allowed (0 for unlimited)")
    max_boards = models.IntegerField(default=10, help_text="Max boards allowed (0 for unlimited)")
    max_automations = models.IntegerField(default=100, help_text="Max automation runs per month")
    
    # Deprecated JSON field, using PlanFeature model now
    # features = models.JSONField(default=list, help_text="List of features") 
    
    is_popular = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'price']

    def __str__(self):
        return f"{self.name} ({self.interval})"

class PlanFeature(models.Model):
    """
    Features belonging to a specific plan (e.g., 'Unix Timeline', 'Unlimited Automations').
    """
    plan = models.ForeignKey(PricingPlan, on_delete=models.CASCADE, related_name='features')
    text = models.CharField(max_length=255)
    is_included = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.plan.name} - {self.text}"

class RolePermission(models.Model):
    """
    Dynamic permissions for each role.
    Admin can edit these to control what Managers/Members can do.
    """
    ROLE_CHOICES = (
        ('manager', 'Manager'),
        ('member', 'Member'),
        ('viewer', 'Viewer'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    can_create_board = models.BooleanField(default=False)
    can_create_automation = models.BooleanField(default=False)
    can_invite_users = models.BooleanField(default=False)
    can_manage_billing = models.BooleanField(default=False)

    class Meta:
        unique_together = ('role',)

    def __str__(self):
        return f"Permissions for {self.role}"

class BillingProfile(models.Model):
    """
    Stripe Customer Data.
    """
    organization = models.OneToOneField(Organization, on_delete=models.CASCADE, related_name='billing')
    stripe_customer_id = models.CharField(max_length=100, blank=True, null=True)
    subscription_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Link to actual Plan model
    plan = models.ForeignKey(PricingPlan, on_delete=models.SET_NULL, null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    next_payment_due = models.DateTimeField(null=True, blank=True)
    
    # Keep legacy/fallback just in case, or remove if confident. 
    # Let's rely on 'plan' relation.
    
    def __str__(self):
        plan_name = self.plan.name if self.plan else "No Plan"
        return f"Billing for {self.organization.name} ({plan_name})"
