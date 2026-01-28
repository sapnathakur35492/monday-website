from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class BaseHandler:
    """Base class for Automation Handlers (Triggers & Actions)"""
    code = None
    name = None
    description = None
    
    # Define what configuration fields this handler needs
    # e.g. [{'name': 'column_id', 'type': 'column', 'label': 'Status Column'}]
    config_schema = []
    
    # Sentence fragment for UI construction
    # e.g. "When status changes" or "Move item to..."
    recipe_template = ""

    def validate_config(self, config):
        """Validate if the provided config matches the schema"""
        return True

class TriggerHandler(BaseHandler):
    """
    Base class for Triggers (e.g., 'Status Changed', 'Date Arrived')
    """
    def check_condition(self, rule, context):
        """
        Return True if the Trigger condition is met.
        context: dict containing event data (e.g. {'item': item, 'new_value': 'Done'})
        """
        raise NotImplementedError 

class ActionHandler(BaseHandler):
    """
    Base class for Actions (e.g., 'Move Item', 'Send Email')
    """
    def execute(self, rule, context):
        """
        Execute the action.
        """
        raise NotImplementedError

class AutomationRegistry:
    """
    Singleton registry to store all available Triggers and Actions.
    """
    _triggers = {}
    _actions = {}

    @classmethod
    def register_trigger(cls, handler_class):
        cls._triggers[handler_class.code] = handler_class()
        return handler_class

    @classmethod
    def register_action(cls, handler_class):
        cls._actions[handler_class.code] = handler_class()
        return handler_class

    @classmethod
    def get_trigger(cls, code):
        return cls._triggers.get(code)

    @classmethod
    def get_action(cls, code):
        return cls._actions.get(code)
    
    @classmethod
    def get_all_triggers(cls):
        return cls._triggers.values()

    @classmethod
    def get_all_actions(cls):
        return cls._actions.values()

# --- Implementations ---

@AutomationRegistry.register_trigger
class StatusChangeTrigger(TriggerHandler):
    code = 'status_change'
    name = 'Status Changes'
    description = 'When a status column changes to a specific value'
    recipe_template = "When {column_id} changes to {value}"
    config_schema = [
        {'name': 'column_id', 'type': 'column', 'param': 'status', 'label': 'Column'},
        {'name': 'value', 'type': 'value', 'label': 'Value'}
    ]

    def check_condition(self, rule, context):
        """
        Context must define: column_id, new_value
        """
        config = rule.trigger_config or {}
        
        # 1. Check Column match
        target_col_id = config.get('column_id')
        event_col_id = str(context.get('column_id'))
        
        if target_col_id and str(target_col_id) != event_col_id:
            return False

        # 2. Check Value match
        target_val = config.get('value')
        new_val = context.get('new_value')
        
        if target_val and target_val != new_val:
            return False
            
        return True

@AutomationRegistry.register_trigger
class ItemCreatedTrigger(TriggerHandler):
    code = 'item_created'
    name = 'Item Created'
    description = 'When a new item is created'
    recipe_template = "When an item is created"
    
    def check_condition(self, rule, context):
        return True

@AutomationRegistry.register_trigger
class ColumnChangeTrigger(TriggerHandler):
    code = 'column_changed'
    name = 'Any Column Changes'
    description = 'When any column value is updated'
    recipe_template = "When any column changes"

    def check_condition(self, rule, context):
        return True


@AutomationRegistry.register_trigger
class PriorityChangeTrigger(TriggerHandler):
    """
    Fires when an item's priority value changes.
    """
    code = 'priority_changed'
    name = 'Priority Changes'
    description = 'When an item’s priority changes to a specific value'
    recipe_template = "When priority changes to {new_priority}"
    config_schema = [
        {'name': 'new_priority', 'type': 'value', 'label': 'Priority value'},
    ]

    def check_condition(self, rule, context):
        config = rule.trigger_config or {}
        expected = config.get('new_priority')
        current = context.get('new_priority')

        # If no specific priority configured, fire for any change
        if not expected:
            return True
        return str(expected) == str(current)


@AutomationRegistry.register_trigger
class ItemAssignedTrigger(TriggerHandler):
    """
    Fires when an item is assigned to a specific person.
    """
    code = 'item_assigned'
    name = 'Item Assigned'
    description = 'When an item is assigned to a specific person'
    recipe_template = "When item is assigned to {user_id}"
    config_schema = [
        {'name': 'user_id', 'type': 'user', 'label': 'Person'},
    ]

    def check_condition(self, rule, context):
        config = rule.trigger_config or {}
        target_user_id = str(config.get('user_id') or "")
        new_user_id = str(context.get('new_assigned_user_id') or "")

        # If no specific user configured, fire for any assignment change
        if not target_user_id:
            return bool(new_user_id)
        return target_user_id == new_user_id


