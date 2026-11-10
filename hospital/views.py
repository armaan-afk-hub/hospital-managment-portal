from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Doctor, Appointment
from .forms import PatientRegistrationForm, DoctorForm, AppointmentBookingForm

def index(request):
    """Landing Page with Hero Section, Navbar, and Footer."""
    return render(request, 'index.html')

def register_view(request):
    """Patient Registration View."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            login(request, user)
            messages.success(request, f"Welcome to MediCare, {user.username}! Your account has been created.")
            return redirect('dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    else:
        form = PatientRegistrationForm()

    return render(request, 'register.html', {'form': form})

def login_view(request):
    """Patient and Admin Login View."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'login.html')

def logout_view(request):
    """User Logout View."""
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('index')

@login_required
def dashboard(request):
    """Dashboard view for both Admin and Patients."""
    if request.user.is_staff:
        # Admin statistics using Django ORM count queries
        total_doctors = Doctor.objects.count()
        total_patients = User.objects.filter(is_staff=False).count()
        total_appointments = Appointment.objects.count()
        pending_appointments = Appointment.objects.filter(status='Pending').count()
        recent_appointments = Appointment.objects.select_related('patient', 'doctor').order_by('-id')[:5]

        context = {
            'is_admin': True,
            'total_doctors': total_doctors,
            'total_patients': total_patients,
            'total_appointments': total_appointments,
            'pending_appointments': pending_appointments,
            'recent_appointments': recent_appointments,
        }
    else:
        # Patient specific data
        my_appointments = Appointment.objects.filter(patient=request.user).select_related('doctor').order_by('-appointment_date', '-appointment_time')
        total_my_appointments = my_appointments.count()
        pending_my_appointments = my_appointments.filter(status='Pending').count()
        confirmed_my_appointments = my_appointments.filter(status='Confirmed').count()
        doctors = Doctor.objects.all()[:4]

        context = {
            'is_admin': False,
            'total_my_appointments': total_my_appointments,
            'pending_my_appointments': pending_my_appointments,
            'confirmed_my_appointments': confirmed_my_appointments,
            'recent_appointments': my_appointments[:5],
            'doctors': doctors,
        }

    return render(request, 'dashboard.html', context)

def doctors_list(request):
    """View all doctors; allow Admin to add/manage doctors."""
    doctors = Doctor.objects.all()
    form = DoctorForm()
    return render(request, 'doctors.html', {'doctors': doctors, 'form': form})

@login_required
def add_doctor(request):
    """Admin-only view to add a new doctor."""
    if not request.user.is_staff:
        messages.error(request, "Unauthorized access. Admin privileges required.")
        return redirect('doctors')

    if request.method == 'POST':
        form = DoctorForm(request.POST)
        if form.is_valid():
            doctor = form.save()
            messages.success(request, f"Doctor {doctor.name} added successfully.")
        else:
            messages.error(request, "Please correct the errors in the doctor form.")
    return redirect('doctors')

@login_required
def edit_doctor(request, doctor_id):
    """Admin-only view to edit doctor details."""
    if not request.user.is_staff:
        messages.error(request, "Unauthorized access. Admin privileges required.")
        return redirect('doctors')

    doctor = get_object_or_404(Doctor, id=doctor_id)
    if request.method == 'POST':
        form = DoctorForm(request.POST, instance=doctor)
        if form.is_valid():
            form.save()
            messages.success(request, f"Doctor {doctor.name} updated successfully.")
            return redirect('doctors')
        else:
            messages.error(request, "Please correct the form errors.")
    else:
        form = DoctorForm(instance=doctor)

    return render(request, 'doctors.html', {
        'doctors': Doctor.objects.all(),
        'edit_doctor': doctor,
        'edit_form': form,
    })

@login_required
def delete_doctor(request, doctor_id):
    """Admin-only view to delete a doctor."""
    if not request.user.is_staff:
        messages.error(request, "Unauthorized access. Admin privileges required.")
        return redirect('doctors')

    if request.method == 'POST':
        doctor = get_object_or_404(Doctor, id=doctor_id)
        doctor_name = doctor.name
        doctor.delete()
        messages.success(request, f"Doctor {doctor_name} deleted successfully.")
    return redirect('doctors')

@login_required
def appointments_view(request):
    """Appointments list and booking form."""
    initial_data = {}
    selected_doctor_id = request.GET.get('doctor')
    if selected_doctor_id:
        initial_data['doctor'] = selected_doctor_id

    form = AppointmentBookingForm(initial=initial_data)

    if request.user.is_staff:
        appointments = Appointment.objects.select_related('patient', 'doctor').order_by('-appointment_date', '-appointment_time')
    else:
        appointments = Appointment.objects.filter(patient=request.user).select_related('doctor').order_by('-appointment_date', '-appointment_time')

    return render(request, 'appointments.html', {
        'appointments': appointments,
        'form': form,
        'is_admin': request.user.is_staff,
    })

@login_required
def book_appointment(request):
    """Patient books a new appointment."""
    if request.method == 'POST':
        form = AppointmentBookingForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user
            appointment.status = 'Pending'
            appointment.save()
            messages.success(request, "Your appointment has been booked successfully!")
            return redirect('appointments')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    return redirect('appointments')

@login_required
def cancel_appointment(request, appointment_id):
    """Cancel an appointment (patient can cancel their own, admin can cancel any)."""
    if request.method == 'POST':
        if request.user.is_staff:
            appointment = get_object_or_404(Appointment, id=appointment_id)
        else:
            # Enforce that patients can only cancel their own appointments
            appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)

        appointment.status = 'Cancelled'
        appointment.save()
        messages.success(request, f"Appointment #{appointment.id} has been cancelled.")
    return redirect('appointments')

@login_required
def confirm_appointment(request, appointment_id):
    """Admin-only view to confirm pending appointments."""
    if not request.user.is_staff:
        messages.error(request, "Unauthorized action.")
        return redirect('appointments')

    if request.method == 'POST':
        appointment = get_object_or_404(Appointment, id=appointment_id)
        appointment.status = 'Confirmed'
        appointment.save()
        messages.success(request, f"Appointment #{appointment.id} confirmed.")
    return redirect('appointments')
