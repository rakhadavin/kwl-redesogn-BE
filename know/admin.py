from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Know, KnowQuizQuestion, KnowQuizOption, KnowQuizStudentAnswer, KnowReflection, KnowReflectionStudentAnswer
class KnowAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
admin.site.register(Know, KnowAdmin)
admin.site.register(KnowQuizQuestion, KnowAdmin)
admin.site.register(KnowQuizOption, KnowAdmin)
admin.site.register(KnowQuizStudentAnswer, KnowAdmin)
admin.site.register(KnowReflection, KnowAdmin)
admin.site.register(KnowReflectionStudentAnswer, KnowAdmin)

