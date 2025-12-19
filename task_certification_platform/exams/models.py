from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from tasks.models import Task

User = get_user_model()

class Exam(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    duration_minutes = models.PositiveIntegerField(default=60)
    passing_score = models.PositiveIntegerField(default=70)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tasks = models.ManyToManyField(Task, related_name='exams')

    def __str__(self):
        return self.title

    @property
    def total_questions(self):
        return self.questions.count()

    class Meta:
        verbose_name = 'Exam'
        verbose_name_plural = 'Exams'
        ordering = ['-created_at']


class Question(models.Model):
    QUESTION_TYPES = [
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('short_answer', 'Short Answer'),
    ]

    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    question_text = models.TextField()
    question_type = models.CharField(
        max_length=20,
        choices=QUESTION_TYPES,
        default='multiple_choice'
    )
    marks = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=0)
    explanation = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'

    def __str__(self):
        return f"{self.question_text[:50]}..."


class Choice(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='choices'
    )
    choice_text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Choice'
        verbose_name_plural = 'Choices'

    def __str__(self):
        return self.choice_text


class ExamAttempt(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='exam_attempts'
    )
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='attempts'
    )
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(null=True, blank=True)
    passed = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-start_time']
        verbose_name = 'Exam Attempt'
        verbose_name_plural = 'Exam Attempts'
        unique_together = ('user', 'exam', 'start_time')

    def __str__(self):
        return f"{self.user.username} - {self.exam.title} - {self.start_time}"

    @property
    def time_remaining(self):
        if not self.end_time:
            return None
        remaining = self.end_time - timezone.now()
        return max(remaining, timezone.timedelta(0))

    def calculate_score(self):
        total_questions = self.responses.count()
        if total_questions == 0:
            return 0
        correct_answers = self.responses.filter(is_correct=True).count()
        return (correct_answers / total_questions) * 100

    def complete_attempt(self):
        if not self.is_completed:
            self.score = self.calculate_score()
            self.passed = self.score >= self.exam.passing_score
            self.is_completed = True
            self.end_time = timezone.now()
            self.save()


class UserResponse(models.Model):
    attempt = models.ForeignKey(
        ExamAttempt,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='user_responses'
    )
    selected_choice = models.ForeignKey(
        'Choice',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    text_response = models.TextField(blank=True, null=True)
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('attempt', 'question')
        verbose_name = 'User Response'
        verbose_name_plural = 'User Responses'

    def __str__(self):
        return f"Response for {self.question} by {self.attempt.user}"

    def save(self, *args, **kwargs):
        # Update is_correct based on question type
        if self.question.question_type == 'multiple_choice' and self.selected_choice:
            self.is_correct = self.selected_choice.is_correct
        elif self.question.question_type == 'true_false' and self.selected_choice:
            self.is_correct = self.selected_choice.is_correct
        # For short_answer, manual grading is required
        
        super().save(*args, **kwargs)
        
        # Update the exam attempt score if the attempt is completed
        if self.attempt.is_completed:
            self.attempt.complete_attempt()
