# learning_platform/views.py

import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView # Login uchun Class-Based View
from django.views.generic import CreateView # Registratsiya uchun Class-Based View
from django.contrib import messages # Foydalanuvchiga xabarlar ko'rsatish uchun
from django.http import HttpResponseForbidden, HttpResponseRedirect, Http404
from django.db import transaction # Atomik operatsiyalar uchun (masalan, test natijasini saqlash)
from django.utils.translation import gettext_lazy as _

# Modellar
# Barcha kerakli modellarni core.models dan import qilamiz
from core.models import (
    Answer, Module, Course, Test, UserCourseProgress, UserTestResult, Certificate,
    # YANGI: CourseSyllabus, CourseImage, ExternalActivity bu yerda to'g'ridan-to'g'ri kerak emas,
    # chunki ular Course orqali olinadi.
)


# Formular
from .forms import CustomAuthenticationForm, TestSubmissionForm # CustomUserCreationForm
from django.contrib.auth.forms import UserCreationForm # Standard form used for simplicity

# Yordamchi funksiyalar (utils.py mavjud deb faraz qilinadi)
# Agar utils.py bo'lmasa, bu funksiyalarni shu yerga ko'chirish yoki yaratish kerak
try:
    from .utils import can_user_access_test, calculate_test_score, has_user_completed_module
except ImportError:
    # Placeholder functions if utils.py doesn't exist or has different names
    def can_user_access_test(user, module):
        # Implement actual logic: Check if all courses in the module are completed by the user
        required_courses = module.courses.all()
        completed_courses = UserCourseProgress.objects.filter(
            user=user, course__in=required_courses
        ).count()
        return completed_courses >= required_courses.count()

    def calculate_test_score(test, user_answers: dict):
        # Implement actual logic: Compare user_answers with correct answers
        score = 0
        total_questions = test.questions.count()
        if total_questions == 0:
            return 0, False

        correct_answers_pks = set(Answer.objects.filter(
            question__test=test, is_correct=True
        ).values_list('pk', flat=True))

        user_correct_count = 0
        for question_pk_str, answer_pk_str in user_answers.items():
            try:
                answer_pk = int(answer_pk_str)
                if answer_pk in correct_answers_pks:
                    user_correct_count += 1
            except (ValueError, TypeError):
                continue # Ignore invalid answer values

        score_percent = round((user_correct_count / total_questions) * 100)
        passed = score_percent >= test.passing_score_percent
        return score_percent, passed

    def has_user_completed_module(user, module):
        # Implement actual logic: Check if all courses in the module are completed
        required_courses = module.courses.all()
        if not required_courses.exists():
             return True # No courses means module is technically "completed"
        completed_courses = UserCourseProgress.objects.filter(
            user=user, course__in=required_courses
        ).count()
        return completed_courses >= required_courses.count()


def handler404(request, exception):
    return render(request, '404.html', status=404)

# --- Authentication Views ---

class RegisterView(CreateView):
    form_class = UserCreationForm # Yoki CustomUserCreationForm
    template_name = 'registration/register.html' # Shabloningiz joylashuvi
    success_url = reverse_lazy('learning_platform:module_list') # Ro'yxatdan o'tgach yo'naltirish

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, _('Muvaffaqiyatli roʻyxatdan oʻtdingiz va tizimga kirdingiz!'))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _('Roʻyxatdan oʻtishda xatolik yuz berdi. Maʼlumotlarni tekshiring.'))
        return super().form_invalid(form)


class CustomLoginView(LoginView):
    """ Login uchun view """
    authentication_form = CustomAuthenticationForm
    template_name = 'registration/login.html' # Shabloningiz joylashuvi
    # success_url standart `settings.LOGIN_REDIRECT_URL` orqali aniqlanadi

    def form_valid(self, form):
        messages.success(self.request, _('Tizimga muvaffaqiyatli kirdingiz!'))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _('Login yoki parol xato.'))
        return super().form_invalid(form)


def logout_view(request):
    """ Logout uchun view """
    logout(request)
    messages.info(request, _('Tizimdan muvaffaqiyatli chiqdingiz.'))
    return redirect('learning_platform:login') # Yoki 'home'


# --- Learning Content Views ---

