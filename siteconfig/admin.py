from django.contrib import admin
from .models import FeatureFlag, UIText


@admin.register(FeatureFlag)
class FeatureFlagAdmin(admin.ModelAdmin):
    list_display = ("key", "enabled", "updated_at", "note")
    list_filter = ("enabled",)
    search_fields = ("key", "note")
    ordering = ("key",)


@admin.register(UIText)
class UITextAdmin(admin.ModelAdmin):
    list_display = ("key", "updated_at", "note")
    search_fields = ("key", "ru", "kz", "note")
    ordering = ("key",)
