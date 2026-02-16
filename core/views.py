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
import uuid
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

def verify_email_view(request, token):
    try:
        user = User.objects.get(verification_token=token)
        user.is_verified = True
        user.verification_token = None
        user.save()
        login(request, user, backend='core.backends.EmailBackend')
        return redirect('dashboard')
    except User.DoesNotExist:
        return render(request, 'core/login.html', {'error': 'Invalid or expired verification link.'})

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
            
            # Generate Verification Token
            token = str(uuid.uuid4())
            user.verification_token = token
            user.is_verified = False
            user.save()
            
            # Send Verification Email (professional HTML template)
            verification_link = request.build_absolute_uri(f'/core/verify/{token}/')
            subject = 'Verify your email for ProjectFlow'

            # Plain-text fallback
            display_name = user.first_name or user.username or user.email
            text_body = (
                f"Hi {display_name},\n\n"
                "Welcome to ProjectFlow! Please confirm your email address to activate your account and access your workspace.\n\n"
                f"Verification link: {verification_link}\n\n"
                "If you did not create a ProjectFlow account, you can safely ignore this email.\n"
            )

            # HTML body using template
            html_body = render_to_string(
                'core/email_verification.html',
                {
                    'user': user,
                    'verification_link': verification_link,
                },
            )

            try:
                send_mail(
                    subject,
                    text_body,
                    'ProjectFlow <noreply@projectflow.com>',
                    [user.email],
                    fail_silently=True,
                    html_message=html_body,
                )
                print(f"Verification Link for {user.email}: {verification_link}")  # For local testing
            except Exception as e:
                print(f"Error sending email: {e}")
            
            return render(request, 'core/verification_sent.html', {'email': user.email})
    else:
        form = SignUpForm()
    return render(request, 'core/signup.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    # Initialize form and error
    form = LoginForm()
    error = None
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email', '').strip()
            password = form.cleaned_data.get('password', '')
            
            # Authenticate user
            user = authenticate(request, email=email, password=password)
            
            if user is not None:
                login(request, user)
                # Check for next parameter
                next_url = request.POST.get('next') or request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('dashboard')
            else:
                error = "Invalid email or password. Please try again."
        else:
            error = "Please enter valid email and password."
    
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
        from core.models import Organization
        org = Organization.objects.create(name=f"{request.user.username}'s Team", owner=request.user)
        
    # Get or create billing profile
    billing, created = BillingProfile.objects.get_or_create(organization=org)
    
    # Context for Plans
    from core.saas_models import PricingPlan
    plans = PricingPlan.objects.filter(is_active=True).order_by('price')
    
    return render(request, 'core/billing.html', {'billing': billing, 'plans': plans})

@login_required
def upgrade_plan(request, plan_name):
    """
    Simulates Stripe Checkout Session creation.
    Redirects to success page to mock a completed payment.
    param plan_name: This matches the 'slug' of the PricingPlan.
    """
    # In real world: 
    # session = stripe.checkout.Session.create(...)
    # return redirect(session.url)
    
    # Verify plan exists (using slug aka plan_name in URL path which we haven't changed yet, assuming it maps to slug)
    from django.shortcuts import get_object_or_404
    from core.saas_models import PricingPlan
    
    # Try looking up by slug first, falling back if needed
    plan = PricingPlan.objects.filter(slug=plan_name).first()
    if not plan:
         # Fallback search by name
         plan = PricingPlan.objects.filter(name__iexact=plan_name).first()
    
    if not plan:
         # Hard fail if invalid plan
         from django.contrib import messages
         messages.error(request, "Invalid plan selected.")
         return redirect('billing')

    # Mocking: Direct redirect to success with plan slug
    return render(request, 'core/upgrade_confirm.html', {'plan': plan})

@login_required
def payment_success(request, plan_name):
    """
    Simulates Stripe Success Callback / Webhook.
    Updates the organization's billing profile.
    """
    org = request.user.owned_organizations.first()
    if org:
        from core.saas_models import PricingPlan
        plan = PricingPlan.objects.filter(slug=plan_name).first()
        if not plan:
            plan = PricingPlan.objects.filter(name__iexact=plan_name).first()

        profile, created = BillingProfile.objects.get_or_create(organization=org)
        
        if plan:
            profile.plan = plan
            profile.save()
            # Add success message
            from django.contrib import messages
            messages.success(request, f"Successfully upgraded to our {plan.name} Plan! Thank you for your business.")
        else:
             from django.contrib import messages
             messages.error(request, "Plan not found during activation.")
        
    return redirect('billing')

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
def remove_member(request, membership_id):
    """
    Remove a member from the current organization.
    Only the organization owner can remove other members;
    members can remove themselves (leave team).
    """
    from django.contrib import messages
    from core.models import Membership
    
    membership = get_object_or_404(Membership, id=membership_id)
    org = membership.organization
    
    # Determine acting user's organization (same logic as team_list)
    user_org = request.user.owned_organizations.first()
    if not user_org:
        m = request.user.memberships.first()
        user_org = m.organization if m else None
    
    # Safety: organization must match
    if not user_org or user_org != org:
        messages.error(request, "You don't have permission to change this member.")
        return redirect('team_list')
    
    # Prevent removing the organization owner from their own org
    if membership.user_id == org.owner_id:
        messages.warning(request, "You cannot remove the organization owner.")
        return redirect('team_list')
    
    # Allow owner to remove anyone; members can remove themselves
    if request.user == org.owner or request.user == membership.user:
        membership.delete()
        if request.user == membership.user:
            messages.success(request, "You have left this team.")
        else:
            messages.success(request, f"{membership.user.email} has been removed from the team.")
    else:
        messages.error(request, "You don't have permission to remove this member.")
    
    return redirect('team_list')

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
                    login_url = request.build_absolute_uri('/core/login/')
                    try:
                        send_mail(
                            subject=f"You've been invited to {org.name} on ProjectFlow",
                            message=f"Hi {user_to_invite.username},\n\n{request.user.username} has invited you to join their team '{org.name}'.\n\nLog in here: {login_url}",
                            from_email='system@projectflow.com',
                            recipient_list=[email],
                            fail_silently=True,
                            html_message=f'Hi {user_to_invite.username},<br><br>{request.user.username} has invited you to join their team <strong>{org.name}</strong>.<br><br><a href="{login_url}" style="background-color:#6366f1;color:white;padding:10px 20px;text-decoration:none;border-radius:5px;">Accept Invitation</a>'
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
                signup_url = request.build_absolute_uri('/core/signup/')
                send_mail(
                    subject=f"You've been invited to ProjectFlow",
                    message=f"Hi,\n\n{request.user.username} wants you to join ProjectFlow to collaborate on '{org.name}'.\n\nSign up here: {signup_url}",
                    from_email='system@projectflow.com',
                    recipient_list=[email],
                    fail_silently=True,
                    html_message=f'Hi,<br><br>{request.user.username} wants you to join ProjectFlow to collaborate on <strong>{org.name}</strong>.<br><br><a href="{signup_url}" style="background-color:#6366f1;color:white;padding:10px 20px;text-decoration:none;border-radius:5px;">Sign Up Now</a>'
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
