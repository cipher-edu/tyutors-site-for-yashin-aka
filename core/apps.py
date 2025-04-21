from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
# learning_platform/apps.py

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class LearningPlatformConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'  # Ensure this matches the app's directory name
    verbose_name = _("O'quv Platformasi") # Admin panelda ko'rinadigan nom

    def ready(self):
        """
        Django ishga tushganda signallarni import qilish va ulash.
        """
        # print("Importing signals for learning_platform...") # Tekshirish uchun
        import core.signals # Signallar faylini import qilamiz
        # print("Signals imported.")