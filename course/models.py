from django.db import models
from authentication.models import Lecturer, Student
COLOR = [
    ('dark-accent', 'dark-accent'),
    ('kiki-blue', 'kiki-blue'),
    ('kowl-orange', 'kowl-orange'),
    ('wawa-pink', 'wawa-pink'),
    ('lulu-yellow', 'lulu-yellow')
]

# Create your models here.
class Course(models.Model):
    short_name = models.CharField(max_length=15)
    full_name = models.CharField(max_length=100)
    color_theme = models.CharField(max_length=11, choices=COLOR)
    lecturer_team = models.ManyToManyField(Lecturer, blank=True, related_name='lecturer')
    students = models.ManyToManyField(Student, blank=True, related_name='students')
    created = models.DateTimeField(auto_now_add=True)
  
    def __str__(self):
        return self.short_name

class Topic(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=250)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, blank=True,
    null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class KwlPoint(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    know_score = models.IntegerField(default=0)
    wtk_score = models.IntegerField(default=0)
    learned_score = models.IntegerField(default=0)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.topic


class RewardStudentPoint(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    total_point = models.IntegerField(default=0)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.student.user.username
    

class RewardItem(models.Model):
    name = models.CharField(max_length=100)
    stock = models.IntegerField(default=0)
    point = models.IntegerField(default=0)
    expired_date = models.CharField(max_length=30)
    detail_instruction = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, blank=True)
    
    def __str__(self):
        return self.name
    

class Feedback(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE)
    feedback = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.feedback