@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   SMILE ESTETIC — Установка проекта
echo ========================================
echo.

:: Проверяем Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Python не найден! Скачайте с https://python.org
    pause
    exit /b 1
)

echo [1/5] Создание виртуального окружения...
python -m venv venv
call venv\Scripts\activate.bat

echo [2/5] Установка зависимостей...
pip install -r requirements.txt --quiet

echo [3/5] Применение миграций базы данных...
python manage.py makemigrations
python manage.py migrate

echo [4/5] Загрузка тестовых данных...
python manage.py shell -c "
from clinic.models import SiteSettings, Service, Specialist, Testimonial, Schedule

# Настройки сайта
s = SiteSettings.get_settings()
s.phone = '+996 (700) 123-456'
s.address_ru = 'г. Бишкек, ул. Токтогула, 85'
s.address_ky = 'Бишкек ш., Токтогул көч., 85'
s.working_hours_ru = 'Пн–Пт: 9:00–19:00, Сб: 9:00–16:00'
s.working_hours_ky = 'Дүйш–Жума: 9:00–19:00, Ишемби: 9:00–16:00'
s.save()
print('✓ Настройки сайта обновлены')

# Услуги
services = [
    ('Терапевтическое лечение', 'Терапевтик дарылоо', 'bi-bandaid',
     'Лечение кариеса, пульпита, реставрация зубов современными материалами',
     'Кариести, пульпитти дарылоо, заманбап материалдар менен тиш калыбына келтирүү', 800, 5000),
    ('Имплантация', 'Имплантация', 'bi-shield-plus',
     'Установка зубных имплантов — надёжное решение для восстановления утраченных зубов',
     'Тиш импланттарын орнотуу — жоголгон тиштерди калыбына келтирүүнүн ишенимдүү жолу', 30000, 80000),
    ('Ортодонтия (брекеты)', 'Ортодонтия (брекеттер)', 'bi-magnet',
     'Исправление прикуса и выравнивание зубов с помощью брекет-систем',
     'Тиштерди тегиздөө жана тиш тизилишин оңдоо', 15000, 60000),
    ('Отбеливание зубов', 'Тиш агартуу', 'bi-brightness-high',
     'Профессиональное отбеливание зубов до 8 тонов. Безопасно и эффективно',
     'Профессионалдуу тиш агартуу. Коопсуз жана натыйжалуу', 5000, 12000),
    ('Протезирование', 'Протездөө', 'bi-award',
     'Изготовление и установка зубных протезов: коронки, мосты, виниры',
     'Тиш протезин жасоо жана орнотуу: тажылар, көпүрөлөр, виниртер', 8000, 50000),
    ('Детская стоматология', 'Балдар стоматологиясы', 'bi-emoji-smile',
     'Бережное лечение зубов для детей в комфортной обстановке без страха',
     'Балдарга коопсуз чөйрөдө мамиле жасалат', 600, 4000),
]

for name_ru, name_ky, icon, desc_ru, desc_ky, p_from, p_to in services:
    Service.objects.get_or_create(name_ru=name_ru, defaults={
        'name_ky': name_ky, 'icon': icon,
        'description_ru': desc_ru, 'description_ky': desc_ky,
        'price_from': p_from, 'price_to': p_to
    })
print('✓ Услуги добавлены:', Service.objects.count())

# Специалист-пример
sp, _ = Specialist.objects.get_or_create(name_ru='Айнур Бекова', defaults={
    'name_ky': 'Айнур Бекова',
    'specialty_ru': 'Стоматолог-терапевт',
    'specialty_ky': 'Стоматолог-терапевт',
    'bio_ru': 'Врач высшей категории с опытом работы 12 лет. Специализируется на лечении сложных случаев кариеса и эндодонтии.',
    'bio_ky': '12 жыл тажрыйбасы бар жогорку категориялуу дарыгер.',
    'experience_years': 12,
})
# Расписание специалиста
days = [(0,9,0,18,0), (1,9,0,18,0), (2,9,0,18,0), (3,9,0,18,0), (4,9,0,17,0)]
from datetime import time
for day, sh, sm, eh, em in days:
    Schedule.objects.get_or_create(specialist=sp, day_of_week=day, defaults={
        'start_time': time(sh, sm), 'end_time': time(eh, em), 'is_working': True
    })
print('✓ Специалист и расписание добавлены')

# Отзывы
reviews = [
    ('Марина С.', 'Прекрасная клиника! Очень внимательный персонал. Лечилась здесь уже несколько раз — всегда довольна результатом.', 5),
    ('Азиз К.', 'Сделали имплант — результат отличный! Врач всё объяснил, боли почти не было. Рекомендую.', 5),
    ('Гульнара Т.', 'Отличное место для лечения зубов. Современное оборудование, чисто, уютно. Цены адекватные.', 5),
]
for name, text, rating in reviews:
    Testimonial.objects.get_or_create(name=name, defaults={'text_ru': text, 'rating': rating})
print('✓ Отзывы добавлены')
"

echo [5/5] Создание администратора...
echo.
echo Введите данные для входа в админ-панель:
python manage.py createsuperuser

echo.
echo ========================================
echo   ГОТОВО! Запуск сервера...
echo ========================================
echo.
echo   Сайт:        http://127.0.0.1:8000
echo   Админ-панель: http://127.0.0.1:8000/admin
echo.
python manage.py runserver
