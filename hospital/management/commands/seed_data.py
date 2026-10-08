import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from hospital.models import Doctor, Patient, Appointment, MedicalReport

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds database with realistic doctors, patients, appointments, and medical reports'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting database seed...'))

        # 1. Superuser
        admin_user, created = User.objects.get_or_create(username='admin', defaults={'email': 'admin@hospital.com', 'is_staff': True, 'is_superuser': True})
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("Created admin user: admin / admin123"))
        else:
            admin_user.set_password('admin123')
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("Updated admin password: admin / admin123"))

        # 2. Doctors
        doctors_data = [
            {
                'name': 'Dr. Marcus Vance',
                'department': 'Cardiology',
                'specialization': 'Interventional Cardiology & Angioplasty',
                'consultation_fee': 650.00,
                'available_days': 'Mon - Fri',
                'active_status': True,
                'email': 'm.vance@hospital.com',
                'phone': '+1 (555) 201-1001',
                'experience_years': 15,
                'qualification': 'MD, FACC, FSCAI',
                'bio': 'Board-certified cardiologist specializing in coronary interventions, cardiac catheterization, and preventative cardiovascular health.'
            },
            {
                'name': 'Dr. Sophia Chen',
                'department': 'Cardiology',
                'specialization': 'Cardiac Electrophysiology & Arrhythmia',
                'consultation_fee': 580.00,
                'available_days': 'Mon, Wed, Fri',
                'active_status': True,
                'email': 's.chen@hospital.com',
                'phone': '+1 (555) 201-1002',
                'experience_years': 11,
                'qualification': 'MD, FHRS',
                'bio': 'Expert in heart rhythm disorders, radiofrequency ablation, pacemaker and ICD implantations.'
            },
            {
                'name': 'Dr. Elena Rostova',
                'department': 'Pediatrics',
                'specialization': 'General Pediatrics & Child Development',
                'consultation_fee': 450.00,
                'available_days': 'Mon - Sat',
                'active_status': True,
                'email': 'e.rostova@hospital.com',
                'phone': '+1 (555) 201-1003',
                'experience_years': 12,
                'qualification': 'MD, FAAP',
                'bio': 'Passionate about comprehensive pediatric healthcare, child immunization, developmental milestone monitoring, and wellness.'
            },
            {
                'name': 'Dr. David Kim',
                'department': 'Pediatrics',
                'specialization': 'Pediatric Pulmonology & Allergy',
                'consultation_fee': 500.00,
                'available_days': 'Tue, Thu, Sat',
                'active_status': True,
                'email': 'd.kim@hospital.com',
                'phone': '+1 (555) 201-1004',
                'experience_years': 9,
                'qualification': 'MD, Pediatric Fellowship',
                'bio': 'Focuses on childhood asthma, chronic respiratory illnesses, pediatric allergic conditions, and neonatal care.'
            },
            {
                'name': 'Dr. Robert Miller',
                'department': 'Orthopedics',
                'specialization': 'Joint Replacement & Arthroscopic Surgery',
                'consultation_fee': 700.00,
                'available_days': 'Mon - Fri',
                'active_status': True,
                'email': 'r.miller@hospital.com',
                'phone': '+1 (555) 201-1005',
                'experience_years': 18,
                'qualification': 'MS, MCh (Orth)',
                'bio': 'Pioneer in minimally invasive total knee and hip replacements, sports medicine, and rotator cuff repairs.'
            },
            {
                'name': 'Dr. Aisha Patel',
                'department': 'Orthopedics',
                'specialization': 'Spine Surgery & Complex Trauma',
                'consultation_fee': 620.00,
                'available_days': 'Mon, Wed, Fri',
                'active_status': True,
                'email': 'a.patel@hospital.com',
                'phone': '+1 (555) 201-1006',
                'experience_years': 10,
                'qualification': 'MS (Ortho), Spine Fellow',
                'bio': 'Specialist in cervical and lumbar spine disorders, disc herniation, spinal stenosis, and musculoskeletal trauma.'
            },
            {
                'name': 'Dr. Julian Thorne',
                'department': 'Neurology',
                'specialization': 'Stroke Management & Neurodegenerative Disorders',
                'consultation_fee': 750.00,
                'available_days': 'Mon - Fri',
                'active_status': True,
                'email': 'j.thorne@hospital.com',
                'phone': '+1 (555) 201-1007',
                'experience_years': 16,
                'qualification': 'MD, DM (Neuro), FAAN',
                'bio': 'Specializing in hyper-acute stroke intervention, Parkinson disease, movement disorders, and comprehensive neurological evaluations.'
            },
            {
                'name': 'Dr. Maya Lin',
                'department': 'Neurology',
                'specialization': 'Epilepsy, Migraine & Neuropathy',
                'consultation_fee': 550.00,
                'available_days': 'Tue, Thu, Sat',
                'active_status': True,
                'email': 'm.lin@hospital.com',
                'phone': '+1 (555) 201-1008',
                'experience_years': 8,
                'qualification': 'MD, Neurology Fellowship',
                'bio': 'Focuses on intractable migraine, seizure disorders, EEG interpretations, and peripheral neuropathies.'
            },
            {
                'name': 'Dr. William Hayes',
                'department': 'General Medicine',
                'specialization': 'Internal Medicine & Chronic Disease Care',
                'consultation_fee': 400.00,
                'available_days': 'Mon - Sat',
                'active_status': True,
                'email': 'w.hayes@hospital.com',
                'phone': '+1 (555) 201-1009',
                'experience_years': 20,
                'qualification': 'MD (Internal Medicine)',
                'bio': 'Primary care specialist dedicated to hypertension, diabetes management, preventive adult health check-ups, and geriatrics.'
            },
        ]

        created_doctors = []
        for d in doctors_data:
            doc, _ = Doctor.objects.update_or_create(email=d['email'], defaults=d)
            created_doctors.append(doc)
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(created_doctors)} doctors across all required departments."))

        # 3. Patients
        patients_data = [
            {
                'first_name': 'Jonathan',
                'last_name': 'Davis',
                'email': 'jdavis@example.com',
                'phone': '5550101',
                'age': 45,
                'gender': 'Male',
                'blood_group': 'O+',
                'address': '742 Evergreen Terrace, Springfield'
            },
            {
                'first_name': 'Emily',
                'last_name': 'Parker',
                'email': 'eparker@example.com',
                'phone': '5550102',
                'age': 29,
                'gender': 'Female',
                'blood_group': 'A+',
                'address': '124 Conch Street, Riverdale'
            },
            {
                'first_name': 'Michael',
                'last_name': 'Zhang',
                'email': 'mzhang@example.com',
                'phone': '5550103',
                'age': 63,
                'gender': 'Male',
                'blood_group': 'B+',
                'address': '89 Maple Road, Oakwood'
            },
            {
                'first_name': 'Sarah',
                'last_name': 'Jenkins',
                'email': 'sjenkins@example.com',
                'phone': '5550104',
                'age': 8,
                'gender': 'Female',
                'blood_group': 'AB+',
                'address': '302 Pine Ridge, Meadowlands'
            },
            {
                'first_name': 'Olivia',
                'last_name': 'Adams',
                'email': 'oadams@example.com',
                'phone': '5550105',
                'age': 34,
                'gender': 'Female',
                'blood_group': 'O-',
                'address': '55 Cedar Blvd, Hillcrest'
            },
        ]

        created_patients = []
        for p in patients_data:
            patient, _ = Patient.objects.update_or_create(phone=p['phone'], defaults=p)
            created_patients.append(patient)
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(created_patients)} patients."))

        # 4. Appointments & Medical Reports
        today = date.today()
        tomorrow = today + timedelta(days=1)
        next_week = today + timedelta(days=4)
        past_week = today - timedelta(days=5)
        past_month = today - timedelta(days=18)

        # Appointments dataset
        appointments_data = [
            # Upcoming Confirmed
            {
                'patient': created_patients[0],  # Jonathan Davis
                'doctor': created_doctors[0],    # Dr. Marcus Vance (Cardio)
                'date': tomorrow,
                'time_slot': '10:00 AM',
                'reason': 'Routine annual cardiac stress test and blood pressure follow-up.',
                'status': 'Confirmed',
            },
            # Upcoming Pending
            {
                'patient': created_patients[1],  # Emily Parker
                'doctor': created_doctors[4],    # Dr. Robert Miller (Ortho)
                'date': next_week,
                'time_slot': '11:00 AM',
                'reason': 'Persistent right knee pain after marathon training.',
                'status': 'Pending',
            },
            # Upcoming Confirmed
            {
                'patient': created_patients[2],  # Michael Zhang
                'doctor': created_doctors[6],    # Dr. Julian Thorne (Neuro)
                'date': today,
                'time_slot': '02:30 PM',
                'reason': 'Experiencing recurring dizziness and minor numbness in fingertips.',
                'status': 'Confirmed',
            },
            # Upcoming Pending
            {
                'patient': created_patients[3],  # Sarah Jenkins (Child)
                'doctor': created_doctors[2],    # Dr. Elena Rostova (Pediatrics)
                'date': tomorrow,
                'time_slot': '09:30 AM',
                'reason': 'Seasonal allergy flare-up and persistent cough for 4 days.',
                'status': 'Pending',
            },
            # Past Completed (with report)
            {
                'patient': created_patients[0],  # Jonathan Davis
                'doctor': created_doctors[0],    # Dr. Marcus Vance (Cardio)
                'date': past_week,
                'time_slot': '09:00 AM',
                'reason': 'Evaluation of mild palpitations during exercise.',
                'status': 'Completed',
            },
            # Past Completed (with report)
            {
                'patient': created_patients[4],  # Olivia Adams
                'doctor': created_doctors[7],    # Dr. Maya Lin (Neuro)
                'date': past_month,
                'time_slot': '03:00 PM',
                'reason': 'Severe chronic migraines and visual aura symptoms.',
                'status': 'Completed',
            },
            # Cancelled
            {
                'patient': created_patients[1],  # Emily Parker
                'doctor': created_doctors[1],    # Dr. Sophia Chen
                'date': today,
                'time_slot': '04:00 PM',
                'reason': 'Patient had conflicting work travel schedule.',
                'status': 'Cancelled',
            },
        ]

        created_appointments = []
        for appt_dict in appointments_data:
            # Check if appointment exists
            appt = Appointment.objects.filter(
                doctor=appt_dict['doctor'],
                date=appt_dict['date'],
                time_slot=appt_dict['time_slot']
            ).first()

            if not appt:
                appt = Appointment.objects.create(**appt_dict)
            else:
                appt.patient = appt_dict['patient']
                appt.reason = appt_dict['reason']
                appt.status = appt_dict['status']
                appt.save()
            created_appointments.append(appt)

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(created_appointments)} appointments with various statuses."))

        # 5. Medical Reports for Completed Appointments
        # Report 1 for Jonathan Davis
        appt1 = created_appointments[4]
        if not hasattr(appt1, 'medical_report') or appt1.medical_report is None:
            MedicalReport.objects.create(
                appointment=appt1,
                patient=appt1.patient,
                doctor=appt1.doctor,
                diagnosis='Mild Sinus Tachycardia with benign ventricular ectopy. Normal resting ECG and normal left ventricular ejection fraction (62%).',
                prescription='1. Metoprolol Tartrate 25mg - 1 tablet once daily morning after breakfast (30 days)\n2. CoQ10 100mg - 1 capsule daily after lunch\n3. Electrolyte hydration powder daily.',
                doctor_notes='Reduce caffeine intake to < 1 cup/day. Hydrate with minimum 2.5L water daily. Repeat echocardiogram in 6 months.',
                report_date=appt1.date
            )
            self.stdout.write(self.style.SUCCESS(f"Created Medical Report for Appointment #{appt1.id}"))

        # Report 2 for Olivia Adams
        appt2 = created_appointments[5]
        if not hasattr(appt2, 'medical_report') or appt2.medical_report is None:
            MedicalReport.objects.create(
                appointment=appt2,
                patient=appt2.patient,
                doctor=appt2.doctor,
                diagnosis='Episodic Migraine with Typical Aura. Cervical muscle tension contributing to occipital headaches.',
                prescription='1. Rizatriptan 10mg - Take 1 tablet at earliest onset of migraine aura (max 2/24hrs)\n2. Magnesium Glycinate 400mg - 1 tablet every night before sleep\n3. Vitamin B2 (Riboflavin) 400mg daily morning.',
                doctor_notes='Maintain a migraine headache diary. Limit blue light exposure after 9 PM. Consider neck physical therapy sessions.',
                report_date=appt2.date
            )
            self.stdout.write(self.style.SUCCESS(f"Created Medical Report for Appointment #{appt2.id}"))

        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))
