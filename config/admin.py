from django.contrib import admin
from .models import FeatureFlag, UIText


@admin.register(FeatureFlag)
class FeatureFlagAdmin(admin.ModelAdmin):
    list_display = ("key", "enabled", "updated_at")
    list_editable = ("enabled",)
    search_fields = ("key",)
    ordering = ("key",)


@admin.register(UIText)
class UITextAdmin(admin.ModelAdmin):
    list_display = ("key", "lang", "short_text", "updated_at")
    list_filter = ("lang",)
    search_fields = ("key", "text")
    ordering = ("key", "lang")

    def short_text(self, obj):
        t = (obj.text or "").strip()
        return (t[:60] + "…") if len(t) > 60 else t
