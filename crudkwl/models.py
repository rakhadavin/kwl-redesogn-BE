from django.db import models
from django.db import models
from django.contrib.postgres.fields import ArrayField

# Create your models here.
class Know(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    topic = models.ForeignKey('Topic', on_delete=models.CASCADE, blank=True, null=True)
    score = models.IntegerField(default=0)
    def __str__(self):
        return self.title

class WantToKnow(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    topic = models.ForeignKey('Topic', on_delete=models.CASCADE, blank=True, null=True)
    score = models.IntegerField(default=0)
    def __str__(self):
        return self.title

class Learned(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    topic = models.ForeignKey('Topic', on_delete=models.CASCADE, blank=True, null=True)
    score = models.IntegerField(default=0)
    def __str__(self):
        return self.title
    
class KnowQuiz(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    question = models.CharField(max_length=255)
    know_id = models.ForeignKey('Know', on_delete=models.CASCADE, blank=True, null=True)
    answers = ArrayField(models.CharField(max_length=255), blank=True, null=True)
    def __str__(self):
        return self.title