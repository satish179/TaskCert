from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Submission, Result
from .gamification import award_points

@receiver(post_save, sender=Submission)
def award_points_for_submission(sender, instance, created, **kwargs):
    if instance.status == 'approved':
        # Check if points were already awarded for this specific submission to avoid duplicates?
        # For simplicity, we assume 'approved' happens once. 
        # A more robust system would need a dedicated 'PointTransaction' model.
        
        # Award 10 points for a task submission approval
        award_points(instance.submitted_by, 10, f"Task Approved: {instance.task.name}")

@receiver(post_save, sender=Result)
def award_points_for_exam(sender, instance, created, **kwargs):
    print(f"Signal failed: {instance}")
    if instance.passed:
        # Award 50 points for passing an exam
        award_points(instance.user, 50, f"Exam Passed: {instance.exam.name}")
