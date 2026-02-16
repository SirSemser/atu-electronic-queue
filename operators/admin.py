from django.contrib import admin
from .models import OperatorProfile

@admin.register(OperatorProfile)
class OperatorProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "desk")
    search_fields = ("user__username",)
    list_filter = ("desk",)
