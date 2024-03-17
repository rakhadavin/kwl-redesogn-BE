from django.db import models
from authentication.models import Lecturer, Student
COLOR = [
    ('blue', 'blue'),
    ('tosca', 'tosca'),
    ('orange', 'orange'),
    ('pink', 'pink'),
    ('yellow', 'yellow')
]

# Create your models here.
class Course(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    color_theme = models.CharField(max_length=6, choices=COLOR)
    lecturer_team = models.ManyToManyField(Lecturer, blank=True, related_name='lecturer')
    assistant_team = models.ManyToManyField(Student, blank=True, related_name='assistants')
    created = models.DateTimeField(auto_now_add=True)
    # Add other fields as needed

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

class Topic(models.Model):
    name = models.CharField(max_length=100)
    goals = models.CharField(max_length=250)
    course = models.ForeignKey(Course, on_delete=models.CASCADE,   blank=True,
    null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name