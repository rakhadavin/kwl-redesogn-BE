from django.contrib import admin

# Register your models here.
from .models import Course, Topic, RewardStudentPoint, RewardItem
class CourseAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
admin.site.register(Course, CourseAdmin)
admin.site.register(Topic, CourseAdmin)
admin.site.register(RewardStudentPoint, CourseAdmin)
admin.site.register(RewardItem, CourseAdmin)