@AutomationRegistry.register_trigger
class ItemMovedTrigger(TriggerHandler):
    """
    Fires when an item moves into a specific group.
    """
    code = 'item_moved'
    name = 'Item moved to group'
    description = 'When an item is moved to a specific group'
    recipe_template = "When item moves to {group_id}"
    config_schema = [
        {'name': 'group_id', 'type': 'group', 'label': 'Group'},
    ]

    def check_condition(self, rule, context):
        config = rule.trigger_config or {}
        target_group_id = str(config.get('group_id') or "")
        new_group_id = str(context.get('new_group_id') or "")

        # If no specific group configured, fire for any move
        if not target_group_id:
            return bool(new_group_id)
        return target_group_id == new_group_id

@AutomationRegistry.register_action
class MoveItemAction(ActionHandler):
    code = 'move_item'
    name = 'Move Item to Group'
    recipe_template = "move item to {group_id}"
    config_schema = [
        {'name': 'group_id', 'type': 'group', 'label': 'Group'}
    ]

    def execute(self, rule, context):
        item = context.get('item')
        if not item: return
        
        config = rule.action_config or {}
        group_id = config.get('group_id')
        
        if group_id:
            from webapp.models import Group
            target_group = Group.objects.filter(id=group_id, board=rule.board).first()
            if target_group:
                item.group = target_group
                item._is_automation_update = True
                item.save()
                print(f"[[AUTOMATION]] Moved item '{item.name}' to group '{target_group.title}'")

@AutomationRegistry.register_action
class ChangeStatusAction(ActionHandler):
    code = 'change_status'
    name = 'Change Status'
    recipe_template = "change status of {column_id} to {new_value}"
    config_schema = [
        {'name': 'column_id', 'type': 'column', 'param': 'status', 'label': 'Column'},
        {'name': 'new_value', 'type': 'value', 'label': 'Status'}
    ]

    def execute(self, rule, context):
        item = context.get('item')
        if not item: return

        config = rule.action_config or {}
        col_id = config.get('column_id')
        new_val = config.get('new_value')

        if col_id and new_val:
            item.values[str(col_id)] = new_val
            item._is_automation_update = True
            item.save()
            print(f"[[AUTOMATION]] Changed status of '{item.name}' to '{new_val}'")

@AutomationRegistry.register_action
class CreateUpdateAction(ActionHandler):
    code = 'create_update'
    name = 'Create an Update'
    recipe_template = "create an update: {message}"
    config_schema = [
        {'name': 'message', 'type': 'text', 'label': 'Message'}
    ]

    def execute(self, rule, context):
        item = context.get('item')
        if not item: return
        
        config = rule.action_config or {}
        body = config.get('message', '')
        
        if body:
            from webapp.models import ItemUpdate
            # Basic variable substitution
            body = body.replace('{item.name}', item.name)
            
            ItemUpdate.objects.create(
                item=item,
                user=rule.board.created_by, # Or a system bot 
                body=f"⚡ Automation: {body}"
            )
            print(f"[[AUTOMATION]] Added update to '{item.name}'")

@AutomationRegistry.register_action
class NotifyAction(ActionHandler):
    code = 'send_notification'
    name = 'Notify User'
    recipe_template = "notify {user_id}"
    config_schema = [
        {'name': 'user_id', 'type': 'user', 'label': 'User'}
    ]

    def execute(self, rule, context):
        item = context.get('item')
        if not item: return

        # Implementation for notification (assuming Notification model exists or just log)
        # from webapp.models import Notification
        print(f"[[AUTOMATION]] Would notify user about {item.name}")

@AutomationRegistry.register_action
class AssignPersonAction(ActionHandler):
    code = 'assign_person'
    name = 'Assign Person'
    recipe_template = "assign {user_id}"
    config_schema = [
        {'name': 'user_id', 'type': 'user', 'label': 'Person'}
    ]
    
    def execute(self, rule, context):
        item = context.get('item')
        if not item: return
        
        config = rule.action_config or {}
        user_id = config.get('user_id')
        
        if user_id:
             from core.models import User
             user = User.objects.filter(id=user_id).first()
             # Find first person column
             person_col = item.group.board.columns.filter(type='person').first()
             
             if user and person_col:
                 item.values[str(person_col.id)] = user.username
                 item._is_automation_update = True
                 item.save()
                 print(f"[[AUTOMATION]] Assigned {user.username} to {item.name}")
