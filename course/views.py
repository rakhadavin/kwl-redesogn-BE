from datetime import datetime

from django.utils import timezone

from django.http import Http404
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.models import Student
from authentication.serializers import LecturerSerializer, StudentSerializer
from know.api_exceptions import KnowDoesNotExistException, KnowReflectionNotFoundException, KnowQuizNotFoundException
from learned.api_exceptions import LearnedDoesNotExistException, LearnedQuizNotFoundException, LearnedReflectionNotFoundException
from learned.models import Learned, LearnedReflectionStudentAnswer, LearnedQuizStudentAnswer, LearnedReflection, LearnedQuizQuestion
from wtk.models import WantToKnow, WtkReflectionStudentAnswer, WtkPollStudentAnswer, WtkReflection, WtkPollQuestion
from .models import Course, Feedback, RedeemHistory, RewardItem, RewardStudentPoint, Topic, KwlPoint
from authentication.models import Lecturer
from rest_framework import status
from wtk.api_exceptions import WtkDoesNotExistException, WtkReflectionNotFoundException, WtkPollNotFoundException
from .serializers import CourseSerializer, RedeemHistoryListSerializer, RewardItemSerializer, RewardPointSerializer, TopicSerializer, AddLecturerToCourseSerializer, AddStudentToCourseSerializer, RemoveStudentFromCourseSerializer, RemoveLecturerFromCourseSerializer, FeedbackSerializer, RedeemSerializer, KwlPointSerializer
from rest_framework import generics
from know.models import KnowReflectionStudentAnswer, KnowQuizStudentAnswer, Know
from rest_framework.decorators import api_view, permission_classes
from drf_yasg.utils import swagger_auto_schema
from .api_exceptions import CourseNotFoundException, StudentPointNotFoundException
from authentication.api_exceptions import LecturerNotFoundException, StudentNotFoundException
from django.db import transaction

