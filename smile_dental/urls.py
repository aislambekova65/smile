from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

admin.site.site_header = 'Smile Estetic — Панель управления'
admin.site.site_title = 'Smile Estetic Admin'
admin.site.index_title = 'Управление клиникой'

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('admin/', admin.site.urls),
    path('', include('clinic.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
