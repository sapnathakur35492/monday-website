from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import Workspace, Board, Group, Item, Column

def get_status_options(column):
    """
    Helper function to get status options dynamically from column settings.
    Falls back to default if not configured.
    """
    if column and column.settings.get('choices'):
        return column.settings.get('choices')
    # Default status options if not configured in column
    return ['Not Started', 'In Progress', 'Done', 'On Hold']

# For simplicity in this demo, we might skip @login_required decorators 
# if we want to test easily without auth, but for production code we add them.
@login_required 
def dashboard(request):
    """
    Shows all workspaces and boards.
    """
    # Optimized query with prefetch_related to avoid N+1 queries
    workspaces = Workspace.objects.prefetch_related(
        'boards',
        'boards__workspace',
        'boards__created_by'
    ).filter(
        organization__memberships__user=request.user
    ).distinct()
    
    return render(request, 'webapp/dashboard.html', {'workspaces': workspaces})

@login_required 
def board_detail(request, board_id):
    """
    Renders the board detail view with its groups and items.
    """
    # Optimized query with select_related and prefetch_related
    board = Board.objects.select_related(
        'workspace',
        'workspace__organization',
        'created_by'
    ).prefetch_related(
        'groups',
        'groups__items',
        'groups__items__created_by',
        'columns'
    ).get(id=board_id)
    
    # Permission Check
    if not check_board_access(request.user, board):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("You do not have access to this board's workspace.")
    
    # Simple Search logic
    search_query = request.GET.get('search', '').strip()
    
    context = {'board': board, 'search_query': search_query}
    
    if search_query:
        # Filter items if search exists. 
        from django.db.models import Prefetch
        items_queryset = Item.objects.filter(name__icontains=search_query).select_related('created_by')
        
        # We need to ensure we only get groups for this board, and within those groups, only matching items
        board = Board.objects.select_related(
            'workspace',
            'workspace__organization'
        ).prefetch_related(
            Prefetch('groups', queryset=Group.objects.filter(board=board).prefetch_related(
                Prefetch('items', queryset=items_queryset)
            )),
            'columns'
        ).get(id=board_id)
        context['board'] = board

    context['columns'] = board.columns.all()
    
    # Get Organization Users for "Person" column
    # Assuming board -> workspace -> organization
    org = board.workspace.organization
    context['users'] = org.memberships.select_related('user').all()
    
    return render(request, 'webapp/board_detail.html', context)

def check_board_access(user, board):
    """
    Verifies if user has access to the board via Organization membership.
    """
    # Allow superusers
    if user.is_superuser:
        return True
    
    # Hardcoded check removed
    # if user.email == 'santoshfasfsdf@redorangetechnologies.com':
    #     return True
        
    # Allow board creator
    if board.created_by == user:
        return True
        
    if board.workspace.organization.memberships.filter(user=user).exists():
        return True
    return False


@require_POST
def add_item(request, group_id):
    """
    HTMX: Adds an item to a group and returns the row HTML.
    """
    group = get_object_or_404(Group, id=group_id)
    
    if not verify_edit_permission(request.user, group.board):
        return JsonResponse({'error': 'Permission Denied'}, status=403)
        
    name = request.POST.get('name', '').strip()
    if not name:
        from django.http import HttpResponseBadRequest
        return HttpResponseBadRequest("Name is required")
    
    # Calculate position
    last_pos = group.items.last().position if group.items.exists() else 0
    
    # Determine defaults
    default_values = {}
    for col in group.board.columns.all():
        if col.type == 'status':
            choices = col.settings.get('choices', [])
            if choices:
                default_values[str(col.id)] = choices[0]
            else:
                default_values[str(col.id)] = 'Not Started'
        elif col.type == 'priority':
             default_values[str(col.id)] = 'Medium'
    
    item = Item.objects.create(
        group=group, 
        name=name, 
        position=last_pos + 1,
        created_by=request.user if request.user.is_authenticated else None,
        values=default_values
    )
    
    columns = group.board.columns.all().order_by('position')
    users = group.board.workspace.organization.memberships.select_related('user').all()
    
    return render(request, 'webapp/partials/item_row.html', {'item': item, 'columns': columns, 'users': users})

def verify_edit_permission(user, board):
    """
    Checks if user is Admin or Member (Permissions to edit).
    Viewers cannot edit.
    """
    # Allow superusers
    if user.is_superuser:
        return True
    
    # Hardcoded check removed
    # if user.email == 'santoshfasfsdf@redorangetechnologies.com':
    #     return True
        
    # Allow board creator
    if board.created_by == user:
        return True

    membership = board.workspace.organization.memberships.filter(user=user).first()
    if membership and membership.role in ['admin', 'member']:
        return True
    return False

