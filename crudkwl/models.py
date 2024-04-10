from django.db import models
from django.db import models
from django.contrib.postgres.fields import ArrayField

# Create your models here.
class Know(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    topic = models.ForeignKey('course.Topic', on_delete=models.CASCADE, blank=True, null=True)
    total_score = models.IntegerField(default=0)
    def __str__(self):
        return self.topic

class WantToKnow(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    topic = models.ForeignKey('course.Topic', on_delete=models.CASCADE, blank=True, null=True)
    total_score = models.IntegerField(default=0)
    def __str__(self):
        return self.topic

class Learned(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    topic = models.ForeignKey('course.Topic', on_delete=models.CASCADE, blank=True, null=True)
    total_score = models.IntegerField(default=0)
    def __str__(self):
        return self.topic
    
class KnowQuiz(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    question = models.CharField(max_length=255)
    know_id = models.ForeignKey('Know', on_delete=models.CASCADE, blank=True, null=True)
    marks = models.IntegerField(default=0)
    def __str__(self):
        return self.question
    
    def get_answers(self):
        return KnowQuizAnswer.objects.filter(know_quiz_id=self.id)
    
 
class KnowQuizAnswer(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    know_quiz_id = models.ForeignKey('KnowQuiz', on_delete=models.CASCADE, blank=True, null=True)
    answer = models.CharField(max_length=255)
    isCorrect = models.BooleanField(default=False)
    def __str__(self):
        return self.answer
    
class WantToKnowPoll(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    want_to_know_id = models.ForeignKey('WantToKnow', on_delete=models.CASCADE, blank=True, null=True)
    question = models.CharField(max_length=200)
    def __str__(self):
        return self.question

class WantToKnowPollChoice(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    want_to_know_poll_id = models.ForeignKey('WantToKnowPoll', on_delete=models.CASCADE, blank=True, null=True)
    choice = models.CharField(max_length=255)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice
    
class LearnedReflection(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    learned_id = models.ForeignKey('Learned', on_delete=models.CASCADE, blank=True, null=True)
    reflection = models.TextField()
    def __str__(self):
        return self.reflection

