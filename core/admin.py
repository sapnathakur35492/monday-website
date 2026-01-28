from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Organization, Membership, Notification, FooterLink
from .saas_models import PricingPlan, BillingProfile, RolePermission

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_admin', 'is_manager')
    fieldsets = UserAdmin.fieldsets + (
        ('Roles', {'fields': ('is_admin', 'is_manager', 'is_verified', 'avatar')}),
    )

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'created_at')
    search_fields = ('name', 'owner__username')

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization', 'role', 'joined_at')
    list_filter = ('role',)

class PlanFeatureInline(admin.TabularInline):
    from core.saas_models import PlanFeature
    model = PlanFeature
    extra = 1

@admin.register(PricingPlan)
class PricingPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'interval', 'max_boards', 'is_active', 'order')
    list_editable = ('price', 'is_active', 'order')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [PlanFeatureInline]

@admin.register(BillingProfile)
class BillingProfileAdmin(admin.ModelAdmin):
    list_display = ('organization', 'plan', 'is_active', 'next_payment_due')

@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ('role', 'can_create_board', 'can_create_automation')
    list_editable = ('can_create_board', 'can_create_automation')

admin.site.register(Notification)

@admin.register(FooterLink)
class FooterLinkAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'section', 'order', 'is_active')
    list_filter = ('section', 'is_active')
    search_fields = ('title', 'url')
    ordering = ('section', 'order')
