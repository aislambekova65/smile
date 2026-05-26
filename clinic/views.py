from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.translation import activate, get_language
from datetime import datetime
from .models import Specialist, Service, Testimonial, Appointment, Schedule
from .forms import AppointmentForm, TIME_SLOTS


def set_language(request):
    lang = request.GET.get('lang', 'ru')
    if lang in ('ru', 'ky'):
        if hasattr(request, 'session'):
            request.session['_language'] = lang
        activate(lang)
    next_url = request.GET.get('next', '/')
    response = redirect(next_url)
    response.set_cookie('django_language', lang, max_age=365 * 24 * 3600)
    return response


def index(request):
    specialists = Specialist.objects.filter(is_active=True)[:4]
    services = Service.objects.filter(is_active=True)[:6]
    testimonials = Testimonial.objects.filter(is_active=True)
    form = AppointmentForm()

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '✓ Ваша заявка принята! Мы свяжемся с вами в ближайшее время.')
            return redirect('index')

    return render(request, 'clinic/index.html', {
        'specialists': specialists,
        'services': services,
        'testimonials': testimonials,
        'form': form,
    })


def specialists_view(request):
    all_specialists = Specialist.objects.filter(is_active=True).prefetch_related('schedules')
    return render(request, 'clinic/specialists.html', {'specialists': all_specialists})


def specialist_detail(request, pk):
    specialist = get_object_or_404(Specialist, pk=pk, is_active=True)
    schedules = specialist.schedules.all().order_by('day_of_week')
    return render(request, 'clinic/specialist_detail.html', {
        'specialist': specialist,
        'schedules': schedules,
    })


def services_view(request):
    all_services = Service.objects.filter(is_active=True)
    return render(request, 'clinic/services.html', {'services': all_services})


def schedule_view(request):
    all_specialists = Specialist.objects.filter(is_active=True).prefetch_related('schedules')
    return render(request, 'clinic/schedule.html', {'specialists': all_specialists})


def contact_view(request):
    form = AppointmentForm()
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '✓ Ваша заявка принята! Мы свяжемся с вами в ближайшее время.')
            return redirect('contact')
    return render(request, 'clinic/contact.html', {'form': form})


# ===== API: Admin login via modal =====
@require_POST
def admin_login_modal(request):
    username = request.POST.get('username', '').strip()
    password = request.POST.get('password', '')
    user = authenticate(request, username=username, password=password)
    if user is not None and user.is_staff:
        auth_login(request, user)
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Неверный логин или пароль'})


# ===== API: Check time availability =====
def check_availability(request):
    specialist_id = request.GET.get('specialist_id')
    date_str = request.GET.get('date')

    if not date_str:
        return JsonResponse({'booked': [], 'slots': [s[0] for s in TIME_SLOTS]})

    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return JsonResponse({'booked': [], 'slots': [s[0] for s in TIME_SLOTS]})

    # Booked times
    qs = Appointment.objects.filter(preferred_date=date_obj, preferred_time__isnull=False)
    if specialist_id and specialist_id.isdigit():
        qs = qs.filter(specialist_id=int(specialist_id))

    booked = [a.preferred_time.strftime('%H:%M') for a in qs]

    # Available slots based on specialist schedule (day of week)
    available_slots = [s[0] for s in TIME_SLOTS]
    if specialist_id and specialist_id.isdigit():
        day_of_week = date_obj.weekday()
        try:
            sched = Schedule.objects.get(specialist_id=int(specialist_id), day_of_week=day_of_week)
            if not sched.is_working:
                return JsonResponse({'booked': booked, 'slots': [], 'day_off': True})
            # Filter slots within working hours
            available_slots = [
                s[0] for s in TIME_SLOTS
                if sched.start_time <= datetime.strptime(s[0], '%H:%M').time() < sched.end_time
            ]
        except Schedule.DoesNotExist:
            pass

    return JsonResponse({'booked': booked, 'slots': available_slots, 'day_off': False})


# ===== Appointments dashboard =====
@login_required(login_url='/admin/login/')
def appointments_dashboard(request):
    if not request.user.is_staff:
        messages.error(request, 'Доступ запрещён.')
        return redirect('index')

    qs = Appointment.objects.select_related('specialist', 'service').order_by('-preferred_date', '-created_at')

    # Filters
    status_filter = request.GET.get('status', '')
    specialist_filter = request.GET.get('specialist', '')
    date_filter = request.GET.get('date', '')

    if status_filter:
        qs = qs.filter(status=status_filter)
    if specialist_filter and specialist_filter.isdigit():
        qs = qs.filter(specialist_id=int(specialist_filter))
    if date_filter:
        try:
            date_obj = datetime.strptime(date_filter, '%Y-%m-%d').date()
            qs = qs.filter(preferred_date=date_obj)
        except ValueError:
            pass

    # Quick status update
    if request.method == 'POST':
        app_id = request.POST.get('app_id')
        new_status = request.POST.get('new_status')
        if app_id and new_status in dict(Appointment.STATUS_CHOICES):
            Appointment.objects.filter(pk=app_id).update(status=new_status)
        return redirect(request.get_full_path())

    specialists = Specialist.objects.filter(is_active=True)
    return render(request, 'clinic/appointments_dashboard.html', {
        'appointments': qs,
        'specialists': specialists,
        'status_choices': Appointment.STATUS_CHOICES,
        'status_filter': status_filter,
        'specialist_filter': specialist_filter,
        'date_filter': date_filter,
        'counts': {
            'all': Appointment.objects.count(),
            'new': Appointment.objects.filter(status='new').count(),
            'confirmed': Appointment.objects.filter(status='confirmed').count(),
            'completed': Appointment.objects.filter(status='completed').count(),
        },
    })
