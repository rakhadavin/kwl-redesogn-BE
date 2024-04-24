from .views import get_learned_by_topic_id, LearnedQuizView, LearnedEssayView, is_learned_exist_by_topic_id, delete_learned_by_topic_id
from django.urls import path


urlpatterns = [
    path('<int:topic_id>', get_learned_by_topic_id),
    path('quiz/add', LearnedQuizView.add_learned_quiz),
    path('quiz/<int:quiz_id>', LearnedQuizView.get_learned_quiz),
    path('quiz/all/<int:know_id>', LearnedQuizView.get_all_learned_quiz),
    path('quiz/edit/<int:quiz_id>', LearnedQuizView.edit_learned_quiz),
    path('essay/add',LearnedEssayView.add_learned_essay),
    path('essay/edit/<int:ref_id>', LearnedEssayView.edit_learned_essay),
    path('essay/<int:know_id>', LearnedEssayView.get_learned_essay),
    path('answer/quiz/<int:know_quiz_id>', LearnedQuizView.save_quiz_answer),
    path('answer/quiz/all/<int:know_id>', LearnedQuizView.save_all_answers_by_know_id),
    path('answer/essay/<int:ref_id>', LearnedEssayView.save_essay_answer),
    path('is_exist/<int:topic_id>', is_learned_exist_by_topic_id),
    path('delete/<int:topic_id>', delete_learned_by_topic_id),
   

] 