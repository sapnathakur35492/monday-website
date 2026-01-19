from django.contrib import admin
from .models import User, Organization, Membership
from .saas_models import RolePermission, BillingProfile, PricingPlan

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff')

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner')

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization', 'role')

@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ('role',)

@admin.register(BillingProfile)
class BillingProfileAdmin(admin.ModelAdmin):
    list_display = ('organization', 'plan_name')

@admin.register(PricingPlan)
class PricingPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'is_popular')
