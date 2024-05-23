
from django.urls import path
from .views import KwlPointLadderView, WordCloudAPIView, KwlParticipantCountView, TopicPollingAnalysisView, QuizAccuracyAnalysisView, QuizBarchartImageView, StudentAnswerDetailAnalysis, StudentKWLRecapView


urlpatterns = [
    path('wordcloud/<str:type>/<int:topic>', WordCloudAPIView.as_view(), name="wordcloud"),
    path('topic-ladder/<int:topic>/<int:filter_number>', KwlPointLadderView.as_view(), name="kwl-point-ladder"),
    path('kwl-participants/<int:topic>', KwlParticipantCountView.as_view(), name="kwl-participants"),
    path('poll/<int:topic>', TopicPollingAnalysisView.as_view(), name="topic-polling"),
    path('quiz-accuracy/<str:type>/<int:topic>', QuizAccuracyAnalysisView.as_view(), name="quiz-analysis"),
    path('quiz-barchart/<str:type>/<int:topic>', QuizBarchartImageView.as_view(), name="quiz-barchart"),
    path('student-answer-detail/<str:type>/<int:topic>', StudentAnswerDetailAnalysis.as_view(), name="student-answer-detail"),
    path('student-kwl-recap/<int:topic>/<int:student_id>', StudentKWLRecapView.as_view(), name="student-kwl-recap"),

   

]