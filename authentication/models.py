from django.db import models
from django.contrib.auth.models import AbstractUser

ROLE_CHOICES = {
        ("Lecturer", "Lecturer"),
        ("Student", "Student"),
        ("Admin", "Admin"),
        ("Asdos","Asdos")
    }

# class Role(models.Model):
#     LECTURER = 1
#     STUDENT = 2
#     ADMIN = 3
#     ASDOS = 4
#     ROLE_CHOICES = {
#         ("lecturer", "Lecturer"),
#         ("Student", "Student"),
#         ("Admin", "Admin"),
#         ("Asdos","Asdos")
#     }

#     id = models.PositiveIntegerField(choices = ROLE_CHOICES, primary_key = True)

#     def __str__(self):
#         return self.get_id_display()

class KwlUser(AbstractUser):
    domisili = models.CharField(max_length=100, null=True, blank=True)
    role = models.CharField(ROLE_CHOICES, max_length=8)

    def __str__(self):
        return self.username


class Lecturer(models.Model):
    user = models.OneToOneField(KwlUser, on_delete=models.CASCADE, related_name='lecturer_profile', null=True)
    department = models.CharField(max_length=100)
    courses_taught = models.ManyToManyField('course.Course')

    def __str__(self):
        return self.user.username

class Student(models.Model):
    user = models.OneToOneField(KwlUser, on_delete=models.CASCADE, null=True)
    student_id = models.CharField(max_length=10)
    major = models.CharField(max_length=100)
    assistant_courses = models.ManyToManyField('course.Course', blank=True, related_name='assistants')
    term = models.CharField(max_length=100)
    faculty = models.CharField(max_length=100)
    def __str__(self):
        return self.user.username






    




