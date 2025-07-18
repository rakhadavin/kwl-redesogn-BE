from django.db import models
from utils.custom_storage import MinioMediaStorage

# Create your models here.
wtk_choices = (("checkbox", "Checkbox"), ("reflection", "Reflection"))
alias_choices = (("option 1","option_1"),("option 2","option_2"),("option 3","option_3"),("option 4","option_4"),("option 5","option_5"),("option 6","option_6"),("option 7","option_7"),("option 8","option_8"),("option 9","option_9"),("option 10","option_10"))
class WantToKnow(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    topic = models.ForeignKey('course.Topic', on_delete=models.CASCADE, blank=True, null=True)
    type = models.CharField(max_length=255, choices=wtk_choices, default='reflection')
    total_participants = models.IntegerField(default=0)
    prereading = models.ForeignKey('Prereading', on_delete=models.CASCADE, blank=True, null=True)
    def __str__(self):
        return self.type

class WtkPollQuestion(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    question = models.TextField()
    wtk = models.ForeignKey('WantToKnow', on_delete=models.CASCADE, blank=True, null=True)
    choices = models.ManyToManyField('WtkChoices', blank=True, related_name='poll_choices')
    score = models.IntegerField(default=0)
    def __str__(self):
        return self.question
    
 
class WtkChoices(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    option_answer = models.TextField()
    total_votes = models.IntegerField(default=0)
    
    def __str__(self):
        return self.option_answer
    
class WtkPollStudentAnswer(models.Model):
    wtk_poll = models.ForeignKey('WtkPollQuestion', on_delete=models.CASCADE, blank=True, null=True)
    student = models.ForeignKey('authentication.Student', on_delete=models.CASCADE, blank=True, null=True)
    choices = models.ManyToManyField(WtkChoices, blank=True, related_name='student_choices')

class WtkReflection(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    question = models.TextField()
    wtk = models.ForeignKey('WantToKnow', on_delete=models.CASCADE, blank=True, null=True)
    score = models.IntegerField(default=0)
    def __str__(self):
        return self.question

class WtkReflectionStudentAnswer(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    wtk_ref = models.ForeignKey('WtkReflection', on_delete=models.CASCADE, blank=True, null=True)
    student = models.ForeignKey('authentication.Student', blank=True, null=True, on_delete=models.CASCADE)
    reflection = models.TextField()
    def __str__(self):
        return self.reflection
    
class Prereading(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    topic = models.ForeignKey('course.Topic', on_delete=models.CASCADE, blank=True, null=True)
    prereading = models.TextField()
    file = models.FileField(upload_to='prereading_files/', blank=True, null=True, storage=MinioMediaStorage())   
    def __str__(self):
        return self.prereading
    