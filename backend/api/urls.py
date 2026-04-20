from django.urls import path
from . import views

urlpatterns = [
   
    path('auth/login/', views.login_view, name='login'),
    path('auth/register/', views.register_view, name='register'),
    path('auth/logout/', views.logout_view, name='logout'),


    path('dashboard/stats/', views.dashboard_stats, name='dashboard-stats'),
    path('tasks/my/', views.my_tasks, name='my-tasks'),
    path('tasks/update-status/', views.update_task_status, name='update-task-status'),

  
    path('users/search/', views.search_users, name='search-users'),

  
    path('subjects/', views.SubjectListCreateView.as_view(), name='subjects'),
    path('subjects/<int:pk>/', views.SubjectDetailView.as_view(), name='subject-detail'),

  
    path('teams/', views.TeamListCreateView.as_view(), name='teams'),
    path('teams/<int:pk>/', views.TeamDetailView.as_view(), name='team-detail'),
    path('teams/<int:pk>/members/', views.TeamMemberView.as_view(), name='team-members'),


    path('tasks/', views.TaskListCreateView.as_view(), name='tasks'),
    path('tasks/<int:pk>/', views.TaskDetailView.as_view(), name='task-detail'),

   
    path('tasks/<int:task_id>/comments/', views.CommentListCreateView.as_view(), name='comments'),
    path('tasks/<int:task_id>/comments/<int:comment_id>/', views.CommentDetailView.as_view(), name='comment-detail'),

    path('notifications/', views.NotificationListView.as_view(), name='notifications'),
    path('notifications/count/', views.NotificationCountView.as_view(), name='notifications-count'),
    path('notifications/<int:pk>/read/', views.NotificationReadView.as_view(), name='notification-read'),

    path('comments/<int:comment_id>/like/', views.CommentLikeView.as_view(), name='comment-like'),
]