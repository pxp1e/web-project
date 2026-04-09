from django.urls import path
from . import views

urlpatterns = [
    path('auth/login/', views.login_view, name='login'),
    path('auth/register/', views.register_view, name='register'),
    path('auth/logout/', views.logout_view, name='logout'),

    #Dashboard
    path('dashboard/stats/', views.dashboard_stats, name='dashboard-stats'),
    path('tasks/my/', views.my_tasks, name='my-tasks'),
    path('tasks/update-status/', views.update_task_status, name='update-task-status'),

    #Subjects 
    path('subjects/', views.SubjectListCreateView.as_view(), name='subjects'),
    path('subjects/<int:pk>/', views.SubjectDetailView.as_view(), name='subject-detail'),

    #Teams
    path('teams/', views.TeamListCreateView.as_view(), name='teams'),
    path('teams/<int:pk>/', views.TeamDetailView.as_view(), name='team-detail'),

    #Tasks
    path('tasks/', views.TaskListCreateView.as_view(), name='tasks'),
    path('tasks/<int:pk>/', views.TaskDetailView.as_view(), name='task-detail'),

    #Comments
    path('tasks/<int:task_id>/comments/', views.CommentListCreateView.as_view(), name='comments'),
]