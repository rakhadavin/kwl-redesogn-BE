from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from course.models import Course
from .models import KwlUser, Student, Lecturer
from course.serializers import CourseSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class KwlUserSerializer(serializers.ModelSerializer):
    nama_lengkap = serializers.CharField(write_only=True)
    nama_lengkap_read = serializers.SerializerMethodField()
    username = serializers.CharField(write_only=True, required=False)  # Add this line
    password = serializers.CharField(write_only=True, required=False)  # Add this line

    class Meta:
        model = KwlUser
        fields = ['username', 'email', 'password', 'role', 'nama_lengkap','nama_lengkap_read','domisili', 'is_active', 'is_staff', 'is_superuser', 'last_login', 'date_joined']

    def get_nama_lengkap_read(self, obj):
        return obj.first_name + ' ' + obj.last_name
    
    


class LecturerSerializer(serializers.ModelSerializer):
    user = KwlUserSerializer(required=True)
    class Meta:
        model = Lecturer
        fields = '__all__'


    def get_initial(self):
        initial = super().get_initial()
        if self.instance is not None:
            initial['user'] = KwlUserSerializer(self.instance.user).data
        return initial

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """

        # Extract user data and assistant courses data
        user_data = validated_data.pop('user', None)
        courses_taught = validated_data.pop('courses_taught', [])

        # Extract first_name and last_name from nama_lengkap
        nama_lengkap = user_data['nama_lengkap']
        nama_lengkap = nama_lengkap[0].upper() + nama_lengkap[1:]   
        first_name = nama_lengkap.split()[0]
        last_name = ' '.join(nama_lengkap.split()[1:]) if len(nama_lengkap) > 1 else ''

        # Modify user_data
        user_data["first_name"]=first_name
        user_data["last_name"]=last_name
        user_data.pop('nama_lengkap', None)

        if user_data:
            user = KwlUser.objects.create_user(**user_data)
        else:
            user = None    
        # Create the Student instance
        lecturer = Lecturer.objects.create(user=user, **validated_data)
        
        user.role = 'lecturer'
        user.save()
        # Add assistant courses if provided
        for course_data in courses_taught:
            courses_taught, _ = Course.objects.get_or_create(**course_data)
            lecturer.courses_taught.add(courses_taught)
        
        lecturer.save()
        
        return lecturer
    
    def update(self, instance, validated_data):
        """
        Update and return an existing `Student` instance, given the validated data.
        """
    
        instance.department = validated_data.get('department', instance.department)

        user_data = validated_data.pop('user', None)
        if user_data:
            user = instance.user
            user.domisili = user_data.get('domisili', user.domisili)
            nama_lengkap = user_data.get('nama_lengkap', user.first_name + ' ' + user.last_name)
            nama_lengkap = nama_lengkap[0].upper() + nama_lengkap[1:]  
            first_name = nama_lengkap.split()[0]
            last_name = ' '.join(nama_lengkap.split()[1:]) if len(nama_lengkap.split()) > 1 else ''
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            instance.user = user
        else:
            user = None   


        instance.save()
        return instance
    

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
    user = KwlUserSerializer(required=False)
    assistant_courses = CourseSerializer(many=True, required=False)
    student_id = serializers.CharField(required=False)
    major = serializers.CharField(required=False)
    faculty = serializers.CharField(required=False)
    term = serializers.CharField(required=False)


    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """

        # Extract user data and assistant courses data
        user_data = validated_data.pop('user', None)
        assistant_courses_data = validated_data.pop('assistant_courses', [])

        # Extract first_name and last_name from nama_lengkap
        if 'nama_lengkap' not in user_data:
            raise serializers.ValidationError("The nama_lengkap field is required.")
        nama_lengkap = user_data['nama_lengkap']
        nama_lengkap = nama_lengkap[0].upper() + nama_lengkap[1:]   
                    
        first_name = nama_lengkap.split()[0]
        last_name = ' '.join(nama_lengkap.split()[1:]) if len(nama_lengkap) > 1 else ''

        # Modify user_data
        user_data["first_name"]=first_name
        user_data["last_name"]=last_name
        user_data.pop('nama_lengkap', None)

        if user_data:
            user = KwlUser.objects.create_user(**user_data)
        else:
            user = None    
        # Create the Student instance
        student = Student.objects.create(user=user, **validated_data)
        
        user.role = 'student'
        user.save()
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
    
        instance.major = validated_data.get('major', instance.major)
        instance.faculty = validated_data.get('faculty', instance.faculty)
        instance.term = validated_data.get('term', instance.term)

        user_data = validated_data.pop('user', None)
        if user_data:
            user = instance.user 
            user.domisili = user_data.get('domisili', user.domisili)
            nama_lengkap = user_data['nama_lengkap']
            nama_lengkap = nama_lengkap[0].upper() + nama_lengkap[1:]  
            first_name = nama_lengkap.split()[0]
            last_name = ' '.join(nama_lengkap.split()[1:]) if len(nama_lengkap) > 1 else ''
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            instance.user=user
        else:
            user = None   



        instance.save()
        return instance
    
