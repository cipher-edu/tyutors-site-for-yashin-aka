import uuid
import re
import os
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, MaxValueValidator, MinValueValidator

DOCUMENT_EXTENSIONS = ('pdf', 'doc', 'docx')
document_file_validator = FileExtensionValidator(
    allowed_extensions=DOCUMENT_EXTENSIONS,
    message=_("Faqat PDF, DOC yoki DOCX fayllarni yuklash mumkin."),
)

# --------------------------------------------------------------------------
# Abstrakt Modellar
# --------------------------------------------------------------------------

class TimestampedModel(models.Model):
    created_at = models.DateTimeField(_("Yaratilgan vaqti"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Yangilangan vaqti"), auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']

# --------------------------------------------------------------------------
# Asosiy Modellar
# --------------------------------------------------------------------------

class Module(TimestampedModel):
    title = models.CharField(_("Modul sarlavhasi"), max_length=200, unique=True)
    description = models.TextField(_("Modul tavsifi"), blank=True, null=True)
    order = models.PositiveIntegerField(_("Tartib raqami"), default=0, help_text=_("Modullarni ko'rsatish tartibi."))

    class Meta:
        verbose_name = _("Modul")
        verbose_name_plural = _("Modullar")
        ordering = ['order', 'title']

    def __str__(self):
        return self.title

class Course(TimestampedModel):
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='courses',
        verbose_name=_("Modul")
    )
    title = models.CharField(_("Kurs sarlavhasi"), max_length=255)
    content = models.TextField(_("Kontent (mavzu)"), blank=True, help_text=_("Kursning asosiy matnli mazmuni.")) # Blank=True qo'shildi
    video_url = models.URLField(_("Video havolasi (YouTube)"), blank=True, null=True, help_text=_("Agar mavjud bo'lsa, YouTube video havolasi."))
    order = models.PositiveIntegerField(_("Tartib raqami"), default=0, help_text=_("Modul ichidagi kurslarni ko'rsatish tartibi."))

    @property
    def get_youtube_embed_url(self):
        if not self.video_url:
            return None
        video_id = None
        # Qo'shimcha patternlar bilan mustahkamlangan regex
        patterns = [
            r"youtube\.com/watch\?v=([a-zA-Z0-9_-]+)",
            r"youtu\.be/([a-zA-Z0-9_-]+)(?:\?.*)?", # Query parametrlarni ham hisobga olish
            r"youtube\.com/embed/([a-zA-Z0-9_-]+)",
            r"youtube\.com/shorts/([a-zA-Z0-9_-]+)", # Shorts uchun
        ]
        for pattern in patterns:
            match = re.search(pattern, self.video_url)
            if match:
                video_id = match.group(1)
                break
        if video_id:
            return f"https://www.youtube.com/embed/{video_id}"
        return None

    class Meta:
        verbose_name = _("Kurs")
        verbose_name_plural = _("Kurslar")
        ordering = ['module__order', 'order', 'title']

    def __str__(self):
        return f"{self.module.title} - {self.title}"

# --- Fayl va Rasm Modellar (O'zgarishsiz, lekin clean muhim) ---

class CourseSyllabus(TimestampedModel):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='syllabi',
        verbose_name=_("Kurs")
    )
    title = models.CharField(_("Fayl sarlavhasi"), max_length=150, blank=True, help_text=_("Masalan, '1-dars syllabusi'. Bo'sh qolsa fayl nomi ishlatiladi."))
    # upload_to yo'li to'g'ri ekanligiga ishonch hosil qiling
    file = models.FileField(
        _("Ma'ruza / material fayli"),
        upload_to='course_syllabi/%Y/%m/',
        help_text=_("PDF yoki Word (.doc, .docx) fayllarni yuklang."),
        validators=[document_file_validator],
    )

    @property
    def filename(self):
        return os.path.basename(self.file.name) if self.file else ''

    @property
    def file_extension(self):
        return os.path.splitext(self.filename)[1].lower()

    @property
    def is_word_file(self):
        return self.file_extension in {'.doc', '.docx'}

    class Meta:
        verbose_name = _("Ma'ruza materiali")
        verbose_name_plural = _("Ma'ruza materiallari")
        ordering = ['course', 'created_at']

    def __str__(self):
        return self.title or self.filename

    def clean(self):
        super().clean()
        if self.file:
            ext = self.file_extension.lstrip('.')
            if ext not in DOCUMENT_EXTENSIONS:
                raise ValidationError(
                    _("Yuklangan fayl formati noto'g'ri. PDF, DOC yoki DOCX yuklang.")
                )

