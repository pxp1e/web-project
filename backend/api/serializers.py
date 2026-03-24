from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Subject, Team, Task, Comment


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class TaskStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['todo', 'in_progress', 'review', 'done'])
    task_id = serializers.IntegerField()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class SubjectSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Subject
        fields = ['id', 'name', 'code', 'semester', 'created_by', 'created_at']
        read_only_fields = ['created_by', 'created_at']


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'task', 'author', 'text', 'created_at']
        read_only_fields = ['author', 'created_at']


class TeamSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True, read_only=True)
    created_by = UserSerializer(read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)

    class Meta:
        model = Team
        fields = ['id', 'name', 'subject', 'subject_name', 'members', 'created_by', 'created_at']
        read_only_fields = ['created_by', 'created_at']


class TaskSerializer(serializers.ModelSerializer):
    assigned_to = UserSerializer(read_only=True)
    assigned_to_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    created_by = UserSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'priority',
            'deadline', 'team', 'team_name', 'assigned_to', 'assigned_to_id',
            'created_by', 'comments', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']