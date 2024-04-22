import datetime
from rest_framework import serializers
from .models import Course, Topic

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
    class Meta:
        model = Topic
        fields = ['name','description','id','course','course_data']