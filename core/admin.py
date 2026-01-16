from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Organization, Membership
from .saas_models import RolePermission, BillingProfile

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('is_verified', 'avatar', 'is_admin', 'is_manager')}),
    )
    list_display = UserAdmin.list_display + ('is_verified', 'is_admin')

admin.site.register(Organization)
admin.site.register(Membership)
admin.site.register(RolePermission)
admin.site.register(BillingProfile)
