from django.core.management.base import BaseCommand
from hospital.models import Doctor

class Command(BaseCommand):
    help = 'Seeds exactly 5 sample Indian doctors into the database without duplicates.'

    def handle(self, *args, **kwargs):
        sample_doctors = [
            {
                'name': 'Dr. Arjun Sharma',
                'specialization': 'Cardiology',
                'available_days': 'Monday, Wednesday, Friday',
            },
            {
                'name': 'Dr. Priya Reddy',
                'specialization': 'Dermatology',
                'available_days': 'Tuesday, Thursday, Saturday',
            },
            {
                'name': 'Dr. Vikram Kumar',
                'specialization': 'Orthopedics',
                'available_days': 'Monday, Tuesday, Thursday',
            },
            {
                'name': 'Dr. Ananya Iyer',
                'specialization': 'Pediatrics',
                'available_days': 'Wednesday, Friday, Saturday',
            },
            {
                'name': 'Dr. Rahul Nair',
                'specialization': 'General Medicine',
                'available_days': 'Monday, Wednesday, Saturday',
            },
        ]

        created_count = 0
        for doc in sample_doctors:
            doctor, created = Doctor.objects.get_or_create(
                name=doc['name'],
                defaults={
                    'specialization': doc['specialization'],
                    'available_days': doc['available_days'],
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created: {doctor.name} ({doctor.specialization})"))
            else:
                self.stdout.write(self.style.WARNING(f"Already exists: {doctor.name}"))

        self.stdout.write(self.style.SUCCESS(f"Successfully finished seeding. {created_count} new doctors added."))

