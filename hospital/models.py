from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import date


class Doctor(models.Model):
    DEPARTMENT_CHOICES = [
        ('Cardiology', 'Cardiology'),
        ('Pediatrics', 'Pediatrics'),
        ('Orthopedics', 'Orthopedics'),
        ('Neurology', 'Neurology'),
        ('General Medicine', 'General Medicine'),
    ]

    AVAILABLE_DAYS_CHOICES = [
        ('Mon - Fri', 'Monday - Friday'),
        ('Mon, Wed, Fri', 'Monday, Wednesday, Friday'),
        ('Tue, Thu, Sat', 'Tuesday, Thursday, Saturday'),
        ('Mon - Sat', 'Monday - Saturday'),
        ('Weekend Only', 'Saturday & Sunday'),
    ]

    name = models.CharField(max_length=150, help_text="Doctor's full name, e.g., Dr. Jane Smith")
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES)
    specialization = models.CharField(max_length=150, help_text="e.g. Interventional Cardiology, Pediatric Neurology")
    consultation_fee = models.DecimalField(max_digits=8, decimal_places=2, default=500.00)
    available_days = models.CharField(max_length=50, choices=AVAILABLE_DAYS_CHOICES, default='Mon - Fri')
    active_status = models.BooleanField(default=True, help_text="Whether doctor is currently accepting appointments")
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    experience_years = models.PositiveIntegerField(default=5)
    qualification = models.CharField(max_length=100, default='MBBS, MD', blank=True)
    bio = models.TextField(blank=True, help_text="Short bio and clinical interests")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.department})"

    @property
    def badge_color(self):
        colors = {
            'Cardiology': 'danger',
            'Pediatrics': 'warning',
            'Orthopedics': 'success',
            'Neurology': 'primary',
            'General Medicine': 'info',
        }
        return colors.get(self.department, 'secondary')


class Patient(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, db_index=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Male')
    blood_group = models.CharField(max_length=5, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.phone})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    TIME_SLOT_CHOICES = [
        ('09:00 AM', '09:00 AM - 09:30 AM'),
        ('09:30 AM', '09:30 AM - 10:00 AM'),
        ('10:00 AM', '10:00 AM - 10:30 AM'),
        ('10:30 AM', '10:30 AM - 11:00 AM'),
        ('11:00 AM', '11:00 AM - 11:30 AM'),
        ('11:30 AM', '11:30 AM - 12:00 PM'),
        ('02:00 PM', '02:00 PM - 02:30 PM'),
        ('02:30 PM', '02:30 PM - 03:00 PM'),
        ('03:00 PM', '03:00 PM - 03:30 PM'),
        ('03:30 PM', '03:30 PM - 04:00 PM'),
        ('04:00 PM', '04:00 PM - 04:30 PM'),
        ('04:30 PM', '04:30 PM - 05:00 PM'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField()
    time_slot = models.CharField(max_length=20, choices=TIME_SLOT_CHOICES)
    reason = models.TextField(help_text="Primary symptoms or reason for visit")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', 'time_slot']

    def __str__(self):
        return f"Appt #{self.id}: {self.patient.full_name} with {self.doctor.name} on {self.date} at {self.time_slot}"

    def clean(self):
        super().clean()
        # Disallow dates in the past for new appointments
        if self.date and self.date < date.today() and not self.pk:
            raise ValidationError({'date': "Appointment date cannot be in the past."})

        # Prevent double booking for the same doctor, date and slot (excluding cancelled appointments)
        conflicts = Appointment.objects.filter(
            doctor=self.doctor,
            date=self.date,
            time_slot=self.time_slot
        ).exclude(status='Cancelled')

        if self.pk:
            conflicts = conflicts.exclude(pk=self.pk)

        if conflicts.exists():
            raise ValidationError(
                f"Doctor {self.doctor.name} already has an active appointment at {self.time_slot} on {self.date}. Please choose another slot."
            )

    @property
    def status_badge_class(self):
        mapping = {
            'Pending': 'bg-warning text-dark',
            'Confirmed': 'bg-primary text-white',
            'Completed': 'bg-success text-white',
            'Cancelled': 'bg-danger text-white',
        }
        return mapping.get(self.status, 'bg-secondary text-white')

    @property
    def is_upcoming(self):
        return self.date >= date.today() and self.status in ['Pending', 'Confirmed']


class MedicalReport(models.Model):
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name='medical_report',
        null=True,
        blank=True,
        help_text="Associated appointment"
    )
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_reports')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='medical_reports')
    diagnosis = models.TextField(help_text="Medical diagnosis / evaluation")
    prescription = models.TextField(help_text="Prescribed medications, dosage, and intake instructions")
    doctor_notes = models.TextField(blank=True, help_text="Follow-up advice, dietary precautions, tests recommended")
    report_date = models.DateField(default=date.today)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-report_date', '-created_at']

    def __str__(self):
        return f"Report #{self.id} for {self.patient.full_name} by {self.doctor.name} ({self.report_date})"
