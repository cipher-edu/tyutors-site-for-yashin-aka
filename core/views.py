from django.shortcuts import render

def course_catalog(request):
    return render(request, 'course_catalog.html')
def course_detail(request):
    return render(request, 'course_detail.html')
def user_profile(request):
    return render(request, 'user_profile.html')

def register(request):
    return render(request, 'register/register.html')

def login(request):
    return render(request, 'register/login.html')