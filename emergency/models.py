from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_volunteer = models.BooleanField(default=False)
    location = models.CharField(max_length=100, blank=True, null=True)  # e.g., "40.7128,-74.0060" for NYC

    def __str__(self):
        return self.user.username
