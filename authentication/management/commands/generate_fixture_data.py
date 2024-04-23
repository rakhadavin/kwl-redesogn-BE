from django.conf import settings
from django.contrib.auth.hashers import make_password



from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Generate fixture data with pre-hashed passwords'

    def handle(self, *args, **options):
        # Prepare fixture data with pre-hashed passwords
        BASE_DIR = settings.BASE_DIR    
        fixture_data = [
        {
          "model": "authentication.kwluser",
          "pk": 1,
          "fields": {
        "username": "john_doe",
        "email": "john.doe@example.com",
        "domisili": "Jakarta",
        "role": "lecturer",
        "password": make_password("password123")
          }
        },
        {
          "model": "authentication.lecturer",
          "pk": 1,
          "fields": {
        "user": 1,
        "department": "Computer Science"
          }
        },
        {
          "model": "authentication.kwluser",
          "pk": 2,
          "fields": {
        "username": "jane_smith",
        "email": "jane.smith@example.com",
        "domisili": "Bandung",
        "role": "lecturer",
        "password": make_password("testpass456")
          }
        },
        {
          "model": "authentication.lecturer",
          "pk": 2,
          "fields": {
        "user": 2,
        "department": "Literature"
          }
        },
        {
          "model": "authentication.kwluser",
          "pk": 3,
          "fields": {
        "username": "emma_jones",
        "email": "emma.jones@example.com",
        "domisili": "Surabaya",
        "role": "student",
        "password": make_password("studentpass789")
          }
        },
        {
          "model": "authentication.student",
          "pk": 1,
          "fields": {
        "user": 3,
        "student_id": "123456",
        "major": "Engineering",
        "term": "Spring 2024",
        "faculty": "Engineering Faculty"
          }
        },
        {
          "model": "authentication.kwluser",
          "pk": 4,
          "fields": {
        "username": "chris_wong",
        "email": "chris.wong@example.com",
        "domisili": "Jakarta",
        "role": "student",
        "password": make_password("studentpass987")
          }
        },
        {
          "model": "authentication.student",
          "pk": 2,
          "fields": {
        "user": 4,
        "student_id": "789012",
        "major": "Literature",
        "term": "Spring 2024",
        "faculty": "Arts Faculty"
          }
        },
        {
          "model": "authentication.kwluser",
          "pk": 5,
          "fields": {
        "username": "lisa_smith",
        "email": "lisa.smith@example.com",
        "domisili": "Bandung",
        "role": "student",
        "password": make_password("studentpass654")
          }
        },
        {
          "model": "authentication.student",
          "pk": 3,
          "fields": {
        "user": 5,
        "student_id": "345678",
        "major": "Computer Science",
        "term": "Spring 2024",
        "faculty": "Engineering Faculty"
          }
        },
        {
          "model": "authentication.kwluser",
          "pk": 6,
          "fields": {
        "username": "alex_wong",
        "email": "alex.wong@example.com",
        "domisili": "Surabaya",
        "role": "student",
        "password": make_password("studentpass321")
          }
        },
        {
          "model": "authentication.student",
          "pk": 4,
          "fields": {
        "user": 6,
        "student_id": "567890",
        "major": "History",
        "term": "Spring 2024",
        "faculty": "Arts Faculty"
          }
        }
      ]
  
  

        # Write fixture data to a JSON file
        import json

        with open(BASE_DIR / 'fixtures/user.json', 'w') as file:
            json.dump(fixture_data, file, indent=4)

        self.stdout.write(self.style.SUCCESS('Fixture data generated successfully.'))