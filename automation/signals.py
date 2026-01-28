from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from webapp.models import Item

@receiver(pre_save, sender=Item)
def check_automation_triggers(sender, instance, **kwargs):
    """
    Check for changes before saving to detect triggers like 'Status Changed'.
    Store the detected changes in the instance validation cache to use in post_save.
    """
    if not instance.pk:
        # Mark as new item for item_created trigger
        instance._is_new_item = True
        return 
    
    try:
        old_instance = Item.objects.get(pk=instance.pk)
    except Item.DoesNotExist:
        return

    # Store changes temporarily
    instance._status_changed = False
    instance._priority_changed = False
    instance._assigned_changed = False
    instance._group_changed = False
    
    # Prevent infinite loops from automation updates
    if getattr(instance, '_is_automation_update', False):
        return

    # Check if any value changed
    if instance.values != old_instance.values:
        instance._values_changed = True
        instance._old_values = old_instance.values
        
        # Check for priority change
        old_priority = old_instance.values.get('priority')
        new_priority = instance.values.get('priority')
        if old_priority != new_priority:
            instance._priority_changed = True
            instance._old_priority = old_priority
            instance._new_priority = new_priority
    
    # Check if assigned_to changed (person column values)
    # Find person columns and check if any changed
    person_cols = instance.group.board.columns.filter(type='person')
    for col in person_cols:
        col_id_str = str(col.id)
        old_assigned = old_instance.values.get(col_id_str)
        new_assigned = instance.values.get(col_id_str)
        if old_assigned != new_assigned:
            instance._assigned_changed = True
            instance._old_assigned = old_assigned
            instance._new_assigned = new_assigned
            break
    
    # Check if group changed
    if instance.group_id != old_instance.group_id:
        instance._group_changed = True
        instance._old_group = old_instance.group
        instance._new_group = instance.group

@receiver(post_save, sender=Item)
def execute_automation_actions(sender, instance, created, **kwargs):
    """
    Execute actions after save.
    """
    from automation.service import AutomationEngine
    
    # 1. Trigger: Item Created
    if created or getattr(instance, '_is_new_item', False):
        AutomationEngine.run_automations(
            instance.group.board,
            'item_created',
            {'item': instance}
        )
            
    # 2. Trigger: Status Change (or any value change)
    if hasattr(instance, '_values_changed') and instance._values_changed:
        # Detect which columns changed
        old_vals = getattr(instance, '_old_values', {})
        new_vals = instance.values
        
        # Find all status columns for this board
        board_status_cols = {str(c.id): c for c in instance.group.board.columns.filter(type='status')}
        
        for col_id, new_val in new_vals.items():
            # If this is a status column and it changed
            if col_id in board_status_cols and new_val != old_vals.get(col_id):
                context = {
                    'item': instance,
                    'column_id': col_id,
                    'new_value': new_val
                }
                AutomationEngine.run_automations(instance.group.board, 'status_change', context)

        # Fire generic "any column changed" trigger
        AutomationEngine.run_automations(
            instance.group.board,
            'column_changed',
            {
                'item': instance,
                'old_values': old_vals,
                'new_values': new_vals,
            }
        )
    
    # 3. Trigger: Priority Changed
    if hasattr(instance, '_priority_changed') and instance._priority_changed:
        context = {
            'item': instance,
            'new_priority': getattr(instance, '_new_priority', None)
        }
        AutomationEngine.run_automations(instance.group.board, 'priority_changed', context)
    
    # 4. Trigger: Item Assigned
    if hasattr(instance, '_assigned_changed') and instance._assigned_changed:
        from core.models import User
        new_username = getattr(instance, '_new_assigned', None)
        new_user_id = None
        if new_username:
            user = User.objects.filter(username=new_username).first()
            if user:
                new_user_id = user.id

        context = {
            'item': instance,
            'new_assigned_username': new_username,
            'new_assigned_user_id': new_user_id,
        }
        AutomationEngine.run_automations(instance.group.board, 'item_assigned', context)
    
    # 5. Trigger: Item Moved to Group
    if hasattr(instance, '_group_changed') and instance._group_changed:
        context = {
            'item': instance,
            'new_group_id': instance.group.id if instance.group else None
        }
        AutomationEngine.run_automations(instance.group.board, 'item_moved', context)
