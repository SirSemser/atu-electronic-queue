from django.db import models
from django.conf import settings

class OperatorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="operator_profile")
    desk = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.user.username} (desk {self.desk})"


class OperatorLog(models.Model):
    operator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    desk = models.PositiveIntegerField()
    action = models.CharField(max_length=32)
    ticket_number = models.CharField(max_length=32, blank=True, null=True)
    meta = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.created_at} {self.operator} {self.action}"
