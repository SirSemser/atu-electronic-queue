from django.db import models


class FeatureFlag(models.Model):
    """
    Флаги включения/выключения функций.
    key пример: app.admission.enabled, operator.done.enabled
    """
    key = models.CharField(max_length=120, unique=True)
    enabled = models.BooleanField(default=True)
    note = models.CharField(max_length=255, blank=True, default="")

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.key} = {self.enabled}"


class UIText(models.Model):
    """
    Редактируемые тексты RU/KZ.
    key пример: btn.admission.title, btn.admission.desc, msg.service_disabled
    """
    key = models.CharField(max_length=120, unique=True)

    ru = models.TextField(blank=True, default="")
    kz = models.TextField(blank=True, default="")

    note = models.CharField(max_length=255, blank=True, default="")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.key
