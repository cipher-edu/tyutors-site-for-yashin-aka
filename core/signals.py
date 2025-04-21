# learning_platform/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction

from .models import UserTestResult, Certificate, Module
from django.conf import settings # Foydalanuvchi modelini olish uchun


@receiver(post_save, sender=UserTestResult)
@transaction.atomic # Atomik operatsiya (sertifikat yaratishda xato bo'lsa, qaytaradi)
def create_certificate_on_pass(sender, instance: UserTestResult, created: bool, **kwargs):
    """
    Agar foydalanuvchi testdan muvaffaqiyatli o'tsa (`passed=True`)
    va uning shu modul uchun hali sertifikati bo'lmasa, yangi sertifikat yaratadi.
    `created` flagiga qaramaydi, har safar natija saqlanganda tekshiriladi (agar o'tmagan bo'lsa ham).
    """
    # Faqat testdan o'tgan holatlar uchun ishlaymiz
    if instance.passed:
        user = instance.user
        module = instance.test.module

        # Ushbu foydalanuvchi uchun ushbu modul bo'yicha sertifikat mavjudligini tekshiramiz
        certificate_exists = Certificate.objects.filter(user=user, module=module).exists()

        if not certificate_exists:
            # Agar sertifikat yo'q bo'lsa, yangisini yaratamiz
            Certificate.objects.create(
                user=user,
                module=module
                # certificate_id va issued_at avtomatik qo'shiladi
            )
            # print(f"Sertifikat {user} uchun {module.title} moduliga yaratildi.") # Konsolga xabar (ixtiyoriy)
    # else:
        # Agar testdan o'ta olmasa va sertifikat mavjud bo'lsa (nazariy jihatdan bo'lmasligi kerak,
        # lekin eski tizimdan migratsiya bo'lsa?), o'chirish logikasini qo'shish mumkin, ammo ehtiyot bo'lish kerak.
        # Certificate.objects.filter(user=instance.user, module=instance.test.module).delete()
        # pass