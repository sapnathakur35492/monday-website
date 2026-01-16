from django.contrib import admin
from django.urls import path, include
from core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Auth & Billing (Root)
    path('login/', core_views.login_view, name='login'),
    path('signup/', core_views.signup_view, name='signup'),
    path('logout/', core_views.logout_view, name='logout'),
    path('billing/', core_views.billing_dashboard, name='billing'),
    
    # Apps
    path('', include('marketing.urls')),
    path('core/', include('core.urls')),
    path('app/', include('webapp.urls')),
    path('automation/', include('automation.urls')),
]
