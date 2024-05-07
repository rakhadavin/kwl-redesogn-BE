from django.shortcuts import render

import os
from django.conf import settings
from wordcloud import WordCloud

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.http import Http404
from analysis import models
from course.api_exceptions import TopicNotFoundException
from course.models import Topic, RewardStudentPoint, KwlPoint
from know.models import KnowReflectionStudentAnswer, KnowReflection
from learned.models import LearnedReflectionStudentAnswer, LearnedReflection
from wtk.models import WtkReflectionStudentAnswer, WtkPollStudentAnswer, WtkChoices



# Create your views here.

class WordCloudAPIView(APIView):
    def get(self, request, type, topic):

        reflections = []

        if type == 'learned':
            reflections = LearnedReflectionStudentAnswer.objects.filter(learned=topic).values_list('reflection', flat=True)
        elif type == 'wtk':
            reflections = WtkReflectionStudentAnswer.objects.filter(wtk=topic).values_list('reflection', flat=True)
        elif type == 'know':
            reflections = KnowReflectionStudentAnswer.objects.filter(know=topic).values_list('reflection', flat=True)

        all_reflections = ' '.join(reflections)

        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_reflections)

        image_path = os.path.join(settings.MEDIA_ROOT, 'word_cloud.png')

        wordcloud.to_file(image_path)

        image_url = os.path.join(settings.MEDIA_URL, 'word_cloud.png')

        return Response({'image_url': image_url})


class KwlParticipantCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request,topic):

        try:
            topic_id = topic

            topic = Topic.objects.get(id=topic_id)
            course = topic.course
            total_enrolled_students = course.students.all().count()
            
            know_participants = KnowReflectionStudentAnswer.objects.filter(know=topic_id).values_list('student_id', flat=True)
            learned_participants = LearnedReflectionStudentAnswer.objects.filter(learned=topic_id).values_list('student_id', flat=True)
            wtk_participants = WtkReflectionStudentAnswer.objects.filter(wtk=topic_id).values_list('student_id', flat=True)

            know_count = len(know_participants)
            know_percentage = (know_count / total_enrolled_students) * 100
            learned_count = len(learned_participants)
            learned_percentage = (learned_count / total_enrolled_students) * 100
            wtk_count = len(wtk_participants)
            wtk_percentage = (wtk_count / total_enrolled_students) * 100

            return Response({'know': {'count': know_count, 'percentage': know_percentage}, 'learned': {'count': learned_count, 'percentage': learned_percentage}, 'wtk': {'count': wtk_count, 'percentage': wtk_percentage}})   
        except Topic.DoesNotExist:
            raise TopicNotFoundException()
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class KwlPointLadderView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, topic):
        four_highest_student_points = KwlPoint.objects.filter(topic=topic).order_by('-total_point')[:4]
        four_lowest_student_points = KwlPoint.objects.filter(topic=topic).order_by('total_point')[:4]


        four_highest_student_points_data = []
        four_lowest_student_points_data = []

        for student_point in four_highest_student_points:
            student_data = {
                'student': student_point.student.user.username,
                'total_point': student_point.total_point
            }
            four_highest_student_points_data.append(student_data)

        for student_point in four_lowest_student_points:
            student_data = {
                'student': student_point.student.user.username,
                'total_point': student_point.total_point
            }
            four_lowest_student_points_data.append(student_data)
        
        return Response({'highest': four_highest_student_points_data, 'lowest': four_lowest_student_points_data})

class TopicPollingAnalysis(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, topic):
        poll_choices = []
        poll_data = []
        topic = Topic.objects.get(id=topic)
        for poll in topic.polls.all():
            poll_data.append({
                'question': poll.question,
                'choices': poll.choices.all().values_list('choice', flat=True)
            })


        poll_data = WtkPollStudentAnswer.objects.filter(wtk=topic).values('poll__question').annotate(count=models.Count('poll__question'))

        
