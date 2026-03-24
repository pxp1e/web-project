from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from .models import Subject, Team, Task, Comment
from .serializers import (
    LoginSerializer, TaskStatusUpdateSerializer,
    UserSerializer, SubjectSerializer, TeamSerializer,
    TaskSerializer, CommentSerializer
)


#FBV

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
    tasks = Task.objects.for_user(request.user)
    return Response(TaskSerializer(tasks, many=True).data)


@api_view(['GET'])
def dashboard_stats(request):
    user_tasks = Task.objects.for_user(request.user)
    return Response({
        'total': user_tasks.count(),
        'todo': user_tasks.by_status('todo').count(),
        'in_progress': user_tasks.by_status('in_progress').count(),
        'review': user_tasks.by_status('review').count(),
        'done': user_tasks.by_status('done').count(),
        'overdue': Task.objects.overdue().filter(assigned_to=request.user).count(),
    })


#CBV

class SubjectListCreateView(APIView):
    def get(self, request):
        subjects = Subject.objects.filter(created_by=request.user)
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
        subject.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TeamListCreateView(APIView):
    def get(self, request):
        teams = (Team.objects.filter(members=request.user) |
                 Team.objects.filter(created_by=request.user)).distinct()
        return Response(TeamSerializer(teams, many=True).data)

    def post(self, request):
        serializer = TeamSerializer(data=request.data)
        if serializer.is_valid():
            team = serializer.save(created_by=request.user)
            team.members.add(request.user)
            return Response(TeamSerializer(team).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TeamDetailView(APIView):
    def get(self, request, pk):
        team = get_object_or_404(Team, pk=pk)
        return Response(TeamSerializer(team).data)

    def put(self, request, pk):
        team = get_object_or_404(Team, pk=pk)
        serializer = TeamSerializer(team, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        team = get_object_or_404(Team, pk=pk)
        team.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TaskListCreateView(APIView):
    def get(self, request):
        team_id = request.query_params.get('team_id')
        if team_id:
            tasks = Task.objects.filter(team_id=team_id)
        else:
            tasks = Task.objects.filter(team__members=request.user).distinct()
        return Response(TaskSerializer(tasks, many=True).data)

    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            assigned_to_id = request.data.get('assigned_to_id')
            task = serializer.save(created_by=request.user)
            if assigned_to_id:
                task.assigned_to_id = assigned_to_id
                task.save()
            return Response(TaskSerializer(task).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskDetailView(APIView):
    def get(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        return Response(TaskSerializer(task).data)

    def put(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
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
            serializer.save(author=request.user, task=task)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)