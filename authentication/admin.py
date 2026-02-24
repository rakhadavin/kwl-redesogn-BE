from django.contrib import admin

# Register your models here.
from .models import KwlUser, Student, Lecturer, Consent, UserConsent

admin.site.register(KwlUser)
admin.site.register(Student)
admin.site.register(Lecturer)
admin.site.register(Consent)
admin.site.register(UserConsent)