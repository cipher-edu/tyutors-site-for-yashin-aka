# from django.urls import path
# from . import views

# urlpatterns = [
#     path('course-catalog/', views.course_catalog, name='course_catalog'),
#     path('user-profile/', views.user_profile, name='user_profile'),
#     path('course-datail/', views.course_detail, name='couse_detail'),
#     path('user-test/', views.user_test, name='user_test'),
#     path('user-sertificate/', views.user_sertificate, name='user_sertificate'),
#     path('register/', views.register, name='register'),
#     path('login/', views.login, name='login'),
# ]

# learning_platform/urls.py

from django.urls import path
from . import views # Shu papkadagi views.py ni import qilish

app_name = 'learning_platform' # Namespace (shablonlarda {% url 'learning_platform:...' %} ishlatish uchun)

urlpatterns = [
    # Authentication URLs
    path('register/', views.RegisterView.as_view(), name='register'),
    # Agar standart Django login/logout views ishlatsangiz:
    # from django.contrib.auth import views as auth_views
    # path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    # path('logout/', auth_views.LogoutView.as_view(next_page='learning_platform:login'), name='logout'),
    # Yoki o'zimizning custom viewlar uchun:
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Module and Course URLs
    path('', views.module_list_view, name='module_list'),
    path('modules/<int:pk>/', views.module_detail_view, name='module_detail'),
    path('courses/<int:pk>/', views.course_detail_view, name='course_detail'),
    path('courses/<int:pk>/complete/', views.mark_course_complete_view, name='mark_course_complete'), # POST request

    # Test URLs
    path('modules/<int:module_pk>/test/', views.take_test_view, name='take_test'), # GET/POST
    path('results/<int:pk>/', views.test_result_view, name='test_result'),

    # Certificate URLs
    path('certificates/', views.my_certificates_view, name='my_certificates'),
    path('certificates/<uuid:certificate_id>/', views.certificate_view, name='certificate_detail'),

    # Bosh sahifa uchun (agar kerak bo'lsa)
    # path('', views.home_view, name='home'),
]