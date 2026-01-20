from django.contrib import admin
from .models import User, Organization, Membership, Notification
from .saas_models import PricingPlan, BillingProfile, RolePermission

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'created_at')
    search_fields = ('name', 'owner__email')

@admin.register(PricingPlan)
class PricingPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'is_popular', 'created_at')
    list_editable = ('price', 'is_popular')
    search_fields = ('name',)

@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ('role', 'can_create_board', 'can_invite_users', 'can_manage_billing')
    list_editable = ('can_create_board', 'can_invite_users', 'can_manage_billing')

@admin.register(BillingProfile)
class BillingProfileAdmin(admin.ModelAdmin):
    list_display = ('organization', 'plan_name', 'is_active', 'next_payment_due')
    list_filter = ('plan_name', 'is_active')
    search_fields = ('organization__name',)

admin.site.register(Membership)
admin.site.register(Notification)
# User is often registered by generic EntityAdmin or UserAdmin, but explicit registration helps if custom User model
from django.contrib.auth.admin import UserAdmin
admin.site.register(User, UserAdmin)
