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
from know.models import KnowReflection
from learned.models import LearnedReflection
from wtk.models import WtkReflection# Create your views here.
# Create your views here.

class WordCloudAPIView(APIView):
    def get(self, request):
        type = request.data['type'] #tipe dari reflection, apakah learned wtk atau know
        topic_id = request.data['topic_id'] #id dari topic yang ingin diambil reflectionnya
        reflections = []

        if type == 'learned':
            reflections = LearnedReflection.objects.filter(learned__topic_id=topic_id).values_list('reflection', flat=True)
        elif type == 'wtk':
            reflections = WtkReflection.objects.filter(wtk__topic_id=topic_id).values_list('reflection', flat=True)
        elif type == 'know':
            reflections = KnowReflection.objects.filter(know__topic_id=topic_id).values_list('reflection', flat=True)

        
        # Get data from request (e.g., reflections)
    #     reflections = [
    #     "Today I learned about Django and how to build web applications using Python. It's fascinating!",
    #     "Reflecting on my coding journey, I realize the importance of practice and perseverance.",
    #     "The concept of machine learning is intriguing, and I'm excited to dive deeper into this field.",
    #     "Exploring new technologies is both challenging and rewarding.",
    #     "Reflecting on my past projects, I see how much I've grown as a developer.",
    #     "I enjoy solving complex problems and finding innovative solutions.",
    #     "Learning new programming languages opens up new opportunities for me.",
    #     "Reflecting on my career goals, I'm motivated to continue learning and improving my skills.",
    #     "The support of the developer community has been invaluable in my learning journey.",
    #     "Building user-friendly interfaces is a key aspect of software development."
    # ]

    

        # Join all reflections into a single string
        all_reflections = ' '.join(reflections)

        # Generate word cloud
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_reflections)

        # Define path to save word cloud image
        image_path = os.path.join(settings.MEDIA_ROOT, 'word_cloud.png')

        # Save word cloud image
        wordcloud.to_file(image_path)

        # Construct image URL
        image_url = os.path.join(settings.MEDIA_URL, 'word_cloud.png')

        # Return response with image URL
        return Response({'image_url': image_url})
    
class KnowParticipant(APIView):
    def get(self, request):
        know_id = request.data['know_id']
        
        participants = KnowReflection.objects.filter(know_id=know_id).values_list('student_id', flat=True)
        return Response({'participants': participants})
