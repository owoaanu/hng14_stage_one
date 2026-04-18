import uuid6
from django.db import models
from django.utils import timezone


class Profile(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid6.uuid7,
        editable=False,
        help_text="Unique ID in UUID v7.",
    )
    name = models.CharField(max_length=255, db_index=True)
    gender = models.CharField(max_length=50, null=True, blank=True)
    gender_probability = models.FloatField(null=True, blank=True)
    sample_size = models.IntegerField(null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    age_group = models.CharField(max_length=50, null=True)
    country_id = models.CharField(max_length=10, null=True)
    country_probability = models.FloatField(null=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return f"{self.name} ({self.id})"

    class Meta:
        ordering = ["-created_at"]