class CourseImage(TimestampedModel):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_("Kurs")
    )
    # upload_to yo'li to'g'ri ekanligiga ishonch hosil qiling
    image = models.ImageField(
        _("Rasm"),
        upload_to='course_images/%Y/%m/' # Yil va oy bo'yicha papkalarga ajratish
    )
    caption = models.CharField(_("Rasm tavsifi"), max_length=255, blank=True, null=True, help_text=_("Rasm ostida ko'rinadigan qisqa izoh."))

    @property
    def filename(self):
        """Rasm faylining nomini qaytaradi."""
        return os.path.basename(self.image.name)

    class Meta:
        verbose_name = _("Kurs Rasmi")
        verbose_name_plural = _("Kurs Rasmlari")
        ordering = ['course', 'created_at']

    def __str__(self):
        return f"Rasm: {self.course.title} - {self.caption or self.filename}"

# --- ExternalActivity (LearningApps uchun tuzatishlar bilan) ---

class ExternalActivity(TimestampedModel):
    LEARNINGAPPS = 'LA'
    KAHOOT = 'KH'
    OTHER = 'OT'
    ACTIVITY_TYPE_CHOICES = [
        (LEARNINGAPPS, _("LearningApps")),
        (KAHOOT, _("Kahoot!")),
        (OTHER, _("Boshqa")),
    ]

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='external_activities',
        verbose_name=_("Kurs")
    )
    title = models.CharField(_("Mashg'ulot sarlavhasi"), max_length=200, help_text=_("Masalan, 'Lug'atlarni mustahkamlash'"))
    activity_type = models.CharField(
        _("Mashg'ulot turi"),
        max_length=2,
        choices=ACTIVITY_TYPE_CHOICES,
        default=OTHER,
    )
    url = models.URLField(
        _("Mashg'ulot manzili (URL)"),
        max_length=500,
        help_text=_(
            "LearningApps uchun 'Share' yoki 'Embed' linkini kiriting (masalan, .../display?id=... yoki .../watch?v=...). "
            "Kahoot yoki boshqa platformalar uchun to'g'ridan-to'g'ri havolani kiriting."
        )
    )
    order = models.PositiveIntegerField(_("Tartib raqami"), default=0, help_text=_("Mashg'ulotlarni ko'rsatish tartibi."))

    class Meta:
        verbose_name = _("Tashqi Mashg'ulot")
        verbose_name_plural = _("Tashqi Mashg'ulotlar")
        ordering = ['course', 'order', 'title']

    def __str__(self):
        return f"{self.course.title} - {self.title} ({self.get_activity_type_display()})"

    @property
    def get_learningapps_embed_url(self):
        """
        LearningApps URL'idan iframe uchun mos 'watch?v=' URL'ini generatsiya qilishga harakat qiladi.
        Turli xil LearningApps URL formatlarini qo'llab-quvvatlaydi.
        """
        if self.activity_type != self.LEARNINGAPPS or not self.url:
            return None

        # /watch?v= shaklidagi URLni to'g'ridan-to'g'ri qaytarish
        watch_match = re.search(r"learningapps\.org/watch\?v=([a-zA-Z0-9_-]+)", self.url)
        if watch_match:
            # Agar allaqachon to'g'ri formatda bo'lsa, shuni qaytaramiz
            return self.url.split('&')[0] # Qo'shimcha parametrlarni olib tashlash

        # /display?id= yoki /view formatidagi URL'dan ID ni ajratib olish
        # ID raqamli yoki harf-raqamli (masalan, p1a2b3c4d) bo'lishi mumkin
        id_match = re.search(r"learningapps\.org/(?:display\?id=|view(?:/)?)([a-zA-Z0-9_-]+)", self.url)
        if id_match:
            app_id = id_match.group(1)
            return f"https://learningapps.org/watch?v={app_id}"

        return None


