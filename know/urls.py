from .views import KnowQuizView, KnowEssayView, KnowTopicView
from django.urls import path


urlpatterns = [
    path('<int:topic_id>', KnowTopicView.get_know_by_topic_id),
    path('quiz/add', KnowQuizView.add_know_quiz),
    path('quiz/<int:quiz_id>', KnowQuizView.get_question_by_quiz_id),
    path('quiz/all/<int:know_id>', KnowQuizView.get_all_questions_by_know_id),
    path('quiz/edit/<int:quiz_id>', KnowQuizView.edit_know_quiz),
    path('essay/add', KnowEssayView.add_know_essay),
    path('essay/edit/<int:ref_id>', KnowEssayView.edit_know_essay_by_ref_id),
    path('essay/<int:know_id>', KnowEssayView.get_know_essay_by_know_id),
    path('answer/quiz/<int:know_quiz_id>', KnowQuizView.save_student_answer),
    path('answer/quiz/all/<int:know_id>', KnowQuizView.save_student_all_answers_by_know_id),
    path('answer/essay/<int:ref_id>', KnowEssayView.save_essay_answer),
    path('is_exist/<int:topic_id>', KnowTopicView.is_know_exist_by_topic_id),

   

] 