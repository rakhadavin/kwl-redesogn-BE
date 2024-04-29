
from django.urls import path
from .views import WordCloudAPIView, LearnedParticipantView, KnowParticipantView, WtkParticipantView


urlpatterns = [
    path('wordcloud/', WordCloudAPIView.as_view(), name="wordcloud"),
    path('learned/participants/count', LearnedParticipantView.count_all_participants, name="learned_participant"),
    path('learned/participants', LearnedParticipantView.get_all_participants, name="learned_participant"),
    path('know/participants/count', KnowParticipantView.count_all_participants, name="know_participant"),
    path('know/participants', KnowParticipantView.get_all_participants, name="know_participant"),
    path('wtk/participants/count', WtkParticipantView.count_all_participants, name="wtk_participant"),
    path('wtk/participants', WtkParticipantView.get_all_participants, name="wtk_participant"),

]