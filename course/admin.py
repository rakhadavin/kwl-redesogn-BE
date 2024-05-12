from django.contrib import admin

# Register your models here.
from .models import Course, Topic, RewardStudentPoint, RewardItem, KwlPoint, LastAccessedStudentCourse, Feedback, RedeemHistory
class CourseAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
admin.site.register(Course, CourseAdmin)
admin.site.register(Topic, CourseAdmin)
admin.site.register(RewardStudentPoint, CourseAdmin)
admin.site.register(RewardItem, CourseAdmin)
admin.site.register(KwlPoint, CourseAdmin)
admin.site.register(LastAccessedStudentCourse, CourseAdmin)
admin.site.register(Feedback, CourseAdmin)
admin.site.register(RedeemHistory, CourseAdmin)