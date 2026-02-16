from django.urls import path
from . import views

urlpatterns = [
    path('saas-admin/', views.admin_dashboard, name='saas_admin_dashboard'),
    path('signup/', views.signup_view, name='signup'),
    path('verify/<str:token>/', views.verify_email_view, name='verify_email'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('billing/', views.billing_dashboard, name='billing'),
    path('team/', views.team_list, name='team_list'),
    path('team/invite/', views.invite_member, name='invite_member'),
    path('team/remove/<int:membership_id>/', views.remove_member, name='remove_member'),
    path('profile/', views.profile_view, name='profile'),
    path('notifications/', views.notifications_view, name='notifications'),
]
