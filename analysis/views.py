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
from know.models import KnowReflectionStudentAnswer, KnowReflection
from learned.models import LearnedReflectionStudentAnswer, LearnedReflection
from wtk.models import WtkReflectionStudentAnswer, WtkReflection

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
    
class KnowParticipantView():
    @api_view(['GET'])
    def get_all_participants(request):
        know_id = request.data['topic_id']
        
        participants = KnowReflectionStudentAnswer.objects.filter(know=know_id).values_list('student_id', flat=True)
        count = len(participants)
        return Response({'participants': participants, 'count': count})
    
    @api_view(['GET'])
    def count_all_participants(request):
        know_id = request.data['know_id']
        
        participants = KnowReflectionStudentAnswer.objects.filter(know=know_id).values_list('student_id', flat=True)
        count = len(participants)
        return Response({'count': count})

class LearnedParticipantView():
    @api_view(['GET'])
    def get_all_participants(request):
        learned_id = request.data['learned_id']
        
        participants = LearnedReflectionStudentAnswer.objects.filter(learned=learned_id).values_list('student_id', flat=True)
        count = len(participants)
        return Response({'participants': participants, 'count': count})
    
    @api_view(['GET'])
    def count_all_participants(request):
        learned_id = request.data['learned_id']
        
        participants = LearnedReflectionStudentAnswer.objects.filter(learned=learned_id).values_list('student_id', flat=True)
        count = len(participants)
        return Response({'count': count})
    
class WtkParticipantView():
    @api_view(['GET'])
    def get_all_participants(request):
        wtk_id = request.data['wtk_id']
        
        participants = WtkReflectionStudentAnswer.objects.filter(wtk=wtk_id).values_list('student_id', flat=True)
        count = len(participants)
        return Response({'participants': participants, 'count': count})
    
    @api_view(['GET'])
    def count_all_participants(request):
        wtk_id = request.data['wtk_id']
        
        participants = WtkReflectionStudentAnswer.objects.filter(wtk=wtk_id).values_list('student_id', flat=True)
        count = len(participants)
        return Response({'count': count})