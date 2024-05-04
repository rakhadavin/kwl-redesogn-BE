from django.http import Http404
from django.shortcuts import render

from authentication.models import Student
from learned.api_exceptions import LearnedDoesNotExistException, LearnedReflectionNotFoundException
from .serializers import AddLearnedEssaySerializer, EditLearnedEssaySerializer, LearnedReflectionSerializer, AddLearnedQuizQuestionSerializer, EditLearnedQuizQuestionSerializer, LearnedQuizQuestionSerializer 
from .models import Learned, LearnedReflection, LearnedReflectionStudentAnswer, LearnedQuizQuestion, LearnedQuizStudentAnswer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from course.models import RewardStudentPoint
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema

class LearnedQuizListView(APIView):
    permission_classes = [IsAuthenticated,]

    @swagger_auto_schema(operation_description="Add a learned quiz", request_body=AddLearnedQuizQuestionSerializer)
    def post(self, request):
        try:
            serializer = AddLearnedQuizQuestionSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"message": "Quiz added successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    @swagger_auto_schema(operation_description="Get all learned quiz")
    def get(self, request):
        try:
            learned_quiz = LearnedQuizQuestion.objects.all()
            serializer = LearnedQuizQuestionSerializer(learned_quiz, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class LearnedQuizzesByTopicView(APIView):   
    permission_classes = [IsAuthenticated,]

    @swagger_auto_schema(operation_description="Get all learned quiz by topic id")
    def get(self, request, topic_id):
        try:
            quiz = LearnedQuizQuestion.objects.filter(learned__topic_id=topic_id)
            serializer = LearnedQuizQuestionSerializer(quiz, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except LearnedQuizQuestion.DoesNotExist:
            raise LearnedReflectionNotFoundException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    @swagger_auto_schema(operation_description="Delete a learned quiz by topic id")
    def delete(self, request, topic_id):
        try:
            learned = Learned.objects.get(topic_id=topic_id)
            learned.delete()
            return Response({"message": "Quiz deleted successfully"}, status=status.HTTP_200_OK)
        except Learned.DoesNotExist:
            raise LearnedDoesNotExistException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class LearnedQuizDetailView(APIView):
    permission_classes = [IsAuthenticated,]

    @swagger_auto_schema(operation_description="Get a learned quiz by id")
    def get(self, request, quiz_id):
        try:
            quiz = LearnedQuizQuestion.objects.get(id=quiz_id)
            serializer = LearnedQuizQuestionSerializer(quiz)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Learned.DoesNotExist:
            raise LearnedDoesNotExistException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    @swagger_auto_schema(operation_description="Edit a learned quiz", request_body=EditLearnedQuizQuestionSerializer)
    def put(self, request, quiz_id):
        try:
            quiz = LearnedQuizQuestion.objects.get(id=quiz_id)
            serializer = EditLearnedQuizQuestionSerializer(quiz, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"message": "Quiz updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
        except LearnedQuizQuestion.DoesNotExist:
            raise LearnedReflectionNotFoundException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class LearnedEssayListView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_description="Add learned essay", request_body=AddLearnedEssaySerializer)
    def post(self, request):
        try:
            serializer = AddLearnedEssaySerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"message": "Reflection question added successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(operation_description="Get all learned essay")
    def get(self, request):
        try:
            learned_essay = LearnedReflection.objects.all()
            serializer = LearnedReflectionSerializer(learned_essay, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class LearnedEssayDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_description="Get a learned essay by topic id")
    def get(self, request, topic_id):
        try: 
            essay = LearnedReflection.objects.get(learned__topic_id=topic_id)
            serializer = LearnedReflectionSerializer(essay)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except LearnedReflection.DoesNotExist:
            raise LearnedReflectionNotFoundException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(operation_description="Edit learned essay", request_body=EditLearnedEssaySerializer)
    def put(self, request, topic_id):
        try:
            essay = LearnedReflection.objects.get(learned__topic_id=topic_id)
            serializer = EditLearnedEssaySerializer(essay, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"message": "Reflection question updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
        except LearnedReflection.DoesNotExist:
            raise LearnedReflectionNotFoundException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    @swagger_auto_schema(operation_description="Delete learned essay")
    def delete(self, request, topic_id):
        try:
            learned = Learned.objects.get(topic_id=topic_id)
            learned.delete()
            return Response({"message": "Reflection deleted successfully"}, status=status.HTTP_200_OK)
        except Learned.DoesNotExist:
            raise LearnedDoesNotExistException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)