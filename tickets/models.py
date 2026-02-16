from django.db import models

class Ticket(models.Model):
    SERVICE_CHOICES = [
        ("consultation", "Consultation"),
        ("admission", "Admission"),
        ("contest", "Grant Contest"),
        ("online", "Online Admission"),
    ]

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("ACCEPTED", "Accepted"),
        ("DONE", "Done"),
        ("CANCELLED", "Cancelled"),
    ]

    number = models.CharField(max_length=20, unique=True, blank=True)  # ✅ blank=True
    service = models.CharField(max_length=20, choices=SERVICE_CHOICES)
    category = models.CharField(max_length=50, blank=True, default="")
    pay_type = models.CharField(max_length=20, blank=True, default="")
    profile = models.CharField(max_length=50, blank=True, default="")
    track = models.CharField(max_length=20, blank=True, default="")
    desk = models.IntegerField(null=True, blank=True)

    fio = models.CharField(max_length=200)
    phone = models.CharField(max_length=30)

    social_category = models.CharField(max_length=50, blank=True, default="")

    is_online = models.BooleanField(default=False)
    meeting_type = models.CharField(max_length=20, blank=True, default="")
    whatsapp = models.CharField(max_length=30, blank=True, default="")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.number} ({self.service})"