class CourseEnrolledView():

    @permission_classes([IsAuthenticated,])
    @api_view(['GET'])
    @swagger_auto_schema(operation_summary="Get all students by course id")
    def get_all_student_by_course_id(request, course_id):
        try:
            course = Course.objects.get(pk=course_id)
            students = course.students.all()
            students = StudentSerializer(students, many=True)
            return Response(students.data, status=status.HTTP_200_OK)
        except Course.DoesNotExist:
            raise CourseNotFoundException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @permission_classes([IsAuthenticated,])
    @api_view(['GET'])
    @swagger_auto_schema(operation_summary="Get all teachers by course id")
    def get_all_lecturers_by_course_id(request,course_id):
        try:
            course = Course.objects.get(pk=course_id)
            teachers = course.lecturer_team.all()
            teachers = LecturerSerializer(teachers, many=True)
            return Response(teachers.data, status=status.HTTP_200_OK)
        except Course.DoesNotExist:
            raise CourseNotFoundException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class EnrollStudentToCourseView(APIView):
    permission_classes = [IsAuthenticated,]

    @swagger_auto_schema(operation_summary="Enroll student to course", request_body=AddStudentToCourseSerializer)
    def post(self, request):
        try:
            serializer = AddStudentToCourseSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            course = Course.objects.get(pk=serializer.validated_data['course_id'])
            student = Student.objects.get(pk=serializer.validated_data['student_id'])
            course.students.add(student)

            students = StudentSerializer(course.students.all(), many=True)
            return Response(students.data, status=status.HTTP_201_CREATED)
        except Course.DoesNotExist:
            raise CourseNotFoundException()
        except Student.DoesNotExist:
            raise StudentNotFoundException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @swagger_auto_schema(operation_summary="Remove student from course", request_body=RemoveStudentFromCourseSerializer)
    def delete(self, request):
        try:
            serializer = RemoveStudentFromCourseSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            course = Course.objects.get(pk=serializer.validated_data['course_id'])
            student = Student.objects.get(pk=serializer.validated_data['student_id'])
            course.students.remove(student)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Course.DoesNotExist:
            raise CourseNotFoundException()
        except Student.DoesNotExist:
            raise StudentNotFoundException()
        except Exception as e:
            print(e)
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class EnrollLecturerToCourseView(APIView):
    permission_classes = [IsAuthenticated,]

    @swagger_auto_schema(operation_summary="Enroll lecturer to course", request_body=AddLecturerToCourseSerializer)
    def post(self, request):
        try:
            serializer = AddLecturerToCourseSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            course = Course.objects.get(pk=serializer.validated_data['course_id'])
            lecturer = Lecturer.objects.get(pk=serializer.validated_data['lecturer_id'])
            course.lecturer_team.add(lecturer)

            lecturers = LecturerSerializer(course.lecturer_team.all(), many=True)
            return Response(lecturers.data, status=status.HTTP_201_CREATED)
        except Course.DoesNotExist:
            raise CourseNotFoundException()
        except Lecturer.DoesNotExist:
            raise LecturerNotFoundException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @swagger_auto_schema(operation_summary="Remove lecturer from course", request_body=RemoveLecturerFromCourseSerializer)
    def delete(self, request):
        try:
            serializer = RemoveLecturerFromCourseSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            course = Course.objects.get(pk=serializer.validated_data['course_id'])
            lecturer = Lecturer.objects.get(pk=serializer.validated_data['lecturer_id'])
            course.lecturer_team.remove(lecturer)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Course.DoesNotExist:
            raise CourseNotFoundException()
        except Lecturer.DoesNotExist:
            raise LecturerNotFoundException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CourseLecturerView(APIView):
    permission_classes = [IsAuthenticated,]
    @swagger_auto_schema(operation_summary="Get all courses taught by lecturer id")
    def get(self, request, format=None):
        try:
            user_id = request.user.id
            lecturer = Lecturer.objects.get(user_id=user_id)
            courses = courses = Course.objects.filter(lecturer_team__id=lecturer.pk)
            serializer = CourseSerializer(courses, many=True)
            return Response(serializer.data)
        except Lecturer.DoesNotExist:
            raise LecturerNotFoundException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CourseTopicView(APIView):
    permission_classes = [IsAuthenticated,]
    @swagger_auto_schema(operation_summary="Get all topics by course id and also give its K-W-L data")
    def get(self, request, course_id, format=None):
        try:
            course = Course.objects.get(pk=course_id)
            topics = Topic.objects.filter(course=course)
            serializer = TopicSerializer(topics, many=True)
            return Response(serializer.data)
        except Course.DoesNotExist:
            raise CourseNotFoundException()
        except Exception as e:
            print(str(e))
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class CourseStudentView(APIView):
    permission_classes = [IsAuthenticated,]
    @swagger_auto_schema(operation_summary="Get all courses enrolled by student id")
    def get(self, request, format=None):
        try:
            user_id = request.user.id
            student = Student.objects.get(user_id=user_id)
            courses = Course.objects.filter(students__id=student.pk)
            serializer = CourseSerializer(courses, many=True)
            return Response(serializer.data)
        except Student.DoesNotExist:
            raise StudentNotFoundException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


