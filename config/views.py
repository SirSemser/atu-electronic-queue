from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import FeatureFlag, UIText


@require_GET
def api_config(request):
    # flags
    flags = {f.key: bool(f.enabled) for f in FeatureFlag.objects.all()}

    # ui texts grouped by lang
    ui = {"ru": {}, "kz": {}, "en": {}}
    for row in UIText.objects.all():
        ui.setdefault(row.lang, {})
        ui[row.lang][row.key] = row.text

    return JsonResponse({
        "flags": flags,
        "ui": ui,
    })
