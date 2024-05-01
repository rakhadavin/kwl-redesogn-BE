import datetime
from rest_framework import serializers

from authentication.models import Lecturer, Student
from know.serializers import KnowSerializer
from .models import Course, RewardItem, RewardPoint, Topic
from know.models import Know
from learned.models import Learned
from wtk.models import WantToKnow
from wtk.serializers import WtkSerializer
from learned.serializers import LearnedSerializer
from .api_exceptions import LecturerNotFoundException
class CourseSerializer(serializers.ModelSerializer):
    lecturer = serializers.IntegerField(write_only=True)
    
    def validate(self, attrs):
        if Lecturer.objects.filter(pk=attrs['lecturer']).exists():
            return super().validate(attrs)
        raise LecturerNotFoundException()

    class Meta:
        model = Course
        fields = ['short_name','full_name','color_theme','lecturer_team','assistant_team','students','id','lecturer']

    def create(self, validated_data):
        today_year = datetime.datetime.now().year
        today_month = datetime.datetime.now().month
        
        term = ""
        if today_month <= 7 and today_month >= 1:
            term = "Genap" 
        else:
            term = "Gasal"
        
        validated_data['short_name'] = validated_data['short_name'] + " " + term + " " + str(today_year-1)+"/"+str(today_year)
        lecturer_id = validated_data.pop('lecturer')
        course = Course.objects.create(**validated_data)
        course.lecturer_team.add(lecturer_id)

        return course
  

class TopicSerializer(serializers.ModelSerializer):
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all(),
                                                  error_messages={
            'required': 'The course field is required.', 'does_not_exist': 'Course does not exist.' 
        }, write_only=True)
    course_data = CourseSerializer(read_only=True, source='course')
    know = serializers.SerializerMethodField(read_only=True)
    learned = serializers.SerializerMethodField(read_only=True )
    wtk = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Topic
        fields = ['name','description','id','course','course_data','know', 'learned', 'wtk']

    def get_know(self, obj):
        return KnowSerializer(Know.objects.filter(topic=obj), many=True).data
    
    def get_learned(self, obj):
        return LearnedSerializer(Learned.objects.filter(topic=obj), many=True).data
    
    def get_wtk(self, obj):
        return WtkSerializer(WantToKnow.objects.filter(topic=obj), many=True).data
    
class RewardPointSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = RewardPoint
        fields = ['student','point','id','course']

class RewardItemSerializer(serializers.ModelSerializer):
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all(),
                                                  error_messages={
            'required': 'The course field is required.', 'does_not_exist': 'Course does not exist.' 
        }, write_only=True)
    
    class Meta:
        model = RewardItem
        fields = ['name','point','id','course']



class AddStudentToCourseSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    course_id = serializers.IntegerField()
    
    def validate(self, data):
        student = data.get('student_id')
        course = data.get('course_id')
        if not student:
            raise serializers.ValidationError('Student id is required')
        if not course:
            raise serializers.ValidationError('Course id is required')
        return data
    
    def update(self, instance, validated_data):
        student = Student.objects.get(pk=validated_data['student_id'])  # Changed from Lecturer to Student
        instance.students.add(student)
        return instance
    
    
class RemoveStudentFromCourseSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    course_id = serializers.IntegerField()
    
    def validate(self, data):
        student = data.get('student_id')
        course = data.get('course_id')
        if not student:
            raise serializers.ValidationError('Student id is required')
        if not course:
            raise serializers.ValidationError('Course id is required')
        return data
    
    def update(self, instance, validated_data):
        student = Student.objects.get(pk=validated_data['student_id'])
        instance.students.remove(student)
        return instance
    
class AddAssistantToCourseSerializer(serializers.Serializer):
    assistant_id = serializers.IntegerField()
    course_id = serializers.IntegerField()
    
    def validate(self, data):
        assistant = data.get('assistant_id')
        course = data.get('course_id')
        if not assistant:
            raise serializers.ValidationError('Assistant id is required')
        if not course:
            raise serializers.ValidationError('Course id is required')
        return data
    
class RemoveAssistantFromCourseSerializer(serializers.Serializer):
    assistant_id = serializers.IntegerField()
    course_id = serializers.IntegerField()
    
    def validate(self, data):
        assistant = data.get('assistant_id')
        course = data.get('course_id')
        if not assistant:
            raise serializers.ValidationError('Assistant id is required')
        if not course:
            raise serializers.ValidationError('Course id is required')
        return data
    
class AddLecturerToCourseSerializer(serializers.Serializer):
    lecturer_id = serializers.IntegerField()
    course_id = serializers.IntegerField()
    
    def validate(self, data):
        lecturer = data.get('lecturer_id')
        course = data.get('course_id')
        if not lecturer:
            raise serializers.ValidationError('Lecturer id is required')
        if not course:
            raise serializers.ValidationError('Course id is required')
        return data
    
class RemoveLecturerFromCourseSerializer(serializers.Serializer):
    lecturer_id = serializers.IntegerField()
    course_id = serializers.IntegerField()
    
    def validate(self, data):
        lecturer = data.get('lecturer_id')
        course = data.get('course_id')
        if not lecturer:
            raise serializers.ValidationError('Lecturer id is required')
        if not course:
            raise serializers.ValidationError('Course id is required')
        return data