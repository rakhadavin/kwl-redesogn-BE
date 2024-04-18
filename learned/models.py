from django.db import models

# Create your models here.

CHOICES = (("reflection", "Reflection"), ("quiz", "Quiz"))
class Learned(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    topic = models.ForeignKey('course.Topic', on_delete=models.CASCADE, blank=True, null=True)
    type = models.CharField(max_length=255, choices=CHOICES, default='reflection')
    def __str__(self):
        return self.type

class LearnedReflection(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    question = models.CharField(max_length=255)
    wtk_id = models.ForeignKey('WantToKnow', on_delete=models.CASCADE, blank=True, null=True)
    score = models.IntegerField(default=0)
    def __str__(self):
        return self.question

class LearnedReflectionStudentAnswer(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    wtk_ref_id = models.ForeignKey('LearnedReflection', on_delete=models.CASCADE, blank=True, null=True)
    student_id = models.ForeignKey('authentication.Student', blank=True, null=True, on_delete=models.CASCADE)
    reflection = models.TextField(max_length=255)
    score = models.IntegerField(default=0)
    def __str__(self):
        return self.reflection
    