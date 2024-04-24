
from django.urls import path
from .views import WordCloudAPIView, LearnedParticipantView, KnowParticipantView, WtkParticipantView


urlpatterns = [
    path('wordcloud/', WordCloudAPIView.as_view(), name="wordcloud"),
    path('learned/participant/', LearnedParticipantView.as_view(), name="learned_participant"),
    path('know/participant/', KnowParticipantView.as_view(), name="know_participant"),
    path('wtk/participant/', WtkParticipantView.as_view(), name="wtk_participant"),

]