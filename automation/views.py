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
    
    if request.headers.get('HX-Request'):
        return render(request, 'automation/center.html', {
            'board': board,
            'rules': rules,
            'status_options': status_options
        })

    return render(request, 'automation/list.html', {
        'board': board, 
        'rules': rules,
        'status_options': status_options
    })


def get_trigger_config_form(request, board_id):
    """
    HTMX: Returns the config inputs for a selected trigger.
    """
    board = get_object_or_404(Board, id=board_id)
    trigger_code = request.GET.get('trigger')
    
    from .registry import AutomationRegistry
    handler = AutomationRegistry.get_trigger(trigger_code)
    
    if not handler or not handler.config_schema:
        return HttpResponse("")
        
    # Parse recipe template
    recipe_template = getattr(handler, 'recipe_template', '')
    tokens = []
    if recipe_template:
        import re
        # Split by {field_name}
        parts = re.split(r'(\{.*?\})', recipe_template)
        for part in parts:
            if part.startswith('{') and part.endswith('}'):
                field_name = part[1:-1]
                # Find field def
                field_def = next((f for f in handler.config_schema if f['name'] == field_name), None)
                if field_def:
                    tokens.append({'type': 'field', 'field': field_def})
                else:
                    tokens.append({'type': 'text', 'content': part}) # Fallback
            else:
                if part: tokens.append({'type': 'text', 'content': part})
    else:
        # Fallback if no template: just list fields
        for field in handler.config_schema:
             tokens.append({'type': 'field', 'field': field})

    return render(request, 'automation/partials/config_form.html', {
        'board': board,
        'tokens': tokens,
        'prefix': 'trigger_'
    })

def get_action_config_form(request, board_id):
    """
    HTMX: Returns the config inputs for a selected action.
    """
    board = get_object_or_404(Board, id=board_id)
    action_code = request.GET.get('action')
    
    from .registry import AutomationRegistry
    handler = AutomationRegistry.get_action(action_code)
    
    if not handler or not handler.config_schema:
        return HttpResponse("")

    # Parse recipe template (Duplicate logic, could extract)
    recipe_template = getattr(handler, 'recipe_template', '')
    tokens = []
    if recipe_template:
        import re
        parts = re.split(r'(\{.*?\})', recipe_template)
        for part in parts:
            if part.startswith('{') and part.endswith('}'):
                field_name = part[1:-1]
                field_def = next((f for f in handler.config_schema if f['name'] == field_name), None)
                if field_def:
                    tokens.append({'type': 'field', 'field': field_def})
                else:
                    tokens.append({'type': 'text', 'content': part})
            else:
                if part: tokens.append({'type': 'text', 'content': part})
    else:
        for field in handler.config_schema:
             tokens.append({'type': 'field', 'field': field})
        
    return render(request, 'automation/partials/config_form.html', {
        'board': board,
        'tokens': tokens,
        'prefix': 'action_'
    })

from django.http import HttpResponse

