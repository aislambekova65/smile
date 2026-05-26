from django.contrib import admin
from django.utils.html import format_html
from .models import Specialist, Schedule, Service, Appointment, SiteSettings, Testimonial


class ScheduleInline(admin.TabularInline):
    model = Schedule
    extra = 7
    fields = ('day_of_week', 'is_working', 'start_time', 'end_time')
    ordering = ('day_of_week',)

    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            existing = obj.schedules.count()
            return max(0, 7 - existing)
        return 7


@admin.register(Specialist)
class SpecialistAdmin(admin.ModelAdmin):
    list_display = ('photo_thumb', 'name_ru', 'specialty_ru', 'experience_years', 'order', 'is_active')
    list_display_links = ('photo_thumb', 'name_ru')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active', 'specialty_ru')
    search_fields = ('name_ru', 'name_ky', 'specialty_ru')
    inlines = [ScheduleInline]

    fieldsets = (
        ('Основное', {
            'fields': ('photo', 'order', 'is_active', 'experience_years'),
        }),
        ('На русском', {
            'fields': ('name_ru', 'specialty_ru', 'bio_ru'),
        }),
        ('На кыргызском', {
            'classes': ('collapse',),
            'fields': ('name_ky', 'specialty_ky', 'bio_ky'),
        }),
    )

    def photo_thumb(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="width:50px;height:50px;object-fit:cover;border-radius:50%;" />',
                obj.photo.url,
            )
        return format_html(
            '<div style="width:50px;height:50px;border-radius:50%;background:#e0f2fe;display:flex;'
            'align-items:center;justify-content:center;font-size:20px;">👤</div>'
        )

    photo_thumb.short_description = 'Фото'


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('specialist', 'day_of_week', 'start_time', 'end_time', 'is_working')
    list_filter = ('specialist', 'is_working', 'day_of_week')
    list_editable = ('start_time', 'end_time', 'is_working')
    ordering = ('specialist', 'day_of_week')


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name_ru', 'price_from', 'price_to', 'order', 'is_active')
    list_editable = ('order', 'is_active', 'price_from', 'price_to')
    list_filter = ('is_active',)
    search_fields = ('name_ru', 'name_ky')

    fieldsets = (
        ('Основное', {
            'fields': ('icon', 'price_from', 'price_to', 'order', 'is_active'),
        }),
        ('На русском', {
            'fields': ('name_ru', 'description_ru'),
        }),
        ('На кыргызском', {
            'classes': ('collapse',),
            'fields': ('name_ky', 'description_ky'),
        }),
    )


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient_name', 'phone', 'specialist', 'service', 'preferred_date', 'preferred_time', 'status', 'created_at')
    list_filter = ('status', 'preferred_date', 'specialist')
    search_fields = ('patient_name', 'phone', 'email')
    list_editable = ('status',)
    readonly_fields = ('created_at',)
    date_hierarchy = 'preferred_date'

    fieldsets = (
        ('Пациент', {
            'fields': ('patient_name', 'phone', 'email'),
        }),
        ('Запись', {
            'fields': ('specialist', 'service', 'preferred_date', 'preferred_time', 'message'),
        }),
        ('Статус', {
            'fields': ('status', 'created_at'),
        }),
    )


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Контакты', {
            'fields': ('phone', 'phone2', 'email', 'whatsapp', 'instagram', 'facebook'),
        }),
        ('Адрес', {
            'fields': ('address_ru', 'address_ky'),
        }),
        ('Часы работы', {
            'fields': ('working_hours_ru', 'working_hours_ky'),
        }),
        ('Главная страница — на русском', {
            'fields': ('hero_title_ru', 'hero_subtitle_ru', 'about_ru'),
        }),
        ('Главная страница — на кыргызском', {
            'classes': ('collapse',),
            'fields': ('hero_title_ky', 'hero_subtitle_ky', 'about_ky'),
        }),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'rating', 'is_active', 'created_at')
    list_editable = ('is_active',)
    list_filter = ('rating', 'is_active')
    search_fields = ('name', 'text_ru')

    fieldsets = (
        ('Основное', {
            'fields': ('name', 'rating', 'is_active'),
        }),
        ('Текст на русском', {
            'fields': ('text_ru',),
        }),
        ('Текст на кыргызском', {
            'classes': ('collapse',),
            'fields': ('text_ky',),
        }),
    )
