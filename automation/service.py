from .models import AutomationRule, AutomationLog
from webapp.models import Item, Column

class AutomationEngine:
    """
    Executes automation rules based on events.
    """
    
    @staticmethod
    def run_automations(board, trigger_type, context):
        """
        Entry point for triggering automations on a board.
        context: dict containing 'item', 'old_value', 'new_value', 'column_id' etc.
        """
        rules = AutomationRule.objects.filter(board=board, trigger_type=trigger_type, is_active=True)
        
        for rule in rules:
            AutomationEngine.evaluate_and_execute(rule, context)

    @staticmethod
    def evaluate_and_execute(rule, context):
        """
        Checks conditions and executes action if matched.
        """
        # 1. Evaluate Trigger Config
        if not AutomationEngine.check_trigger_match(rule, context):
            return

        # 2. Execute Action
        try:
            if rule.action_type == 'send_email':
                AutomationEngine.action_send_email(rule, context)
            elif rule.action_type == 'change_status':
                AutomationEngine.action_change_status(rule, context)
            
            # Log Success
            AutomationLog.objects.create(rule=rule, status='success', meta={'context': str(context)})
            
        except Exception as e:
            # Log Failure
            AutomationLog.objects.create(rule=rule, status='failed', meta={'error': str(e), 'context': str(context)})

    @staticmethod
    def check_trigger_match(rule, context):
        """
        Returns True if rule trigger config matches current context.
        """
        config = rule.trigger_config
        
        # Logic for 'status_change'
        if rule.trigger_type == 'status_change':
            # Check if value matches (e.g. "Done")
            if config.get('value'):
                if str(context.get('new_value')) != str(config.get('value')):
                    return False
            return True
            
        return True

    @staticmethod
    def action_send_email(rule, context):
        """
        Mocks sending an email.
        """
        item = context.get('item')
        print(f"[[AUTOMATION EMAIL]] Sending email for Item {item.name}: {rule.name}")
        # In real world: send_mail(...)

    @staticmethod
    def action_change_status(rule, context):
        """
        Changes a status column value.
        """
        item = context.get('item')
        config = rule.action_config
        
        col_id = config.get('column_id')
        new_val = config.get('new_value')
        
        if col_id and new_val:
            # Update the item's values
            item.values[str(col_id)] = new_val
            item.save()
            print(f"[[AUTOMATION UPDATE]] Changed status of {item.name} to {new_val}")
