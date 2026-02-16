from .models import FeatureFlag


def is_enabled(key: str, default: bool = True) -> bool:
    """
    Feature flags from DB.
    If flag not found => default
    """
    try:
        obj = FeatureFlag.objects.get(key=key)
        return bool(obj.enabled)
    except FeatureFlag.DoesNotExist:
        return bool(default)
