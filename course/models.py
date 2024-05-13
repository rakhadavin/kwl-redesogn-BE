from django.db import models
from authentication.models import Lecturer, Student
COLOR = [
    ('dark-accent', 'dark-accent'),
    ('kiki-blue', 'kiki-blue'),
    ('kowl-orange', 'kowl-orange'),
    ('wawa-pink', 'wawa-pink'),
    ('lulu-yellow', 'lulu-yellow')
]

KWL_STATUS = [
    ('know', 'know'),
    ('wtk', 'wtk'),
    ('learned', 'learned')
]
# Create your models here.
class Course(models.Model):
    short_name = models.CharField(max_length=30)
    full_name = models.CharField(max_length=100)
    color_theme = models.CharField(max_length=11, choices=COLOR)
    lecturer_team = models.ManyToManyField(Lecturer, blank=True, related_name='lecturer')
    students = models.ManyToManyField(Student, blank=True, related_name='students')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
  
    def __str__(self):
        return self.short_name

class Topic(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=250)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, blank=True,
    null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class LastAccessedStudentCourse(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, blank=True)
    last_accessed = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.student.user.username

class KwlPoint(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    know_score = models.IntegerField(default=0)
    wtk_score = models.IntegerField(default=0)
    learned_score = models.IntegerField(default=0)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    kwl_status = models.CharField(max_length=10, choices=KWL_STATUS, default='know')
    
    def __str__(self):
        return self.topic.name
    
    def get_total_point(self):
        return self.know_score + self.wtk_score + self.learned_score


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
    
class RedeemHistory(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    reward_item = models.ForeignKey(RewardItem, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.student.user.username
    
class LecturerPinnedCourse(models.Model):
    lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE)
    pinned_course = models.ManyToManyField(Course, blank=True, related_name='lecturer_pinned_course')
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.lecturer.user.username