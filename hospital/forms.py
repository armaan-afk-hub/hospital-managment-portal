from django import forms
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Doctor, Appointment
import datetime

class PatientRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter Password'})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter Email Address'}),
        }

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match!")
        return confirm_password

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("Email is required.")
        return email

class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['name', 'specialization', 'available_days']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Dr. Ramesh Patel'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Cardiology'}),
            'available_days': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Monday, Wednesday, Friday'}),
        }

class AppointmentBookingForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor', 'appointment_date', 'appointment_time']
        widgets = {
            'doctor': forms.Select(attrs={'class': 'form-select'}),
            'appointment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'id': 'appointment_date'}),
            'appointment_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control', 'id': 'appointment_time'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        appointment_date = cleaned_data.get('appointment_date')
        appointment_time = cleaned_data.get('appointment_time')

        if appointment_date:
            today = timezone.localdate()
            if appointment_date < today:
                self.add_error('appointment_date', 'Appointment date cannot be in the past.')

            if appointment_date == today and appointment_time:
                current_time = timezone.localtime().time()
                if appointment_time < current_time:
                    self.add_error('appointment_time', 'Appointment time cannot be in the past for today.')

        return cleaned_data

