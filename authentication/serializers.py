from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from kwl import settings
from django.contrib.auth import get_user_model
from rest_framework import exceptions
from django.urls import exceptions as url_exceptions
from .models import KwlUser, Course, Lecturer, Student

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

class KwlUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = KwlUser
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'

# class LecturerSerializer(serializers.ModelSerializer):
#     user = KwlUserSerializer()
#     courses_taught = CourseSerializer(many=True)

#     class Meta:
#         model = Lecturer
#         fields = ['id', 'user', 'department', 'courses_taught']

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})
    
# class StudentSerializer(serializers.ModelSerializer):
#     user = KwlUserSerializer()
#     assistant_courses = CourseSerializer(many=True)

#     class Meta:
#         model = Student
#         fields = ['id', 'user', 'student_id', 'major', 'assistant_courses', 'term']

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['name'] = user.name
        # ...

        return token

class StudentSerializer(serializers.Serializer):
    # email = serializers.EmailField(required=True)
    # username = serializers.CharField(
    #     max_length=30,
    #     min_length=6,
    #     required=True
    # )
    # nama_lengkap = serializers.CharField(required=True)
    # password = serializers.CharField(write_only=True, required=True)
    user = KwlUserSerializer(required=True)
    assistant_courses = CourseSerializer(many=True, required=False)
    student_id = serializers.CharField(required=True)
    major = serializers.CharField(required=True)
    faculty = serializers.CharField(required=True)
    term = serializers.CharField(required=True)
    
    


    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        user_data = validated_data.pop('user', None)
        assistant_courses_data = validated_data.pop('assistant_courses', [])
        if user_data:
            user = KwlUser.objects.create_user(**user_data)
        else:
            user = None

        print(user)     
        # Create the Student instance
        student = Student.objects.create(user=user, **validated_data)
        
        # Add assistant courses if provided
        for course_data in assistant_courses_data:
            assistant_course, _ = Course.objects.get_or_create(**course_data)
            student.assistant_courses.add(assistant_course)
        
        student.save()
        
        return student

      
    
    def update(self, instance, validated_data):
        """
        Update and return an existing `Student` instance, given the validated data.
        """
        instance.student_id = validated_data.get('student_id', instance.student_id)
        instance.domisili = validated_data.get('domisili', instance.domisili)
        instance.jurusan = validated_data.get('jurusan', instance.jurusan)
        instance.fakultas = validated_data.get('fakultas', instance.fakultas)
        instance.semester = validated_data.get('semester', instance.semester)
        
        instance.save()
        return instance
    
    
# class DosenRegisterSerializer(RegisterSerializer):
#     lecturerId = serializers.CharField()
