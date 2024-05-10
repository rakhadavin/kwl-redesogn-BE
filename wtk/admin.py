from django.contrib import admin

from .models import WantToKnow, WtkPollQuestion, WtkChoices, WtkPollStudentAnswer, Prereading, WtkReflection, WtkReflectionStudentAnswer
class WtkAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)

admin.site.register(WantToKnow, WtkAdmin)
admin.site.register(WtkPollQuestion, WtkAdmin)
admin.site.register(WtkChoices, WtkAdmin)
admin.site.register(WtkPollStudentAnswer, WtkAdmin)
admin.site.register(Prereading, WtkAdmin)
admin.site.register(WtkReflection, WtkAdmin)
admin.site.register(WtkReflectionStudentAnswer, WtkAdmin)