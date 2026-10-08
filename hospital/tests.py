from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from hospital.models import Doctor, Patient, Appointment, MedicalReport

User = get_user_model()


class HospitalPortalTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.doctor = Doctor.objects.create(
            name='Dr. Test Cardiologist',
            department='Cardiology',
            specialization='Heart Surgery',
            consultation_fee=500.00,
            available_days='Mon - Fri',
            active_status=True,
            email='testcardio@hospital.com'
        )
        self.patient = Patient.objects.create(
            first_name='Alice',
            last_name='Smith',
            email='alice@example.com',
            phone='1234567890',
            age=30,
            gender='Female'
        )
        self.user = User.objects.create_user(username='staffuser', password='password123', is_staff=True)

    def test_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AuraCare')

    def test_doctor_list_view(self):
        response = self.client.get(reverse('doctor_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dr. Test Cardiologist')
        self.assertContains(response, 'Cardiology')

    def test_doctor_department_filtering(self):
        Doctor.objects.create(
            name='Dr. Test Pediatrician',
            department='Pediatrics',
            specialization='Child Care',
            consultation_fee=400.00,
            active_status=True
        )
        response = self.client.get(reverse('doctor_list'), {'department': 'Cardiology'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dr. Test Cardiologist')
        self.assertNotContains(response, 'Dr. Test Pediatrician')

    def test_available_slots_api(self):
        target_date = (date.today() + timedelta(days=2)).isoformat()
        response = self.client.get(reverse('get_available_slots'), {
            'doctor_id': self.doctor.id,
            'date': target_date
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['doctor_id'], self.doctor.id)
        self.assertIn('09:00 AM', data['available_slots'])
        self.assertEqual(data['booked_slots'], [])

    def test_book_appointment_and_prevent_double_booking(self):
        target_date = date.today() + timedelta(days=3)
        time_slot = '10:00 AM'

        # First booking succeeds
        booking_data = {
            'doctor': self.doctor.id,
            'date': target_date.isoformat(),
            'time_slot': time_slot,
            'reason': 'Routine heart checkup',
            'first_name': 'Alice',
            'last_name': 'Smith',
            'email': 'alice@example.com',
            'phone': '1234567890',
            'age': 30,
            'gender': 'Female'
        }
        response = self.client.post(reverse('book_appointment'), booking_data)
        self.assertEqual(response.status_code, 302)  # Redirects to success
        self.assertEqual(Appointment.objects.count(), 1)
        appt = Appointment.objects.first()
        self.assertEqual(appt.status, 'Pending')
        self.assertEqual(appt.time_slot, time_slot)

        # Attempt to double-book the exact same doctor, date, and slot
        double_booking_data = {
            'doctor': self.doctor.id,
            'date': target_date.isoformat(),
            'time_slot': time_slot,
            'reason': 'Second patient trying same slot',
            'first_name': 'Bob',
            'last_name': 'Jones',
            'email': 'bob@example.com',
            'phone': '9876543210',
            'age': 40,
            'gender': 'Male'
        }
        res_conflict = self.client.post(reverse('book_appointment'), double_booking_data)
        # Should NOT redirect, should re-render form with error
        self.assertEqual(res_conflict.status_code, 200)
        self.assertEqual(Appointment.objects.count(), 1)  # No second booking created

    def test_reject_past_date_booking(self):
        past_date = date.today() - timedelta(days=2)
        booking_data = {
            'doctor': self.doctor.id,
            'date': past_date.isoformat(),
            'time_slot': '09:00 AM',
            'reason': 'Check past date',
            'first_name': 'Alice',
            'last_name': 'Smith',
            'email': 'alice@example.com',
            'phone': '1234567890',
            'age': 30,
            'gender': 'Female'
        }
        response = self.client.post(reverse('book_appointment'), booking_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Appointment.objects.count(), 0)

    def test_patient_dashboard_lookup(self):
        appt = Appointment.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            date=date.today() + timedelta(days=1),
            time_slot='09:00 AM',
            reason='Follow up',
            status='Confirmed'
        )
        response = self.client.get(reverse('patient_dashboard'), {'query': self.patient.phone})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.patient.full_name)
        self.assertContains(response, 'Confirmed')

    def test_staff_update_status(self):
        appt = Appointment.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            date=date.today() + timedelta(days=1),
            time_slot='09:00 AM',
            reason='Consultation',
            status='Pending'
        )
        self.client.login(username='staffuser', password='password123')
        response = self.client.post(reverse('staff_update_status', args=[appt.id]), {'status': 'Confirmed'})
        self.assertEqual(response.status_code, 302)
        appt.refresh_from_db()
        self.assertEqual(appt.status, 'Confirmed')
