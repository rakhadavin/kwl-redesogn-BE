from django.db import models
import uuid
import random

# Create your models here.
class QuestionType(models.TextChoices):
    MULTIPLE_CHOICE = 'Multiple Choice', 'Multiple Choice'
    POLLING = 'Polling', 'Polling'
    OPEN_ENDED = 'Open Ended', 'Open Ended'

def generate_unique_pin():
    """Generate a unique 6-digit PIN for kuesioner"""
    while True:
        pin = random.randint(100000, 999999)
        if not Kuesioner.objects.filter(pin=pin).exists():
            return pin
        
class Kuesioner(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    question_type = models.CharField(max_length=50, choices=QuestionType)
    lecturer_team = models.ManyToManyField('authentication.Lecturer', related_name='kuesioners')   
    visibility = models.CharField(max_length=50, choices=[('Public', 'Public'), ('Private', 'Private')], default='private')
    pin = models.IntegerField(default=generate_unique_pin, unique=True)
    is_started = models.BooleanField(default=False)
    is_lobby = models.BooleanField(default=False)
    if_finished = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if not self.pin:
            self.pin = generate_unique_pin()
        super().save(*args, **kwargs)

class Question(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    number = models.IntegerField(null=True, blank=True)
    kuesioner = models.ForeignKey('Kuesioner', on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    time_limit = models.IntegerField(default=5)
    score = models.IntegerField(default=0)

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
    kuesioner = models.ForeignKey('Kuesioner', on_delete=models.CASCADE, related_name='guest_attempts')
    session = models.ForeignKey('KuesionerSession', on_delete=models.CASCADE, related_name='attempts', null=True, blank=True)
    score = models.IntegerField(default=0)
    completed_at = models.DateTimeField(blank=True, null=True)

class GuestQuizAnswer(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    guest = models.ForeignKey('GuestQuizAttempt', on_delete=models.CASCADE, blank=True, null=True, related_name='answers')
    question = models.ForeignKey('Question', on_delete=models.CASCADE, blank=True, null=True)
    selected_choices = models.ManyToManyField('Choice', blank=True)
    text_answer = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ('guest', 'question')

class KuesionerSession(models.Model):
    """Model untuk mencatat setiap sesi kuesioner yang dimulai"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    kuesioner = models.ForeignKey('Kuesioner', on_delete=models.CASCADE, related_name='sessions')
    session_number = models.IntegerField(default=1)  # Urutan sesi ke berapa untuk kuesioner ini
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(blank=True, null=True)
    started_by = models.ForeignKey('authentication.Lecturer', on_delete=models.SET_NULL, null=True, blank=True)
    total_participants = models.IntegerField(default=0)  # Cache jumlah peserta
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('kuesioner', 'session_number')
        ordering = ['-started_at']