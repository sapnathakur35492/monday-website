from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import UserDashboard, DashboardWidget, Workspace

@login_required
def dashboard_list(request):
    dashboards = UserDashboard.objects.filter(owner=request.user)
    return render(request, 'webapp/dashboard_list.html', {'dashboards': dashboards})

@login_required
def create_dashboard(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        workspace_id = request.POST.get('workspace_id')
        
        workspace = None
        if workspace_id:
            workspace = get_object_or_404(Workspace, id=workspace_id)
            
        dashboard = UserDashboard.objects.create(
            name=name,
            owner=request.user,
            workspace=workspace
        )
        return redirect('user_dashboard_detail', dashboard_id=dashboard.id)
    return redirect('dashboard')

@login_required
def dashboard_detail(request, dashboard_id):
    dashboard = get_object_or_404(UserDashboard, id=dashboard_id)
    return render(request, 'webapp/user_dashboard.html', {'dashboard': dashboard})
