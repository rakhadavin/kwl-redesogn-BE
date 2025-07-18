from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from authentication.api_exceptions import ExistingEmailException, ExistingUsernameException, ChangePasswordException
from course.models import Course
from .models import KwlUser, Student, Lecturer
from course.serializers import CourseSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# Register User, Get User
class KwlUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)  
    profile_photo = serializers.ImageField(required=False, allow_null=True)
    nama_lengkap = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = KwlUser
        fields = ['username', 'email', 'password', 'role', 'nama_lengkap','domisili', 'profile_photo']

    def to_internal_value(self, data):
        if KwlUser.objects.filter(email=data['email']).exists():
            raise ExistingEmailException
        if KwlUser.objects.filter(username=data['username']).exists():
            raise ExistingUsernameException
   
        return super().to_internal_value(data)
    def get_nama_lengkap(self, obj):
        return obj.first_name + ' ' + obj.last_name

    
    
# Register Lecturer, Get Lecturer
class LecturerSerializer(serializers.ModelSerializer):
    user = KwlUserSerializer(required=True)
    nama_lengkap = serializers.CharField(write_only=True)

    class Meta:
        model = Lecturer
        fields = '__all__'


    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """

        # Extract user data and assistant courses data
        user_data = validated_data.pop('user', None)
        courses_taught = validated_data.pop('courses_taught', [])

        # Extract first_name and last_name from nama_lengkap
        nama_lengkap = validated_data.pop('nama_lengkap', None)
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
    

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})
    

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['username'] = user.username
        token['name'] = user.first_name + ' ' + user.last_name
        if user.role == 'lecturer':
            lecturer = Lecturer.objects.get(user=user)
            token['lecturer_pk'] = lecturer.pk
        elif user.role == 'student':
            student = Student.objects.get(user=user)
            token['student_pk'] = student.pk

        return token



class StudentSerializer(serializers.ModelSerializer):
    user = KwlUserSerializer(required=True)
    nama_lengkap = serializers.CharField(write_only=True)

    class Meta:
        model = Student
        fields = '__all__'

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        
        # Extract user data and assistant courses data
        user_data = validated_data.pop('user', None)
    
        nama_lengkap = validated_data.pop('nama_lengkap', None)
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
        student.save()
        
        return student

class CreateStudentSerializer(serializers.ModelSerializer):
    user = serializers.DictField(write_only=True, required=False)
    nama_lengkap = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Student
        fields = ['student_id', 'major', 'faculty', 'term', 'user', 'nama_lengkap']
        
    def create(self, validated_data):
        """
        Create and return a new Student instance for an existing user.
        """
        user = validated_data.pop('user', None)
        nama_lengkap = validated_data.pop('nama_lengkap', None)

        if not user:
            raise serializers.ValidationError("User is required")
            
        if Student.objects.filter(user=user).exists():
            raise serializers.ValidationError("Student profile already exists for this user")
        
        student = Student.objects.create(user=user, **validated_data)
        return student

class EditLecturerSerializer(serializers.Serializer):
    nama_lengkap = serializers.CharField(write_only=True, required=False)
    email = serializers.EmailField(write_only=True, required=False)
    domisili = serializers.CharField(write_only=True, required=False)
    profile_photo = serializers.ImageField(required=False, allow_null=True)
    department = serializers.CharField(required=False)
    lecturer_id = serializers.CharField(required=False)
    courses_taught = CourseSerializer(many=True, required=False)
    
    def update(self, instance, validated_data):
        """
        Update and return an existing `Lecturer` instance, given the validated data.
        """
        instance.department = validated_data.get('department', instance.department)
        print(validated_data)
        instance.lecturer_id = validated_data.get('lecturer_id', instance.lecturer_id)
        user = instance.user
        user.email = validated_data.get('email', user.email)
        user.domisili = validated_data.get('domisili', user.domisili)
        user.profile_photo = validated_data.get('profile_photo', user.profile_photo)
        nama_lengkap = validated_data.get('nama_lengkap', user.first_name + ' ' + user.last_name)
        if 'nama_lengkap' in validated_data:
            nama_lengkap = nama_lengkap[0].upper() + nama_lengkap[1:]
            nama_lengkap_parts = nama_lengkap.split()
            first_name = nama_lengkap_parts[0]
            last_name = ' '.join(nama_lengkap_parts[1:]) if len(nama_lengkap_parts) > 1 else ''
            user.first_name = first_name
            user.last_name = last_name
        user.save()

        instance.save()

        return instance
    
    def validate_email(self, value):
        user = self.context.get('user', None)

        if user and KwlUser.objects.filter(email=value).exclude(id=user.id).exists():
            raise ExistingEmailException
        
        return value

    
class EditStudentSerializer(serializers.Serializer):
    nama_lengkap = serializers.CharField(write_only=True, required=False)
    email = serializers.EmailField(write_only=True, required=False)
    domisili = serializers.CharField(write_only=True, required=False)
    profile_photo = serializers.ImageField(required=False, allow_null=True)
    student_id = serializers.CharField(required=False)
    major = serializers.CharField(required=False)
    faculty = serializers.CharField(required=False)
    term = serializers.CharField(required=False)

    
    def update(self, instance, validated_data):
        """
        Update and return an existing `Student` instance, given the validated data.
        """
        instance.major = validated_data.get('major', instance.major)
        instance.faculty = validated_data.get('faculty', instance.faculty)
        instance.term = validated_data.get('term', instance.term)
        instance.student_id = validated_data.get('student_id', instance.student_id)
        user = instance.user
        user.email = validated_data.get('email', user.email)
        user.domisili = validated_data.get('domisili', user.domisili)
        user.profile_photo = validated_data.get('profile_photo', user.profile_photo)
        nama_lengkap = validated_data.get('nama_lengkap', user.first_name + ' ' + user.last_name)
        if 'nama_lengkap' in validated_data:
            nama_lengkap = nama_lengkap[0].upper() + nama_lengkap[1:]
            nama_lengkap_parts = nama_lengkap.split()
            first_name = nama_lengkap_parts[0]
            last_name = ' '.join(nama_lengkap_parts[1:]) if len(nama_lengkap_parts) > 1 else ''
            user.first_name = first_name
            user.last_name = last_name
        user.save()

        instance.save()

        return instance
    
    def validate_email(self, value):
        user = self.context.get('user', None)
        
        if user and KwlUser.objects.filter(email=value).exclude(id=user.id).exists():
            raise ExistingEmailException
        
        return value

class ResetPasswordRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, data):
        if not KwlUser.objects.filter(email=data['email']).exists():
            raise ChangePasswordException(_("Email does not exist"))
        return data

# class ChangePasswordSerializer(serializers.Serializer):
#     old_password = serializers.CharField()
#     new_password = serializers.CharField()
  
#     def validate(self, data):
#         if data['old_password'] == data['new_password']:
#             raise ChangePasswordException(_("New password must be different from old password"))
#         if len(data['new_password']) < 8:
#             raise ChangePasswordException(_("Password must be at least 8 characters long"))
        
#         return data

class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField()
  
    def validate(self, data):
        # if data['old_password'] == data['new_password']:
        #     raise ChangePasswordException(_("New password must be different from old password"))
        if len(data['new_password']) < 8:
            raise ChangePasswordException(_("Password must be at least 8 characters long"))
        
        return data