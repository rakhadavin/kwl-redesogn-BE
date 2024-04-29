from authentication import views
from django.urls import path

from course import views

urlpatterns = [
    path('', views.CourseList.as_view()),
    path('<int:pk>', views.CourseDetailView.as_view()),
    path('topic', views.TopicList.as_view()),
    path('topic/<int:pk>', views.TopicDetail.as_view()),
    path('topic/all/<int:course_id>', views.CourseTopicView.as_view()),
    path('<int:course_id>/students', views.CourseStudentView.get_all_student_by_course_id),
    path('<int:course_id>/teachers', views.CourseStudentView.get_all_teachers_by_course_id),
]

