from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from core.models import User, Organization
from core.saas_models import BillingProfile
from webapp.models import Board
from automation.models import AutomationRule, AutomationLog
from .forms import SignUpForm  # Need to create this form

from django.contrib.auth import authenticate, login, logout
from .forms import SignUpForm, LoginForm

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Create default Organization and Membership
            from core.models import Organization, Membership
            from webapp.models import Workspace, Board, Group, Column, Item
            
            org = Organization.objects.create(name=f"{user.username}'s Team", owner=user)
            Membership.objects.create(user=user, organization=org, role='admin')
            
            # Create Default Workspace & Board
            ws = Workspace.objects.create(organization=org, name="Main Workspace")
            board = Board.objects.create(workspace=ws, name="My First Board", description="Welcome to ProjectFlow!")
            
            # Default Group
            group = Group.objects.create(board=board, title="Things to do", color="#6366f1", position=0)
            Group.objects.create(board=board, title="Done", color="#22c55e", position=1)
            
            # Default Columns
            Column.objects.create(board=board, title="Status", type="status", position=0, settings={'choices': ['Done', 'Working on it', 'Stuck', 'Not Started']})
            Column.objects.create(board=board, title="Person", type="person", position=1)
            Column.objects.create(board=board, title="Date", type="date", position=2)
            
            # Default Item
            Item.objects.create(group=group, name="Explore ProjectFlow", created_by=user)
            Item.objects.create(group=group, name="Invite team members", created_by=user)
            
            login(request, user, backend='core.backends.EmailBackend')
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'core/signup.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    error = None
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            
            if user is not None:
                login(request, user)
                if 'next' in request.POST:
                    return redirect(request.POST.get('next'))
                return redirect('dashboard')
            else:
                error = "Invalid email or password"
    else:
        form = LoginForm()
    return render(request, 'core/login.html', {'form': form, 'error': error})

def logout_view(request):
    logout(request)
    return redirect('landing')

@staff_member_required
def admin_dashboard(request):
    """
    Custom Admin Dashboard for SaaS Metrics.
    """
    total_users = User.objects.count()
    active_companies = Organization.objects.count()
    boards_count = Board.objects.count()
    automations_count = AutomationRule.objects.filter(is_active=True).count()
    
    # Recent logs for activity feed
    recent_logs = AutomationLog.objects.select_related('rule').order_by('-executed_at')[:10]
    
    context = {
        'total_users': total_users,
        'active_companies': active_companies,
        'boards_count': boards_count,
        'automations_count': automations_count,
        'recent_logs': recent_logs,
    }
    return render(request, 'core/admin_dashboard.html', context)

@login_required
def billing_dashboard(request):
    """
    User facing billing dashboard.
    """
    # Assuming user belongs to an organization. 
    # For MVP, just get the first organization owned by user or create a dummy one
    org = request.user.owned_organizations.first()
    if not org:
        # Create default org if missing (fallback for MVP)
        org = Organization.objects.create(name=f"{request.user.username}'s Team", owner=request.user)
        
    # Get or create billing profile
    billing, created = BillingProfile.objects.get_or_create(organization=org)
    
    return render(request, 'core/billing.html', {'billing': billing})

@login_required
def team_list(request):
    """
    List all members in the user's organization.
    """
    # Simple logic: Get first owned org or where user is admin
    # For MVP: assume first owned org
    org = request.user.owned_organizations.first()
    if not org:
        # Maybe they are a member?
        membership = request.user.memberships.first()
        if membership:
            org = membership.organization
        else:
             org = Organization.objects.create(name=f"{request.user.username}'s Team", owner=request.user)
             
    members = org.memberships.select_related('user').all()
    
    return render(request, 'core/team_list.html', {'org': org, 'members': members})

@login_required
def invite_member(request):
    """
    Invite a user to the organization by email.
    Sends an email and creates a notification.
    """
    from django.contrib import messages
    from django.core.mail import send_mail
    from core.models import Membership, Notification
    
    if request.method == 'POST':
        email = request.POST.get('email')
        role = request.POST.get('role', 'member')
        
        if not email:
            messages.error(request, "Email address is required.")
            return redirect('team_list')
        
        # Get Organization
        org = request.user.owned_organizations.first()
        if not org:
             org = Organization.objects.create(name=f"{request.user.username}'s Team", owner=request.user)

        # Find User
        try:
            user_to_invite = User.objects.get(email=email)
            if user_to_invite == request.user:
                 messages.warning(request, "You cannot invite yourself.")
            else:
                # Create Membership
                obj, created = Membership.objects.get_or_create(
                    user=user_to_invite, 
                    organization=org,
                    defaults={'role': role}
                )
                
                if created:
                    # 1. Send Email
                    try:
                        send_mail(
                            subject=f"You've been invited to {org.name} on ProjectFlow",
                            message=f"Hi {user_to_invite.username},\n\n{request.user.username} has invited you to join their team '{org.name}'.\n\nLog in to check it out!",
                            from_email='system@projectflow.com',
                            recipient_list=[email],
                            fail_silently=True
                        )
                    except:
                        pass # Fail silently for demo if no SMTP
                        
                    # 2. PROPER NOTIFICATION (Dynamic)
                    # Notify the INVITEE
                    Notification.objects.create(
                        user=user_to_invite,
                        title="New Team Invitation",
                        message=f"You have been added to {org.name} by {request.user.username}."
                    )
                    
                    messages.success(request, f"{email} has been invited and notified.")
                else:
                    messages.info(request, f"{email} is already a member.")
                    
        except User.DoesNotExist:
            # For MVP, we can't invite non-users easily without a signup flow token.
            # We'll simulate sending an invite email.
            try:
                send_mail(
                    subject=f"You've been invited to ProjectFlow",
                    message=f"Hi,\n\n{request.user.username} wants you to join ProjectFlow to collaborate on '{org.name}'.\n\nSign up here: https://amjim.com/core/signup/",
                    from_email='system@projectflow.com',
                    recipient_list=[email],
                    fail_silently=True
                )
                messages.success(request, f"Invitation email sent to {email}.")
            except:
                 messages.success(request, f"Invitation generated for {email} (Simulated).")

        except Exception as e:
            messages.error(request, "An error occurred during invitation.")
             
        return redirect('team_list')
    return redirect('team_list')

@login_required
def profile_view(request):
    """
    User Profile Settings with Validation
    """
    from django.contrib import messages
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        
        # Validation
        if not first_name or not last_name:
            messages.error(request, "First Name and Last Name are required.")
            return render(request, 'core/profile.html')
            
        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        
        messages.success(request, 'Profile updated successfully.')
        return redirect('profile')
        
    return render(request, 'core/profile.html')

@login_required
def notifications_view(request):
    """
    User Notifications
    """
    notifications = request.user.notifications.all()
    # Mark as read logic could go here or via AJAX
    return render(request, 'core/notifications.html', {'notifications': notifications})