class CourseList(APIView):
    permission_classes = [IsAuthenticated,]
    @swagger_auto_schema(operation_summary="List all courses")
    def get(self, request, format=None):
        try:
            courses = Course.objects.all()
            serializer = CourseSerializer(courses, many=True)
            return Response(serializer.data)
        except Exception as e:
            print(str(e))
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @swagger_auto_schema(operation_summary="Create a course",request_body=CourseSerializer, responses={201: 'Created'})
    def post(self, request,  format=None):
        try:
            user_id = request.user.id
            lecturer = Lecturer.objects.get(user_id=user_id)
            data = request.data.copy()
            data['lecturer'] = lecturer.id

            serializer = CourseSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Lecturer.DoesNotExist:
            raise LecturerNotFoundException()
        except Exception as e:
            print(str(e))
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CourseDetailView(APIView):
    permission_classes = [IsAuthenticated,]
    def get_object(self, pk):
        try:
            return Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            raise CourseNotFoundException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(operation_summary="Retrieve a course")
    def get(self, request, pk, format=None):
        try:
            course = self.get_object(pk)
            serializer = CourseSerializer(course)
            return Response(serializer.data)
        except Course.DoesNotExist:
            raise CourseNotFoundException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @swagger_auto_schema(request_body=CourseSerializer, operation_summary="Update a course")
    def put(self, request, pk, format=None):
        try:
            user_id = request.user.id
            lecturer = Lecturer.objects.get(user_id=user_id)
            data = request.data.copy()
            data['lecturer'] = lecturer.id
            course = self.get_object(pk)
            serializer = CourseSerializer(course, data=data)
            serializer.is_valid(raise_exception=True)   
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Lecturer.DoesNotExist:
            raise LecturerNotFoundException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
    @swagger_auto_schema(operation_summary="delete a course")
    def delete(self, request, pk, format=None):
        try:
            course = self.get_object(pk)
            course.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Course.DoesNotExist:
            raise CourseNotFoundException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class RewardCourseView(APIView):
    permission_classes = [IsAuthenticated,]
    @swagger_auto_schema(operation_summary="Get all rewards by course id")
    def get(self, request, course_id, format=None):
        try:
            course = Course.objects.get(pk=course_id)
            rewards = RewardItem.objects.filter(course=course)
            rewards = [reward for reward in rewards if datetime.strptime(reward.expired_date, '%Y-%m-%d').date() >= timezone.now().date()]
            serializer = RewardItemSerializer(rewards, many=True)
            return Response(serializer.data)
        except Course.DoesNotExist:
            raise CourseNotFoundException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class RewardRedeemCourseView(APIView):
    permission_classes = [IsAuthenticated,]
    @swagger_auto_schema(operation_summary="Get all rewards with redeemed status by course id and student_id")
    def get(self, request, course_id, student_id, format=None):
        try:
            course = Course.objects.get(pk=course_id)
            student = Student.objects.get(pk=student_id)
            rewards = RewardItem.objects.filter(course=course)
            rewards = [reward for reward in rewards if datetime.strptime(reward.expired_date, '%Y-%m-%d').date() >= timezone.now().date()]
            serializer = RewardItemSerializer(rewards, many=True)
            for reward in serializer.data:
                reward['redeemed'] = False
                if RedeemHistory.objects.filter(reward_item_id=reward['id'], student=student).exists():
                    reward['redeemed'] = True
     
            return Response(serializer.data)
        except Course.DoesNotExist:
            raise CourseNotFoundException()
        except Student.DoesNotExist:
            raise StudentNotFoundException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class RewardList(APIView):
    permission_classes = [IsAuthenticated,]
    @swagger_auto_schema(operation_summary="List all rewards")
    def get(self, request, format=None):
        try:
            rewards = RewardItem.objects.all()
            serializer = RewardItemSerializer(rewards, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @swagger_auto_schema(request_body=RewardItemSerializer, operation_summary="create a new reward")
    def post(self, request, format=None):
        try:
            serializer = RewardItemSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
   
    
class RewardDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated,]
    queryset = RewardItem.objects.all()
    serializer_class = RewardItemSerializer

    @swagger_auto_schema(operation_summary="Retrieve a reward item")
    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @swagger_auto_schema(operation_summary="Update a reward item")
    def put(self, request, *args, **kwargs):
        try:
            return super().put(request, *args, **kwargs)
        except Exception as e:
            print(str(e))
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(operation_summary="Delete a reward item")
    def delete(self, request, *args, **kwargs):
        try:
            return super().delete(request, *args, **kwargs)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TopicList(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated,]
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer

    @swagger_auto_schema(operation_summary="List all topics")
    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(operation_summary="Create a new topic")
    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TopicDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated,]
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer

    @swagger_auto_schema(operation_summary="Retrieve a topic")
    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(operation_summary="Update a topic")
    def put(self, request, *args, **kwargs):
        try:
            return super().put(request, *args, **kwargs)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(operation_summary="Delete a topic")
    def delete(self, request, *args, **kwargs):
        try:
            return super().delete(request, *args, **kwargs)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class FeedbackList(APIView):
    permission_classes = [IsAuthenticated,]
    @swagger_auto_schema(operation_summary="Add feedback to a course", request_body=FeedbackSerializer)
    def post(self, request, format=None):
        try:
            serializer = FeedbackSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
       
            serializer.save()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @swagger_auto_schema(operation_summary="List all feedbacks")
    def get(self, request, format=None):
        try:
            feedbacks = Feedback.objects.all()
            serializer = FeedbackSerializer(feedbacks, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    
class FeedbackDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated,]
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer

    @swagger_auto_schema(operation_summary="Retrieve a feedback")
    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(operation_summary="Update a feedback")
    def put(self, request, *args, **kwargs):
        try:
            return super().put(request, *args, **kwargs)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(operation_summary="Delete a feedback")
    def delete(self, request, *args, **kwargs):
        try:
            return super().delete(request, *args, **kwargs)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class FeedbackTopicView(APIView):
    permission_classes = [IsAuthenticated,]
    def get(self, request, topic_id, format=None):
        try:
            topic = Topic.objects.get(pk=topic_id)
            feedbacks = Feedback.objects.filter(topic=topic)
            serializer = FeedbackSerializer(feedbacks, many=True)
            return Response(serializer.data)
        except Topic.DoesNotExist:
            raise CourseNotFoundException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class RedeemRewardView(APIView):
    permission_classes = [IsAuthenticated,]
    @swagger_auto_schema(operation_summary="Redeem reward by student id and reward id")
    def post(self, request, format=None):
        try:
            with transaction.atomic():
                serializer = RedeemSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)

                student_id = serializer.validated_data['student_id']
                reward_id = serializer.validated_data['reward_id']
                course_id = serializer.validated_data['course_id']

                student = Student.objects.get(pk=student_id)
                reward = RewardItem.objects.get(pk=reward_id)
                course = Course.objects.get(pk=course_id)

                student_point = RewardStudentPoint.objects.get(student=student, course=course)

                if student_point.total_point < reward.point:
                    return Response({"message":"Insufficient point"}, status=status.HTTP_400_BAD_REQUEST)
                
                if reward.stock > 0:
                    reward.stock -= 1
                    student_point.total_point -= reward.point
                    student_point.save()
                    reward.save()
                    RedeemHistory.objects.create(student=student, reward_item=reward)
                    return Response({"message":"Reward redeemed"}, status=status.HTTP_200_OK)
                else:
                    return Response({"message":"Reward out of stock"}, status=status.HTTP_400_BAD_REQUEST)
                
        except Student.DoesNotExist:
            raise StudentNotFoundException()
        except RewardItem.DoesNotExist:
            raise CourseNotFoundException()
        except RewardStudentPoint.DoesNotExist:
            raise StudentPointNotFoundException()
        except Course.DoesNotExist:
            raise CourseNotFoundException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)  
        
