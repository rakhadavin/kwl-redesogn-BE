
import os
from django.conf import settings

from authentication.models import Student
from course.models import KwlPoint, RewardStudentPoint
from wtk.api_exceptions import WtkDoesNotExistException, WtkReflectionNotFoundException, PrereadingDoesNotExistException
from .models import Prereading, WtkPollQuestion, WantToKnow, WtkPollStudentAnswer, WtkChoices, WtkReflection, WtkReflectionStudentAnswer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .serializers import AddPollingQuestionSerializer, EditWtkEssaySerializer, WtkPollingQuestionSerializer, WtkPollingAnswerSerializer, AddWtkEssaySerializer, WtkReflectionAnswerSerializer, WtkReflectionSerializer, AddPrereadingSerializer, EditPrereadingSerializer, PrereadingSerializer, EditPollingQuestionSerializer, WtkMultipleChoiceAnswerSerializer
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.http import Http404
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from django.db import transaction
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
            prereading = Prereading.objects.get(topic_id=topic_id)
            serializer = PrereadingSerializer(prereading)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Prereading.DoesNotExist:
            raise WtkDoesNotExistException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(operation_summary="Edit Prereading", request_body=EditPrereadingSerializer)
    def put(self, request, topic_id):
        try:
            prereading = Prereading.objects.get(topic_id=topic_id)
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
            prereading = Prereading.objects.get(topic_id=topic_id)
            if prereading.file:
                os.remove(os.path.join(settings.MEDIA_ROOT, prereading.file.name))
            prereading.delete()
            return Response({"message": "Prereading deleted successfully"}, status=status.HTTP_200_OK)
        except Prereading.DoesNotExist:
            raise PrereadingDoesNotExistException()
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
        
    @swagger_auto_schema(operation_summary="Edit Polling question", request_body=EditPollingQuestionSerializer)
    def put(self, request, topic_id):
        try:
            question = WtkPollQuestion.objects.get(wtk__topic_id=topic_id)
            serializer = EditPollingQuestionSerializer(question, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"message": "Polling question updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
        except WtkPollQuestion.DoesNotExist:
            raise WtkDoesNotExistException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    @swagger_auto_schema(operation_summary="Delete Polling question")
    def delete(self, request, topic_id):
        try:
            wtk = WantToKnow.objects.get(topic_id=topic_id)
            wtk.delete()
            return Response({"message": "Polling question deleted successfully"}, status=status.HTTP_200_OK)
        except WantToKnow.DoesNotExist:
            raise WtkDoesNotExistException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class WtkMultipleVoteView(APIView):
    permission_classes = [IsAuthenticated,]

    @swagger_auto_schema(operation_description="Save a multiple choice answer")
    def post(self, request):
        try:
            with transaction.atomic():
                userid = request.user
                student = Student.objects.get(user_id=userid)
                serializer = WtkMultipleChoiceAnswerSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                choices = serializer.validated_data['choices']
                topic = serializer.validated_data['topic']
                wtk_poll_question = WtkPollQuestion.objects.get(wtk__topic_id=topic)
                student_answer, answer_created = WtkPollStudentAnswer.objects.get_or_create(wtk_poll=wtk_poll_question, student=student)
                for choice in choices:
                    choice = WtkChoices.objects.get(id=choice)
                    student_answer.choices.add(choice)
                    choice.total_votes += 1
                    choice.save()
                wtk_poll_question.wtk.total_participants += 1  
                wtk_poll_question.save() 
                reward_point, reward_created = RewardStudentPoint.objects.get_or_create(student=student, course=wtk_poll_question.wtk.topic.course)
                if answer_created:
                    reward_point.total_point = wtk_poll_question.score
                    kwl_point, kwl_created = KwlPoint.objects.get_or_create(student=student, topic=wtk_poll_question.wtk.topic)
                    kwl_point.kwl_status = 'wtk'
                    kwl_point.wtk_score = wtk_poll_question.score
                    reward_point.total_point += wtk_poll_question.score
            return Response({"message": "Multiple choice answer saved successfully"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    


class WtkEssayAnswerView(APIView):
    permission_classes = [IsAuthenticated,]

    @swagger_auto_schema(operation_description="Save a reflection answer")
    def post(self, request):
        try:
            with transaction.atomic():
                userid = request.user
                serializer = WtkReflectionAnswerSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                topic = serializer.validated_data['topic']
                reflection = serializer.validated_data['reflection']
                student = Student.objects.get(user_id=userid)
            
                wtk_reflection = WtkReflection.objects.get(wtk__topic_id=topic)
                answer, answer_created = WtkReflectionStudentAnswer.objects.get_or_create(wtk_ref=wtk_reflection, student=student)
                answer.reflection = reflection
                answer.save()
                student_point, reward_created = RewardStudentPoint.objects.get_or_create(student=student, course=wtk_reflection.wtk.topic.course)
                kwl_point, kwl_created = KwlPoint.objects.get_or_create(student=student, topic=wtk_reflection.wtk.topic)
                kwl_point.kwl_status = 'wtk'
                wtk_reflection.wtk.total_participants += 1
                wtk_reflection.save()
                if kwl_created:
                    kwl_point.wtk_score = wtk_reflection.score
                    kwl_point.save()
                if reward_created:
                    total_score = wtk_reflection.score + student_point.total_point
                    student_point.total_point = total_score
                    student_point.save()
            return Response({"message": "Reflection answer saved successfully"}, status=status.HTTP_201_CREATED)
        except WtkReflection.DoesNotExist:
            raise WtkReflectionNotFoundException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