@login_required
def module_list_view(request):
    """ Barcha modullar ro'yxatini ko'rsatadi """
    modules = Module.objects.order_by('order').prefetch_related('courses') # Kurslar sonini kamaytirish uchun
    context = {
        'modules': modules
    }
    return render(request, 'learning_platform/module_list.html', context)


@login_required
def module_detail_view(request, pk):
    """ Bitta modul va uning ichidagi kurslar ro'yxatini ko'rsatadi """
    # Test mavjudligini ham prefetch qilish mumkin (agar ko'p ishlatilsa)
    module = get_object_or_404(
        Module.objects.prefetch_related('courses', 'test'), # Prefetch courses and test
        pk=pk
    )

    user_completed_courses_pks = set(UserCourseProgress.objects.filter(
        user=request.user,
        course__module=module
    ).values_list('course__pk', flat=True))

    module_completed = has_user_completed_module(request.user, module)

    last_test_result = None
    # `module.test` ni tekshirishdan oldin `hasattr` ishlatish shart emas, chunki OneToOneField None qaytarishi mumkin
    test_instance = getattr(module, 'test', None) # Xavfsizroq usul
    test_available = test_instance is not None

    if test_available:
        last_test_result = UserTestResult.objects.filter(
            user=request.user, test=test_instance
        ).order_by('-attempted_at').first()

    context = {
        'module': module,
        'user_completed_courses_pks': user_completed_courses_pks,
        'module_completed': module_completed,
        'test_available': test_available,
        'test_instance': test_instance, # Shablon uchun test obyektini ham beramiz
        'last_test_result': last_test_result,
    }
    return render(request, 'learning_platform/module_detail.html', context)


@login_required
def course_detail_view(request, pk):
    """ Bitta kursning (darsning) mazmunini ko'rsatadi """
    # YANILANGAN: prefetch_related bilan syllabus, images, activities olinadi
    try:
        course = get_object_or_404(
            Course.objects.select_related('module') # Module ma'lumotlari uchun
                         .prefetch_related(
                             'syllabi',                 # Syllabi larni yuklash
                             'images',                  # Rasmlarni yuklash
                             'external_activities'      # Tashqi mashg'ulotlarni yuklash
                         ),
            pk=pk
        )
    except Http404:
         messages.error(request, _("Kurs topilmadi."))
         # Mumkin bo'lsa, oldingi sahifaga yoki modullar ro'yxatiga qaytarish
         referer = request.META.get('HTTP_REFERER')
         if referer:
              return redirect(referer)
         return redirect('learning_platform:module_list')


    is_completed = UserCourseProgress.objects.filter(user=request.user, course=course).exists()

    # YANGI: Related objects ni contextga qo'shamiz
    syllabi = course.syllabi.all() # related manager orqali
    images = course.images.all()   # related manager orqali
    external_activities = course.external_activities.order_by('order') # related manager orqali

    context = {
        'course': course,
        'is_completed': is_completed,
        'syllabi': syllabi,                     # Contextga qo'shildi
        'images': images,                       # Contextga qo'shildi
        'external_activities': external_activities, # Contextga qo'shildi
    }
    return render(request, 'learning_platform/course_detail.html', context)


@login_required
@transaction.atomic
def mark_course_complete_view(request, pk):
    """ Kursni 'Tugatildi' deb belgilash (POST request) """
    if request.method != 'POST':
        return HttpResponseForbidden(_("Faqat POST so'rovlariga ruxsat etilgan."))

    course = get_object_or_404(Course, pk=pk)

    progress, created = UserCourseProgress.objects.get_or_create(
        user=request.user,
        course=course,
        # completed_at avtomatik qo'shiladi (auto_now_add=True)
    )

    if created:
        messages.success(request, _("'{course_title}' kursi muvaffaqiyatli tugatildi deb belgilandi.").format(course_title=course.title))
    else:
        messages.info(request, _("Siz '{course_title}' kursini avvalroq tugatgansiz.").format(course_title=course.title))

    # Foydalanuvchini modul sahifasiga qaytarish
    return redirect('learning_platform:module_detail', pk=course.module.pk)


# --- Test Views ---

