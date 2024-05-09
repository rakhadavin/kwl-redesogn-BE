from .views import LearnedEssayListView, LearnedEssayDetailView, LearnedQuizDetailView, LearnedQuizListView, LearnedQuizzesByTopicView, LearnedEssayAnswerView, LearnedQuizAnswerView
from django.urls import path


urlpatterns = [
    # path('<int:topic_id>', get_learned_by_topic_id),
    # path('quiz/add', LearnedQuizView.add_learned_quiz),
    # path('quiz/<int:quiz_id>', LearnedQuizView.get_learned_quiz),
    # path('quiz/all/<int:know_id>', LearnedQuizView.get_all_learned_quiz),
    # path('quiz/edit/<int:quiz_id>', LearnedQuizView.edit_learned_quiz),
    # path('essay/add',LearnedEssayView.add_learned_essay),
    # path('essay/edit/<int:ref_id>', LearnedEssayView.edit_learned_essay),
    # path('essay/<int:learned_id>', LearnedEssayView.get_learned_essay),
    # path('answer/quiz/<int:know_quiz_id>', LearnedQuizView.save_quiz_answer),
    # path('answer/quiz/all/<int:know_id>', LearnedQuizView.save_all_answers_by_know_id),
    # path('answer/essay/<int:ref_id>', LearnedEssayView.save_essay_answer),
    # path('is_exist/<int:topic_id>', is_learned_exist_by_topic_id),
    # path('delete/<int:topic_id>', delete_learned_by_topic_id),

   path('essay', LearnedEssayListView.as_view()), #get all & create
   path('essay/<int:topic_id>', LearnedEssayDetailView.as_view()), #get 1, update, delete
    path('essay/answer', LearnedEssayAnswerView.as_view()), #save answer

    path('quiz', LearnedQuizListView.as_view()), #get all & create
    path('quiz/<int:topic_id>', LearnedQuizzesByTopicView.as_view()), #get all quiz by topic id, delete
    path('quiz/detail/<int:quiz_id>', LearnedQuizDetailView.as_view()), #get 1, edit
    path('quiz/answer', LearnedQuizAnswerView.as_view()), #save answer

   


] 