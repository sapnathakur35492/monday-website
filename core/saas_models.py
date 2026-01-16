from django.db import models
from .models import User, Organization

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
    plan_name = models.CharField(max_length=50, default='free')
    is_active = models.BooleanField(default=True)
    next_payment_due = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Billing for {self.organization.name}"
