from django.db import models
from webapp.models import Board

class TriggerType(models.Model):
    """
    Dynamic trigger types for automation engine.
    Admin can add/edit triggers via Django admin.
    """
    name = models.CharField(max_length=100, help_text="Display name (e.g., 'Status Changed')")
    code = models.SlugField(unique=True, help_text="Code identifier (e.g., 'status_change')")
    icon = models.CharField(max_length=50, default='lightning', help_text="Icon identifier")
    description = models.TextField(help_text="User-facing description")
    color = models.CharField(max_length=20, default='blue', help_text="Color theme (blue, green, purple, etc.)")
    requires_value = models.BooleanField(default=False, help_text="Does this trigger need a value selection?")
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0, help_text="Display order")
    
    class Meta:
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name

class ActionType(models.Model):
    """
    Dynamic action types for automation engine.
    Admin can add/edit actions via Django admin.
    """
    name = models.CharField(max_length=100, help_text="Display name (e.g., 'Send Email')")
    code = models.SlugField(unique=True, help_text="Code identifier (e.g., 'send_email')")
    icon = models.CharField(max_length=50, default='mail', help_text="Icon identifier")
    description = models.TextField(help_text="User-facing description")
    color = models.CharField(max_length=20, default='orange', help_text="Color theme (orange, pink, purple, etc.)")
    requires_value = models.BooleanField(default=False, help_text="Does this action need a value selection?")
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0, help_text="Display order")
    
    class Meta:
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class AutomationRule(models.Model):
    """
    A rule connecting a trigger to an action on a specific board.
    e.g. When Status changes to 'Done' (Trigger), Send Email (Action).
    """
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='automations')
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    
    # Trigger definition (e.g. type='status_change', field='status', value='Done')
    trigger_type = models.CharField(max_length=100)
    trigger_config = models.JSONField(default=dict)
    
    # Action definition (e.g. type='create_item', target_group='Archive')
    action_type = models.CharField(max_length=100)
    action_config = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class AutomationLog(models.Model):
    rule = models.ForeignKey(AutomationRule, on_delete=models.CASCADE, related_name='logs')
    executed_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('success', 'Success'), ('failed', 'Failed')])
    meta = models.JSONField(default=dict)
