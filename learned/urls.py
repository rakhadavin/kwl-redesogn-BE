from .views import LearnedEssayListView, LearnedEssayDetailView, LearnedQuizDetailView, LearnedQuizListView, LearnedQuizzesByTopicView, LearnedEssayAnswerView, LearnedQuizAnswerView
from django.urls import path


urlpatterns = [

   path('essay', LearnedEssayListView.as_view()), #get all & create
   path('essay/<int:topic_id>', LearnedEssayDetailView.as_view()), #get 1, update, delete
    path('essay/answer', LearnedEssayAnswerView.as_view()), #save answer

    path('quiz', LearnedQuizListView.as_view()), #get all & create
    path('quiz/<int:topic_id>', LearnedQuizzesByTopicView.as_view()), #get all quiz by topic id, delete
    path('quiz/detail/<int:quiz_id>', LearnedQuizDetailView.as_view()), #get 1, edit
    path('quiz/answer', LearnedQuizAnswerView.as_view()), #save answer

   


] 