from django.http import Http404, JsonResponse
from django.shortcuts import render
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.models import Student
from authentication.serializers import StudentSerializer
from .models import Course, Topic
from rest_framework import status
from .serializers import CourseSerializer, TopicSerializer
# Create your views here.
from rest_framework import generics
from rest_framework.decorators import api_view

class CourseStudentView():
    @api_view(['GET'])
    def get_all_student_by_course_id(self, course_id):
        course = Course.objects.get(pk=course_id)
        students = course.students.all()
        students = StudentSerializer(students, many=True)
        return students.data


    @api_view(['POST'])
    def enroll_student_to_course(self, course_id, student_id):
        course = Course.objects.get(pk=course_id)
        student = Student.objects.get(pk=student_id)
        course.students.add(student)
        students = StudentSerializer(course.students.all(), many=True)
        return students.data
    
    @api_view(['DELETE'])
    def remove_student_from_course(self, course_id, student_id):
        course = Course.objects.get(pk=course_id)
        student = Student.objects.get(pk=student_id)
        course.students.remove(student)

        return course.students.all()
    
    @api_view(['GET'])
    def get_lecturer_by_course_id(self, course_id):
        course = Course.objects.get(pk=course_id)
        lecturer = course.lecturer_team.all()
        return lecturer
    
    @api_view(['GET'])
    def get_assistant_by_course_id(self, course_id):
        course = Course.objects.get(pk=course_id)
        assistant = course.assistant_team.all()
        return assistant
    
    @api_view(['POST'])
    def enroll_assistant_to_course(self, course_id, student_id):
        course = Course.objects.get(pk=course_id)
        student = Student.objects.get(pk=student_id)
        course.assistant_team.add(student)
        return course.assistant_team.all()
    
    @api_view(['DELETE'])
    def remove_assistant_from_course(self, course_id, student_id):
        course = Course.objects.get(pk=course_id)
        student = Student.objects.get(pk=student_id)
        course.assistant_team.remove(student)
        return course.assistant_team.all()
    
    @api_view(['POST'])
    def enroll_lecturer_to_course(self, course_id, lecturer_id):
        course = Course.objects.get(pk=course_id)
        lecturer = Student.objects.get(pk=lecturer_id)
        course.lecturer_team.add(lecturer)
        return course.lecturer_team.all()
    
    @api_view(['DELETE'])
    def remove_lecturer_from_course(self, course_id, lecturer_id):
        course = Course.objects.get(pk=course_id)
        lecturer = Student.objects.get(pk=lecturer_id)
        course.lecturer_team.remove(lecturer)
        return course.lecturer_team.all()
    
class CourseList(APIView):
    # permission_classes = (AllowAny,)
    def get(self, request, format=None):
        try:
            courses = Course.objects.all()
            serializer = CourseSerializer(courses, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request,  format=None):
     
        serializer = CourseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class CourseDetailView(APIView):
    # permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            raise Http404
        
    def get(self, request, pk, format=None):
        course = self.get_object(pk)
        serializer = CourseSerializer(course)
        return Response(serializer.data)
    
    def put(self, request, pk, format=None):
       
        course = self.get_object(pk)
        serializer = CourseSerializer(course, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error": str(serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)
        
    
    def delete(self, request, pk, format=None):
        course = self.get_object(pk)
        course.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TopicList(generics.ListCreateAPIView):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer


class TopicDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer