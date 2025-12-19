from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    MENTOR = 'mentor'
    LEARNER = 'learner'
    ADMIN = 'admin'
    
    ROLE_CHOICES = [
        (MENTOR, 'Mentor'),
        (LEARNER, 'Learner'),
        (ADMIN, 'Admin'),
    ]
    
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default=LEARNER,
    )
    mentor = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': MENTOR},
        related_name='mentees'
    )
    phone = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"

    def is_mentor(self):
        return self.role == self.MENTOR

    def is_learner(self):
        return self.role == self.LEARNER

    def is_admin_user(self):
        return self.role == self.ADMIN or self.is_superuser

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
