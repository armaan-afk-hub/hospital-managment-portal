// MediCare Hospital Management System - Vanilla JavaScript

document.addEventListener('DOMContentLoaded', function () {
    // 1. Auto-set minimum date for appointment booking to today
    const appointmentDateInput = document.getElementById('appointment_date');
    if (appointmentDateInput) {
        const today = new Date().toISOString().split('T')[0];
        appointmentDateInput.setAttribute('min', today);
    }

    // 2. Appointment form client-side validation
    const appointmentForm = document.getElementById('appointmentBookingForm');
    if (appointmentForm) {
        appointmentForm.addEventListener('submit', function (e) {
            const dateVal = document.getElementById('appointment_date').value;
            const timeVal = document.getElementById('appointment_time').value;

            if (!dateVal || !timeVal) {
                alert('Please select both appointment date and time.');
                e.preventDefault();
                return;
            }

            const selectedDate = new Date(dateVal);
            const now = new Date();
            const todayDateString = now.toISOString().split('T')[0];

            if (dateVal < todayDateString) {
                alert('Appointment date cannot be in the past.');
                e.preventDefault();
                return;
            }

            if (dateVal === todayDateString) {
                const currentTime = now.getHours().toString().padStart(2, '0') + ':' + now.getMinutes().toString().padStart(2, '0');
                if (timeVal < currentTime) {
                    alert('Appointment time cannot be in the past for today.');
                    e.preventDefault();
                    return;
                }
            }
        });
    }

    // 3. Registration password confirmation validation
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', function (e) {
            const password = document.getElementById('id_password') || document.querySelector('input[name="password"]');
            const confirmPassword = document.getElementById('id_confirm_password') || document.querySelector('input[name="confirm_password"]');

            if (password && confirmPassword && password.value !== confirmPassword.value) {
                alert('Passwords do not match. Please re-enter matching passwords.');
                e.preventDefault();
                confirmPassword.focus();
            }
        });
    }

    // 4. Auto-dismiss alert messages after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            alert.style.transition = 'opacity 0.5s ease';
            alert.style.opacity = '0';
            setTimeout(function () {
                alert.remove();
            }, 500);
        }, 5000);
    });
});

// 5. Global confirmation before cancelling an appointment
function confirmCancellation(event) {
    if (!confirm('Are you sure you want to cancel this appointment?')) {
        event.preventDefault();
        return false;
    }
    return true;
}

// 6. Global confirmation before deleting a doctor (Admin)
function confirmDeleteDoctor(event, doctorName) {
    if (!confirm('Are you sure you want to delete ' + doctorName + '? This action cannot be undone.')) {
        event.preventDefault();
        return false;
    }
    return true;
}

