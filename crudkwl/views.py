from django.shortcuts import render
from rest_framework import viewsets
from .models import Know, WantToKnow, Learned, KnowQuiz, KnowQuizAnswer, WantToKnowPoll, WantToKnowPollChoice
from .serializer import KnowSerializer, WantToKnowSerializer, LearnedSerializer, KnowQuizSerializer, KnowQuizAnswerSerializer, WantToKnowPollSerializer, WantToKnowPollChoiceSerializer
# Create your views here.

class KnowView(viewsets.ModelViewSet):
    queryset = Know.objects.all()
    serializer_class = KnowSerializer

class WantToKnowView(viewsets.ModelViewSet):
    queryset = WantToKnow.objects.all()
    serializer_class = WantToKnowSerializer

class LearnedView(viewsets.ModelViewSet):
    queryset = Learned.objects.all()
    serializer_class = LearnedSerializer

class KnowQuizView(viewsets.ModelViewSet):
    queryset = KnowQuiz.objects.all()
    serializer_class = KnowQuizSerializer

class KnowQuizAnswerView(viewsets.ModelViewSet):
    queryset = KnowQuizAnswer.objects.all()
    serializer_class = KnowQuizAnswerSerializer

class WantToKnowPollView(viewsets.ModelViewSet):
    queryset = WantToKnowPoll.objects.all()
    serializer_class = WantToKnowPollSerializer

class  WantToKnowPollChoiceView(viewsets.ModelViewSet):
    queryset = WantToKnowPollChoice.objects.all()
    serializer_class = WantToKnowPollChoiceSerializer

