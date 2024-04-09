from django.contrib import admin

# Register your models here.
from .models import KwlUser, Student, Lecturer

admin.site.register(KwlUser)
admin.site.register(Student)
admin.site.register(Lecturer)