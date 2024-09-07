from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
# Create your models here.

class TrackedTime(models.Model):
    user = models.ForeignKey(User, related_name="trackedtimes", on_delete=models.CASCADE)
    year = models.IntegerField(editable=False, blank=False, default=datetime.now().year)
    month = models.IntegerField(editable=False, blank=False, default=datetime.now().month)
    day = models.IntegerField(editable=False, blank=False, default=datetime.now().day)
    apps = models.JSONField()

    class Meta:
        verbose_name = "TrackedTime"
        verbose_name_plural = "TrackedTimes"
    def __str__(self):
        return f"Tracked time(d-{self.day}, m-{self.month}, y-{self.year}) for user id:{self.user.id}"

