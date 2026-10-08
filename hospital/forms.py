from django import forms
from django.core.exceptions import ValidationError
from datetime import date
from .models import Doctor, Patient, Appointment, MedicalReport


class AppointmentBookingForm(forms.ModelForm):
    # Patient fields for seamless one-step booking
    first_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. John'})
    )
    last_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Doe'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'e.g. john@example.com'})
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. +1 555-0199 or 9876543210'})
    )
    age = forms.IntegerField(
        required=False,
        min_value=0,
        max_value=120,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 32'})
    )
    gender = forms.ChoiceField(
        choices=Patient.GENDER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Appointment
        fields = ['doctor', 'date', 'time_slot', 'reason']
        widgets = {
            'doctor': forms.Select(attrs={'class': 'form-select', 'id': 'id_doctor'}),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'id': 'id_date',
                'min': date.today().isoformat()
            }),
            'time_slot': forms.Select(attrs={'class': 'form-select', 'id': 'id_time_slot'}),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe your symptoms or reason for the consultation...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only active doctors can be selected
        self.fields['doctor'].queryset = Doctor.objects.filter(active_status=True)
        self.fields['doctor'].empty_label = "Select a Doctor"

    def clean_date(self):
        appointment_date = self.cleaned_data.get('date')
        if appointment_date and appointment_date < date.today():
            raise ValidationError("Appointment date cannot be in the past.")
        return appointment_date

    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get('doctor')
        appointment_date = cleaned_data.get('date')
        time_slot = cleaned_data.get('time_slot')

        if doctor and appointment_date and time_slot:
            # Check for existing non-cancelled appointment
            conflict = Appointment.objects.filter(
                doctor=doctor,
                date=appointment_date,
                time_slot=time_slot
            ).exclude(status='Cancelled')

            if self.instance and self.instance.pk:
                conflict = conflict.exclude(pk=self.instance.pk)

            if conflict.exists():
                raise ValidationError(
                    f"Dr. {doctor.name} already has a booking at {time_slot} on {appointment_date}. "
                    "Please select an alternative available time slot."
                )

        return cleaned_data


class AppointmentStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select form-select-sm'})
        }


class MedicalReportForm(forms.ModelForm):
    class Meta:
        model = MedicalReport
        fields = ['diagnosis', 'prescription', 'doctor_notes', 'report_date']
        widgets = {
            'diagnosis': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Clinical diagnosis, observed symptoms, test findings...'
            }),
            'prescription': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Prescribed medicines, dosage (e.g. 500mg), timing (e.g. 1-0-1 after food)...'
            }),
            'doctor_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Dietary guidelines, follow-up date, lifestyle advice...'
            }),
            'report_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }


class PatientLookupForm(forms.Form):
    query = forms.CharField(
        label="Phone Number or Email",
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter phone number or email address...'
        })
    )
