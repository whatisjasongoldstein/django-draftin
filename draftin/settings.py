from django.conf import settings

DRAFTIN_SETTINGS = {
    "MAX_IMAGE_SIZE": [900, 1000],
}

DRAFTIN_SETTINGS.update(getattr(settings, "DRAFTIN_SETTINGS", {}))