from django.db import models
from django.contrib.postgres.fields import ArrayField
import uuid

class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.TextField(blank=True, null=True)
    google_refresh_token = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email or str(self.id)

class Preference(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='preferences')
    preferred_days = ArrayField(models.TextField(), blank=True, null=True)
    preferred_times = ArrayField(models.TextField(), blank=True, null=True)
    buffer_minutes = models.IntegerField(blank=True, null=True)
    tone = models.TextField(blank=True, null=True)
    style = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Preferences for {self.user.email if self.user else self.user_id}"

# Create your models here.
