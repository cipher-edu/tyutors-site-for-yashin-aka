# core/models.py

import uuid
import re  # YouTube URLni qayta ishlash uchun
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.db.models import Count # admin.py da annotate uchun

# --------------------------------------------------------------------------
# Abstrakt Modellar
# --------------------------------------------------------------------------

class TimestampedModel(models.Model):
    """Yaratilgan va yangilangan vaqtni avtomatik qo'shadigan abstrakt model."""
    created_at = models.DateTimeField(_("Yaratilgan vaqti"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Yangilangan vaqti"), auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']

# --------------------------------------------------------------------------
# Asosiy Modellar
# --------------------------------------------------------------------------

class Module(TimestampedModel):
    """O'quv kurslarini guruhlash uchun Modul modeli."""
    title = models.CharField(_("Modul sarlavhasi"), max_length=200, unique=True)
    description = models.TextField(_("Modul tavsifi"), blank=True, null=True)
    order = models.PositiveIntegerField(_("Tartib raqami"), default=0, help_text=_("Modullarni ko'rsatish tartibi."))
    # image = models.ImageField(_("Modul rasmi"), upload_to='module_images/', blank=True, null=True)

    class Meta:
        verbose_name = _("Modul")
        verbose_name_plural = _("Modullar")
        ordering = ['order', 'title']

    def __str__(self):
        return self.title

class Course(TimestampedModel):
    """Modul ichidagi alohida o'quv materiali (kurs/dars)."""
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='courses',
        verbose_name=_("Modul")
    )
    title = models.CharField(_("Kurs sarlavhasi"), max_length=255)
    content = models.TextField(_("Kontent (mavzu)"), help_text=_("Kursning asosiy matnli mazmuni."))
    video_url = models.URLField(_("Video havolasi (YouTube)"), blank=True, null=True, help_text=_("Agar mavjud bo'lsa, YouTube video havolasi."))
    order = models.PositiveIntegerField(_("Tartib raqami"), default=0, help_text=_("Modul ichidagi kurslarni ko'rsatish tartibi."))

    @property
    def get_youtube_embed_url(self):
        """ Saqlangan YouTube URL'dan 'embed' formatidagi URL'ni qaytaradi. """
        if not self.video_url:
            return None
        video_id = None
        patterns = [
            r"youtube\.com/watch\?v=([a-zA-Z0-9_-]+)", # Standart format
            r"youtu\.be/([a-zA-Z0-9_-]+)",             # Qisqa format
            r"youtube\.com/embed/([a-zA-Z0-9_-]+)"    # Embed format (agar shunday saqlangan bo'lsa)
        ]
        for pattern in patterns:
            match = re.search(pattern, self.video_url)
            if match:
                video_id = match.group(1)
                break # Birinchi moslik topilgach chiqish
        if video_id:
            return f"https://www.youtube.com/embed/{video_id}"
        return None # Moslik topilmasa

    class Meta:
        verbose_name = _("Kurs")
        verbose_name_plural = _("Kurslar")
        ordering = ['module__order', 'order', 'title'] # Modul tartibi, keyin kurs tartibi

    def __str__(self):
        return f"{self.module.title} - {self.title}"

# --------------------------------------------------------------------------
# Test va Savollar Modeli
# --------------------------------------------------------------------------

class Test(TimestampedModel):
    """Modul yakunida topshiriladigan test."""
    module = models.OneToOneField(
        Module,
        on_delete=models.CASCADE,
        related_name='test',
        verbose_name=_("Modul")
    )
    title = models.CharField(_("Test sarlavhasi"), max_length=255)
    description = models.TextField(_("Test tavsifi"), blank=True, null=True)
    passing_score_percent = models.PositiveIntegerField(
        _("O'tish bali (foizda)"),
        default=70,
        help_text=_("Testdan muvaffaqiyatli o'tish uchun talab qilinadigan minimal foiz (0-100).")
    )

    class Meta:
        verbose_name = _("Test")
        verbose_name_plural = _("Testlar")
        ordering = ['module__order', 'module__title']

    def __str__(self):
        return f"{self.module.title} - Test"

class Question(TimestampedModel):
    """Test ichidagi alohida savol."""
    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name=_("Test")
    )
    text = models.TextField(_("Savol matni"))
    order = models.PositiveIntegerField(_("Tartib raqami"), default=0)

    class Meta:
        verbose_name = _("Savol")
        verbose_name_plural = _("Savollar")
        ordering = ['test', 'order']

    def __str__(self):
        return f"{self.test.title} - Savol {self.order}: {self.text[:50]}..."

