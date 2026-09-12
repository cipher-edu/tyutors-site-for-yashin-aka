from .models import UserCourseProgress, Module


def has_user_completed_module(user, module: Module) -> bool:
    """
    Foydalanuvchi berilgan modulning barcha kurslarini tugatganligini tekshiradi.
    """
    if not user.is_authenticated:
        return False

    total_courses_in_module = module.courses.count()
    if total_courses_in_module == 0:
        return True

    completed_courses_count = UserCourseProgress.objects.filter(
        user=user,
        course__module=module,
    ).count()

    return completed_courses_count >= total_courses_in_module


def can_user_access_test(user, module: Module) -> bool:
    return has_user_completed_module(user, module)


def calculate_test_score(test, user_answers: dict) -> tuple[int, bool]:
    """
    user_answers: {'question_pk': 'answer_pk', ...}
    Returns: (score_percent, passed)
    """
    if not test:
        return 0, False

    questions = test.questions.prefetch_related('answers')
    total_questions = questions.count()
    if total_questions == 0:
        return 0, False

    correct_answers_count = 0
    for question in questions:
        user_answer_pk = user_answers.get(str(question.pk))
        if not user_answer_pk:
            continue
        try:
            selected_pk = int(user_answer_pk)
        except (TypeError, ValueError):
            continue
        correct_pks = {
            answer.pk
            for answer in question.answers.all()
            if answer.is_correct
        }
        if selected_pk in correct_pks:
            correct_answers_count += 1

    score_percent = round((correct_answers_count / total_questions) * 100)
    passed = score_percent >= test.passing_score_percent
    return score_percent, passed