class RewardStudentPointView(APIView):
    permission_classes = [IsAuthenticated,]
    @swagger_auto_schema(operation_summary="Get student point by student id and course id")
    def get(self, request, student_id, course_id, format=None):
        try:
            student = Student.objects.get(pk=student_id)
            course = Course.objects.get(pk=course_id)
            student_point = RewardStudentPoint.objects.get(student=student, course=course)
            serializer = RewardPointSerializer(student_point)
            return Response(serializer.data)
        except Student.DoesNotExist:
            raise StudentNotFoundException()
        except Course.DoesNotExist:
            raise CourseNotFoundException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CourseEnrollmentStatusView(APIView):
    permission_classes = [IsAuthenticated,]
    @swagger_auto_schema(operation_summary="Get all courses and its enrollment status by student id")
    def get(self, request, student_id, format=None):
        try:
            courses = Course.objects.all()
            courses_data = []
            for course in courses:
                course_data = CourseSerializer(course).data
                course_data['enrolled'] = course.students.filter(pk=student_id).exists()
                courses_data.append(course_data)
            return Response(courses_data, status=status.HTTP_200_OK)
        except Student.DoesNotExist:
            raise StudentNotFoundException
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FeedbackStudentCourseView(APIView):
    permission_classes = [IsAuthenticated,]
    @swagger_auto_schema(operation_summary="Get all feedbacks by course id and student_id")
    def get(self, request, course_id, student_id, format=None):
        try:
            student = Student.objects.get(pk=student_id)
            course = Course.objects.get(pk=course_id)
            feedbacks = Feedback.objects.filter(topic__course=course, student=student)
            serializer = FeedbackSerializer(feedbacks, many=True)
            new_data = {
                'course_full_name': course.full_name,
                'course_short_name': course.short_name,
                'feedbacks': serializer.data
            }
            return Response(new_data, status=status.HTTP_200_OK)
        except Course.DoesNotExist:
            raise CourseNotFoundException()
        except Student.DoesNotExist:
            raise StudentNotFoundException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class RedeemHistoryDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated,]
    queryset = RedeemHistory.objects.all()
    serializer_class = RedeemSerializer

    @swagger_auto_schema(operation_summary="Retrieve reward history by student id")
    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    
