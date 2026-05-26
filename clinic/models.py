from django.db import models
from django.utils.translation import get_language


class Specialist(models.Model):
    name_ru = models.CharField('Имя (рус)', max_length=200)
    name_ky = models.CharField('Аты (кыр)', max_length=200, blank=True)
    specialty_ru = models.CharField('Специальность (рус)', max_length=200)
    specialty_ky = models.CharField('Адистиги (кыр)', max_length=200, blank=True)
    photo = models.ImageField('Фото', upload_to='specialists/', blank=True, null=True)
    bio_ru = models.TextField('Биография (рус)', blank=True)
    bio_ky = models.TextField('Өмүр баяны (кыр)', blank=True)
    experience_years = models.PositiveIntegerField('Опыт (лет)', default=1)
    is_active = models.BooleanField('Активен', default=True)
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Специалист'
        verbose_name_plural = 'Специалисты'
        ordering = ['order', 'name_ru']

    def __str__(self):
        return self.name_ru

    @property
    def name(self):
        lang = get_language() or 'ru'
        return (self.name_ky if lang == 'ky' and self.name_ky else self.name_ru)

    @property
    def specialty(self):
        lang = get_language() or 'ru'
        return (self.specialty_ky if lang == 'ky' and self.specialty_ky else self.specialty_ru)

    @property
    def bio(self):
        lang = get_language() or 'ru'
        return (self.bio_ky if lang == 'ky' and self.bio_ky else self.bio_ru)


DAYS_OF_WEEK = [
    (0, 'Понедельник / Дүйшөмбү'),
    (1, 'Вторник / Шейшемби'),
    (2, 'Среда / Шаршемби'),
    (3, 'Четверг / Бейшемби'),
    (4, 'Пятница / Жума'),
    (5, 'Суббота / Ишемби'),
    (6, 'Воскресенье / Жекшемби'),
]

DAYS_RU = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
DAYS_KY = ['Дүйшөмбү', 'Шейшемби', 'Шаршемби', 'Бейшемби', 'Жума', 'Ишемби', 'Жекшемби']


class Schedule(models.Model):
    specialist = models.ForeignKey(
        Specialist,
        on_delete=models.CASCADE,
        related_name='schedules',
        verbose_name='Специалист',
    )
    day_of_week = models.IntegerField('День недели', choices=DAYS_OF_WEEK)
    start_time = models.TimeField('Начало работы')
    end_time = models.TimeField('Конец работы')
    is_working = models.BooleanField('Рабочий день', default=True)

    class Meta:
        verbose_name = 'Расписание'
        verbose_name_plural = 'Расписание'
        ordering = ['specialist', 'day_of_week']
        unique_together = ['specialist', 'day_of_week']

    def __str__(self):
        return f'{self.specialist.name_ru} — {self.get_day_of_week_display()}'

    @property
    def day_name(self):
        lang = get_language() or 'ru'
        if lang == 'ky':
            return DAYS_KY[self.day_of_week]
        return DAYS_RU[self.day_of_week]


class Service(models.Model):
    name_ru = models.CharField('Название (рус)', max_length=200)
    name_ky = models.CharField('Аталышы (кыр)', max_length=200, blank=True)
    description_ru = models.TextField('Описание (рус)')
    description_ky = models.TextField('Сүрөттөмө (кыр)', blank=True)
    price_from = models.DecimalField('Цена от (сом)', max_digits=10, decimal_places=0, null=True, blank=True)
    price_to = models.DecimalField('Цена до (сом)', max_digits=10, decimal_places=0, null=True, blank=True)
    icon = models.CharField(
        'Иконка Bootstrap',
        max_length=60,
        default='bi-bandaid',
        help_text='Класс Bootstrap Icons, например: bi-tooth, bi-heart-pulse',
    )
    is_active = models.BooleanField('Активна', default=True)
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'
        ordering = ['order', 'name_ru']

    def __str__(self):
        return self.name_ru

    @property
    def name(self):
        lang = get_language() or 'ru'
        return (self.name_ky if lang == 'ky' and self.name_ky else self.name_ru)

    @property
    def description(self):
        lang = get_language() or 'ru'
        return (self.description_ky if lang == 'ky' and self.description_ky else self.description_ru)

    @property
    def price_display(self):
        if self.price_from and self.price_to:
            return f'{int(self.price_from):,} — {int(self.price_to):,} сом'
        elif self.price_from:
            return f'от {int(self.price_from):,} сом'
        return None


