from crudkwl.views import KnowView, WantToKnowView, LearnedView, KnowQuizView, KnowQuizAnswerView, WantToKnowPollView, WantToKnowPollChoiceView
from django.urls import path



urlpatterns = [
    path('know', KnowView.as_view()),
    path('wanttoknow', WantToKnowView.as_view()),
    path('learned', LearnedView.as_view()),
    path('knowquiz', KnowQuizView.as_view()),
    path('knowquizanswer', KnowQuizAnswerView.as_view()),
    path('wanttoknowpoll', WantToKnowPollView.as_view()),
    path('wanttoknowpollchoice', WantToKnowPollChoiceView.as_view()),

]