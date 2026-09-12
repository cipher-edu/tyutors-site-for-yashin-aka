import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction

from core.models import UserTestResult, Certificate

logger = logging.getLogger(__name__)


@receiver(post_save, sender=UserTestResult)
def create_certificate_on_pass(sender, instance: UserTestResult, created: bool, **kwargs):
    """Testdan o'tganda, modul uchun sertifikat yo'q bo'lsa yaratadi."""
    if not instance.passed:
        return

    module = getattr(instance.test, 'module', None)
    if module is None:
        logger.warning("Test ID %s modulga bog'lanmagan.", instance.test_id)
        return

    with transaction.atomic():
        certificate, cert_created = Certificate.objects.get_or_create(
            user=instance.user,
            module=module,
        )
        if cert_created:
            logger.info(
                "Sertifikat yaratildi: user=%s module=%s",
                instance.user_id,
                module.pk,
            )
