from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q, Count
from datetime import date, datetime

from .models import Doctor, Patient, Appointment, MedicalReport
from .forms import (
    AppointmentBookingForm,
    AppointmentStatusUpdateForm,
    MedicalReportForm,
    PatientLookupForm
)


def home(request):
    """Landing page with hospital overview, quick stats, and featured doctors."""
    featured_doctors = Doctor.objects.filter(active_status=True)[:4]
    total_doctors = Doctor.objects.filter(active_status=True).count()
    total_patients = Patient.objects.count()
    total_appointments = Appointment.objects.count()
    departments_count = Doctor.objects.values('department').distinct().count()

    context = {
        'featured_doctors': featured_doctors,
        'total_doctors': total_doctors,
        'total_patients': total_patients,
        'total_appointments': total_appointments,
        'departments_count': departments_count,
    }
    return render(request, 'hospital/home.html', context)


def doctor_list(request):
    """
    Doctor list/search/filter page.
    Supports server-side filtering as fallback and provides data attributes
    for snappy client-side JavaScript filtering across Cardiology, Pediatrics,
    Orthopedics, Neurology, and General Medicine.
    """
    department_filter = request.GET.get('department', '').strip()
    search_query = request.GET.get('q', '').strip()

    doctors = Doctor.objects.filter(active_status=True)

    if department_filter and department_filter.lower() != 'all':
        doctors = doctors.filter(department__iexact=department_filter)

    if search_query:
        doctors = doctors.filter(
            Q(name__icontains=search_query) |
            Q(specialization__icontains=search_query) |
            Q(department__icontains=search_query)
        )

    # Department list with counts for UI badges
    all_active = Doctor.objects.filter(active_status=True)
    department_list = [
        {'name': 'All', 'count': all_active.count()},
        {'name': 'Cardiology', 'count': all_active.filter(department='Cardiology').count()},
        {'name': 'Pediatrics', 'count': all_active.filter(department='Pediatrics').count()},
        {'name': 'Orthopedics', 'count': all_active.filter(department='Orthopedics').count()},
        {'name': 'Neurology', 'count': all_active.filter(department='Neurology').count()},
        {'name': 'General Medicine', 'count': all_active.filter(department='General Medicine').count()},
    ]

    context = {
        'doctors': doctors,
        'selected_department': department_filter or 'All',
        'search_query': search_query,
        'department_list': department_list,
    }
    return render(request, 'hospital/doctor_list.html', context)


def book_appointment(request):
    """
    Appointment creation page with form validation, dynamic slot checking,
    and automated patient creation or lookup.
    """
    initial_doctor_id = request.GET.get('doctor')
    initial_doctor = None
    if initial_doctor_id:
        try:
            initial_doctor = Doctor.objects.get(id=initial_doctor_id, active_status=True)
        except Doctor.DoesNotExist:
            initial_doctor = None

    if request.method == 'POST':
        form = AppointmentBookingForm(request.POST)
        if form.is_valid():
            cleaned = form.cleaned_data
            
            # Find or create patient record by phone
            patient, created = Patient.objects.get_or_create(
                phone=cleaned['phone'],
                defaults={
                    'first_name': cleaned['first_name'],
                    'last_name': cleaned['last_name'],
                    'email': cleaned['email'],
                    'age': cleaned['age'],
                    'gender': cleaned['gender'],
                }
            )
            
            # If patient existed, update details if provided
            if not created:
                patient.first_name = cleaned['first_name']
                patient.last_name = cleaned['last_name']
                patient.email = cleaned['email']
                if cleaned['age']:
                    patient.age = cleaned['age']
                patient.gender = cleaned['gender']
                patient.save()

            # Create appointment
            appointment = Appointment(
                patient=patient,
                doctor=cleaned['doctor'],
                date=cleaned['date'],
                time_slot=cleaned['time_slot'],
                reason=cleaned['reason'],
                status='Pending'
            )
            appointment.save()

            # Store patient ID in session for immediate dashboard access
            request.session['current_patient_id'] = patient.id
            request.session['current_patient_phone'] = patient.phone

            messages.success(
                request,
                f"Appointment booked successfully with {appointment.doctor.name} on {appointment.date} at {appointment.time_slot}! Status: Pending."
            )
            return redirect('appointment_success', appointment_id=appointment.id)
        else:
            messages.error(request, "Please review the form errors below and ensure the chosen slot is available.")
    else:
        initial_data = {}
        if initial_doctor:
            initial_data['doctor'] = initial_doctor
        # Pre-fill patient info from session if available
        if 'current_patient_id' in request.session:
            try:
                p = Patient.objects.get(id=request.session['current_patient_id'])
                initial_data.update({
                    'first_name': p.first_name,
                    'last_name': p.last_name,
                    'email': p.email,
                    'phone': p.phone,
                    'age': p.age,
                    'gender': p.gender,
                })
            except Patient.DoesNotExist:
                pass
        form = AppointmentBookingForm(initial=initial_data)

    active_doctors = Doctor.objects.filter(active_status=True)
    time_slots = [choice[0] for choice in Appointment.TIME_SLOT_CHOICES]

    context = {
        'form': form,
        'doctors': active_doctors,
        'time_slots': time_slots,
        'selected_doctor': initial_doctor,
        'today_date': date.today().isoformat(),
    }
    return render(request, 'hospital/book_appointment.html', context)


