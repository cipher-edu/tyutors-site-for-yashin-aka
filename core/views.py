# from django.shortcuts import render

# def course_catalog(request):
#     return render(request, 'course_catalog.html')
# def course_detail(request):
#     return render(request, 'course_detail.html')

# def user_profile(request):
#     return render(request, 'user_profile.html')

# def user_test(request):
#     return render(request, 'test.html')

# def user_sertificate(request):
#     return render(request, 'user_sertificate.html')

# def register(request):
#     return render(request, 'register/register.html')

# def login(request):
#     return render(request, 'register/login.html')

# learning_platform/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView # Login uchun Class-Based View
from django.views.generic import CreateView # Registratsiya uchun Class-Based View
from django.contrib import messages # Foydalanuvchiga xabarlar ko'rsatish uchun
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.db import transaction # Atomik operatsiyalar uchun (masalan, test natijasini saqlash)

# Modellar
from .models import Module, Course, Test, UserCourseProgress, UserTestResult, Certificate

# Formular
from .forms import CustomAuthenticationForm, TestSubmissionForm # CustomUserCreationForm
from django.contrib.auth.forms import UserCreationForm # Standard form used for simplicity

# Yordamchi funksiyalar
from .utils import can_user_access_test, calculate_test_score, has_user_completed_module
def handler404(request, exception):
    return render(request, '404.html', status=404)

# --- Authentication Views ---

# Option 1: Function-Based View for Registration
# def register_view(request):
#     if request.method == 'POST':
#         form = UserCreationForm(request.POST) # Yoki CustomUserCreationForm
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             messages.success(request, 'Muvaffaqiyatli roʻyxatdan oʻtdingiz va tizimga kirdingiz!')
#             return redirect('learning_platform:module_list') # Yoki boshqa sahifaga
#         else:
#             messages.error(request, 'Roʻyxatdan oʻtishda xatolik yuz berdi. Maʼlumotlarni tekshiring.')
#     else:
#         form = UserCreationForm()
#     return render(request, 'registration/register.html', {'form': form})

# Option 2: Class-Based View for Registration (more standard)
class RegisterView(CreateView):
    form_class = UserCreationForm # Yoki CustomUserCreationForm
    template_name = 'registration/register.html' # Shabloningiz joylashuvi
    success_url = reverse_lazy('learning_platform:module_list') # Ro'yxatdan o'tgach yo'naltirish

    def form_valid(self, form):
        # Form to'g'ri to'ldirilganda
        user = form.save()
        login(self.request, user)
        messages.success(self.request, 'Muvaffaqiyatli roʻyxatdan oʻtdingiz va tizimga kirdingiz!')
        return super().form_valid(form)

    def form_invalid(self, form):
        # Form xato to'ldirilganda
        messages.error(self.request, 'Roʻyxatdan oʻtishda xatolik yuz berdi. Maʼlumotlarni tekshiring.')
        return super().form_invalid(form)


class CustomLoginView(LoginView):
    """ Login uchun view """
    authentication_form = CustomAuthenticationForm
    template_name = 'registration/login.html' # Shabloningiz joylashuvi
    # success_url (redirect) standart `settings.LOGIN_REDIRECT_URL` orqali aniqlanadi
    # yoki bu yerda `get_success_url` methodini override qilish mumkin.

    def form_valid(self, form):
        messages.success(self.request, 'Tizimga muvaffaqiyatli kirdingiz!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Login yoki parol xato.')
        return super().form_invalid(form)


def logout_view(request):
    """ Logout uchun view """
    logout(request)
    messages.info(request, 'Tizimdan muvaffaqiyatli chiqdingiz.')
    # Qaytadan login sahifasiga yoki bosh sahifaga yo'naltirish
    return redirect('learning_platform:login') # Yoki 'home'


# --- Learning Content Views ---

@login_required # Faqat avtorizatsiyadan o'tganlar ko'ra oladi
def module_list_view(request):
    """ Barcha modullar ro'yxatini ko'rsatadi """
    modules = Module.objects.order_by('order')
    context = {
        'modules': modules
    }
    return render(request, 'learning_platform/module_list.html', context)


@login_required
def module_detail_view(request, pk):
    """ Bitta modul va uning ichidagi kurslar ro'yxatini ko'rsatadi """
    module = get_object_or_404(Module.objects.prefetch_related('courses'), pk=pk)

    # Foydalanuvchi ushbu modul kurslarini tugatganligini tekshirish (shablonda ishlatish uchun)
    user_completed_courses_pks = set(UserCourseProgress.objects.filter(
        user=request.user,
        course__module=module
    ).values_list('course__pk', flat=True))

    # Modul tugaganmi (testga kirish uchun)
    module_completed = has_user_completed_module(request.user, module)

    # Foydalanuvchi test topshirganmi va natijasi qanday?
    last_test_result = UserTestResult.objects.filter(
        user=request.user, test=module.test
    ).order_by('-attempted_at').first() if hasattr(module, 'test') else None

    context = {
        'module': module,
        'user_completed_courses_pks': user_completed_courses_pks,
        'module_completed': module_completed,
        'test_available': hasattr(module, 'test'), # Test mavjudmi?
        'last_test_result': last_test_result,
    }
    return render(request, 'learning_platform/module_detail.html', context)