class Infographic(TimestampedModel):
    """Bosh sahifada aylanadigan microlearning infografikasi."""
    title = models.CharField(_("Sarlavha"), max_length=200)
    image = models.ImageField(_("Infografika rasmi"), upload_to='infographics/%Y/%m/')
    caption = models.CharField(
        _("Qisqa axborot"),
        max_length=300,
        blank=True,
        help_text=_("Karusel ostida ko'rinadigan qisqa matn."),
    )
    link = models.URLField(
        _("Havola"),
        blank=True,
        help_text=_("Bosilganda ochiladigan ixtiyoriy havola."),
    )
    order = models.PositiveIntegerField(_("Tartib raqami"), default=0)
    is_active = models.BooleanField(
        _("Faol"),
        default=True,
        help_text=_("Bosh sahifada ko'rsatilsinmi?"),
    )

    class Meta:
        verbose_name = _("Infografika")
        verbose_name_plural = _("Infografikalar")
        ordering = ['order', 'id']

    def __str__(self):
        return self.title


class SiteDocument(TimestampedModel):
    """Kurs dasturi, ish reja va huquqiy asoslar uchun sayt darajasidagi hujjat."""
    PROGRAM = 'program'
    PLAN = 'plan'
    LEGAL = 'legal'
    OTHER = 'other'
    DOCUMENT_TYPE_CHOICES = [
        (PROGRAM, _("Kurs dasturi")),
        (PLAN, _("Ish reja")),
        (LEGAL, _("Huquqiy asoslar")),
        (OTHER, _("Boshqa")),
    ]

    title = models.CharField(_("Hujjat sarlavhasi"), max_length=200)
    document_type = models.CharField(
        _("Hujjat turi"),
        max_length=20,
        choices=DOCUMENT_TYPE_CHOICES,
        default=OTHER,
    )
    file = models.FileField(
        _("Fayl (PDF/Word)"),
        upload_to='site_documents/%Y/%m/',
        help_text=_("PDF yoki Word (.doc, .docx) fayllarni yuklang."),
        validators=[document_file_validator],
    )
    order = models.PositiveIntegerField(_("Tartib raqami"), default=0)
    is_active = models.BooleanField(
        _("Faol"),
        default=True,
        help_text=_("Bosh sahifada ko'rsatilsinmi?"),
    )

    class Meta:
        verbose_name = _("Sayt hujjati")
        verbose_name_plural = _("Sayt hujjatlari (dastur, ish reja)")
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.get_document_type_display()} — {self.title}"

    @property
    def filename(self):
        return os.path.basename(self.file.name) if self.file else ''

    @property
    def file_extension(self):
        return os.path.splitext(self.filename)[1].lower()

    @property
    def is_word_file(self):
        return self.file_extension in {'.doc', '.docx'}

    def clean(self):
        super().clean()
        if self.file:
            ext = self.file_extension.lstrip('.')
            if ext not in DOCUMENT_EXTENSIONS:
                raise ValidationError(
                    _("Yuklangan fayl formati noto'g'ri. PDF, DOC yoki DOCX yuklang.")
                )


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
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_("Testdan muvaffaqiyatli o'tish uchun talab qilinadigan minimal foiz (0-100)."),
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