# AuraCare — Hospital & Patient Appointment Management Portal
**Django Full-Stack Capstone Project**

A modern, responsive hospital management portal where patients browse specialist doctors by department, book appointment slots with real-time double-booking prevention, and manage their clinical consultation history and medical reports, while hospital staff and administrators manage schedules and appointment statuses.

---

## 🌟 Key Features

### 1. Doctor Directory & Filtering
- **JavaScript Instant Filtering** across departments:
  - **Cardiology**
  - **Pediatrics**
  - **Orthopedics**
  - **Neurology**
  - **General Medicine**
- Real-time text search by doctor name, specialization, and clinical expertise.
- Doctor detail modal showcasing credentials, consultation fee, available days, and clinical bio.

### 2. Interactive Date & Time Slot Selection
- Visual time slot selector with **live slot status**:
  - 🟢 **Available Slots**: Clickable and responsive.
  - 🔴 **Booked Slots**: Disabled with "Booked" indicator.
- Dynamic slot checking via JSON API endpoint (`/api/available-slots/?doctor_id=X&date=YYYY-MM-DD`).
- **Zero Double-Booking Guarantee**: Server-side and client-side validation prevent duplicate bookings for the same doctor, date, and slot.
- Disallows past-date bookings.

### 3. Patient Dashboard
- Profile lookup by registered phone number or email address.
- Status badges:
  - <span style="color:#d97706; font-weight:bold;">Pending</span> (Amber)
  - <span style="color:#2563eb; font-weight:bold;">Confirmed</span> (Blue)
  - <span style="color:#16a34a; font-weight:bold;">Completed</span> (Green)
  - <span style="color:#dc2626; font-weight:bold;">Cancelled</span> (Red)
- Real-time appointment cancellation for upcoming visits.
- **Medical Reports & Prescriptions**: View complete clinical diagnoses, Rx medications with dosages, doctor notes, and printable slips.

### 4. Admin & Staff Workflow
- Protected staff operations dashboard (`/staff/dashboard/`).
- Quick one-click status transitions (`Confirm`, `Complete`, `Cancel`, `Reopen`).
- File or edit **Medical Reports** linked to appointments.
- Metric counters: Total bookings, Pending requests, Confirmed, Completed, Cancelled, and Today's schedule.
- Direct access to Django ORM Admin (`/admin/`).

---

## 🛠️ Technology Stack
- **Backend**: Python 3.11+, Django 6.1 (MVT architecture, Django ORM, ModelForms)
- **Database**: SQLite (`db.sqlite3` — Django default)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Bootstrap Icons
- **Production Server**: Gunicorn, WhiteNoise
- **Cloud Platform**: Render

---

## 📁 Project Structure

```
Amulya/
├── manage.py
├── requirements.txt
├── render.yaml
├── create_superuser.py
├── db.sqlite3
├── .gitignore
├── README.md
├── hospital_portal/           # Django Project Package
│   ├── __init__.py
│   ├── settings.py           # Production & dev configuration
│   ├── urls.py               # Main URL router
│   ├── wsgi.py               # WSGI application for Gunicorn
│   └── asgi.py
├── hospital/                  # Core Hospital Application
│   ├── admin.py              # Django admin registration
│   ├── apps.py
│   ├── forms.py              # ModelForms & validation
│   ├── models.py             # Doctor, Patient, Appointment, MedicalReport
│   ├── urls.py               # App routes
│   ├── views.py              # Business logic & views
│   ├── tests.py              # Unit & integration test suite
│   ├── management/
│   │   └── commands/
│   │       └── seed_data.py  # Realistic demo dataset seeder
│   └── templates/
│       └── hospital/
│           ├── base.html
│           ├── home.html
│           ├── doctor_list.html
│           ├── book_appointment.html
│           ├── appointment_success.html
│           ├── patient_dashboard.html
│           ├── medical_report_detail.html
│           ├── staff_login.html
│           ├── staff_dashboard.html
│           └── staff_create_report.html
└── static/
    ├── css/
    │   └── styles.css        # Custom medical design system
    ├── js/
    │   └── main.js           # Interactive filtering & slot selector
    └── images/
```

---

## 🚀 Local Development Setup

### 1. Activate the Virtual Environment
**Windows (PowerShell):**
```powershell
.\venv\Scripts\activate
```
**Linux / macOS:**
```bash
source venv/bin/activate
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Run Migrations & Seed Sample Data
```powershell
python manage.py migrate
python manage.py seed_data
```

> **Default Admin / Staff Credentials:**
> - **Username:** `admin`
> - **Password:** `admin123`

### 4. Run Automated Tests
```powershell
python manage.py test
```

### 5. Start Development Server
```powershell
python manage.py runserver
```
Open **`http://127.0.0.1:8000/`** in your browser.

---

## 🌐 Render Deployment Guide

### 1. Push to GitHub
Initialize your git repository and push to GitHub:
```bash
git init
git add .
git commit -m "Hospital & Patient Appointment Management Portal"
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
```

### 2. Create Render Web Service
1. Sign in to [Render](https://render.com/).
2. Click **New +** → **Web Service** (or use **Blueprint** with `render.yaml`).
3. Connect your GitHub repository.
4. Configure service settings:
   - **Environment:** `Python 3`
   - **Root Directory:** `.` (leave as repository root)
   - **Build Command:**
     ```bash
     pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate && python create_superuser.py
     ```
   - **Start Command:**
     ```bash
     python manage.py migrate && python create_superuser.py && gunicorn hospital_portal.wsgi:application
     ```
5. In **Environment Variables**, add:
   - `PYTHON_VERSION`: `3.11.0`
   - `RENDER`: `true`
   - `SECRET_KEY`: `your-random-production-secret-key`
   - *(Optional)* `DJANGO_SUPERUSER_USERNAME`: `admin`
   - *(Optional)* `DJANGO_SUPERUSER_PASSWORD`: `admin123`

### 3. Verify Live Deployment
1. Open the generated `https://<service-name>.onrender.com` URL.
2. Visit `/doctors/`, filter doctors, and book an appointment slot.
3. Access `/patient-dashboard/?query=5550101` to view Jonathan Davis's dashboard and medical report.
4. Log in at `/staff/login/` with `admin` / `admin123` to manage appointments.
5. Access `/admin/` to inspect Django's built-in administration console.

> **Note on Render SQLite Ephemeral Storage:**
> Render's free tier filesystem is ephemeral, meaning SQLite data resets if the instance sleeps or redeploys. The included `create_superuser.py` automatically initializes the superuser and seeds sample data during each deployment for a frictionless demonstration.

---

## 🔒 Security Checklist
- [x] Protected all POST forms with `{% csrf_token %}`.
- [x] Form-level and model-level validation preventing past-date bookings and double bookings.
- [x] Staff dashboard protected with `@login_required`.
- [x] Production `SECRET_KEY` pulled from environment variable.
- [x] `DEBUG` automatically disabled in production (`RENDER=true`).
- [x] `CSRF_TRUSTED_ORIGINS` configured for `https://*.onrender.com`.
