from django.contrib import admin

# Register your models here.
from .models import Learned, LearnedQuizQuestion, LearnedQuizOption, LearnedReflection, LearnedReflectionStudentAnswer, LearnedQuizStudentAnswer

class LearnedAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)

admin.site.register(Learned, LearnedAdmin)
admin.site.register(LearnedQuizQuestion, LearnedAdmin)
admin.site.register(LearnedQuizOption, LearnedAdmin)
admin.site.register(LearnedReflection, LearnedAdmin)
admin.site.register(LearnedReflectionStudentAnswer, LearnedAdmin)
admin.site.register(LearnedQuizStudentAnswer, LearnedAdmin)