class Answer(TimestampedModel):
    """Savol uchun variant (javob)."""
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name=_("Savol")
    )
    text = models.CharField(_("Javob matni"), max_length=255)
    is_correct = models.BooleanField(_("To'g'ri javob"), default=False, help_text=_("Agar bu javob to'g'ri bo'lsa belgilang."))

    class Meta:
        verbose_name = _("Javob")
        verbose_name_plural = _("Javoblar")
        # Bitta savol uchun faqat bitta to'g'ri javob bo'lishini tekshirish (clean metodida)
        ordering = ['question', 'id']

    def __str__(self):
        correct_marker = " (To'g'ri)" if self.is_correct else ""
        return f"{self.question.text[:30]}... - Javob: {self.text}{correct_marker}"

# --------------------------------------------------------------------------
# Foydalanuvchi Progressi va Sertifikat Modeli
# --------------------------------------------------------------------------

class UserCourseProgress(TimestampedModel):
    """Foydalanuvchining qaysi kursni tugatganligini kuzatib boradi."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='course_progress',
        verbose_name=_("Foydalanuvchi")
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='user_progress',
        verbose_name=_("Kurs")
    )
    completed_at = models.DateTimeField(_("Tugatilgan vaqti"), auto_now_add=True)

    class Meta:
        verbose_name = _("Foydalanuvchi Kurs Progressi")
        verbose_name_plural = _("Foydalanuvchilar Kurs Progresslari")
        unique_together = ('user', 'course') # Bir foydalanuvchi bir kursni bir marta belgilaydi
        ordering = ['user', '-completed_at']

    def __str__(self):
        return f"{self.user.username} - {self.course.title} (Tugatildi)"

class UserTestResult(TimestampedModel):
    """Foydalanuvchining test natijalarini saqlaydi."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='test_results',
        verbose_name=_("Foydalanuvchi")
    )
    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        related_name='user_results',
        verbose_name=_("Test")
    )
    score = models.PositiveIntegerField(_("To'plangan ball (foizda)"), default=0)
    passed = models.BooleanField(_("O'tdi"), default=False)
    attempted_at = models.DateTimeField(_("Urinish vaqti"), auto_now_add=True)

    class Meta:
        verbose_name = _("Foydalanuvchi Test Natijasi")
        verbose_name_plural = _("Foydalanuvchilar Test Natijalari")
        ordering = ['user', 'test', '-attempted_at']

    def __str__(self):
        status = "O'tdi" if self.passed else "Yiqildi"
        return f"{self.user.username} - {self.test.title} - {self.score}% ({status})"

class Certificate(TimestampedModel):
    """Modulni muvaffaqiyatli tugatgan foydalanuvchilarga beriladigan sertifikat."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='certificates',
        verbose_name=_("Foydalanuvchi")
    )
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='certificates_issued',
        verbose_name=_("Modul")
    )
    certificate_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name=_("Sertifikat ID"))
    issued_at = models.DateTimeField(_("Berilgan vaqti"), auto_now_add=True)
    # certificate_file = models.FileField(_("Sertifikat Fayli"), upload_to='certificates/', blank=True, null=True)

    class Meta:
        verbose_name = _("Sertifikat")
        verbose_name_plural = _("Sertifikatlar")
        unique_together = ('user', 'module') # Bitta modul uchun bitta sertifikat
        ordering = ['user', '-issued_at']

    def __str__(self):
        return f"Sertifikat №{str(self.certificate_id)[:8]}... - {self.user.username} - {self.module.title}"