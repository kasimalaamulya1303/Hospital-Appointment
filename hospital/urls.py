from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('doctors/', views.doctor_list, name='doctor_list'),
    path('book-appointment/', views.book_appointment, name='book_appointment'),
    path('appointment-success/<int:appointment_id>/', views.appointment_success, name='appointment_success'),
    path('patient-dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('cancel-appointment/<int:appointment_id>/', views.cancel_appointment_patient, name='cancel_appointment_patient'),
    path('medical-report/<int:report_id>/', views.medical_report_detail, name='medical_report_detail'),
    
    # Staff / Admin routes
    path('staff/login/', views.staff_login, name='staff_login'),
    path('staff/logout/', views.staff_logout, name='staff_logout'),
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/appointment/<int:appointment_id>/status/', views.staff_update_appointment_status, name='staff_update_status'),
    path('staff/appointment/<int:appointment_id>/report/', views.staff_create_report, name='staff_create_report'),
    
    # Dynamic slot availability API
    path('api/available-slots/', views.get_available_slots, name='get_available_slots'),
]
