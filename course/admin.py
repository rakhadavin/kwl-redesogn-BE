from django.contrib import admin

# Register your models here.
from .models import Course, Topic

admin.site.register(Course)
admin.site.register(Topic)