from django.urls import path
from . import views

urlpatterns = [
    path('board/<int:board_id>/automations/', views.automation_list, name='automation_list'),
    path('board/<int:board_id>/automations/new/', views.create_rule, name='create_rule'),
    path('board/<int:board_id>/automations/<int:rule_id>/delete/', views.delete_rule, name='delete_rule'),
    path('board/<int:board_id>/automations/<int:rule_id>/edit/', views.edit_rule, name='edit_rule'),
]