@login_required
def take_test_view(request, module_pk):
    """ Testni ko'rsatish va topshirish (GET va POST) """
    module = get_object_or_404(Module.objects.prefetch_related('test__questions__answers'), pk=module_pk)

    test_instance = getattr(module, 'test', None)
    if not test_instance:
        messages.error(request, _("Bu modul uchun test topilmadi."))
        return redirect('learning_platform:module_detail', pk=module.pk)

    # Testga kirish huquqini tekshirish
    if not can_user_access_test(request.user, module):
        messages.warning(request, _("Testni topshirish uchun avval modulning barcha kurslarini tugatishingiz kerak."))
        return redirect('learning_platform:module_detail', pk=module.pk)

    # Test savollari mavjudligini tekshirish
    if not test_instance.questions.exists():
         messages.warning(request, _("Bu testda hali savollar qo'shilmagan."))
         return redirect('learning_platform:module_detail', pk=module.pk)

    if request.method == 'POST':
        # Test obyektini formaga uzatamiz
        form = TestSubmissionForm(request.POST, test=test_instance)
        if form.is_valid():
            user_answers = form.get_user_answers()
            score, passed = calculate_test_score(test_instance, user_answers)

            # Test natijasini bazaga saqlash
            with transaction.atomic():
                result = UserTestResult.objects.create(
                    user=request.user,
                    test=test_instance,
                    score=score,
                    passed=passed
                )
            # Foydalanuvchini natija sahifasiga yo'naltiramiz
            messages.success(request, _("Test muvaffaqiyatli topshirildi! Natijangizni ko'ring."))
            return redirect('learning_platform:test_result', pk=result.pk)
        else:
            messages.error(request, _("Iltimos, barcha savollarga javob bering."))
    else:
        # GET request: Test savollarini forma bilan ko'rsatish
        form = TestSubmissionForm(test=test_instance)

    context = {
        'test': test_instance,
        'form': form,
        'module': module,
    }
    return render(request, 'learning_platform/take_test.html', context)


@login_required
def test_result_view(request, pk):
    """ Test natijasini ko'rsatish """
    result = get_object_or_404(
        UserTestResult.objects.select_related('user', 'test__module'),
        pk=pk
    )

    # Faqat o'zining natijasini ko'ra olishini ta'minlash
    if result.user != request.user:
        return HttpResponseForbidden(_("Sizga bu natijani ko'rishga ruxsat yo'q."))

    certificate = None
    if result.passed:
        try:
            certificate = Certificate.objects.get(user=request.user, module=result.test.module)
        except Certificate.DoesNotExist:
            # Signal ishlamagan bo'lishi yoki hali yaratilmagan bo'lishi mumkin
            # Bu yerda qayta yaratish logikasi qo'shish mumkin, lekin signalga ishonish yaxshiroq
            pass

    context = {
        'result': result,
        'certificate': certificate,
    }
    return render(request, 'learning_platform/test_result.html', context)


# --- Certificate Views ---

@login_required
def my_certificates_view(request):
    """ Foydalanuvchining barcha sertifikatlarini ko'rsatish """
    certificates = Certificate.objects.filter(user=request.user).select_related('module').order_by('-issued_at')
    context = {
        'certificates': certificates
    }
    return render(request, 'learning_platform/my_certificates.html', context)

@login_required
def certificate_view(request, certificate_id):
    """ Bitta sertifikatni ko'rsatish (detalli) - UUID bo'yicha """
    try:
        # UUID formatini tekshirish uchun
        uuid.UUID(str(certificate_id))
        certificate = get_object_or_404(
            Certificate.objects.select_related('user', 'module'),
            certificate_id=certificate_id
        )
    except (ValueError, Http404):
        raise Http404(_("Bunday ID bilan sertifikat topilmadi."))


    # Faqat sertifikat egasi yoki admin ko'ra olishi kerak (yoki public qilinishi kerak)
    # Hozircha faqat egasiga ruxsat beramiz
    if certificate.user != request.user and not request.user.is_staff:
        return HttpResponseForbidden(_("Sizga bu sertifikatni ko'rishga ruxsat yo'q."))

    context = {
        'certificate': certificate
    }
    # Kelajakda bu yerda PDF generatsiya logikasi qo'shilishi mumkin
    return render(request, 'learning_platform/certificate_detail.html', context)


# --- Keraksiz yoki eski view (o'chirilsa bo'ladi) ---
# def learning_platform_module_change(request):
#     # Bu view endi kerak emasga o'xshaydi, chunki admin panelda module_change bor
#     # Agar maxsus logikasi bo'lmasa, o'chirish mumkin
#     return render(request, 'core/module_change.html') # Shablon topilmasligi mumkin