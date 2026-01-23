from .models import AutomationRule, AutomationLog
import logging

logger = logging.getLogger(__name__)

class AutomationEngine:
    """
    Service to evaluate and execute automation rules using the Registry pattern.
    """
    
    @staticmethod
    def run_automations(board, trigger_code, context):
        """
        Entry point to find and run matching rules.
        """
        from .registry import AutomationRegistry
        
        # print(f"Checking automations for board {board.id}, trigger {trigger_code}")
        
        # 1. Find active rules for this board and trigger
        rules = AutomationRule.objects.filter(
            board=board,
            trigger_type=trigger_code,
            is_active=True
        )
        
        # Get Handler
        trigger_handler = AutomationRegistry.get_trigger(trigger_code)
        if not trigger_handler:
            print(f"No handler found for trigger: {trigger_code}")
            return

        for rule in rules:
            try:
                # 2. Check Condition via Handler
                if trigger_handler.check_condition(rule, context):
                    print(f" -> Rule '{rule.name}' matched! Executing action...")
                    AutomationEngine._execute_action(rule, context)
                    AutomationLog.objects.create(rule=rule, status='success', meta={'context': str(context)})
                else:
                    # print(f" -> Rule '{rule.name}' skipped (condition failed).")
                    pass
            except Exception as e:
                print(f"Error running rule {rule.id}: {e}")
                AutomationLog.objects.create(rule=rule, status='failed', meta={'error': str(e)})

    @staticmethod
    def _execute_action(rule, context):
        """
        Performs the action using the Action Handler.
        """
        from .registry import AutomationRegistry
        
        action_code = rule.action_type
        action_handler = AutomationRegistry.get_action(action_code)
        
        if not action_handler:
            print(f"No handler found for action: {action_code}")
            return
            
        # Execute Action
        try:
            action_handler.execute(rule, context)
        except Exception as e:
            print(f"Error executing action {action_code}: {e}")
            raise e