@login_required
def course_detail_view(request, pk):
    """ Bitta kursning (darsning) mazmunini ko'rsatadi """
    # select_related orqali module ma'lumotlarini ham bir so'rovda olish
    course = get_object_or_404(Course.objects.select_related('module'), pk=pk)

    # Foydalanuvchi bu kursni tugatganmi?
    is_completed = UserCourseProgress.objects.filter(user=request.user, course=course).exists()

    context = {
        'course': course,
        'is_completed': is_completed,
    }
    return render(request, 'learning_platform/course_detail.html', context)


@login_required
@transaction.atomic # Atomiklikni ta'minlash
def mark_course_complete_view(request, pk):
    """ Kursni 'Tugatildi' deb belgilash (POST request) """
    if request.method != 'POST':
        # Faqat POST metodini qabul qilamiz
        return HttpResponseForbidden("Faqat POST so'rovlariga ruxsat etilgan.")

    course = get_object_or_404(Course, pk=pk)

    # Agar avval belgilangan bo'lsa, qayta yaratmaymiz
    progress, created = UserCourseProgress.objects.get_or_create(
        user=request.user,
        course=course
        # completed_at avtomatik qo'shiladi (auto_now_add=True)
    )

    if created:
        messages.success(request, f"'{course.title}' kursi muvaffaqiyatli tugatildi deb belgilandi.")
    else:
        messages.info(request, f"Siz '{course.title}' kursini avvalroq tugatgansiz.")

    # Foydalanuvchini modul sahifasiga qaytarish
    return redirect('learning_platform:module_detail', pk=course.module.pk)


# --- Test Views ---

@login_required
def take_test_view(request, module_pk):
    """ Testni ko'rsatish va topshirish (GET va POST) """
    module = get_object_or_404(Module, pk=module_pk)

    # Test mavjudligini tekshirish
    try:
        test = module.test # OneToOneField tufayli related_name 'test'
    except Test.DoesNotExist:
        messages.error(request, "Bu modul uchun test topilmadi.")
        return redirect('learning_platform:module_detail', pk=module.pk)

    # Testga kirish huquqini tekshirish (utils.py dagi funksiya)
    if not can_user_access_test(request.user, module):
        messages.warning(request, "Testni topshirish uchun avval modulning barcha kurslarini tugatishingiz kerak.")
        return redirect('learning_platform:module_detail', pk=module.pk)

    if request.method == 'POST':
        form = TestSubmissionForm(request.POST, test=test)
        if form.is_valid():
            user_answers = form.get_user_answers()
            score, passed = calculate_test_score(test, user_answers)

            # Test natijasini bazaga saqlash
            with transaction.atomic(): # Agar biror xatolik bo'lsa, yozuv saqlanmaydi
                result = UserTestResult.objects.create(
                    user=request.user,
                    test=test,
                    score=score,
                    passed=passed
                    # attempted_at avtomatik (auto_now_add=True)
                )
            # Foydalanuvchini natija sahifasiga yo'naltiramiz (signals.py ishga tushishi mumkin)
            return redirect('learning_platform:test_result', pk=result.pk)
        else:
            # Forma validatsiyadan o'tmasa, xatoliklarni ko'rsatamiz
            messages.error(request, "Iltimos, barcha savollarga javob bering.")
            # Qayta GET requestdek forma ko'rsatiladi (xatolar bilan)
    else:
        # GET request: Test savollarini forma bilan ko'rsatish
        form = TestSubmissionForm(test=test)

    context = {
        'test': test,
        'form': form,
        'module': module,
    }
    return render(request, 'learning_platform/take_test.html', context)


@login_required
def test_result_view(request, pk):
    """ Test natijasini ko'rsatish """
    result = get_object_or_404(UserTestResult.objects.select_related('user', 'test__module'), pk=pk)

    # Faqat o'zining natijasini ko'ra olishini ta'minlash
    if result.user != request.user:
        return HttpResponseForbidden("Sizga bu natijani ko'rishga ruxsat yo'q.")

    # Sertifikat mavjud bo'lsa (signal orqali yaratilgan bo'lishi mumkin)
    certificate = None
    if result.passed:
        try:
            certificate = Certificate.objects.get(user=request.user, module=result.test.module)
        except Certificate.DoesNotExist:
            pass # Hali yaratilmagan bo'lishi mumkin

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
    """ Bitta sertifikatni ko'rsatish (detalli) """
    # UUID bo'yicha qidirish
    certificate = get_object_or_404(Certificate.objects.select_related('user', 'module'), certificate_id=certificate_id)

    # Faqat sertifikat egasi ko'ra olishi kerak
    if certificate.user != request.user:
        # Yoki public qilish mumkin, lekin hozircha faqat egasiga
        return HttpResponseForbidden("Sizga bu sertifikatni ko'rishga ruxsat yo'q.")

    context = {
        'certificate': certificate
    }
    # Bu yerda PDF generatsiya qilish yoki tayyor shablonni ko'rsatish mumkin
    return render(request, 'learning_platform/certificate_detail.html', context)


def learning_platform_module_change(request):
    # Add logic for handling the module change
    return render(request, 'core/module_change.html')