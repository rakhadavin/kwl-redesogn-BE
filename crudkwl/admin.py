from django.contrib import admin
from .models import Know, WantToKnow, Learned, KnowQuiz, KnowQuizAnswer, WantToKnowPoll, WantToKnowPollChoice
# Register your models here.
admin.site.register(Know)
admin.site.register(WantToKnow)
admin.site.register(Learned)
admin.site.register(KnowQuiz)
admin.site.register(KnowQuizAnswer)
admin.site.register(WantToKnowPoll)
admin.site.register(WantToKnowPollChoice)
