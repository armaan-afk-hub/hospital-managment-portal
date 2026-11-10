from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta, time
from .models import Doctor, Appointment

class HospitalSystemTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Admin User
        self.admin = User.objects.create_superuser('admin_test', 'admin@test.com', 'adminpass123')
        # Patient User
        self.patient1 = User.objects.create_user('patient_test1', 'p1@test.com', 'patientpass123')
        self.patient2 = User.objects.create_user('patient_test2', 'p2@test.com', 'patientpass123')
        # Sample Doctor
        self.doctor = Doctor.objects.create(
            name='Dr. Arjun Sharma',
            specialization='Cardiology',
            available_days='Monday, Wednesday, Friday'
        )

    def test_landing_page(self):
        """Landing page should load with status 200."""
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your Health, Our Priority")

    def test_doctors_page(self):
        """Doctors page should display existing doctors."""
        response = self.client.get(reverse('doctors'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dr. Arjun Sharma")
        self.assertContains(response, "Cardiology")

    def test_patient_registration(self):
        """Test patient registration flow."""
        response = self.client.post(reverse('register'), {
            'username': 'newpatient',
            'email': 'new@patient.com',
            'password': 'password123',
            'confirm_password': 'password123',
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username='newpatient').exists())

    def test_appointment_booking_and_isolation(self):
        """Test booking an appointment and verifying that patient only sees their own."""
        self.client.login(username='patient_test1', password='patientpass123')
        future_date = timezone.localdate() + timedelta(days=2)
        response = self.client.post(reverse('book_appointment'), {
            'doctor': self.doctor.id,
            'appointment_date': future_date.strftime('%Y-%m-%d'),
            'appointment_time': '10:00',
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Appointment.objects.filter(patient=self.patient1).count(), 1)

        # Login as patient2 and verify appointment of patient1 is not visible
        self.client.logout()
        self.client.login(username='patient_test2', password='patientpass123')
        response = self.client.get(reverse('appointments'))
        self.assertNotContains(response, "patient_test1")
        self.assertEqual(response.context['appointments'].count(), 0)

    def test_past_date_appointment_validation(self):
        """Past dates must be rejected by backend form validation."""
        self.client.login(username='patient_test1', password='patientpass123')
        past_date = timezone.localdate() - timedelta(days=2)
        response = self.client.post(reverse('book_appointment'), {
            'doctor': self.doctor.id,
            'appointment_date': past_date.strftime('%Y-%m-%d'),
            'appointment_time': '10:00',
        }, follow=True)
        # Should not create appointment
        self.assertEqual(Appointment.objects.count(), 0)

    def test_admin_dashboard_metrics(self):
        """Admin dashboard should calculate correct ORM counts."""
        self.client.login(username='admin_test', password='adminpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_doctors'], 1)
        self.assertEqual(response.context['total_patients'], 2)
