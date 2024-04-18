from django.contrib import admin

from .models import WantToKnow, WtkPollQuestion, WtkChoices, WtkStudentAnswer, Prereading
class WtkAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)

admin.site.register(WantToKnow, WtkAdmin)
admin.site.register(WtkPollQuestion, WtkAdmin)
admin.site.register(WtkChoices, WtkAdmin)
admin.site.register(WtkStudentAnswer, WtkAdmin)
admin.site.register(Prereading, WtkAdmin)