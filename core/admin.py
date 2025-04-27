
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, TextField
from django.contrib.admin import widgets as admin_widgets # To'g'ri import
from django.utils.translation import gettext_lazy as _

# Modellar
from .models import (
    Module, Course, CourseSyllabus, CourseImage, ExternalActivity,
    Test, Question, Answer, UserCourseProgress, UserTestResult, Certificate
)

# --- Inlines ---
class CourseSyllabusInline(admin.TabularInline):
    model = CourseSyllabus
    fields = ('title', 'file') # filename bu yerda kerak emas
    extra = 1
    verbose_name = _("Syllabus Fayli")
    verbose_name_plural = _("Syllabus Fayllari")

class CourseImageInline(admin.TabularInline):
    model = CourseImage
    fields = ('image_preview', 'image', 'caption')
    readonly_fields = ('image_preview',)
    extra = 1
    verbose_name = _("Kurs Rasmi")
    verbose_name_plural = _("Kurs Rasmlari")

    @admin.display(description=_('Rasm (Koʻrish)'))
    def image_preview(self, obj):
        if obj.image:
            return format_html('<a href="{0}" target="_blank"><img src="{0}" style="max-height: 100px; max-width: 150px;" /></a>', obj.image.url)
        return _("Rasm yo'q")

class ExternalActivityInline(admin.TabularInline):
    model = ExternalActivity
    fields = ('title', 'activity_type', 'url', 'order')
    extra = 1
    ordering = ('order',)
    verbose_name = _("Tashqi Mashg'ulot")
    verbose_name_plural = _("Tashqi Mashg'ulotlar")

class CourseInline(admin.TabularInline):
    model = Course
    fields = ('title', 'order', 'video_url', )
    extra = 1; ordering = ('order',); show_change_link = True
    verbose_name = _("Modul kursi"); verbose_name_plural = _("Modul kurslari")

class TestInline(admin.StackedInline):
    model = Test
    fields = ('title', 'description', 'passing_score_percent')
    can_delete = False; verbose_name = _("Modul testi"); verbose_name_plural = _("Modul Testi")

class AnswerInline(admin.TabularInline):
    model = Answer
    fields = ('text', 'is_correct'); extra = 3

class QuestionInline(admin.StackedInline):
    model = Question
    fields = ('text', 'order'); extra = 1; ordering = ('order',); show_change_link = True
    verbose_name = _("Test savoli"); verbose_name_plural = _("Test savollari")

# --- ModelAdmin Classlari ---

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'display_course_count', 'display_has_test', 'created_at_formatted')
    list_filter = ('created_at',)
    search_fields = ('title', 'description')
    ordering = ('order', 'title')
    fieldsets = ( (None, {'fields': ('title', 'order', 'description')}),
                  (_('Vaqt Belgilari'), {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}) )
    readonly_fields = ('created_at', 'updated_at'); inlines = [CourseInline, TestInline]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(course_count_annotation=Count('courses'))

    @admin.display(description=_('Kurslar soni'), ordering='course_count_annotation')
    def display_course_count(self, obj): return obj.course_count_annotation

    @admin.display(description=_('Test mavjud'), boolean=True)
    def display_has_test(self, obj): return hasattr(obj, 'test') and obj.test is not None

    @admin.display(description=_('Yaratilgan sana'), ordering='created_at')
    def created_at_formatted(self, obj): return obj.created_at.strftime('%d-%m-%Y %H:%M') if obj.created_at else '-'

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'module_link', 'order', 'has_video', 'created_at_formatted')
    list_filter = ('module', 'created_at'); search_fields = ('title', 'content', 'module__title')
    ordering = ('module__order', 'order', 'title')
    fieldsets = (
        (None, {'fields': ('module', 'title', 'order', 'video_url')}),
        (_('Kurs Mazmuni'), {'fields': ('content',)}),
    )
    list_select_related = ('module',)
    formfield_overrides = {
        TextField: {'widget': admin_widgets.AdminTextareaWidget(attrs={'rows': 15, 'cols': 80})}
    }
    inlines = [CourseSyllabusInline, CourseImageInline, ExternalActivityInline] # Inlines

    @admin.display(description=_('Modul'), ordering='module__title')
    def module_link(self, obj):
        link = reverse("admin:core_module_change", args=[obj.module.id])
        return format_html('<a href="{}">{}</a>', link, obj.module.title)

    @admin.display(description=_('Video mavjud'), boolean=True)
    def has_video(self, obj): return bool(obj.video_url)

    created_at_formatted = ModuleAdmin.created_at_formatted # Reuse


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('title', 'module_link', 'display_question_count', 'passing_score_percent')
    list_filter = ('module',); search_fields = ('title', 'description', 'module__title')
    ordering = ('module__order', 'title')
    fields = ('module', 'title', 'description', 'passing_score_percent')
    inlines = [QuestionInline]; list_select_related = ('module',)
    module_link = CourseAdmin.module_link # Reuse from CourseAdmin
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(question_count_annotation=Count('questions'))
    @admin.display(description=_('Savollar soni'), ordering='question_count_annotation')
    def display_question_count(self, obj): return obj.question_count_annotation


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('short_text', 'test_link', 'order', 'display_answer_count')
    list_filter = ('test__module', 'test')
    search_fields = ('text', 'test__title')
    fields = ('test', 'text', 'order')
    inlines = [AnswerInline]
    list_select_related = ('test', 'test__module')
    @admin.display(description=_('Savol matni (qisqa)'), ordering='text')
    def short_text(self, obj): return mark_safe(f"{obj.text[:70]}...") if len(obj.text) > 70 else obj.text
    @admin.display(description=_('Test'), ordering='test__title')
    def test_link(self, obj):
        link = reverse("admin:core_test_change", args=[obj.test.id])
        return format_html('<a href="{}">{} ({})</a>', link, obj.test.title, obj.test.module.title)
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(answer_count_annotation=Count('answers'))
    @admin.display(description=_('Javoblar soni'), ordering='answer_count_annotation')
    def display_answer_count(self, obj): return obj.answer_count_annotation


