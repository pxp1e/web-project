from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from .models import Subject, Team, Task, Comment, TeamMember, Notification
from .serializers import (
    LoginSerializer, TaskStatusUpdateSerializer,
    UserSerializer, SubjectSerializer, TeamSerializer,
    TaskSerializer, CommentSerializer, TeamMemberSerializer,
    NotificationSerializer
)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    user = authenticate(
        username=serializer.validated_data['username'],
        password=serializer.validated_data['password']
    )
    if not user:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    refresh = RefreshToken.for_user(user)
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': UserSerializer(user).data
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email', '')
    first_name = request.data.get('first_name', '')
    last_name = request.data.get('last_name', '')
    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already taken'}, status=status.HTTP_400_BAD_REQUEST)
    user = User.objects.create_user(
        username=username, password=password,
        email=email, first_name=first_name, last_name=last_name
    )
    refresh = RefreshToken.for_user(user)
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': UserSerializer(user).data
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def logout_view(request):
    try:
        refresh_token = request.data.get('refresh')
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': 'Logged out successfully'})
    except Exception:
        return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
def update_task_status(request):
    serializer = TaskStatusUpdateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    task = get_object_or_404(Task, id=serializer.validated_data['task_id'])
    task.status = serializer.validated_data['status']
    task.save()
    return Response(TaskSerializer(task).data)


@api_view(['GET'])
def my_tasks(request):
    from django.db.models import Case, When, IntegerField
    tasks = Task.objects.filter(assigned_to=request.user).exclude(status='done').annotate(
        priority_order=Case(
            When(priority='high', then=1),
            When(priority='medium', then=2),
            When(priority='low', then=3),
            default=4,
            output_field=IntegerField()
        )
    ).order_by('priority_order', 'deadline')
    return Response(TaskSerializer(tasks, many=True).data)


@api_view(['GET'])
def dashboard_stats(request):
    from django.utils import timezone
    user_tasks = Task.objects.filter(assigned_to=request.user)
    return Response({
        'total': user_tasks.count(),
        'todo': user_tasks.filter(status='todo').count(),
        'in_progress': user_tasks.filter(status='in_progress').count(),
        'review': user_tasks.filter(status='review').count(),
        'done': user_tasks.filter(status='done').count(),
        'overdue': user_tasks.filter(
            deadline__lt=timezone.now().date(),
            status__in=['todo', 'in_progress']
        ).count(),
    })


@api_view(['GET'])
def search_users(request):
    query = request.query_params.get('q', '')
    if len(query) < 2:
        return Response([])
    users = User.objects.filter(username__icontains=query)[:10]
    return Response(UserSerializer(users, many=True).data)


