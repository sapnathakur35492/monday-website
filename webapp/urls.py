from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('my-work/', views.my_work_view, name='my_work'),
    path('workspace/create/', views.create_workspace, name='create_workspace'),
    path('workspace/<int:workspace_id>/board/create/', views.create_board, name='create_board'),
    path('board/<int:board_id>/', views.board_detail, name='board_detail'),
    path('group/<int:group_id>/add_item/', views.add_item, name='add_item'),
    path('item/<int:item_id>/update/<int:col_id>/', views.update_status, name='update_status'),
    path('board/<int:board_id>/kanban/', views.kanban_view, name='board_kanban'),
    path('board/<int:board_id>/calendar/', views.calendar_view, name='board_calendar'),
    path('board/<int:board_id>/gantt/', views.gantt_view, name='board_gantt'),
    path('search/', views.global_search, name='global_search'),
    path('api/update-order/', views.update_item_order, name='update_item_order'),
    path('item/<int:item_id>/details/', views.get_item_details, name='get_item_details'),
    path('item/<int:item_id>/update/post/', views.post_item_update, name='post_item_update'),
    path('board/<int:board_id>/add_column/', views.add_column, name='add_column'),
    path('board/<int:board_id>/add_group/', views.add_group, name='add_group'),
    path('board/<int:board_id>/group/<int:group_id>/delete/', views.delete_group, name='delete_group'),
    path('board/group/update_title/', views.update_group_title, name='update_group_title'),
    path('board/<int:board_id>/item/<int:item_id>/delete/', views.delete_item, name='delete_item'),
]

