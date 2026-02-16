from django.contrib import admin
from .models import Ticket

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("number", "service", "category", "desk", "fio", "phone", "status", "created_at")
    list_filter = ("service", "status", "category", "desk")
    search_fields = ("number", "fio", "phone")
