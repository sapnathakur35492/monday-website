from celery import shared_task
from django.core.mail import send_mail
from core.models import User, Notification
import time

@shared_task
def process_automation_action(rule_id, item_id, target_config):
    """
    Background task to execute an automation action.
    """
    from webapp.models import Item, Column
    from .models import AutomationRule, AutomationLog
    
    try:
        rule = AutomationRule.objects.get(id=rule_id)
        item = Item.objects.get(id=item_id)
    except (AutomationRule.DoesNotExist, Item.DoesNotExist):
        return "Resource Missing"

    action_type = rule.action_type
    log_status = 'success'
    log_message = f"Executed {action_type}"
    
    try:
        # --- Action 1: Send Email ---
        if action_type == 'send_email':
            # Dynamic Recipient: Board Owner or Organization Owner
            recipient_email = rule.board.workspace.organization.owner.email
            recipient_user = rule.board.workspace.organization.owner
            
            send_mail(
                'Automation Triggered',
                f'Rule "{rule.name}" triggered for item "{item.name}".\n\nLink: /board/{rule.board.id}',
                'system@projectflow.com',
                [recipient_email],
                fail_silently=False,
            )
            
            # Create In-App Notification
            Notification.objects.create(
                user=recipient_user,
                title="Automation Triggered",
                message=f'Rule "{rule.name}" triggered for item "{item.name}".'
            )
            
        # --- Action 2: Change Status ---
        elif action_type == 'change_status':
            # Config: {'column_id': '123', 'new_value': 'Done'}
            col_id = target_config.get('column_id')
            new_value = target_config.get('new_value')
            
            if col_id and new_value:
                # Update the specific column value
                item.values[str(col_id)] = new_value
                # Prevent infinite loops: Don't trigger 'status_change' if we are changing status?
                item._is_automation_update = True
                item.save()
                log_message = f"Changed column {col_id} to {new_value}"

        # --- Action 3: Archive Item ---
        elif action_type == 'archive_item':
            # Assuming we have an 'is_archived' field or similar. 
            # For this MVP, let's just prepend [ARCHIVED] to name as a soft delete demo
            item.name = f"[ARCHIVED] {item.name}"
            item.save()
            log_message = "Item marked as archived"
            
        else:
            log_status = 'failed'
            log_message = f"Unknown action type: {action_type}"

    except Exception as e:
        log_status = 'failed'
        log_message = str(e)
    
    # Create Log
    AutomationLog.objects.create(
        rule=rule,
        status=log_status,
        meta={'message': log_message, 'item_id': item.id}
    )
    
    return log_message
