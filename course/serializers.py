import datetime
from rest_framework import serializers

from know.serializers import KnowSerializer
from .models import Course, RewardItem, RewardPoint, Topic
from know.models import Know
from learned.models import Learned
from wtk.models import WantToKnow
from wtk.serializers import WtkSerializer
from learned.serializers import LearnedSerializer
class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['short_name','full_name','color_theme','lecturer_team','assistant_team','students','id']

    def create(self, validated_data):
        today_year = datetime.datetime.now().year
        today_month = datetime.datetime.now().month

        term = ""
        if today_month <= 7 and today_month >= 1:
            term = "Genap" 
        else:
            term = "Gasal"
        
        validated_data['short_name'] = validated_data['short_name'] + " " + term + " " + str(today_year-1)+"/"+str(today_year)

        return Course.objects.create(**validated_data)
  

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