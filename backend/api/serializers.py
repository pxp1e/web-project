from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Subject, Team, Task, Comment, TeamMember, Notification
from .models import Subject, Team, Task, Comment, TeamMember, CommentLike


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


class TeamMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = TeamMember
        fields = ['id', 'user', 'role', 'joined_at']
        read_only_fields = ['joined_at']


class SubjectSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Subject
        fields = ['id', 'name', 'code', 'semester', 'created_by', 'created_at']
        read_only_fields = ['created_by', 'created_at']


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    author_role = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'task', 'author', 'author_role', 'text', 'likes_count', 'is_liked', 'created_at']
        read_only_fields = ['author', 'created_at', 'task']

    def get_author_role(self, obj):
        membership = TeamMember.objects.filter(
            user=obj.author,
            team=obj.task.team
        ).first()
        return membership.role if membership else 'member'

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False
    
class TeamSerializer(serializers.ModelSerializer):
    memberships = TeamMemberSerializer(many=True, read_only=True)
    created_by = UserSerializer(read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = ['id', 'name', 'subject', 'subject_name', 'memberships', 'member_count', 'created_by', 'created_at']
        read_only_fields = ['created_by', 'created_at']

    def get_member_count(self, obj):
        return obj.memberships.count()


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

class NotificationSerializer(serializers.ModelSerializer):
    task_title = serializers.CharField(source='task.title', read_only=True)
    team_id = serializers.IntegerField(source='team.id', read_only=True)
    task_id = serializers.IntegerField(source='task.id', read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'type', 'message', 'task_id', 'task_title', 'team_id', 'is_read', 'created_at']
        read_only_fields = ['created_at']