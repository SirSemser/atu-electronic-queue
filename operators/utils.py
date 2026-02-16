from .models import FeatureFlag

def is_enabled(key: str, default: bool = True) -> bool:
    """
    True/False по ключу флага.
    Если записи нет — возвращаем default (чтобы ничего не ломалось).
    """
    try:
        f = FeatureFlag.objects.only("enabled").get(key=key)
        return bool(f.enabled)
    except FeatureFlag.DoesNotExist:
        return default