@require_POST
def update_status(request, item_id, col_id):
    """
    Cycles status on click. HTMX. Now 100% DYNAMIC!
    """
    item = get_object_or_404(Item, id=item_id)
    
    # Permission Check
    if not verify_edit_permission(request.user, item.group.board):
        return JsonResponse({'error': 'Permission Denied'}, status=403)
        
    column = get_object_or_404(Column, id=col_id)
    
    # ... logic continues ...
    column = get_object_or_404(Column, id=col_id)
    
    # Get dynamic status options from column
    status_options = get_status_options(column)
    
    # Check if a specific value was requested (Dropdown selection)
    requested_val = request.POST.get('action_value')
    
    import json
    if requested_val:
        if column.type in ['dependency', 'connect_boards']:
            try:
                new_val = json.loads(requested_val)
            except json.JSONDecodeError:
                new_val = requested_val
        else:
            new_val = requested_val
    else:
        # Cycle to next status (Legacy/Cycle click)
        current_val = item.values.get(str(col_id), status_options[0] if status_options else '')
        try:
            current_index = status_options.index(current_val)
            next_index = (current_index + 1) % len(status_options)
            new_val = status_options[next_index]
        except (ValueError, IndexError):
            new_val = status_options[0] if status_options else current_val
    
    item.values[str(col_id)] = new_val
    item.save()
    
    # --- AUTOMATION TRIGGER ---
    # Handled by signals (automation.signals.execute_automation_actions)
    # --------------------------

    # --- FORMULA CALCULATION ---
    # When any value changes, re-evaluate all formulas on this item
    try:
        from .formula_service import FormulaEngine
        formula_cols = item.group.board.columns.filter(type='formula')
        for f_col in formula_cols:
            expression = item.values.get(str(f_col.id), "")
            if expression and isinstance(expression, str) and expression.startswith("="):
                 result = FormulaEngine.evaluate(expression[1:], item)
                 item.values[str(f_col.id) + '_result'] = result
        item.save()
    except Exception as e:
         print(f"Formula Error: {e}")
    # ---------------------------
    
    columns = item.group.board.columns.all()
    users = item.group.board.workspace.organization.memberships.select_related('user').all()
    return render(request, 'webapp/partials/item_row.html', {'item': item, 'columns': columns, 'users': users})

def kanban_view(request, board_id):
    """
    Renders the Kanban board view. Now 100% DYNAMIC!
    """
    board = Board.objects.select_related('workspace').prefetch_related('columns').get(id=board_id)
    
    # 1. Identify the 'Status' column to group by
    status_column = board.columns.filter(type='status').first()
    
    # Default statuses if no column found (fallback)
    kanban_columns = {}
    if status_column:
        # Get dynamic status options from column settings
        defined_statuses = get_status_options(status_column)
        
        # Initialize buckets
        for status in defined_statuses:
            kanban_columns[status] = []
            
        # 2. Distribute Items into Buckets
        # Optimized query with select_related
        items = Item.objects.filter(
            group__board=board
        ).select_related(
            'group',
            'created_by'
        ).order_by('group__position', 'position')
        
        for item in items:
            val = item.values.get(str(status_column.id), defined_statuses[0] if defined_statuses else '')
            if val not in kanban_columns:
                kanban_columns[val] = [] # Handle unknown/new statuses dynamically
            kanban_columns[val].append(item)
            
    return render(request, 'webapp/kanban.html', {
        'board': board, 
        'columns_data': kanban_columns,
        'exclude_col_id': str(status_column.id) if status_column else None
    })

@require_POST
def update_item_order(request):
    """
    API to handle Drag & Drop reordering and Status changes.
    Expected Payload: item_id, new_status (optional), position (optional)
    """
    import json
    data = json.loads(request.body)
    
    item_id = data.get('itemId')
    new_status = data.get('newStatus')
    new_position = data.get('newPosition')
    new_group_id = data.get('newGroupId')

    item = get_object_or_404(Item, id=item_id)
    
    # Permission Check
    if not verify_edit_permission(request.user, item.group.board):
        return JsonResponse({'error': 'Permission Denied'}, status=403)

    # 1. Handle Status Change
    if new_status:
        status_column = item.group.board.columns.filter(type='status').first()
        if status_column:
            item.values[str(status_column.id)] = new_status
            item.save()

    # 2. Handle Reordering (Position / Group Change)
    if new_position is not None:
        # If group changed
        if new_group_id:
            try:
                new_group = Group.objects.get(id=new_group_id)
                item.group = new_group
            except Group.DoesNotExist:
                pass
        
        # Update position
        # In a real app, we would shift other items' positions. 
        # For this MVP, we will rely on flex/sort order or simple overwrite.
        # A robust way is to use a library like django-ordered-model.
        # Here we just update the specific item's position.
        item.position = int(new_position)
        item.save()

    return JsonResponse({'status': 'success'})