def appointment_success(request, appointment_id):
    """Confirmation page shown right after a booking."""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    return render(request, 'hospital/appointment_success.html', {'appointment': appointment})


def patient_dashboard(request):
    """
    Patient dashboard showing upcoming and past appointments,
    plus medical reports. Supports lookup by phone/email.
    """
    query = request.GET.get('query', '').strip()
    session_patient_id = request.session.get('current_patient_id')
    
    patient = None
    patients_list = []

    if query:
        # Search by phone or email
        patients = Patient.objects.filter(Q(phone__icontains=query) | Q(email__iexact=query))
        if patients.count() == 1:
            patient = patients.first()
            request.session['current_patient_id'] = patient.id
        elif patients.count() > 1:
            patients_list = patients
    elif session_patient_id:
        try:
            patient = Patient.objects.get(id=session_patient_id)
        except Patient.DoesNotExist:
            patient = None

    appointments = []
    upcoming_appointments = []
    past_appointments = []
    medical_reports = []

    if patient:
        appointments = Appointment.objects.filter(patient=patient).select_related('doctor')
        today = date.today()
        upcoming_appointments = appointments.filter(date__gte=today).exclude(status='Cancelled').order_by('date', 'time_slot')
        past_appointments = appointments.filter(Q(date__lt=today) | Q(status__in=['Completed', 'Cancelled'])).order_by('-date', '-time_slot')
        medical_reports = MedicalReport.objects.filter(patient=patient).select_related('doctor', 'appointment')

    context = {
        'patient': patient,
        'patients_list': patients_list,
        'query': query,
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments,
        'medical_reports': medical_reports,
        'today': date.today(),
    }
    return render(request, 'hospital/patient_dashboard.html', context)


@require_POST
def cancel_appointment_patient(request, appointment_id):
    """Allow a patient to cancel their upcoming appointment."""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Ensure status is not already completed or cancelled
    if appointment.status in ['Completed', 'Cancelled']:
        messages.warning(request, f"Cannot cancel an appointment that is already {appointment.status.lower()}.")
    else:
        appointment.status = 'Cancelled'
        appointment.save()
        messages.success(request, f"Appointment #{appointment.id} has been cancelled.")

    return redirect('patient_dashboard')


def medical_report_detail(request, report_id):
    """View a detailed medical report with diagnosis and prescription."""
    report = get_object_or_404(MedicalReport.objects.select_related('patient', 'doctor', 'appointment'), id=report_id)
    return render(request, 'hospital/medical_report_detail.html', {'report': report})


# =========================================================
# Admin / Staff Views & Workflow
# =========================================================

def staff_login(request):
    """Login view for hospital staff/admin."""
    if request.user.is_authenticated:
        return redirect('staff_dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('staff_dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'hospital/staff_login.html', {'form': form})


def staff_logout(request):
    """Logout view for hospital staff."""
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')


