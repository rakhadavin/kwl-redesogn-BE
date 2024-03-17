from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from course.models import Course
from .models import KwlUser, Student, Lecturer
from course.serializers import CourseSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class KwlUserSerializer(serializers.ModelSerializer):
    nama_lengkap = serializers.CharField(required=True)
    class Meta:
        model = KwlUser
        fields = '__all__'


class LecturerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lecturer
        fields = '__all__'

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})
    

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['name'] = user.first_name+" "+user.last_name
        token['email'] = user.email
        token['username'] = user.username

        return token



class StudentSerializer(serializers.Serializer):
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

        nama_lengkap = user_data['nama_lengkap']
        nama_lengkap = nama_lengkap[0].upper() + nama_lengkap[1:]
                    
        first_name = nama_lengkap.split()[0]

        last_name = ' '.join(nama_lengkap.split()[1:]) if len(nama_lengkap) > 1 else ''
        user_data["first_name"]=first_name
        user_data["last_name"]=last_name
        user_data.pop('nama_lengkap', None)

        if user_data:
            user = KwlUser.objects.create_user(**user_data)
        else:
            user = None    
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
    
        instance.jurusan = validated_data.get('jurusan', instance.jurusan)
        instance.fakultas = validated_data.get('fakultas', instance.fakultas)
        instance.semester = validated_data.get('semester', instance.semester)

        user_data = validated_data.pop('user', None)
        if user_data:
            user = KwlUser.objects.get(username=user_data.username)
            user.domisili
        else:
            user = None   
        nama_lengkap = user_data['nama_lengkap']
        nama_lengkap = nama_lengkap[0].upper() + nama_lengkap[1:]  


        instance.save()
        return instance
    
    
# class DosenRegisterSerializer(RegisterSerializer):
#     lecturerId = serializers.CharField()
