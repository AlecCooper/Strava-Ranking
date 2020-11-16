from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group, User

from .models import Ranking, Segment, Performance, Profile

# When membership of the group changes, we must create
# Preformances for the new user
@receiver(post_save, sender=Group)
def create_preformances(sender, instance, **kwargs):
    
    # Get users in group
    users = User.objects.filter(groups__name=instance.name)
    
    # Get the ranking
    ranking = Ranking.objects.get(name=instance.name)

    # Determine which user has no performances
    for user in users:
        
        if not Performance.objects.filter(owner=user).exists():
            
            # Create a performance for each segment in the ranking
            for segment in Segment.objects.filter(ranking=ranking):
                performance = Performance.create(user, segment)
                performance.save()

# For hooking a profile model to users when they are created/deleted
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()