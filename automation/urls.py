from django.urls import path
from . import views

urlpatterns = [
    path('board/<int:board_id>/automations/', views.automation_list, name='automation_list'),
    path('board/<int:board_id>/automations/new/', views.create_rule, name='create_rule'),
]
