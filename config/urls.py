from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Auth & Billing (Root)
    path('login/', core_views.login_view, name='login'),
    path('signup/', core_views.signup_view, name='signup'),
    path('logout/', core_views.logout_view, name='logout'),
    
    # Password Reset
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='core/password_reset_form.html',
        extra_email_context={'domain': 'amjim.com', 'site_name': 'ProjectFlow', 'protocol': 'https'}
    ), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='core/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='core/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='core/password_reset_complete.html'), name='password_reset_complete'),

    path('billing/', core_views.billing_dashboard, name='billing'),
    path('billing/upgrade/<str:plan_name>/', core_views.upgrade_plan, name='upgrade_plan'),
    path('billing/success/<str:plan_name>/', core_views.payment_success, name='payment_success'),
    
    # Apps
    path('', include('marketing.urls')),
    path('core/', include('core.urls')),
    path('app/', include('webapp.urls')),
    path('automation/', include('automation.urls')),
]