@login_required
def staff_dashboard(request):
    """
    Staff / Admin appointment management dashboard.
    Enables status updates (Pending -> Confirmed -> Completed / Cancelled),
    filtering by status and doctor, and creating medical reports.
    """
    status_filter = request.GET.get('status', 'All')
    doctor_filter = request.GET.get('doctor', 'All')
    search_query = request.GET.get('q', '').strip()
    date_filter = request.GET.get('date', '').strip()

    appointments = Appointment.objects.all().select_related('patient', 'doctor', 'medical_report')

    if status_filter != 'All':
        appointments = appointments.filter(status=status_filter)

    if doctor_filter != 'All':
        appointments = appointments.filter(doctor_id=doctor_filter)

    if date_filter:
        appointments = appointments.filter(date=date_filter)

    if search_query:
        appointments = appointments.filter(
            Q(patient__first_name__icontains=search_query) |
            Q(patient__last_name__icontains=search_query) |
            Q(patient__phone__icontains=search_query) |
            Q(doctor__name__icontains=search_query)
        )

    # Statistics counters
    total_count = Appointment.objects.count()
    pending_count = Appointment.objects.filter(status='Pending').count()
    confirmed_count = Appointment.objects.filter(status='Confirmed').count()
    completed_count = Appointment.objects.filter(status='Completed').count()
    cancelled_count = Appointment.objects.filter(status='Cancelled').count()
    today_count = Appointment.objects.filter(date=date.today()).count()

    doctors = Doctor.objects.all()

    context = {
        'appointments': appointments,
        'status_filter': status_filter,
        'doctor_filter': doctor_filter,
        'search_query': search_query,
        'date_filter': date_filter,
        'doctors': doctors,
        'total_count': total_count,
        'pending_count': pending_count,
        'confirmed_count': confirmed_count,
        'completed_count': completed_count,
        'cancelled_count': cancelled_count,
        'today_count': today_count,
        'today_date': date.today(),
    }
    return render(request, 'hospital/staff_dashboard.html', context)


@login_required
@require_POST
def staff_update_appointment_status(request, appointment_id):
    """Staff action to quickly change status of an appointment."""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    new_status = request.POST.get('status')
    
    if new_status in dict(Appointment.STATUS_CHOICES):
        old_status = appointment.status
        appointment.status = new_status
        appointment.save()
        messages.success(request, f"Appointment #{appointment.id} updated from '{old_status}' to '{new_status}'.")
    else:
        messages.error(request, "Invalid status choice provided.")

    return redirect('staff_dashboard')


@login_required
def staff_create_report(request, appointment_id):
    """Staff / Doctor view to create or edit a medical report for an appointment."""
    appointment = get_object_or_404(Appointment.objects.select_related('patient', 'doctor'), id=appointment_id)
    
    # Check if report already exists
    report = getattr(appointment, 'medical_report', None)

    if request.method == 'POST':
        form = MedicalReportForm(request.POST, instance=report)
        if form.is_valid():
            report_instance = form.save(commit=False)
            report_instance.appointment = appointment
            report_instance.patient = appointment.patient
            report_instance.doctor = appointment.doctor
            report_instance.save()
            
            # Automatically mark appointment as Completed once report is filed
            if appointment.status != 'Completed':
                appointment.status = 'Completed'
                appointment.save()

            messages.success(request, f"Medical report for {appointment.patient.full_name} saved successfully.")
            return redirect('staff_dashboard')
    else:
        form = MedicalReportForm(instance=report, initial={'report_date': date.today()})

    context = {
        'form': form,
        'appointment': appointment,
        'is_edit': report is not None,
    }
    return render(request, 'hospital/staff_create_report.html', context)


# =========================================================
# JSON API View for dynamic slot availability
# =========================================================

def get_available_slots(request):
    """
    API endpoint: /api/available-slots/?doctor_id=X&date=YYYY-MM-DD
    Returns booked slots and remaining available slots for dynamic JS rendering.
    """
    doctor_id = request.GET.get('doctor_id')
    slot_date = request.GET.get('date')

    if not doctor_id or not slot_date:
        return JsonResponse({'error': 'doctor_id and date parameters are required.'}, status=400)

    try:
        doctor = Doctor.objects.get(id=doctor_id, active_status=True)
    except Doctor.DoesNotExist:
        return JsonResponse({'error': 'Doctor not found or inactive.'}, status=404)

    try:
        # Validate date format
        parsed_date = datetime.strptime(slot_date, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)

    all_slots = [choice[0] for choice in Appointment.TIME_SLOT_CHOICES]

    # Query active/non-cancelled bookings
    booked_slots = list(
        Appointment.objects.filter(
            doctor=doctor,
            date=parsed_date
        ).exclude(status='Cancelled').values_list('time_slot', flat=True)
    )

    available_slots = [s for s in all_slots if s not in booked_slots]

    return JsonResponse({
        'doctor_id': doctor.id,
        'doctor_name': doctor.name,
        'department': doctor.department,
        'date': slot_date,
        'all_slots': all_slots,
        'booked_slots': booked_slots,
        'available_slots': available_slots,
        'is_past_date': parsed_date < date.today(),
    })