class RedeemHistoryListView(APIView):
    permission_classes = [IsAuthenticated,]

    @swagger_auto_schema(operation_summary="List all redeem history by course id and student id")
    def get(self, request, student_id, course_id, format=None):
        try:
            course = Course.objects.get(pk=course_id)
            student = Student.objects.get(pk=student_id)
            rewards = RedeemHistory.objects.filter(student=student, reward_item__course=course)
            serializer = RedeemHistoryListSerializer(rewards, many=True)
            return Response(serializer.data)
        except Student.DoesNotExist:
            raise StudentNotFoundException()
        except Course.DoesNotExist:
            raise CourseNotFoundException()
        except Exception as e:
            print(str(e))
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

# class KwlStatusView(APIView):
#     permission_classes = [IsAuthenticated,]

#     @swagger_auto_schema(operation_summary="Get Kwl Status by topic id and student id")
#     def get(self, request, topic_id, student_id, format=None):
#         try:
#             student = Student.objects.get(pk=student_id)
#             topic = Topic.objects.get(pk=topic_id)
#             kwl_points = KwlPoint.objects.get(student=student, topic=topic)
#             serializer = KwlPointSerializer(kwl_points)
#             return Response(serializer.data)
#         except Student.DoesNotExist:
#             raise StudentNotFoundException()
#         except Topic.DoesNotExist:
#             raise CourseNotFoundException()
#         except Exception as e:
#             return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class KwlStatusView(APIView):
    permission_classes = [IsAuthenticated,]

    @swagger_auto_schema(operation_summary="Get topics with kwl status of the student")
    def get(self, request, course_id, student_id, format=None):
        try:
            topics_data = []
            student = Student.objects.get(pk=student_id)
            course = Course.objects.get(pk=course_id)
            topics = Topic.objects.filter(course=course)
            for topic in topics:
                topic_data = {}
                topic_data['topic_data'] = TopicSerializer(topic).data
                try:
                    kwl_point = KwlPoint.objects.get(student=student, topic=topic)
                    kwl_data = KwlPointSerializer(kwl_point).data
                    topic_data['kwl_data'] = kwl_data
                except KwlPoint.DoesNotExist:
                    topic_data['kwl_data'] = "kosong"

                topics_data.append(topic_data)

            return Response(topics_data, status=status.HTTP_200_OK)
        except Student.DoesNotExist:
            raise StudentNotFoundException()
        except Topic.DoesNotExist:
            raise CourseNotFoundException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class KwlPointView(APIView):
    permission_classes = [IsAuthenticated,]

    @swagger_auto_schema(operation_summary="Get student kwl point by topic id and student id")
    def get(self, request, topic_id, student_id, format=None):
        try:
            student = Student.objects.get(pk=student_id)
            topic = Topic.objects.get(pk=topic_id)
            kwl_points = KwlPoint.objects.get(student=student, topic=topic)
            serializer = KwlPointSerializer(kwl_points)
            return Response(serializer.data)
        except Student.DoesNotExist:
            raise StudentNotFoundException()
        except Topic.DoesNotExist:
            raise CourseNotFoundException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# class KwlPointView(APIView):
