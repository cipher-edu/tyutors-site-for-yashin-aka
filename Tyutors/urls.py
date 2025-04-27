from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),  
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
<<<<<<< HEAD
    # Agar static fayllar bilan ham muammo bo'lsa, buni ham qo'shing:
    # urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

=======
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
>>>>>>> aeb74ee0da082676582a69441da7656c46579614
handler404 = 'core.views.handler404'