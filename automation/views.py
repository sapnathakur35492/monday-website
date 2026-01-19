from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from webapp.models import Board
from .models import AutomationRule, TriggerType, ActionType

def automation_list(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    rules = board.automations.all()
    return render(request, 'automation/list.html', {'board': board, 'rules': rules})

@login_required
def create_rule(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    
    # Load dynamic triggers and actions from database
    triggers = TriggerType.objects.filter(is_active=True)
    actions = ActionType.objects.filter(is_active=True)
    
    # Get status options dynamically from board columns
    status_col = board.columns.filter(type='status').first()
    if status_col and status_col.settings.get('choices'):
        # Load from column settings if available
        status_options = status_col.settings.get('choices', [])
    else:
        # Default status options if not configured
        status_options = ['Not Started', 'In Progress', 'Done', 'On Hold']

    if request.method == 'POST':
        trigger_code = request.POST.get('trigger')
        action_code = request.POST.get('action')
        
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

        # Get trigger and action names for display
        trigger_obj = TriggerType.objects.filter(code=trigger_code).first()
        action_obj = ActionType.objects.filter(code=action_code).first()
        
        rule_name = f"When {trigger_obj.name if trigger_obj else trigger_code}"
        if trigger_config.get('value'):
            rule_name += f" ({trigger_config['value']})"
        rule_name += f" → {action_obj.name if action_obj else action_code}"
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