class SubjectListCreateView(APIView):
    def get(self, request):
        subjects = Subject.objects.all()
        return Response(SubjectSerializer(subjects, many=True).data)

    def post(self, request):
        serializer = SubjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubjectDetailView(APIView):
    def get(self, request, pk):
        subject = get_object_or_404(Subject, pk=pk)
        return Response(SubjectSerializer(subject).data)

    def put(self, request, pk):
        subject = get_object_or_404(Subject, pk=pk)
        serializer = SubjectSerializer(subject, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        subject = get_object_or_404(Subject, pk=pk)
        if subject.is_system:
            return Response({'error': 'Cannot delete system subject'}, status=status.HTTP_403_FORBIDDEN)
        subject.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TeamListCreateView(APIView):
    def get(self, request):
        memberships = TeamMember.objects.filter(user=request.user)
        teams = Team.objects.filter(memberships__in=memberships).distinct()
        serializer = TeamSerializer(teams, many=True)
        data = serializer.data
        for i, team in enumerate(teams):
            membership = memberships.filter(team=team).first()
            data[i]['my_role'] = membership.role if membership else 'member'
        return Response(data)

    def post(self, request):
        serializer = TeamSerializer(data=request.data)
        if serializer.is_valid():
            team = serializer.save(created_by=request.user)
            TeamMember.objects.create(user=request.user, team=team, role='admin')
            data = TeamSerializer(team).data
            data['my_role'] = 'admin'
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TeamDetailView(APIView):
    def get(self, request, pk):
        team = get_object_or_404(Team, pk=pk)
        return Response(TeamSerializer(team).data)

    def put(self, request, pk):
        team = get_object_or_404(Team, pk=pk)
        membership = TeamMember.objects.filter(team=team, user=request.user).first()
        if not membership or membership.role != 'admin':
            return Response({'error': 'Only admin can edit team'}, status=status.HTTP_403_FORBIDDEN)
        serializer = TeamSerializer(team, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        team = get_object_or_404(Team, pk=pk)
        membership = TeamMember.objects.filter(team=team, user=request.user).first()
        if not membership or membership.role != 'admin':
            return Response({'error': 'Only admin can delete team'}, status=status.HTTP_403_FORBIDDEN)
        team.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TeamMemberView(APIView):
    def post(self, request, pk):
        team = get_object_or_404(Team, pk=pk)
        membership = TeamMember.objects.filter(team=team, user=request.user).first()
        if not membership or membership.role != 'admin':
            return Response({'error': 'Only admin can add members'}, status=status.HTTP_403_FORBIDDEN)
        username = request.data.get('username')
        user = User.objects.filter(username=username).first()
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        if TeamMember.objects.filter(team=team, user=user).exists():
            return Response({'error': 'User already in team'}, status=status.HTTP_400_BAD_REQUEST)
        TeamMember.objects.create(team=team, user=user, role='member')
        Notification.objects.create(
            user=user,
            type='comment',
            message=f'You were added to team "{team.name}"',
            team=team
        )
        return Response(TeamSerializer(team).data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        team = get_object_or_404(Team, pk=pk)
        membership = TeamMember.objects.filter(team=team, user=request.user).first()
        if not membership or membership.role != 'admin':
            return Response({'error': 'Only admin can remove members'}, status=status.HTTP_403_FORBIDDEN)
        user_id = request.data.get('user_id')
        member = get_object_or_404(TeamMember, team=team, user_id=user_id)
        member.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TaskListCreateView(APIView):
    def get(self, request):
        team_id = request.query_params.get('team_id')
        if team_id:
            tasks = Task.objects.filter(team_id=team_id)
        else:
            tasks = Task.objects.filter(
                team__memberships__user=request.user
            ).distinct()
        return Response(TaskSerializer(tasks, many=True).data)

    def post(self, request):
        membership = TeamMember.objects.filter(
            team_id=request.data.get('team'),
            user=request.user
        ).first()
        if not membership or membership.role != 'admin':
            return Response({'error': 'Only admin can create tasks'}, status=status.HTTP_403_FORBIDDEN)
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            assigned_to_id = request.data.get('assigned_to_id')
            task = serializer.save(created_by=request.user)
            if assigned_to_id:
                task.assigned_to_id = assigned_to_id
            else:
                task.assigned_to = request.user
            task.save()
            if task.assigned_to and task.assigned_to != request.user:
                Notification.objects.create(
                    user=task.assigned_to,
                    type='comment',
                    message=f'You were assigned to task "{task.title}"',
                    task=task,
                    team=task.team
                )
            members = TeamMember.objects.filter(team=task.team).exclude(user=request.user)
            for member in members:
                Notification.objects.create(
                    user=member.user,
                    type='comment',
                    message=f'New task created: "{task.title}"',
                    task=task,
                    team=task.team
                )
            return Response(TaskSerializer(task).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskDetailView(APIView):
    def get(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        return Response(TaskSerializer(task).data)

    def put(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        membership = TeamMember.objects.filter(team=task.team, user=request.user).first()
        if not membership:
            return Response({'error': 'No permission'}, status=status.HTTP_403_FORBIDDEN)
        if membership.role == 'member':
            if task.assigned_to != request.user:
                return Response({'error': 'You can only edit your own tasks'}, status=status.HTTP_403_FORBIDDEN)
            allowed_fields = {'status', 'description'}
            for field in request.data:
                if field not in allowed_fields:
                    return Response({'error': f'Members cannot change {field}'}, status=status.HTTP_403_FORBIDDEN)
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        membership = TeamMember.objects.filter(team=task.team, user=request.user).first()
        if task.created_by != request.user and (not membership or membership.role != 'admin'):
            return Response({'error': 'Only admin can delete tasks'}, status=status.HTTP_403_FORBIDDEN)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentListCreateView(APIView):
    def get(self, request, task_id):
        comments = Comment.objects.filter(task_id=task_id)
        return Response(CommentSerializer(comments, many=True).data)

    def post(self, request, task_id):
        task = get_object_or_404(Task, pk=task_id)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            comment = serializer.save(author=request.user, task=task)
            members = TeamMember.objects.filter(team=task.team).exclude(user=request.user)
            for member in members:
                Notification.objects.create(
                    user=member.user,
                    type='comment',
                    message=f'{request.user.username} commented on "{task.title}"',
                    task=task,
                    team=task.team
                )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentDetailView(APIView):
    def delete(self, request, task_id, comment_id):
        comment = get_object_or_404(Comment, pk=comment_id, task_id=task_id)
        if comment.author != request.user:
            return Response({'error': 'You can only delete your own comments'}, status=status.HTTP_403_FORBIDDEN)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class NotificationListView(APIView):
    def get(self, request):
        notifications = Notification.objects.filter(
            user=request.user
        ).order_by('-created_at')[:20]
        return Response(NotificationSerializer(notifications, many=True).data)

    def post(self, request):
        Notification.objects.filter(user=request.user).update(is_read=True)
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({'count': count})


class NotificationCountView(APIView):
    def get(self, request):
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({'count': count})


class NotificationReadView(APIView):
    def patch(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, user=request.user)
        notification.is_read = True
        notification.save()
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({'count': count})
    

class CommentLikeView(APIView):
    def post(self, request, comment_id):
        from .models import CommentLike
        comment = get_object_or_404(Comment, pk=comment_id)
        like, created = CommentLike.objects.get_or_create(
            comment=comment, user=request.user
        )
        if not created:
            like.delete()
            return Response({'liked': False, 'likes_count': comment.likes.count()})
        if comment.author != request.user:
            Notification.objects.create(
                user=comment.author,
                type='comment',
                message=f'{request.user.username} liked your comment on "{comment.task.title}"',
                task=comment.task,
                team=comment.task.team
            )
        return Response({'liked': True, 'likes_count': comment.likes.count()})
