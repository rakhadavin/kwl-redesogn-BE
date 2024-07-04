
import datetime
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.utils import timezone
ROLE_CHOICES = (
    ("lecturer", "Lecturer"),
    ("student", "Student"),
)

class ResetPasswordToken(models.Model):
    token = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.token

    def is_expired(self):
        # Ensure both datetimes are timezone-aware or naive for a correct comparison
        now = timezone.now() if settings.USE_TZ else datetime.datetime.now()
        return now > self.created_at + datetime.timedelta(hours=2)

    def generate_token(self):
        return uuid.uuid4().hex

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_token()
        super().save(*args, **kwargs)  # Call the "real" save() method.


class KwlUser(AbstractUser):
    domisili = models.CharField(max_length=100, help_text="User's domicile", null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student', help_text="User's role")
    reset_password_token = models.OneToOneField(ResetPasswordToken, on_delete=models.CASCADE, null=True, blank=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True, help_text="User's profile photo")
    def __str__(self):
        return self.username

class Lecturer(models.Model):
    user = models.OneToOneField(KwlUser, on_delete=models.CASCADE, related_name='lecturer_profile', null=True)
    department = models.CharField(max_length=100, null=True, blank=True)
    lecturer_id =  models.CharField(max_length=10, null=True, blank=True) 

    def __str__(self):
        return self.user.username

class Student(models.Model):
    user = models.OneToOneField(KwlUser, on_delete=models.CASCADE, null=True)
    student_id = models.CharField(max_length=10, null=True, blank=True)
    major = models.CharField(max_length=100, null=True, blank=True)
    term = models.CharField(max_length=100, null=True, blank=True)
    faculty = models.CharField(max_length=100, null=True, blank=True)
    def __str__(self):
        return self.user.username
    
    def get_full_name(self):
        return self.user.first_name + " " + self.user.last_name






    




