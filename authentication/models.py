from django.db import models
from django.contrib.auth.models import AbstractUser


ROLE_CHOICES = [
        ("Admin", "Admin"),
        ("User", "User"),
        ("Guest", "Guest"),
    ]


class KwlUser(AbstractUser):
    domisili = models.CharField(max_length=100, null=True, blank=True)


    def __str__(self):
        return self.username

class Course(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    # Add other fields as needed

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title



class Lecturer(models.Model):
    user = models.OneToOneField(KwlUser, on_delete=models.CASCADE, related_name='lecturer_profile', null=True)
    department = models.CharField(max_length=100)
    courses_taught = models.ManyToManyField(Course)

    def __str__(self):
        return self.user.username

class Student(models.Model):
    user = models.OneToOneField(KwlUser, on_delete=models.CASCADE, null=True)
    student_id = models.CharField(max_length=10)
    major = models.CharField(max_length=100)
    assistant_courses = models.ManyToManyField(Course, blank=True, related_name='assistants')
    term = models.CharField(max_length=100)
    faculty = models.CharField(max_length=100)
    def __str__(self):
        return self.user.username






    