# --- Foydalanuvchi bilan bog'liq modellar ---
@admin.register(UserCourseProgress)
class UserCourseProgressAdmin(admin.ModelAdmin):
    list_display = ('user_link', 'course_link', 'module_title', 'completed_at_formatted')
    list_filter = ('completed_at', 'course__module', 'user__username')
    search_fields = ('user__username', 'course__title', 'course__module__title')
    ordering = ('-completed_at',); readonly_fields = ('user', 'course', 'completed_at', 'created_at', 'updated_at')
    list_select_related = ('user', 'course', 'course__module')
    @admin.display(description=_('Foydalanuvchi'), ordering='user__username')
    def user_link(self, obj):
        user_admin_url = reverse("admin:auth_user_change", args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', user_admin_url, obj.user.username)
    @admin.display(description=_('Kurs'), ordering='course__title')
    def course_link(self, obj):
        link = reverse("admin:core_course_change", args=[obj.course.id])
        return format_html('<a href="{}">{}</a>', link, obj.course.title)
    @admin.display(description=_('Modul'), ordering='course__module__title')
    def module_title(self, obj): return obj.course.module.title
    @admin.display(description=_('Tugatilgan sana'), ordering='completed_at')
    def completed_at_formatted(self, obj): return obj.completed_at.strftime('%d-%m-%Y %H:%M') if obj.completed_at else '-'
    def has_add_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False

@admin.register(UserTestResult)
class UserTestResultAdmin(admin.ModelAdmin):
    list_display = ('user_link', 'test_link', 'module_title', 'score', 'passed_status', 'attempted_at_formatted')
    list_filter = ('attempted_at', 'passed', 'test__module', 'user__username')
    search_fields = ('user__username', 'test__title', 'test__module__title')
    ordering = ('-attempted_at',)
    readonly_fields = ('user', 'test', 'score', 'passed', 'attempted_at', 'created_at', 'updated_at')
    list_select_related = ('user', 'test', 'test__module')
    user_link = UserCourseProgressAdmin.user_link # Reuse
    @admin.display(description=_('Test'), ordering='test__title')
    def test_link(self, obj):
         link = reverse("admin:core_test_change", args=[obj.test.id])
         return format_html('<a href="{}">{}</a>', link, obj.test.title)
    @admin.display(description=_('Modul'), ordering='test__module__title')
    def module_title(self, obj): return obj.test.module.title
    @admin.display(description=_("O'tganligi"), boolean=True, ordering='passed')
    def passed_status(self, obj): return obj.passed
    @admin.display(description=_('Urinish vaqti'), ordering='attempted_at')
    def attempted_at_formatted(self, obj): return obj.attempted_at.strftime('%d-%m-%Y %H:%M') if obj.attempted_at else '-'
    def has_add_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('certificate_link', 'user_link', 'module_link', 'issued_at_formatted')
    list_filter = ('issued_at', 'module', 'user__username')
    search_fields = ('user__username', 'module__title', 'certificate_id')
    ordering = ('-issued_at',)
    readonly_fields = ('user', 'module', 'certificate_id', 'issued_at', 'created_at', 'updated_at')
    list_select_related = ('user', 'module')
    user_link = UserCourseProgressAdmin.user_link # Reuse
    @admin.display(description=_('Modul'), ordering='module__title')
    def module_link(self, obj):
        link = reverse("admin:core_module_change", args=[obj.module.id])
        return format_html('<a href="{}">{}</a>', link, obj.module.title)
    @admin.display(description=_('Sertifikat ID'), ordering='certificate_id')
    def certificate_link(self, obj):
        link = reverse("admin:core_certificate_change", args=[obj.id])
        return format_html('<a href="{}">{}...</a>', link, str(obj.certificate_id)[:13])
    @admin.display(description=_('Berilgan sana'), ordering='issued_at')
    def issued_at_formatted(self, obj): return obj.issued_at.strftime('%d-%m-%Y %H:%M') if obj.issued_at else '-'
    def has_add_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False


# --- Admin sayt sozlamalari ---
admin.site.site_header = _("Platforma Admin Paneli")
admin.site.site_title = _("Admin Panel")
admin.site.index_title = _("Boshqaruv Paneli")