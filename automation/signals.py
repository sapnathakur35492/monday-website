from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from webapp.models import Item
from .models import AutomationRule, AutomationLog
import json

@receiver(pre_save, sender=Item)
def check_automation_triggers(sender, instance, **kwargs):
    """
    Check for changes before saving to detect triggers like 'Status Changed'.
    Store the detected changes in the instance validation cache to use in post_save.
    """
    if not instance.pk:
        return 
    
    try:
        old_instance = Item.objects.get(pk=instance.pk)
    except Item.DoesNotExist:
        return

    # Store changes temporarily
    instance._status_changed = False
    
    # Prevent infinite loops from automation updates
    if getattr(instance, '_is_automation_update', False):
        return

    # Check if any "status" column changed
    # We iterate over stored values.
    # In a robust system we need to know WHICH column is a status column.
    
    # For now, let's assume if ANY value changed we check automations
    if instance.values != old_instance.values:
        instance._values_changed = True
        instance._old_values = old_instance.values

@receiver(post_save, sender=Item)
def execute_automation_actions(sender, instance, created, **kwargs):
    """
    Execute actions after save.
    """
    from .tasks import process_automation_action
    
    # 1. Trigger: Item Created
    if created:
        rules = AutomationRule.objects.filter(board=instance.group.board, trigger_type='item_created', is_active=True)
        for rule in rules:
            process_automation_action.delay(rule.id, instance.id, rule.action_config)
            
    # 2. Trigger: Status Change (or any value change)
    if hasattr(instance, '_values_changed') and instance._values_changed:
        # Find 'status_change' rules for this board
        rules = AutomationRule.objects.filter(board=instance.group.board, trigger_type='status_change', is_active=True)
        for rule in rules:
            # Check condition (e.g. if status became 'Done')
            # detailed matching logic usually goes here or inside the task for complexity
            # For this MVP, we just fire the task and let it decide or simple match here
            process_automation_action.delay(rule.id, instance.id, rule.action_config)
