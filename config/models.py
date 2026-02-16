from django.db import models


class FeatureFlag(models.Model):
    key = models.CharField(max_length=120, unique=True)
    enabled = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.key} = {'ON' if self.enabled else 'OFF'}"


class UIText(models.Model):
    LANG_CHOICES = (
        ("ru", "Russian"),
        ("kz", "Kazakh"),
        ("en", "English"),
    )

    key = models.CharField(max_length=120)
    lang = models.CharField(max_length=2, choices=LANG_CHOICES)
    text = models.TextField(blank=True, default="")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("key", "lang")
        indexes = [
            models.Index(fields=["key", "lang"]),
        ]

    def __str__(self):
        return f"{self.key} [{self.lang}]"
