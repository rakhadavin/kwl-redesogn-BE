from django.http import Http404, JsonResponse
from django.shortcuts import render
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.models import Student
from authentication.serializers import StudentSerializer
from .models import Course, RewardItem, Topic
from authentication.models import Lecturer
from rest_framework import status
from .serializers import CourseSerializer, RewardItemSerializer, TopicSerializer, AddAssistantToCourseSerializer, AddLecturerToCourseSerializer, AddStudentToCourseSerializer, RemoveAssistantFromCourseSerializer, RemoveStudentFromCourseSerializer, RemoveLecturerFromCourseSerializer
# Create your views here.
from rest_framework import generics
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from drf_yasg.utils import swagger_auto_schema
from .api_exceptions import CourseNotFoundException
from authentication.api_exceptions import LecturerNotFoundException




class CourseEnrollView():
    @api_view(['GET'])
    @swagger_auto_schema(operation_summary="Get all students by course id")
    def get_all_student_by_course_id(request, course_id):
        try:
            course = Course.objects.get(pk=course_id)
            students = course.students.all()
            students = StudentSerializer(students, many=True)
            return students.data
        except Course.DoesNotExist:
            raise CourseNotFoundException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @api_view(['GET'])
    @swagger_auto_schema(operation_summary="Get all teachers by course id")
    def get_all_teachers_by_course_id(request,course_id):
        try:
            course = Course.objects.get(pk=course_id)
            teachers = course.lecturer_team.all()
            teachers = StudentSerializer(teachers, many=True)
            return teachers.data
        except Course.DoesNotExist:
            raise CourseNotFoundException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @api_view(['POST'])
    @swagger_auto_schema(operation_summary="Enroll student to course", request_body=AddStudentToCourseSerializer)
    def enroll_student_to_course(self, request):
        serializer = AddStudentToCourseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course = Course.objects.get(pk=serializer.validated_data['course_id'])
        student = Student.objects.get(pk=serializer.validated_data['student_id'])
        course.students.add(student)
        students = StudentSerializer(course.students.all(), many=True)
        return students.data
    

    
    # @api_view(['DELETE'])
    # def remove_student_from_course(self, course_id, student_id):
    #     course = Course.objects.get(pk=course_id)
    #     student = Student.objects.get(pk=student_id)
    #     course.students.remove(student)

    #     return course.students.all()
    
    # @api_view(['GET'])
    # def get_lecturer_by_course_id(self, course_id):
    #     course = Course.objects.get(pk=course_id)
    #     lecturer = course.lecturer_team.all()
    #     return lecturer
    
    # @api_view(['GET'])
    # def get_assistant_by_course_id(self, course_id):
    #     course = Course.objects.get(pk=course_id)
    #     assistant = course.assistant_team.all()
    #     return assistant
    
    # @api_view(['POST'])
    # def enroll_assistant_to_course(self, course_id, student_id):
    #     course = Course.objects.get(pk=course_id)
    #     student = Student.objects.get(pk=student_id)
    #     course.assistant_team.add(student)
    #     return course.assistant_team.all()
    
    # @api_view(['DELETE'])
    # def remove_assistant_from_course(self, course_id, student_id):
    #     course = Course.objects.get(pk=course_id)
    #     student = Student.objects.get(pk=student_id)
    #     course.assistant_team.remove(student)
    #     return course.assistant_team.all()
    
    # @api_view(['POST'])
    # def enroll_lecturer_to_course(self, course_id, lecturer_id):
    #     course = Course.objects.get(pk=course_id)
    #     lecturer = Student.objects.get(pk=lecturer_id)
    #     course.lecturer_team.add(lecturer)
    #     return course.lecturer_team.all()
    
    # @api_view(['DELETE'])
    # def remove_lecturer_from_course(self, course_id, lecturer_id):
    #     course = Course.objects.get(pk=course_id)
    #     lecturer = Student.objects.get(pk=lecturer_id)
    #     course.lecturer_team.remove(lecturer)
    #     return course.lecturer_team.all()

class CourseLecturerView(APIView):
    permission_classes = [IsAuthenticated,]
    @swagger_auto_schema(operation_description="Get all courses by lecturer id")
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
    @swagger_auto_schema(operation_description="Get all topics by course id")
    def get(self, request, course_id, format=None):
        try:
            course = Course.objects.get(pk=course_id)
            topics = Topic.objects.filter(course=course)
            serializer = TopicSerializer(topics, many=True)
            return Response(serializer.data)
        except Course.DoesNotExist:
            raise CourseNotFoundException()
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
        course = self.get_object(pk)
        serializer = CourseSerializer(course)
        return Response(serializer.data)
    
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
        course = self.get_object(pk)
        course.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class RewardList(APIView):
    permission_classes = [IsAuthenticated,]
    @swagger_auto_schema(operation_description="List all rewards or create a new reward")
    def get(self, request, course_id, format=None):
        try:
            course = Course.objects.get(pk=course_id)
            rewards = RewardItem.objects.filter(course=course)
            serializer = RewardItemSerializer(rewards, many=True)
            return Response(serializer.data)
        except Course.DoesNotExist:
            return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)
        
    @swagger_auto_schema(request_body=RewardItemSerializer, operation_description="create a new reward")
    def post(self, request, format=None):
        serializer = RewardItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
   
    
class RewardDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated,]
    queryset = RewardItem.objects.all()
    serializer_class = RewardItemSerializer

    @swagger_auto_schema(operation_description="Retrieve, update or delete a reward item")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Retrieve, update or delete a reward item")
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Retrieve, update or delete a reward item")
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class TopicList(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated,]
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer

    @swagger_auto_schema(operation_description="List all topics or create a new topic")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="List all topics or create a new topic")
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class TopicDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated,]
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer

    @swagger_auto_schema(operation_description="Retrieve, update or delete a topic")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Retrieve, update or delete a topic")
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Retrieve, update or delete a topic")
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)