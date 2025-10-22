from django.db import models
import uuid

# Create your models here.
class Quiz(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    lecturer_team = models.ManyToManyField('authentication.Lecturer', related_name='quizzes')   
    visibility = models.CharField(max_length=50, choices=[('Public', 'Public'), ('Private', 'Private')], default='private')
    quiz_pin = models.IntegerField(default=0)
    is_started = models.BooleanField(default=False)
    is_lobby = models.BooleanField(default=False)
    if_finished = models.BooleanField(default=False)

class Question(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    quiz = models.ForeignKey('Quiz', on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    # time_limit = models.IntegerField(default=5)
    score = models.IntegerField(default=0)
    # answer_type = models.CharField(max_length=50, choices=[('Single Choice', 'Single Choice'), ('Multiple Choice', 'Multiple Choice')], default='Single Choice')

class Choice(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    question = models.ForeignKey('Question', on_delete=models.CASCADE, related_name='choices')
    choice_text = models.TextField()
    is_correct = models.BooleanField(default=False)
  
class GuestQuizAttempt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    guest_name = models.CharField(max_length=255, null=True, blank=True)
    quiz = models.ForeignKey('Quiz', on_delete=models.CASCADE, related_name='guest_attempts')
    score = models.IntegerField(default=0)
    completed_at = models.DateTimeField(blank=True, null=True)

class StudentQuizAnswer(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    student = models.ForeignKey('GuestQuizAttempt', on_delete=models.CASCADE, blank=True, null=True, related_name='answers')
    question = models.ForeignKey('Question', on_delete=models.CASCADE, blank=True, null=True)
    selected_choices = models.ManyToManyField('Choice', blank=True)
    
    class Meta:
        unique_together = ('student', 'question')  # Satu jawaban per student per question