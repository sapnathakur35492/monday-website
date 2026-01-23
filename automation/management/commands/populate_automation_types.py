from django.core.management.base import BaseCommand
from automation.models import TriggerType, ActionType

class Command(BaseCommand):
    help = 'Populates default automation triggers and actions'

    def handle(self, *args, **options):
        # ============ TRIGGERS ============
        
        triggers = [
            {
                'code': 'status_change',
                'name': 'Status Changed',
                'description': 'When a status column changes to a specific value',
                'icon': 'lightning',
                'color': 'blue',
                'requires_value': True,
                'order': 1
            },
            {
                'code': 'item_created',
                'name': 'Item Created',
                'description': 'When a new item is added to the board',
                'icon': 'plus-circle',
                'color': 'green',
                'requires_value': False,
                'order': 2
            },
            {
                'code': 'item_assigned',
                'name': 'Person Assigned',
                'description': 'When someone is assigned to an item',
                'icon': 'user-plus',
                'color': 'purple',
                'requires_value': False,
                'order': 3
            },
            {
                'code': 'priority_changed',
                'name': 'Priority Changed',
                'description': 'When priority column changes',
                'icon': 'alert-triangle',
                'color': 'red',
                'requires_value': True,
                'order': 4
            },
            {
                'code': 'date_arrives',
                'name': 'Date Arrives',
                'description': 'When a date column reaches today',
                'icon': 'calendar',
                'color': 'orange',
                'requires_value': False,
                'order': 5
            },
            {
                'code': 'column_changed',
                'name': 'Any Column Changed',
                'description': 'When any column value changes',
                'icon': 'edit',
                'color': 'indigo',
                'requires_value': False,
                'order': 6
            },
            {
                'code': 'item_moved',
                'name': 'Item Moved to Group',
                'description': 'When an item is moved to a different group',
                'icon': 'move',
                'color': 'teal',
                'requires_value': True,
                'order': 7
            },
        ]
        
        for trigger_data in triggers:
            TriggerType.objects.get_or_create(
                code=trigger_data['code'],
                defaults=trigger_data
            )
            self.stdout.write(self.style.SUCCESS(f'✓ Trigger: {trigger_data["name"]}'))

        # ============ ACTIONS ============
        
        actions = [
            {
                'code': 'send_email',
                'name': 'Send Email',
                'description': 'Send an email notification',
                'icon': 'mail',
                'color': 'orange',
                'requires_value': False,
                'order': 1
            },
            {
                'code': 'change_status',
                'name': 'Change Status',
                'description': 'Change a status column value',
                'icon': 'refresh',
                'color': 'purple',
                'requires_value': True,
                'order': 2
            },
            {
                'code': 'create_item',
                'name': 'Create Item',
                'description': 'Create a new item in a group',
                'icon': 'plus',
                'color': 'green',
                'requires_value': True,
                'order': 3
            },
            {
                'code': 'duplicate_item',
                'name': 'Duplicate Item',
                'description': 'Create a copy of the current item',
                'icon': 'copy',
                'color': 'blue',
                'requires_value': False,
                'order': 4
            },
            {
                'code': 'move_item',
                'name': 'Move Item',
                'description': 'Move item to another group',
                'icon': 'arrow-right',
                'color': 'teal',
                'requires_value': True,
                'order': 5
            },
            {
                'code': 'assign_person',
                'name': 'Assign Person',
                'description': 'Assign someone to the item',
                'icon': 'user',
                'color': 'indigo',
                'requires_value': True,
                'order': 6
            },
            {
                'code': 'set_date',
                'name': 'Set Date',
                'description': 'Set a date column value',
                'icon': 'calendar',
                'color': 'orange',
                'requires_value': True,
                'order': 7
            },
            {
                'code': 'send_notification',
                'name': 'Send Notification',
                'description': 'Send in-app notification',
                'icon': 'bell',
                'color': 'yellow',
                'requires_value': False,
                'order': 8
            },
            {
                'code': 'create_update',
                'name': 'Post Update',
                'description': 'Add a comment/update to the item',
                'icon': 'message-square',
                'color': 'pink',
                'requires_value': True,
                'order': 9
            },
            {
                'code': 'archive_item',
                'name': 'Archive Item',
                'description': 'Move item to archive',
                'icon': 'archive',
                'color': 'gray',
                'requires_value': False,
                'order': 10
            },
            {
                'code': 'set_priority',
                'name': 'Set Priority',
                'description': 'Change priority level',
                'icon': 'flag',
                'color': 'red',
                'requires_value': True,
                'order': 11
            },
        ]
        
        for action_data in actions:
            ActionType.objects.get_or_create(
                code=action_data['code'],
                defaults=action_data
            )
            self.stdout.write(self.style.SUCCESS(f'✓ Action: {action_data["name"]}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Total: {len(triggers)} triggers, {len(actions)} actions'))
