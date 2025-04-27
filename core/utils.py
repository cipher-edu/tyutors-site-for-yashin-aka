# learning_platform/utils.py

from .models import UserCourseProgress, Module

def has_user_completed_module(user, module: Module) -> bool:
    """
    Foydalanuvchi berilgan modulning *barcha* kurslarini tugatganligini tekshiradi.
    Testga kirish huquqini tekshirish uchun ishlatiladi.
    """
    if not user.is_authenticated:
        return False

    # Moduldagi barcha kurslar soni
    total_courses_in_module = module.courses.count()
    if total_courses_in_module == 0:
        return True # Kursi yo'q modul tugatilgan hisoblanadi (yoki boshqacha mantiq)

    # Foydalanuvchi tomonidan ushbu modulda tugatilgan kurslar soni
    completed_courses_count = UserCourseProgress.objects.filter(
        user=user,
        course__module=module
    ).count()

    return completed_courses_count >= total_courses_in_module

def can_user_access_test(user, module: Module) -> bool:
    """
    Foydalanuvchi modul testiga kira oladimi yoki yo'qligini tekshiradi.
    Asosan has_user_completed_module ni chaqiradi.
    """
    # Kelajakda qo'shimcha shartlar qo'shilishi mumkin (masalan, to'lov statusi)
    return has_user_completed_module(user, module)

def calculate_test_score(test, user_answers: dict) -> tuple[int, bool]:
    """
    Foydalanuvchi javoblariga asoslanib test natijasini (foizda) hisoblaydi.
    user_answers formati: {'question_pk_1': 'answer_pk_1', 'question_pk_2': 'answer_pk_3', ...}
    Returns: (score_percent, passed)
    """
    if not test:
        return 0, False

    questions = test.questions.prefetch_related('answers')
    total_questions = questions.count()
    if total_questions == 0:
        return 100, True # Savol yo'q bo'lsa, o'tgan hisoblanadi

    correct_answers_count = 0
    for question in questions:
        # Foydalanuvchi tanlagan javob ID'si (string kelishi mumkin)
        user_answer_pk = user_answers.get(str(question.pk))
        if user_answer_pk:
            try:
                # To'g'ri javobni topish
                correct_answer = question.answers.get(is_correct=True)
                # Foydalanuvchi javobi to'g'ri javobga mos keladimi?
                if str(correct_answer.pk) == user_answer_pk:
                    correct_answers_count += 1
            except (question.answers.model.DoesNotExist, ValueError):
                # Agar to'g'ri javob belgilanmagan bo'lsa yoki ID xato bo'lsa
                continue # Yoki xatolik qaytarish

    score_percent = round((correct_answers_count / total_questions) * 100) if total_questions > 0 else 0
    passed = score_percent >= test.passing_score_percent

    return score_percent, passed