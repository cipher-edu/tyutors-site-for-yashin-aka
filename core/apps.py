from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class LearningPlatformConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = _("O'quv Platformasi")

    def ready(self):
        import core.signals  # noqa: F401
