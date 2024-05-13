
from django.urls import path
from .views import KwlPointLadderView, WordCloudAPIView, KwlParticipantCountView, TopicPollingAnalysisView, QuizAccuracyAnalysisView, QuizBarchartImageView


urlpatterns = [
    path('wordcloud/<str:type>/<int:topic>', WordCloudAPIView.as_view(), name="wordcloud"),
    path('topic-ladder/<int:topic>', KwlPointLadderView.as_view(), name="kwl-point-ladder"),
    path('kwl-participants/<int:topic>', KwlParticipantCountView.as_view(), name="kwl-participants"),
    path('poll/<int:topic>', TopicPollingAnalysisView.as_view(), name="topic-polling"),
    path('quiz-accuracy/<str:type>/<int:topic>', QuizAccuracyAnalysisView.as_view(), name="quiz-analysis"),
    path('quiz-barchart/<str:type>/<int:topic>', QuizBarchartImageView.as_view(), name="quiz-barchart"),

   

]