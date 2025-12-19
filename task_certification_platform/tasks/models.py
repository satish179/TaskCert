from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class Task(models.Model):
    PENDING = 'pending'
    IN_PROGRESS = 'in_progress'
    SUBMITTED = 'submitted'
    COMPLETED = 'completed'
    REJECTED = 'rejected'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (IN_PROGRESS, 'In Progress'),
        (SUBMITTED, 'Submitted for Review'),
        (COMPLETED, 'Completed'),
        (REJECTED, 'Rejected'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assigned_tasks',
        limit_choices_to={'role': User.LEARNER}
    )
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_tasks',
        limit_choices_to={'role__in': [User.ADMIN, User.MENTOR]}
    )
    due_date = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    remarks = models.TextField(blank=True, null=True)
    submission_notes = models.TextField(blank=True, null=True)
    submission_file = models.FileField(upload_to='task_submissions/', null=True, blank=True)
    next_task = models.OneToOneField(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='previous_task'
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"

    def is_overdue(self):
        return timezone.now() > self.due_date and self.status != self.COMPLETED

    def save(self, *args, **kwargs):
        if self.status == self.COMPLETED and not self.completed_at:
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)

    def get_next_task(self):
        if hasattr(self, 'next_task') and self.next_task:
            return self.next_task
        return None

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('task-detail', kwargs={'pk': self.pk})
