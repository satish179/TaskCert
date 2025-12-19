from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ExamResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exam = models.CharField(max_length=255)
    score = models.FloatField()
    passed = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.exam}"

class Certificate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exam = models.CharField(max_length=255)
    institution_name = models.CharField(max_length=255)
    certificate_id = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Certificate {self.certificate_id} for {self.user.username}"