#         permission_classes = [IsAuthenticated,]

#         @swagger_auto_schema(operation_summary="Get student kwl point by topic id and student id")
#         def get(self, request, topic_id, student_id, format=None):
#             try:
#                 student = Student.objects.get(pk=student_id)
#                 topic = Topic.objects.get(pk=topic_id)
#                 know = Know.objects.filter(topic=topic)
#                 learned = Learned.objects.filter(topic=topic)
#                 wtk = WantToKnow.objects.filter(topic=topic)
           
#                 kwl_points = {'know_score': 0, 'learned_score': 0, 'wtk_score': 0}
#                 if know.exists():
#                     know_type = know.first().type
#                     if know_type == 'reflection':
#                         know_ref = KnowReflectionStudentAnswer.objects.filter(student=student)
#                         if know_ref.exists():
#                             kwl_points['know_score'] = know_ref.first().know_ref.score

#                     if know_type == 'quiz':
#                         know_quiz_answer = KnowQuizStudentAnswer.objects.filter(student=student)
#                         if know_quiz_answer.exists():
#                             answers = know_quiz_answer.first().answers.all()
#                             for answer in answers:
#                                 if answer.isCorrect:
#                                     kwl_points['know_score'] += answer.know_quiz.score
                
#                 if learned.exists():
#                     learned_type = learned.first().type
             
#                     if learned_type == 'reflection':
#                         learned_answer = LearnedReflectionStudentAnswer.objects.filter(student=student)
#                         if learned_answer.exists():
#                             kwl_points['learned_score'] = learned_answer.first().learned_ref.score

#                     if learned_type == 'quiz':
#                         learned_quiz_answer = LearnedQuizStudentAnswer.objects.filter(student=student)
#                         if learned_quiz_answer.exists():
#                             answers = learned_quiz_answer.first().answers.all()
#                             for answer in answers:
#                                 if answer.isCorrect:
#                                     kwl_points['learned_score'] += answer.learned_quiz.score

#                 if wtk.exists():
#                     wtk_type = wtk.first().type
#                     if wtk_type == 'reflection':
#                         wtk_ref = WtkReflectionStudentAnswer.objects.filter(student=student)
#                         if wtk_ref.exists():
#                             kwl_points['wtk_score'] = wtk_ref.first().wtk_ref.score

#                     if wtk_type == 'checkbox':
#                         print('hello')
#                         wtk_poll = WtkPollStudentAnswer.objects.filter(student=student)
#                         if wtk_poll.exists():
#                             kwl_points['wtk_score'] = wtk_poll.first().wtk_poll.score
                
#                 return Response(kwl_points, status=status.HTTP_200_OK)
            
#             except Student.DoesNotExist:
#                 raise StudentNotFoundException()
#             except Topic.DoesNotExist:
#                 raise CourseNotFoundException()
        
#             except Exception as e:
#                 return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            

