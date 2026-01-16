from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
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
# @login_required 
def dashboard(request):
    """
    Shows all workspaces and boards.
    """
    workspaces = Workspace.objects.all()
    return render(request, 'webapp/dashboard.html', {'workspaces': workspaces})

@login_required 
def board_detail(request, board_id):
    """
    Renders the board detail view with its groups and items.
    """
    board = get_object_or_404(Board, id=board_id)
    
    # Simple Search logic
    search_query = request.GET.get('search', '').strip()
    
    context = {'board': board, 'search_query': search_query}
    
    if search_query:
        # Filter items if search exists. 
        from django.db.models import Prefetch
        items_queryset = Item.objects.filter(name__icontains=search_query)
        
        # We need to ensure we only get groups for this board, and within those groups, only matching items
        board = Board.objects.prefetch_related(
            Prefetch('groups', queryset=Group.objects.filter(board=board).prefetch_related(
                Prefetch('items', queryset=items_queryset)
            ))
        ).get(id=board_id)
        context['board'] = board

    context['columns'] = board.columns.all()
    return render(request, 'webapp/board_detail.html', context)
    # return render(request, 'webapp/board_detail_debug.html', context)

@require_POST
def add_item(request, group_id):
    """
    HTMX: Adds an item to a group and returns the row HTML.
    """
    group = get_object_or_404(Group, id=group_id)
    name = request.POST.get('name', '').strip()
    if not name:
        # Return nothing or error if empty name (Basic validation)
        # For HTMX, simplest is to return empty response or 400
        from django.http import HttpResponseBadRequest
        return HttpResponseBadRequest("Name is required")
    
    item = Item.objects.create(group=group, name=name, created_by=request.user if request.user.is_authenticated else None)
    
    # In a real scenario, we would grab columns to render the empty cells correctly
    columns = group.board.columns.all()
    
    return render(request, 'webapp/partials/item_row.html', {'item': item, 'columns': columns})

@require_POST
def update_status(request, item_id, col_id):
    """
    Cycles status on click. HTMX. Now 100% DYNAMIC!
    """
    item = get_object_or_404(Item, id=item_id)
    column = get_object_or_404(Column, id=col_id)
    
    # Get dynamic status options from column
    status_options = get_status_options(column)
    
    # Get current value
    current_val = item.values.get(str(col_id), status_options[0] if status_options else '')
    
    # Cycle to next status
    try:
        current_index = status_options.index(current_val)
        next_index = (current_index + 1) % len(status_options)
        new_val = status_options[next_index]
    except (ValueError, IndexError):
        # If current value not in list or list is empty, use first option
        new_val = status_options[0] if status_options else current_val
    
    item.values[str(col_id)] = new_val
    item.save()
    
    columns = item.group.board.columns.all()
    return render(request, 'webapp/partials/item_row.html', {'item': item, 'columns': columns})

def kanban_view(request, board_id):
    """
    Renders the Kanban board view. Now 100% DYNAMIC!
    """
    board = get_object_or_404(Board, id=board_id)
    
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
        # We need to fetch ALL items from ALL groups
        items = Item.objects.filter(group__board=board).select_related('group')
        
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
    
    item = get_object_or_404(Item, id=item_id)
    
    if new_status:
        # Find status column again
        status_column = item.group.board.columns.filter(type='status').first()
        if status_column:
            item.values[str(status_column.id)] = new_status
            item.save()
            
    return JsonResponse({'status': 'success'})

def calendar_view(request, board_id):
    """
    Renders items on a calendar.
    Requires at least one 'date' column.
    """
    board = get_object_or_404(Board, id=board_id)
    import json
    
    # 1. Find Date Column
    date_col = board.columns.filter(type='date').first()
    
    events = []
    if date_col:
        # 2. Get all Items with that date value
        items = Item.objects.filter(group__board=board)
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
    my_items = Item.objects.filter(
        created_by=request.user
    ).select_related('group__board__workspace').order_by('-created_at')[:50]
    
    return render(request, 'webapp/my_work.html', {
        'items': my_items
    })

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
