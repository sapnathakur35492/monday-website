from django.urls import path
from . import views

urlpatterns = [
    path('board/<int:board_id>/automations/', views.automation_list, name='automation_list'),
    path('board/<int:board_id>/automations/new/', views.create_rule, name='create_rule'),
    path('board/<int:board_id>/automations/<int:rule_id>/delete/', views.delete_rule, name='delete_rule'),
    path('board/<int:board_id>/automations/<int:rule_id>/edit/', views.edit_rule, name='edit_rule'),
    path('board/<int:board_id>/automations/<int:rule_id>/toggle/', views.toggle_rule, name='toggle_rule'),
    path('board/<int:board_id>/automations/history/', views.run_history, name='run_history'),
    
    # HTMX endpoints for dynamic builder
    path('board/<int:board_id>/automations/config/trigger/', views.get_trigger_config_form, name='get_trigger_config_form'),
    path('board/<int:board_id>/automations/config/action/', views.get_action_config_form, name='get_action_config_form'),
]

