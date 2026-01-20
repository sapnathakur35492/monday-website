from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from webapp.models import Board
from .models import AutomationRule, TriggerType, ActionType
from django.views.decorators.http import require_POST

def automation_list(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    rules = board.automations.all()
    # Pass status options for the 'Create' modal if we add one here
    status_col = board.columns.filter(type='status').first()
    status_options = status_col.settings.get('choices', []) if status_col else ['Not Started', 'Done']
    
    return render(request, 'automation/list.html', {
        'board': board, 
        'rules': rules,
        'status_options': status_options
    })

@login_required
def create_rule(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    
    # Load dynamic triggers and actions from database
    triggers = TriggerType.objects.filter(is_active=True)
    actions = ActionType.objects.filter(is_active=True)
    
    # Get status options dynamically from board columns
    status_col = board.columns.filter(type='status').first()
    if status_col and status_col.settings.get('choices'):
        status_options = status_col.settings.get('choices', [])
    else:
        status_options = ['Not Started', 'In Progress', 'Done', 'On Hold']

    if request.method == 'POST':
        trigger_code = request.POST.get('trigger')
        action_code = request.POST.get('action')
        
        # Validations
        if not trigger_code or not action_code:
            # Should handle error better
            return redirect('create_rule', board_id=board_id)

        # Extract Configs
        trigger_config = {}
        action_config = {}
        
        # 1. Trigger Config
        if trigger_code == 'status_change':
            target_val = request.POST.get('trigger_value')
            if target_val:
                trigger_config['value'] = target_val
                
        # 2. Action Config
        if action_code == 'change_status':
            target_val = request.POST.get('action_value')
            if status_col and target_val:
                action_config = {'column_id': status_col.id, 'new_value': target_val}
                
        elif action_code == 'send_email':
            action_config = {'recipient': 'owner'}

        # Get names for display
        trigger_obj = TriggerType.objects.filter(code=trigger_code).first()
        action_obj = ActionType.objects.filter(code=action_code).first()
        
        t_name = trigger_obj.name if trigger_obj else trigger_code
        a_name = action_obj.name if action_obj else action_code
        
        rule_name = f"When {t_name}"
        if trigger_config.get('value'):
            rule_name += f" ({trigger_config['value']})"
        rule_name += f" → {a_name}"
        if action_config.get('new_value'):
            rule_name += f" ({action_config['new_value']})"

        rule = AutomationRule.objects.create(
            board=board,
            name=rule_name,
            trigger_type=trigger_code,
            action_type=action_code,
            trigger_config=trigger_config,
            action_config=action_config
        )
        return redirect('automation_list', board_id=board.id)
        
    return render(request, 'automation/builder.html', {
        'board': board,
        'triggers': triggers,
        'actions': actions,
        'status_options': status_options
    })

@require_POST
@login_required
def delete_rule(request, board_id, rule_id):
    board = get_object_or_404(Board, id=board_id)
    rule = get_object_or_404(AutomationRule, id=rule_id, board=board)
    rule.delete()
    return redirect('automation_list', board_id=board.id)

@login_required
def edit_rule(request, board_id, rule_id):
    # For MVP, we'll just delete and recreate or show the builder pre-filled.
    # To keep it simple and robust, we will redirect to builder but passing initial values context would be complex without a proper React form.
    # We will just treat 'Edit' as deleting and creating new for now, or 
    # better: Redirect to builder, but we need to pass the existing config.
    # Let's just implement Delete for now as prioritized, and for Edit we can redirect to a "Not Implemented" or reuse create.
    # Actually, the user demanded "Edit". Let's try to support it.
    
    board = get_object_or_404(Board, id=board_id)
    rule = get_object_or_404(AutomationRule, id=rule_id, board=board)
    
    # We will reuse the builder template but populate it
    triggers = TriggerType.objects.filter(is_active=True)
    actions = ActionType.objects.filter(is_active=True)
    
    status_col = board.columns.filter(type='status').first()
    status_options = status_col.settings.get('choices', []) if status_col else ['Not Started', 'Done']

    if request.method == 'POST':
        # Same update logic (simplified: update the fields)
        trigger_code = request.POST.get('trigger')
        action_code = request.POST.get('action')
        
        # ... (Duplicate logic from create_rule, should refactor) ...
        # For speed, I'll basically recreate the rule object
        
        trigger_config = {}
        if trigger_code == 'status_change':
             trigger_config['value'] = request.POST.get('trigger_value')
             
        action_config = {}
        if action_code == 'change_status':
             val = request.POST.get('action_value')
             if status_col: action_config = {'column_id': status_col.id, 'new_value': val}
        elif action_code == 'send_email':
             action_config = {'recipient': 'owner'}

        # Update params
        rule.trigger_type = trigger_code
        rule.action_type = action_code
        rule.trigger_config = trigger_config
        rule.action_config = action_config
        
        # Regen name
        trigger_obj = TriggerType.objects.filter(code=trigger_code).first()
        action_obj = ActionType.objects.filter(code=action_code).first()
        t_name = trigger_obj.name if trigger_obj else trigger_code
        a_name = action_obj.name if action_obj else action_code
        
        rule_name = f"When {t_name}"
        if trigger_config.get('value'): rule_name += f" ({trigger_config['value']})"
        rule_name += f" → {a_name}"
        if action_config.get('new_value'): rule_name += f" ({action_config['new_value']})"
        
        rule.name = rule_name
        rule.save()
        
        return redirect('automation_list', board_id=board.id)

    # Context for filling inputs
    initial_data = {
        'trigger': rule.trigger_type,
        'action': rule.action_type,
        'trigger_value': rule.trigger_config.get('value'),
        'action_value': rule.action_config.get('new_value')
    }

    return render(request, 'automation/builder.html', {
        'board': board,
        'triggers': triggers,
        'actions': actions,
        'status_options': status_options,
        'initial': initial_data,
        'is_edit': True,
        'rule_id': rule.id
    })
