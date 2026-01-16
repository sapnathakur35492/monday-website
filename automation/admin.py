from django.contrib import admin
from .models import AutomationRule, AutomationLog, TriggerType, ActionType

@admin.register(TriggerType)
class TriggerTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'color', 'requires_value', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    prepopulated_fields = {'code': ('name',)}

@admin.register(ActionType)
class ActionTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'color', 'requires_value', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    prepopulated_fields = {'code': ('name',)}

@admin.register(AutomationRule)
class AutomationRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'board', 'trigger_type', 'action_type', 'is_active')
    list_filter = ('is_active', 'board')

@admin.register(AutomationLog)
class AutomationLogAdmin(admin.ModelAdmin):
    list_display = ('rule', 'status', 'executed_at')
    list_filter = ('status', 'executed_at')
    readonly_fields = ('rule', 'executed_at', 'status', 'meta')
