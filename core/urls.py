from django.urls import path
from . import views

urlpatterns = [
    path('course-catalog/', views.course_catalog, name='course_catalog'),
    path('user-profile/', views.user_profile, name='user_profile'),
    path('course-datail/', views.course_detail, name='couse_detail'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
]