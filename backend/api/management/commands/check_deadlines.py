from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from api.models import Task, Notification, TeamMember


class Command(BaseCommand):
    help = 'Send deadline notifications'

    def handle(self, *args, **kwargs):
        tomorrow = timezone.now().date() + timedelta(days=1)
        tasks = Task.objects.filter(
            deadline=tomorrow,
            status__in=['todo', 'in_progress', 'review']
        )
        for task in tasks:
            members = TeamMember.objects.filter(team=task.team)
            for member in members:
                already_notified = Notification.objects.filter(
                    user=member.user,
                    task=task,
                    type='deadline'
                ).exists()
                if not already_notified:
                    Notification.objects.create(
                        user=member.user,
                        type='deadline',
                        message=f'Deadline tomorrow: "{task.title}"',
                        task=task,
                        team=task.team
                    )
        self.stdout.write(f'Sent deadline notifications for {tasks.count()} tasks')