@login_required
def gantt_view(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    return render(request, 'webapp/board_gantt.html', {
        'board': board,
        'workspace': board.workspace
    })

def calendar_view(request, board_id):
    """
    Renders items on a calendar.
    Requires at least one 'date' column.
    """
    board = Board.objects.select_related('workspace').prefetch_related('columns').get(id=board_id)
    import json
    
    # 1. Find Date Column
    date_col = board.columns.filter(type='date').first()
    
    events = []
    if date_col:
        # 2. Get all Items with that date value - optimized query
        items = Item.objects.filter(
            group__board=board
        ).select_related('group').only('id', 'name', 'values', 'group__color')
        
        col_id_str = str(date_col.id)
        
        for item in items:
            date_val = item.values.get(col_id_str)
            if date_val:
                # Basic YYYY-MM-DD check or format
                events.append({
                    'title': item.name,
                    'start': date_val,
                    'color': item.group.color,
                    'id': item.id
                })
    
    return render(request, 'webapp/calendar.html', {
        'board': board,
        'date_col_id': date_col.id if date_col else None,
        'events_json': json.dumps(events)
    })

@login_required
def my_work_view(request):
    """
    Shows all items created by or assigned to the current user.
    This is different from dashboard which shows all workspaces.
    """
    # Get items created by user
    # 1. Created by User
    created_items = Item.objects.filter(created_by=request.user).select_related('group__board__workspace')
    
    # 2. Assigned to User
    from django.db.models import Q
    
    # Find all "person" columns
    person_cols = Column.objects.filter(type='person')
    
    # Build query: For each column, check if its ID is in values with the username
    # JSONField filtering: values__<col_id> = username. 
    # Since keys are strings of IDs, we can construct filters.
    
    assigned_items = []
    # Fetch all items that rely on person columns to limit DB hits slightly
    # Ideally, we would filter by board/person cols first, but for MVP:
    # Get all items connected to board columns of type 'person'
    candidate_items = Item.objects.filter(group__board__columns__in=person_cols).distinct()
    
    username = request.user.username
    
    for item in candidate_items:
        # Check values manually
        # values is a dict {col_id: username}
        for col in person_cols:
            col_id_str = str(col.id)
            if item.values.get(col_id_str) == username:
                assigned_items.append(item)
                break # Sent for this item

        
    # Merge and Deduplicate
    all_items = list(created_items) + assigned_items
    # Sort by created_at desc
    all_items.sort(key=lambda x: x.created_at, reverse=True)
     
    return render(request, 'webapp/my_work.html', {
        'items': all_items[:50] # Limit to recent 50
    })

@login_required
def global_search(request):
    """
    Searches across Workspaces, Boards, and Items.
    """
    query = request.GET.get('q', '').strip()
    from django.db.models import Q
    
    results = {
        'workspaces': [],
        'boards': [],
        'items': []
    }
    
    if query:
        # Search Workspaces
        results['workspaces'] = Workspace.objects.filter(
            organization__memberships__user=request.user,
            name__icontains=query
        )[:5]
        
        # Search Boards
        results['boards'] = Board.objects.filter(
            workspace__organization__memberships__user=request.user,
            name__icontains=query
        )[:10]
        
        # Search Items
        # Filter items where user has access to the board
        results['items'] = Item.objects.filter(
            group__board__workspace__organization__memberships__user=request.user,
            name__icontains=query
        ).select_related('group', 'group__board')[:50]
        
    return render(request, 'webapp/global_search.html', {'query': query, 'results': results})

@login_required
def create_workspace(request):
    """
    Create a new workspace for the user's organization.
    """
    from core.models import Organization
    from django.contrib import messages
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        
        if not name:
            messages.error(request, 'Workspace name is required.')
            return render(request, 'webapp/create_workspace.html')
        
        # Get or create user's organization
        org = request.user.owned_organizations.first()
        if not org:
            org = Organization.objects.create(
                name=f"{request.user.username}'s Organization",
                owner=request.user
            )
        
        # Ensure owner is a member (Fix for existing users)
        from core.models import Membership
        Membership.objects.get_or_create(user=request.user, organization=org, defaults={'role': 'admin'})
        
        workspace = Workspace.objects.create(
            name=name,
            organization=org,
            description=request.POST.get('description', '')
        )
        
        messages.success(request, f'Workspace "{name}" created successfully!')
        return redirect('dashboard')
    
    return render(request, 'webapp/create_workspace.html')

@login_required
def create_board(request, workspace_id):
    """
    Create a new board in a workspace with default columns and groups.
    """
    from django.contrib import messages
    
    workspace = get_object_or_404(Workspace, id=workspace_id)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        board_type = request.POST.get('type', 'table')
        
        if not name:
            messages.error(request, 'Board name is required.')
            return render(request, 'webapp/create_board.html', {'workspace': workspace})
        
        # Create board
        board = Board.objects.create(
            workspace=workspace,
            name=name,
            type=board_type,
            created_by=request.user,
            description=request.POST.get('description', '')
        )
        
        # Create default columns
        Column.objects.create(
            board=board, 
            title='Task Name', 
            type='text', 
            position=0
        )
        Column.objects.create(
            board=board, 
            title='Status', 
            type='status', 
            position=1,
            settings={'choices': ['Not Started', 'In Progress', 'Done', 'On Hold']}
        )
        Column.objects.create(
            board=board, 
            title='Priority', 
            type='priority', 
            position=2
        )
        Column.objects.create(
            board=board, 
            title='Due Date', 
            type='date', 
            position=3
        )
        Column.objects.create(
            board=board, 
            title='Assigned To', 
            type='person', 
            position=4
        )

        if board_type == 'gantt':
            Column.objects.create(
                board=board,
                title='Timeline',
                type='timeline',
                position=5
            )
        
        # Create default group
        Group.objects.create(
            board=board, 
            title='Tasks', 
            color='#6366f1', 
            position=0
        )
        
        messages.success(request, f'Board "{name}" created successfully!')
        return redirect('board_detail', board_id=board.id)
    
    return render(request, 'webapp/create_board.html', {'workspace': workspace})

@login_required
def get_item_details(request, item_id):
    """
    Returns the Side Panel HTML for an item.
    """
    item = get_object_or_404(Item, id=item_id)
    updates = item.updates.all()
    # If using HTMX to just load the content
    return render(request, 'webapp/partials/side_panel.html', {'item': item, 'updates': updates})

@require_POST
@login_required
def post_item_update(request, item_id):
    """
    HTMX: Posts a new update/comment to an item.
    """
    item = get_object_or_404(Item, id=item_id)
    body = request.POST.get('body', '').strip()
    
    if body:
        from .models import ItemUpdate
        update = ItemUpdate.objects.create(
            item=item,
            user=request.user,
            body=body
        )
        return render(request, 'webapp/partials/update_card.html', {'update': update})
    
    return JsonResponse({})

@require_POST
@login_required
def add_group(request, board_id):
    """
    Adds a new group to the board.
    """
    board = get_object_or_404(Board, id=board_id)
    
    if not verify_edit_permission(request.user, board):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("You do not have permission to add groups.")
        
    title = request.POST.get('title', 'New Group')
    
    # Calculate position
    last_pos = board.groups.last().position if board.groups.exists() else 0
    
    Group.objects.create(
        board=board,
        title=title,
        color='#579bfc', # Default blue
        position=last_pos + 1
    )
    
    # Refresh page to show new group (simplest for now)
    return redirect('board_detail', board_id=board.id)

@require_POST
@login_required
def delete_group(request, board_id, group_id):
    board = get_object_or_404(Board, id=board_id)
    group = get_object_or_404(Group, id=group_id, board=board)
    
    if not verify_edit_permission(request.user, board):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("You do not have permission to delete groups.")
        
    group.delete()
    if request.headers.get('HX-Request'):
        return HttpResponse('')
    return redirect('board_detail', board_id=board.id)

@require_POST
@login_required
def delete_item(request, board_id, item_id):
    board = get_object_or_404(Board, id=board_id)
    # Ensure item belongs to board
    item = get_object_or_404(Item, id=item_id, group__board=board)
    
    if not verify_edit_permission(request.user, board):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("You do not have permission to delete items.")
        
    item.delete()
    if request.headers.get('HX-Request'):
        return HttpResponse('')
    return redirect('board_detail', board_id=board.id)

@require_POST
@login_required
def update_group_title(request):
    import json
    data = json.loads(request.body)
    group_id = data.get('id')
    new_title = data.get('title')
    
    group = get_object_or_404(Group, id=group_id)
    
    if not verify_edit_permission(request.user, group.board):
        return JsonResponse({'error': 'Permission Denied'}, status=403)
        
    group.title = new_title
    group.save()
    return JsonResponse({'status': 'ok'})

@require_POST
@login_required
def add_column(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    if not verify_edit_permission(request.user, board):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    col_type = request.POST.get('type')
    title = request.POST.get('title', col_type.capitalize())
    position = board.columns.count()
    settings = {}
    if col_type == 'status':
        settings['choices'] = ['Done', 'Working on it', 'Stuck', 'Not Started']
    elif col_type == 'priority':
        settings['choices'] = ['High', 'Medium', 'Low']
    
    Column.objects.create(board=board, title=title, type=col_type, position=position, settings=settings)
    return redirect('board_detail', board_id=board.id)


@login_required
def get_board_items(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    # Return items for picking (Dependency / Connect logic)
    items = Item.objects.filter(group__board=board).select_related('group').order_by('group__position', 'id')
    return render(request, 'webapp/partials/board_items_list.html', {'items': items})
