from django import forms
from datetime import time as dtime
from .models import Appointment, Specialist, Service

# Временные слоты с 9:00 до 18:30 с шагом 30 мин
TIME_SLOTS = []
for h in range(9, 19):
    for m in (0, 30):
        if h == 18 and m == 30:
            break
        t = dtime(h, m)
        TIME_SLOTS.append((t.strftime('%H:%M'), t.strftime('%H:%M')))


class AppointmentForm(forms.ModelForm):
    preferred_time = forms.ChoiceField(
        choices=[('', '— выберите время —')] + TIME_SLOTS,
        label='Желаемое время',
        required=False,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_preferred_time'}),
    )

    class Meta:
        model = Appointment
        fields = ['patient_name', 'phone', 'email', 'specialist', 'service',
                  'preferred_date', 'preferred_time', 'message']
        widgets = {
            'patient_name': forms.TextInput(attrs={
                'placeholder': 'Иван Иванов', 'class': 'form-control'
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': '+996 700 000 000', 'class': 'form-control'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'email@example.com', 'class': 'form-control'
            }),
            'preferred_date': forms.DateInput(attrs={
                'type': 'date', 'class': 'form-control', 'id': 'id_preferred_date'
            }),
            'message': forms.Textarea(attrs={
                'rows': 3, 'placeholder': 'Ваш комментарий (необязательно)',
                'class': 'form-control'
            }),
            'specialist': forms.Select(attrs={
                'class': 'form-control', 'id': 'id_specialist'
            }),
            'service': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'patient_name': 'Имя / Аты',
            'phone': 'Телефон *',
            'email': 'Email',
            'specialist': 'Специалист',
            'service': 'Услуга',
            'preferred_date': 'Дата *',
            'message': 'Комментарий',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['specialist'].queryset = Specialist.objects.filter(is_active=True)
        self.fields['specialist'].empty_label = 'Любой специалист'
        self.fields['service'].queryset = Service.objects.filter(is_active=True)
        self.fields['service'].empty_label = '— выберите услугу —'
        self.fields['specialist'].required = False
        self.fields['service'].required = False
        self.fields['email'].required = False
        self.fields['message'].required = False

    def clean(self):
        cleaned = super().clean()
        specialist = cleaned.get('specialist')
        date = cleaned.get('preferred_date')
        time_str = cleaned.get('preferred_time')

        if specialist and date and time_str:
            from datetime import datetime
            try:
                t = datetime.strptime(time_str, '%H:%M').time()
            except (ValueError, TypeError):
                return cleaned

            conflict = Appointment.objects.filter(
                specialist=specialist,
                preferred_date=date,
                preferred_time=t,
            )
            if self.instance.pk:
                conflict = conflict.exclude(pk=self.instance.pk)
            if conflict.exists():
                raise forms.ValidationError(
                    f'Время {time_str} у выбранного специалиста уже занято. Выберите другое время.'
                )
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        time_str = self.cleaned_data.get('preferred_time')
        if time_str:
            from datetime import datetime
            try:
                instance.preferred_time = datetime.strptime(time_str, '%H:%M').time()
            except (ValueError, TypeError):
                instance.preferred_time = None
        else:
            instance.preferred_time = None
        if commit:
            instance.save()
        return instance
