from django.contrib import admin

# Register your models here.
from .models import Course, Topic
class CourseAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
admin.site.register(Course, CourseAdmin)
admin.site.register(Topic, CourseAdmin)