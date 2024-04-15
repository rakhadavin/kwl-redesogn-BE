from .views import KnowQuizView, KnowEssayView
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    # path('know', KnowView.as_view()),
    # path('wtk', WantToKnowView.as_view()),
    # path('learned', LearnedView.as_view()),
    path('quiz/add', KnowQuizView.add_know_quiz),
    path('quiz/<int:pk>', KnowQuizView.get_question_by_quiz_id),
    path('quizzes/<int:pk>', KnowQuizView.get_questions_answers_by_know_id),
    path('essay/add', KnowEssayView.add_know_essay),
    path('answer/quiz/<int:know_quiz_id>', KnowQuizView.save_student_answer),
    path('answer/quizzes/<int:know_id>', KnowQuizView.evaluate_save_student_all_answers_by_know_id),
    path('answer/essay/<int:know_ref_id>', KnowEssayView.save_essay_answer),
    # path('wanttoknowpoll', WantToKnowPollView.as_view()),
    # path('wanttoknowpollchoice', WantToKnowPollChoiceView.as_view()),

] 