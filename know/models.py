from django.db import models

# Create your models here.

alias_choices = (("Opsi A", "Opsi A"), ("Opsi B", "Opsi B"), ("Opsi C", "Opsi C"), ("Opsi D", "Opsi D"))
CHOICES = (("reflection", "Reflection"), ("quiz", "Quiz"))
class Know(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    topic = models.ForeignKey('course.Topic', on_delete=models.CASCADE, blank=True, null=True)
    type = models.CharField(max_length=255, choices=CHOICES, default='reflection')
    total_participants = models.IntegerField(default=0)
    def __str__(self):
        return self.type

    
class KnowQuizQuestion(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    question = models.CharField(max_length=255)
    know = models.ForeignKey('Know', on_delete=models.CASCADE, blank=True, null=True)
    score = models.IntegerField(default=0)
    image = models.ImageField(upload_to='know_images/', blank=True, null=True)
    def __str__(self):
        return self.question
    
    def get_answers(self):
        return KnowQuizOption.objects.filter(know_quiz=self.id)
    
class KnowQuizOption(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    know_quiz = models.ForeignKey('KnowQuizQuestion', on_delete=models.CASCADE, blank=True, null=True)
    option_answer = models.CharField(max_length=255)
    isCorrect = models.BooleanField(default=False)
    alias = models.CharField(choices=alias_choices, max_length=255, blank=True, null=True)
    def __str__(self):
        return self.option_answer

    
class KnowQuizStudentAnswer(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    student = models.ForeignKey('authentication.Student', on_delete=models.CASCADE, blank=True, null=True)
    answers = models.ManyToManyField(KnowQuizOption, blank=True, related_name='student_answers')
    def __str__(self):
        return self.student.user.username
    
class KnowReflection(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    question = models.CharField(max_length=255)
    know = models.ForeignKey('Know', on_delete=models.CASCADE, blank=True, null=True)
    score = models.IntegerField(default=0)
    def __str__(self):
        return self.question
 

class KnowReflectionStudentAnswer(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    know_ref = models.ForeignKey('KnowReflection', on_delete=models.CASCADE, blank=True, null=True)
    student = models.ForeignKey('authentication.Student', blank=True, null=True, on_delete=models.CASCADE)
    reflection = models.TextField(max_length=255)
    def __str__(self):
        return self.reflection
    
