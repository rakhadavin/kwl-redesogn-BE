import datetime
from pytz import timezone
from rest_framework import serializers

from authentication.models import Lecturer, Student
from know.serializers import KnowSerializer
from .models import Course, RewardItem, RewardStudentPoint, Topic, Feedback, RedeemHistory, KwlPoint
from know.models import Know
from learned.models import Learned
from wtk.models import WantToKnow
from wtk.serializers import WtkSerializer
from learned.serializers import LearnedSerializer
from .api_exceptions import CourseNotFoundException, TopicNotFoundException

class CourseSerializer(serializers.ModelSerializer):
    lecturer = serializers.IntegerField(write_only=True)
    
    # def validate(self, attrs):
    #     if Lecturer.objects.filter(pk=attrs['lecturer']).exists():
    #         return super().validate(attrs)
    #     raise LecturerNotFoundException()

    class Meta:
        model = Course
        fields = ['short_name','full_name','color_theme','lecturer_team','students','id','lecturer', 'enrollment_key', 'created','updated']

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
        lecturer_team_ids = validated_data.pop('lecturer_team', [])
        course = Course.objects.create(**validated_data)
        course.lecturer_team.add(lecturer_id, *lecturer_team_ids)
        

        return course
    
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['created'] = instance.created.strftime("%Y-%m-%d")
        ret['updated'] = instance.updated.strftime("%Y-%m-%d")
        return ret
  

class TopicSerializer(serializers.ModelSerializer):
    course = serializers.IntegerField(write_only=True)
    course_data = CourseSerializer(read_only=True, source='course')
    know = serializers.SerializerMethodField(read_only=True)
    learned = serializers.SerializerMethodField(read_only=True )
    wtk = serializers.SerializerMethodField(read_only=True)

    def validate(self, attrs):
        if 'course' in attrs:
            if not Course.objects.filter(pk=attrs['course']).exists():
                raise CourseNotFoundException()
        return super().validate(attrs)

    class Meta:
        model = Topic
        fields = ['name','description','id','course','course_data','know', 'learned', 'wtk', 'is_hidden']

    def get_know(self, obj):
        return KnowSerializer(Know.objects.filter(topic=obj), many=True).data
    
    def get_learned(self, obj):
        return LearnedSerializer(Learned.objects.filter(topic=obj), many=True).data
    
    def get_wtk(self, obj):
        return WtkSerializer(WantToKnow.objects.filter(topic=obj), many=True).data
    
    def create(self, validated_data):
        course_id = validated_data.pop('course')
        course = Course.objects.get(pk=course_id)
        topic = Topic.objects.create(course=course, **validated_data)
        return topic
    
    def update(self, instance, validated_data):
        course_id = validated_data.get('course', instance.course.id)
        course = Course.objects.get(pk=course_id)
        instance.course = course
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance
    
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['created'] = instance.created.strftime("%Y-%m-%d")
        ret['updated'] = instance.updated.strftime("%Y-%m-%d")
        return ret
    
class RewardPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = RewardStudentPoint
        fields = ['student','total_point','id','course']


class RewardItemSerializer(serializers.ModelSerializer):
    course = serializers.IntegerField(write_only=True)
    course_data = CourseSerializer(read_only=True, source='course')
    class Meta:
        model = RewardItem
        fields = ['name','stock','point','expired_date','detail_instruction','id','course','course_data']

    def validate(self, attrs):  
        if 'course' in attrs:
            if not Course.objects.filter(pk=attrs['course']).exists():
                raise CourseNotFoundException()
        return super().validate(attrs)
    
    def create(self, validated_data):
        course_id = validated_data.pop('course')
        course = Course.objects.get(pk=course_id)
        reward = RewardItem.objects.create(course=course, **validated_data)
        return reward
    
    def update(self, instance, validated_data):
        course_id = validated_data.get('course', instance.course.id)
        course = Course.objects.get(pk=course_id)
        instance.course = course
        instance.name = validated_data.get('name', instance.name)
        instance.stock = validated_data.get('stock', instance.stock)
        instance.point = validated_data.get('point', instance.point)
        instance.expired_date = validated_data.get('expired_date', instance.expired_date)
        instance.detail_instruction = validated_data.get('detail_instruction', instance.detail_instruction)
        instance.save()
        return instance
    

    
class RewardPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = RewardStudentPoint
        fields = ['student','total_point','id','course']
    # def validate(self, attrs):
    #     if 'course' in attrs:
    #         if not Course.objects.filter(pk=attrs['course']).exists():
    #             raise CourseNotFoundException()
    #     return super().validate(attrs)
    
class AddStudentToCourseSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    course_id = serializers.IntegerField()
    enrollment_key = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    def validate(self, attrs):
        course_id = attrs['course_id']
        enrollment_key = attrs.get('enrollment_key', '')
        
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            raise serializers.ValidationError("Course not found")
        
        if course.enrollment_key:
            if not enrollment_key:
                raise serializers.ValidationError("Enrollment key is required for this course")
            if enrollment_key != course.enrollment_key:
                raise serializers.ValidationError("Invalid enrollment key")
        
        return attrs
    
    def update(self, instance, validated_data):
        student = Student.objects.get(pk=validated_data['student_id'])
        instance.students.add(student)
        return instance
    
    
class RemoveStudentFromCourseSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    course_id = serializers.IntegerField()
    
    def update(self, instance, validated_data):
        student = Student.objects.get(pk=validated_data['student_id'])
        instance.students.remove(student)
        return instance
    
    
class AddLecturerToCourseSerializer(serializers.Serializer): #Unused, currenly only one lecturer per course
    lecturer_id = serializers.IntegerField()
    course_id = serializers.IntegerField()
    
class RemoveLecturerFromCourseSerializer(serializers.Serializer): #Unused, currenly only one lecturer per course
    lecturer_id = serializers.IntegerField()
    course_id = serializers.IntegerField()
    
class FeedbackSerializer(serializers.ModelSerializer):
    student = serializers.IntegerField(write_only=True)
    topic = serializers.IntegerField(write_only=True)
    lecturer = serializers.IntegerField(write_only=True)
    student_name = serializers.CharField(source='student.user.username', read_only=True)
    lecturer_name = serializers.CharField(source='lecturer.user.username', read_only=True)
    topic_name = serializers.CharField(source='topic.name', read_only=True)
    class Meta:
        model = Feedback
        fields = ['student','topic','feedback','id','lecturer', 'student_name','lecturer_name', 'topic_name','created']
    
    def create(self, validated_data):
        student_id = validated_data.pop('student')
        topic_id = validated_data.pop('topic')
        lecturer_id = validated_data.pop('lecturer')
        feedback = Feedback.objects.create(student_id=student_id, topic_id=topic_id, lecturer_id=lecturer_id, **validated_data)

        return feedback
    
    def update(self, instance, validated_data): #Unused, feedback cannot be updated right now
        student_id = validated_data.get('student', instance.student.id)
        topic_id = validated_data.get('topic', instance.topic.id)
        lecturer_id = validated_data.get('lecturer', instance.lecturer.id)
        instance.student_id = student_id
        instance.topic_id = topic_id
        instance.lecturer_id = lecturer_id
        instance.feedback = validated_data.get('feedback', instance.feedback)
        instance.save()

        return instance
    
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['created'] = instance.created.strftime("%Y-%m-%d")

        return ret
    


#Serializer that is used to serialize a redeemed reward item by a student
class RedeemHistorySerializer(serializers.ModelSerializer): 
    class Meta:
        model = RedeemHistory
        fields = ['student','reward','course','created','id']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['created'] = instance.created.strftime("%Y-%m-%d")
        return ret
    
#Serializer that is used to redeem a reward item by a student
class RedeemSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    reward_id = serializers.IntegerField()
    course_id = serializers.IntegerField()


#Serializer that is used to list all redeemed reward items by a student 
class RedeemHistoryListSerializer(serializers.ModelSerializer):
    reward_item = RewardItemSerializer(read_only=True)
    class Meta:
        model = RedeemHistory
        fields = ['student','reward_item','created','id']
    
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['created'] = instance.created.strftime("%Y-%m-%d")
        return ret
    
class KwlPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = KwlPoint
        fields = '__all__'

