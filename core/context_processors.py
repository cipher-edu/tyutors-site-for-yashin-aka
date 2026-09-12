from django.conf import settings


def site_branding(request):
    data = {
        'SITE_NAME': getattr(settings, 'SITE_NAME', 'VUCA-konseptida axloq'),
        'SITE_TAGLINE': getattr(settings, 'SITE_TAGLINE', ''),
        'user_xp': 0,
        'user_completed': 0,
        'user_certs': 0,
        'user_streak': 0,
        'user_gems': 0,
    }
    user = getattr(request, 'user', None)
    if user is not None and user.is_authenticated:
        from core.models import UserCourseProgress, Certificate
        completed = UserCourseProgress.objects.filter(user=user).count()
        certs = Certificate.objects.filter(user=user).count()
        data['user_completed'] = completed
        data['user_certs'] = certs
        data['user_xp'] = completed * 20 + certs * 50
        data['user_streak'] = min(max(completed, 1), 99) if completed else 0
        data['user_gems'] = certs * 5 + completed
    return data
