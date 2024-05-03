
import os
from django.conf import settings

from authentication.models import Student
from wtk.api_exceptions import WtkDoesNotExistException, WtkReflectionNotFoundException
from .models import Prereading, WtkPollQuestion, WantToKnow, WtkStudentAnswer, WtkChoices, WtkReflection, WtkReflectionStudentAnswer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .serializers import AddPollingQuestionSerializer, EditWtkEssaySerializer, WtkPollingQuestionSerializer, WtkPollingAnswerSerializer, AddWtkEssaySerializer, WtkReflectionSerializer, AddPrereadingSerializer, EditPrereadingSerializer, PrereadingSerializer, EditPollingQuestionSerializer
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.http import Http404
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
# Create your views here.

class WtkEssayListView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_summary="Add Wtk essay", request_body=AddWtkEssaySerializer)
    def post(self, request):
        try:
            serializer = AddWtkEssaySerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"message": "Reflection question added successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(operation_summary="Get all Wtk essay")
    def get(self, request):
        try:
            wtk_essay = WtkReflection.objects.all()
            serializer = WtkReflectionSerializer(wtk_essay, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class WtkEssayDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_summary="Get a Wtk essay by topic id")
    def get(self, request, topic_id):
        try: 
            essay = WtkReflection.objects.get(wtk__topic_id=topic_id)
            serializer = WtkReflectionSerializer(essay)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except WtkReflection.DoesNotExist:
            raise WtkReflectionNotFoundException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(operation_summary="Edit Wtk essay", request_body=EditWtkEssaySerializer)
    def put(self, request, topic_id):
        try:
            essay = WtkReflection.objects.get(wtk__topic_id=topic_id)
            serializer = EditWtkEssaySerializer(essay, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"message": "Reflection question updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
        except WtkReflection.DoesNotExist:
            raise WtkReflectionNotFoundException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    @swagger_auto_schema(operation_summary="Delete Wtk essay")
    def delete(self, request, topic_id):
        try:
            wtk = WantToKnow.objects.get(topic_id=topic_id)
            wtk.delete()
            return Response({"message": "Reflection deleted successfully"}, status=status.HTTP_200_OK)
        except WantToKnow.DoesNotExist:
            raise WtkDoesNotExistException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PrereadingListView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_summary="Add Prereading", request_body=AddPrereadingSerializer)
    def post(self, request):
        try:
            serializer = AddPrereadingSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"message": "Prereading added successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(operation_summary="Get all Prereading")
    def get(self, request):
        try:
            prereading = Prereading.objects.all()
            serializer = PrereadingSerializer(prereading, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class PrereadingDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_summary="Get a Prereading by topic id")
    def get(self, request, topic_id):
        try:
            prereading = Prereading.objects.get(wtk__topic_id=topic_id)
            serializer = PrereadingSerializer(prereading)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Prereading.DoesNotExist:
            raise WtkDoesNotExistException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(operation_summary="Edit Prereading", request_body=EditPrereadingSerializer)
    def put(self, request, topic_id):
        try:
            prereading = Prereading.objects.get(wtk__topic_id=topic_id)
            serializer = EditPrereadingSerializer(prereading, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"message": "Prereading updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
        except Prereading.DoesNotExist:
            raise WtkDoesNotExistException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    @swagger_auto_schema(operation_summary="Delete Prereading")
    def delete(self, request, topic_id):
        try:
            wtk = WantToKnow.objects.get(topic_id=topic_id)
            wtk.delete()
            return Response({"message": "Prereading deleted successfully"}, status=status.HTTP_200_OK)
        except WantToKnow.DoesNotExist:
            raise WtkDoesNotExistException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class PollingListView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_summary="Add Polling question", request_body=AddPollingQuestionSerializer)
    def post(self, request):
        try:
            serializer = AddPollingQuestionSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"message": "Polling question added successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(operation_summary="Get all Polling question")
    def get(self, request):
        try:
            polling = WtkPollQuestion.objects.all()
            serializer = WtkPollingQuestionSerializer(polling, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class PollingDetailView(APIView):
    permission_classes = [IsAuthenticated,]

    @swagger_auto_schema(operation_summary="Get a Polling question by topic id")
    def get(self, request, topic_id):
        try:
            question = WtkPollQuestion.objects.get(wtk__topic_id=topic_id)
            question_serializer = WtkPollingQuestionSerializer(question)
            answer_serializer = WtkPollingAnswerSerializer(question.choices.all(), many=True)
            poll = {"question": question_serializer.data, "options": answer_serializer.data}
            return Response(poll, status=status.HTTP_200_OK)
        except WtkPollQuestion.DoesNotExist:
            raise WtkDoesNotExistException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)



        
#     @api_view(['POST'])
#     @permission_classes([IsAuthenticated])
#     def vote_multiple_choice(request):
#         try:
#             user_id = request.user
#             student = Student.objects.get(user_id=user_id)
#             question_id = request.data['question_id']
#             choices = request.data['choices_ids']
#             if not choices and not question_id:
#                 return Response({"error": "Question id and choices ids are required"}, status=status.HTTP_400_BAD_REQUEST)
#             question = get_wtk_question_or_404(question_id)
#             student_answer, created = WtkStudentAnswer.objects.get_or_create(wtk_poll_question_id=question, student_id=student, score=question.score)
#             for choice_id in choices:
#                 try:
#                     choice = WtkChoices.objects.get(id=choice_id)
#                     student_answer.choices.add(choice)
#                 except WtkChoices.DoesNotExist:
#                     return Response({"error": f"Choice with id {choice_id} does not exist"}, status=status.HTTP_400_BAD_REQUEST)
#             student_answer.save()
#             return Response({"message": "Voted successfully"}, status=status.HTTP_201_CREATED)
#         except Http404:
#             return Response({"error": "Polling question not found"}, status=status.HTTP_404_NOT_FOUND)
        
#     @api_view(['GET'])
#     def count_votes(request, question_id):
#         try:
#             question = get_wtk_question_or_404(question_id)
#             choices = question.choices.all()
#             student_answers = WtkStudentAnswer.objects.filter(wtk_poll_question_id=question)
#             votes = {}
#             for student_answer in student_answers:
#                 for choice in choices:
#                     if choice in student_answer.choices.all():
#                         if choice.option_answer in votes:
#                             votes[choice.option_answer] += 1
#                         else:
#                             votes[choice.option_answer] = 1
#                     else:
#                         if choice.option_answer not in votes:
#                             votes[choice.option_answer] = 0
#             return Response({"votes": votes}, status=status.HTTP_200_OK)
#         except Http404:
#             return Response({"error": "Polling question not found"}, status=status.HTTP_404_NOT_FOUND)

