from django.contrib import admin
from .models import Doctor, Patient, Appointment, MedicalReport


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'specialization', 'consultation_fee', 'available_days', 'active_status')
    list_filter = ('department', 'active_status', 'available_days')
    search_fields = ('name', 'specialization', 'email', 'phone')
    list_editable = ('active_status', 'consultation_fee')
    ordering = ('name',)


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'email', 'age', 'gender', 'blood_group', 'created_at')
    search_fields = ('first_name', 'last_name', 'phone', 'email')
    list_filter = ('gender', 'blood_group')
    ordering = ('last_name', 'first_name')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'doctor', 'date', 'time_slot', 'status', 'created_date')
    list_filter = ('status', 'date', 'doctor__department')
    search_fields = ('patient__first_name', 'patient__last_name', 'patient__phone', 'doctor__name')
    list_editable = ('status',)
    date_hierarchy = 'date'
    ordering = ('-date', 'time_slot')


@admin.register(MedicalReport)
class MedicalReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'doctor', 'report_date', 'created_at')
    search_fields = ('patient__first_name', 'patient__last_name', 'diagnosis', 'prescription')
    list_filter = ('report_date', 'doctor__department')
    ordering = ('-report_date',)