@login_required
def create_rule(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    
    # Load dynamic triggers and actions from Registry
    from .registry import AutomationRegistry
    triggers = AutomationRegistry.get_all_triggers()
    actions = AutomationRegistry.get_all_actions()
    
    if request.method == 'POST':
        trigger_code = request.POST.get('trigger')
        action_code = request.POST.get('action')
        
        if not trigger_code or not action_code:
            return redirect('create_rule', board_id=board_id)

        # Extract Configs dynamically based on schema
        trigger_handler = AutomationRegistry.get_trigger(trigger_code)
        action_handler = AutomationRegistry.get_action(action_code)
        
        trigger_config = {}
        if trigger_handler:
            for field in trigger_handler.config_schema:
                key = field['name']
                val = request.POST.get(f"trigger_{key}")
                if val: trigger_config[key] = val
                
        action_config = {}
        if action_handler:
            for field in action_handler.config_schema:
                key = field['name']
                val = request.POST.get(f"action_{key}")
                if val: action_config[key] = val

        # Helper to generate name
        t_name = trigger_handler.name if trigger_handler else trigger_code
        a_name = action_handler.name if action_handler else action_code
        
        # Try to make a readable name
        # e.g. "Status Changes (Done) -> Move Item (Archive)"
        rule_name = f"When {t_name}"
        # Check specific known keys for better naming
        if trigger_config.get('value'): rule_name += f" is {trigger_config['value']}"
        rule_name += f", then {a_name}"
        
        rule = AutomationRule.objects.create(
            board=board,
            name=rule_name,
            trigger_type=trigger_code,
            action_type=action_code,
            trigger_config=trigger_config,
            action_config=action_config
        )
        return redirect('automation_list', board_id=board.id)
        
    if request.headers.get('HX-Request'):
        return render(request, 'automation/builder.html', {
            'board': board,
            'triggers': triggers,
            'actions': actions,
            'partial': True
        })

    base_template = 'automation/partial_base.html' if request.headers.get('HX-Request') else 'base.html'

    return render(request, 'automation/builder.html', {
        'board': board,
        'triggers': triggers,
        'actions': actions,
        'base_template': base_template,
        'partial': request.headers.get('HX-Request')
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
    """
    Edits an existing automation rule.
    """
    board = get_object_or_404(Board, id=board_id)
    rule = get_object_or_404(AutomationRule, id=rule_id, board=board)
    
    # Load registry
    from .registry import AutomationRegistry
    triggers = AutomationRegistry.get_all_triggers()
    actions = AutomationRegistry.get_all_actions()
    
    status_col = board.columns.filter(type='status').first()
    status_options = status_col.settings.get('choices', []) if status_col else ['Not Started', 'Done']

    if request.method == 'POST':
        trigger_code = request.POST.get('trigger')
        action_code = request.POST.get('action')
        
        # Determine Handlers
        trigger_handler = AutomationRegistry.get_trigger(trigger_code)
        action_handler = AutomationRegistry.get_action(action_code)

        # Build Configs dynamically
        trigger_config = {}
        if trigger_handler and trigger_handler.config_schema:
            for field in trigger_handler.config_schema:
                key = field['name']
                val = request.POST.get(f"trigger_{key}")
                if val: trigger_config[key] = val
                
        action_config = {}
        if action_handler and action_handler.config_schema:
            for field in action_handler.config_schema:
                key = field['name']
                val = request.POST.get(f"action_{key}")
                if val: action_config[key] = val

        # Generate Name
        t_name = trigger_handler.name if trigger_handler else trigger_code
        a_name = action_handler.name if action_handler else action_code
        
        rule_name = f"When {t_name}"
        # Heuristic for "value" in name
        if trigger_config.get('value'): 
            rule_name += f" is {trigger_config['value']}"
        rule_name += f", then {a_name}"
        if action_config.get('new_value'):
            rule_name += f" to {action_config['new_value']}"
        
        # Save updates
        rule.trigger_type = trigger_code
        rule.action_type = action_code
        rule.trigger_config = trigger_config
        rule.action_config = action_config
        rule.name = rule_name
        rule.save()
        
        return redirect('automation_list', board_id=board.id)

    # Initial Data for pre-filling the form
    # We flatten the config into a single dict for the template to access easily
    initial_data = {
        'trigger': rule.trigger_type,
        'action': rule.action_type,
    }
    # Prefix trigger config keys
    for k, v in rule.trigger_config.items():
        initial_data[f"trigger_{k}"] = v
    # Prefix action config keys
    for k, v in rule.action_config.items():
        initial_data[f"action_{k}"] = v

    return render(request, 'automation/builder.html', {
        'board': board,
        'triggers': triggers,
        'actions': actions,
        'status_options': status_options,
        'initial': initial_data,
        'is_edit': True,
        'rule_id': rule.id
    })

@require_POST
@login_required
def toggle_rule(request, board_id, rule_id):
    """
    Toggle an automation rule's active state via HTMX.
    """
    board = get_object_or_404(Board, id=board_id)
    rule = get_object_or_404(AutomationRule, id=rule_id, board=board)
    
    # Toggle the is_active state
    rule.is_active = not rule.is_active
    rule.save()
    
    # Return the updated toggle HTML
    return render(request, 'automation/partials/toggle_switch.html', {
        'rule': rule,
        'board': board
    })

@login_required
def run_history(request, board_id):
    """
    Show automation run history for a board.
    """
    from .models import AutomationLog
    
    board = get_object_or_404(Board, id=board_id)
    logs = AutomationLog.objects.filter(rule__board=board).select_related('rule').order_by('-executed_at')[:50]
    
    return render(request, 'automation/run_history.html', {
        'board': board,
        'logs': logs
    })

