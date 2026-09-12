from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm

from core.models import (
    Module,
    Course,
    UserCourseProgress,
    UserTestResult,
    Certificate,
    Infographic,
    SiteDocument,
)
from .forms import CustomAuthenticationForm, TestSubmissionForm
from .utils import can_user_access_test, calculate_test_score, has_user_completed_module


def handler404(request, exception):
    return render(request, '404.html', status=404)

# --- Authentication Views ---

class RegisterView(CreateView):
    form_class = UserCreationForm # Yoki CustomUserCreationForm
    template_name = 'registration/register.html' # Shabloningiz joylashuvi
    success_url = reverse_lazy('learning_platform:module_list') # Ro'yxatdan o'tgach yo'naltirish

    def form_valid(self, form):
        self.object = form.save()
        login(self.request, self.object)
        messages.success(self.request, _('Muvaffaqiyatli roʻyxatdan oʻtdingiz va tizimga kirdingiz!'))
        return redirect(self.get_success_url())

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

def module_list_view(request):
    """Bosh sahifa: infografikalar, dastur/ish reja va modullar (login shart emas)."""
    modules = list(Module.objects.order_by('order').prefetch_related('courses'))
    infographics = Infographic.objects.filter(is_active=True).order_by('order', 'id')
    site_documents = SiteDocument.objects.filter(is_active=True).order_by('order', 'id')
    completed_pks = set()
    if request.user.is_authenticated:
        completed_pks = set(
            UserCourseProgress.objects.filter(user=request.user).values_list('course_id', flat=True)
        )
    for n, module in enumerate(modules, start=1):
        courses = list(module.courses.all())
        total = len(courses)
        done = sum(1 for course in courses if course.pk in completed_pks)
        module.number = n
        module.progress_total = total
        module.progress_done = done
        module.progress_percent = int(done / total * 100) if total else 0

    unit_meta = [
        ("1-qism · Asoslar", "VUCA, axloq va huquqiy poydevor"),
        ("2-qism · Qadriyatlar", "Halollik, adolat, hurmat, mas’uliyat"),
        ("3-qism · Raqamli dunyo", "Internet, tarmoq, jamoa, liderlik"),
        ("4-qism · Jamiyat", "Tabiat, fuqarolik, stress va yakun"),
    ]
    module_units = []
    for i in range(0, len(modules), 5):
        chunk = modules[i:i + 5]
        meta_i = i // 5
        title, subtitle = unit_meta[meta_i] if meta_i < len(unit_meta) else (f"{meta_i + 1}-qism", "")
        done_units = sum(1 for m in chunk if m.progress_percent == 100)
        module_units.append({
            'title': title,
            'subtitle': subtitle,
            'modules': chunk,
            'done': done_units,
            'total': len(chunk),
            'complete': bool(chunk) and done_units == len(chunk),
            'index': meta_i,
        })

    context = {
        'modules': modules,
        'module_units': module_units,
        'infographics': infographics,
        'site_documents': site_documents,
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
    course = get_object_or_404(
        Course.objects.select_related('module').prefetch_related(
            'syllabi',
            'images',
            'external_activities',
        ),
        pk=pk,
    )


    is_completed = UserCourseProgress.objects.filter(user=request.user, course=course).exists()

    # Sibling courses navigation
    module_courses = list(course.module.courses.order_by('order', 'id'))
    user_completed_pks = set(UserCourseProgress.objects.filter(
        user=request.user,
        course__module=course.module
    ).values_list('course_id', flat=True))

    current_index = None
    for idx, c in enumerate(module_courses):
        c.is_done = c.pk in user_completed_pks
        if c.pk == course.pk:
            current_index = idx

    prev_course = module_courses[current_index - 1] if current_index is not None and current_index > 0 else None
    next_course = module_courses[current_index + 1] if current_index is not None and current_index < len(module_courses) - 1 else None

    # YANGI: Related objects ni contextga qo'shamiz
    syllabi = course.syllabi.all() # related manager orqali
    images = course.images.all()   # related manager orqali
    external_activities = course.external_activities.order_by('order') # related manager orqali

    context = {
        'course': course,
        'is_completed': is_completed,
        'syllabi': syllabi,
        'images': images,
        'external_activities': external_activities,
        'module_courses': module_courses,
        'prev_course': prev_course,
        'next_course': next_course,
        'course_index': current_index + 1 if current_index is not None else 1,
        'total_courses': len(module_courses),
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

            result = UserTestResult.objects.create(
                user=request.user,
                test=test_instance,
                score=score,
                passed=passed,
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
        certificate, _ = Certificate.objects.get_or_create(
            user=request.user,
            module=result.test.module,
        )

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
    """Bitta sertifikatni ko'rsatish — UUID bo'yicha."""
    certificate = get_object_or_404(
        Certificate.objects.select_related('user', 'module'),
        certificate_id=certificate_id,
    )
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