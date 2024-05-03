from authentication import views
from django.urls import path

from course import views

urlpatterns = [
    path('', views.CourseList.as_view()),
    path('<int:pk>', views.CourseDetailView.as_view()),
    
    path('topic', views.TopicList.as_view()),
    path('topic/<int:pk>', views.TopicDetail.as_view()),
    path('topic/<int:course_id>/all', views.CourseTopicView.as_view()),

    path('<int:course_id>/students', views.CourseEnrolledView.get_all_student_by_course_id),
    path('<int:course_id>/lecturers', views.CourseEnrolledView.get_all_lecturers_by_course_id),

    path('enroll-student', views.EnrollStudentToCourseView.as_view()),
    path('enroll-lecturer', views.EnrollLecturerToCourseView.as_view()),
    path('enroll-assistant', views.EnrollAssistantToCourseView.as_view()),
    path('lecturer', views.CourseLecturerView.as_view()),

    path('reward/', views.RewardList.as_view()),
    path('reward/<int:pk>', views.RewardDetail.as_view()),
    path('reward/<int:course_id>/all', views.RewardCourseView.as_view()),
    

]

