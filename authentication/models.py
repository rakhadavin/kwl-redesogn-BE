from django.db import models
from django.contrib.auth.models import AbstractUser

ROLE_CHOICES = (
    ("lecturer", "Lecturer"),
    ("student", "Student"),
)

class KwlUser(AbstractUser):
    domisili = models.CharField(max_length=100, help_text="User's domicile", null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    reset_password_token = models.CharField(max_length=100, null=True, blank=True, help_text="Token for resetting password")
    role = models.ManyToManyField(Role, related_name='user_role', null=True)
    reset_password_token = models.CharField(max_length=100, null=True, blank=True, help_text="Token for resetting password")
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    def __str__(self):
        return self.username

class Lecturer(models.Model):
    user = models.OneToOneField(KwlUser, on_delete=models.CASCADE, related_name='lecturer_profile', null=True)
    department = models.CharField(max_length=100)
    lecturer_id =  models.CharField(max_length=10)

    def __str__(self):
        return self.user.username

class Student(models.Model):
    user = models.OneToOneField(KwlUser, on_delete=models.CASCADE, null=True)
    student_id = models.CharField(max_length=10)
    major = models.CharField(max_length=100)
    term = models.CharField(max_length=100)
    faculty = models.CharField(max_length=100)
    def __str__(self):
        return self.user.username






    




