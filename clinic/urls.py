from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('specialists/', views.specialists_view, name='specialists'),
    path('specialists/<int:pk>/', views.specialist_detail, name='specialist_detail'),
    path('services/', views.services_view, name='services'),
    path('schedule/', views.schedule_view, name='schedule'),
    path('contact/', views.contact_view, name='contact'),
    path('set-language/', views.set_language, name='set_language'),
    # API
    path('api/login/', views.admin_login_modal, name='admin_login_modal'),
    path('api/availability/', views.check_availability, name='check_availability'),
    # Dashboard
    path('dashboard/', views.appointments_dashboard, name='appointments_dashboard'),
]
