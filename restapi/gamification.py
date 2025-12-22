from django.db.models import F
from .models import CustomUser, UserActivityLog

def award_points(user, points, description):
    """
    Awards points to a user and logs the activity.
    """
    if points <= 0:
        return

    # Atomic update to avoid race conditions
    CustomUser.objects.filter(pk=user.pk).update(points=F('points') + points)
    
    # Refresh user instance to get updated points if needed immediately after
    user.refresh_from_db()
    
    # Log the activity (optional, but good for tracking)
    # We can reuse UserActivityLog or create a new PointLog
    # For now, let's append to UserActivityLog if appropriate or just print
    print(f"Awarded {points} points to {user.username} for: {description}")