class Appointment(models.Model):
    STATUS_NEW = 'new'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_NEW, 'Новая'),
        (STATUS_CONFIRMED, 'Подтверждена'),
        (STATUS_COMPLETED, 'Завершена'),
        (STATUS_CANCELLED, 'Отменена'),
    ]

    patient_name = models.CharField('Имя пациента', max_length=200)
    phone = models.CharField('Телефон', max_length=30)
    email = models.EmailField('Email', blank=True)
    specialist = models.ForeignKey(
        Specialist,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Специалист',
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Услуга',
    )
    preferred_date = models.DateField('Желаемая дата')
    preferred_time = models.TimeField('Желаемое время', null=True, blank=True)
    message = models.TextField('Комментарий', blank=True)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        verbose_name = 'Запись на приём'
        verbose_name_plural = 'Записи на приём'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.patient_name} — {self.preferred_date}'


class SiteSettings(models.Model):
    address_ru = models.CharField('Адрес (рус)', max_length=500, default='г. Бишкек')
    address_ky = models.CharField('Дарек (кыр)', max_length=500, default='Бишкек ш.')
    phone = models.CharField('Телефон', max_length=50, default='+996 (700) 000-000')
    phone2 = models.CharField('Телефон 2', max_length=50, blank=True)
    email = models.EmailField('Email', blank=True, default='info@smile-estetic.kg')
    working_hours_ru = models.CharField(
        'Часы работы (рус)', max_length=200, default='Пн–Пт: 9:00–19:00, Сб: 9:00–16:00'
    )
    working_hours_ky = models.CharField(
        'Иштөө убактысы (кыр)', max_length=200, default='Дүйш–Жума: 9:00–19:00, Ишемби: 9:00–16:00'
    )
    instagram = models.URLField('Instagram', blank=True)
    facebook = models.URLField('Facebook', blank=True)
    whatsapp = models.CharField('WhatsApp (номер)', max_length=30, blank=True)
    hero_title_ru = models.CharField('Заголовок главной (рус)', max_length=200, default='Ваша улыбка — наша забота')
    hero_title_ky = models.CharField(
        'Заголовок главной (кыр)', max_length=200, default='Сиздин жылмайуу — биздин камкордук'
    )
    hero_subtitle_ru = models.TextField(
        'Подзаголовок главной (рус)',
        default='Профессиональная стоматологическая помощь в Бишкеке. Современное оборудование, опытные врачи.',
    )
    hero_subtitle_ky = models.TextField(
        'Подзаголовок главной (кыр)',
        default='Бишкекте профессионалдуу стоматологиялык жардам. Заманбап жабдуулар, тажрыйбалуу дарыгерлер.',
    )
    about_ru = models.TextField(
        'О клинике (рус)',
        default='Smile Estetic — современный стоматологический центр, где каждый пациент получает индивидуальный подход и качественное лечение.',
    )
    about_ky = models.TextField(
        'О клинике (кыр)',
        default='Smile Estetic — заманбап стоматологиялык борбор, ар бир бейтап жеке мамиле жана сапаттуу дарылоо алат.',
    )

    class Meta:
        verbose_name = 'Настройки сайта'
        verbose_name_plural = 'Настройки сайта'

    def __str__(self):
        return 'Настройки сайта'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def address(self):
        lang = get_language() or 'ru'
        return (self.address_ky if lang == 'ky' and self.address_ky else self.address_ru)

    @property
    def working_hours(self):
        lang = get_language() or 'ru'
        return (self.working_hours_ky if lang == 'ky' and self.working_hours_ky else self.working_hours_ru)

    @property
    def hero_title(self):
        lang = get_language() or 'ru'
        return (self.hero_title_ky if lang == 'ky' and self.hero_title_ky else self.hero_title_ru)

    @property
    def hero_subtitle(self):
        lang = get_language() or 'ru'
        return (self.hero_subtitle_ky if lang == 'ky' and self.hero_subtitle_ky else self.hero_subtitle_ru)

    @property
    def about(self):
        lang = get_language() or 'ru'
        return (self.about_ky if lang == 'ky' and self.about_ky else self.about_ru)


class Testimonial(models.Model):
    name = models.CharField('Имя', max_length=200)
    text_ru = models.TextField('Отзыв (рус)')
    text_ky = models.TextField('Пикир (кыр)', blank=True)
    rating = models.PositiveSmallIntegerField('Рейтинг', default=5, choices=[(i, f'{i} ★') for i in range(1, 6)])
    is_active = models.BooleanField('Активен', default=True)
    created_at = models.DateTimeField('Дата', auto_now_add=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} — {self.rating}★'

    @property
    def text(self):
        lang = get_language() or 'ru'
        return (self.text_ky if lang == 'ky' and self.text_ky else self.text_ru)
