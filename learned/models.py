from django.db import models

# Create your models here.

CHOICES = (("reflection", "Reflection"), ("quiz", "Quiz"))
class Learned(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    topic = models.ForeignKey('course.Topic', on_delete=models.CASCADE, blank=True, null=True)
    type = models.CharField(max_length=255, choices=CHOICES, default='reflection')
    total_participants = models.IntegerField(default=0)
    def __str__(self):
        return self.type

class LearnedQuizQuestion(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    question = models.CharField(max_length=255)
    learned = models.ForeignKey('Learned', on_delete=models.CASCADE, blank=True, null=True)
    score = models.IntegerField(default=0)
    image = models.ImageField(upload_to='learned_images/', blank=True, null=True)
    def __str__(self):
        return self.question
    
    def get_answers(self):
        return LearnedQuizOption.objects.filter(learned_quiz_id=self.id)
    
    
class LearnedQuizOption(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    learned_quiz = models.ForeignKey('LearnedQuizQuestion', on_delete=models.CASCADE, blank=True, null=True)
    option_answer = models.CharField(max_length=255)
    isCorrect = models.BooleanField(default=False)
    alias = models.CharField(max_length=255, blank=True, null=True)
    def __str__(self):
        return self.option_answer
    
class LearnedQuizStudentAnswer(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    student = models.ForeignKey('authentication.Student', blank=True, null=True, on_delete=models.CASCADE)
    answers = models.ManyToManyField(LearnedQuizOption, blank=True, related_name='student_answers')
    def __str__(self):
        return self.student.user.username

class LearnedReflection(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    question = models.CharField(max_length=255)
    learned = models.ForeignKey('Learned', on_delete=models.CASCADE, blank=True, null=True)
    score = models.IntegerField(default=0)
    def __str__(self):
        return self.question

class LearnedReflectionStudentAnswer(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    learned_ref = models.ForeignKey('LearnedReflection', on_delete=models.CASCADE, blank=True, null=True)
    student = models.ForeignKey('authentication.Student', blank=True, null=True, on_delete=models.CASCADE)
    reflection = models.TextField(max_length=255)
    def __str__(self):
        return self.reflection


    