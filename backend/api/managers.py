from django.db import models


class TaskManager(models.Manager):
    def by_status(self, status):
        return self.filter(status=status)

    def overdue(self):
        from django.utils import timezone
        return self.filter(
            deadline__lt=timezone.now().date(),
            status__in=['todo', 'in_progress']
        )

    def for_user(self, user):
        return self.filter(assigned_to=user)