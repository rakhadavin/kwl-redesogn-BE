from django.urls import path
from . import views


urlpatterns = [
    path('quizzes/', views.quiz_list_create, name='quiz-list-create'),
    path('quizzes/<uuid:quiz_id>/', views.quiz_detail, name='quiz-detail'),
    
    path('quizzes/<uuid:quiz_id>/questions/', views.update_quiz_questions, name='update-quiz-questions'),
    
    # Guest quiz endpoints
    path('quizzes/<uuid:quiz_id>/join/', views.join_quiz, name='join-quiz'),
    path('quiz-attempts/<uuid:attempt_id>/update-name/', views.update_guest_name, name='update-guest-name'),
    
    # Public endpoints for QR code
    path('quiz-by-pin/<int:quiz_pin>/', views.get_quiz_by_pin, name='get-quiz-by-pin'),

]