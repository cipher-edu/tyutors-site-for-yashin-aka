# learning_platform/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from django.utils.translation import gettext_lazy as _ # Agar xabar kerak bo'lsa

# Modellarni import qilish (to'g'ri yo'lni ko'rsating)
from core.models import UserTestResult, Certificate, Module
from django.conf import settings # Foydalanuvchi modelini olish uchun
# from django.contrib.auth import get_user_model # Yoki bu usul

# User = get_user_model() # Agar settings.AUTH_USER_MODEL o'rniga ishlatsangiz


@receiver(post_save, sender=UserTestResult)
@transaction.atomic # Atomik operatsiya (sertifikat yaratishda xato bo'lsa, qaytaradi)
def create_certificate_on_pass(sender, instance: UserTestResult, created: bool, **kwargs):
    """
    Agar foydalanuvchi testdan muvaffaqiyatli o'tsa (`passed=True`)
    va uning shu modul uchun hali sertifikati bo'lmasa, yangi sertifikat yaratadi.
    Bu funksiya UserTestResult saqlanganidan keyin ishga tushadi.
    """
    # Faqat testdan o'tgan holatlar uchun ishlaymiz
    if instance.passed:
        user = instance.user
        # Test orqali modulni olamiz
        try:
            module = instance.test.module
        except Module.DoesNotExist:
             # Agar test qandaydir modulga bog'lanmagan bo'lsa (bo'lmasligi kerak)
             # Bu yerda log yozish yoki jim o'tkazib yuborish mumkin
             print(f"Xatolik: Test ID {instance.test.pk} hech qanday modulga bog'lanmagan.")
             return

        # Ushbu foydalanuvchi uchun ushbu modul bo'yicha sertifikat mavjudligini tekshiramiz
        # `get_or_create` atomiklikni ta'minlash uchun yaxshiroq
        certificate, cert_created = Certificate.objects.get_or_create(
            user=user,
            module=module,
            # Agar defaults kerak bo'lsa, shu yerga qo'shiladi
            # defaults={'issued_at': timezone.now()} # Agar auto_now_add=False bo'lsa
        )

        if cert_created:
            # Yangi sertifikat yaratildi
            # Bu yerda qo'shimcha amallar bajarish mumkin (masalan, xabar yuborish)
            print(f"Sertifikat {user.username} uchun '{module.title}' moduliga yaratildi.")
            # messages.success(request, "Tabriklaymiz! Sizga sertifikat berildi.") # Signalda request yo'q
    # else:
        # Agar testdan o'ta olmagan bo'lsa va sertifikat mavjud bo'lsa,
        # uni o'chirish logikasi qo'shilishi mumkin, ammo bu xavfli bo'lishi mumkin.
        # Masalan, foydalanuvchi qayta topshirib o'ta olmasa, sertifikati o'chib ketadi.
        # Odatda o'chirish shart emas.
        # pass