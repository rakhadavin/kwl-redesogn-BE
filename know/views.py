
from django.http import Http404
from django.shortcuts import render

from authentication.models import Student
from know.models import KnowQuizQuestion, KnowQuizStudentAnswer, KnowReflectionStudentAnswer
from .serializers import AddKnowQuizQuestionSerializer, KnowQuizOptionsSerializer, KnowQuizQuestionSerializer, AddKnowEssaySerializer, KnowReflectionSerializer, EditKnowQuizQuestionSerializer, EditKnowEssaySerializer, KnowSerializer, KnowReflectionAnswerSerializer, KnowQuizAnswerSerializer
from rest_framework import status
from course.models import RewardStudentPoint, KwlPoint
from .models import Know, KnowQuizOption, KnowQuizQuestion, KnowReflection
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .api_exceptions import ExistingKnowException, KnowQuizNotFoundException, KnowReflectionNotFoundException, KnowDoesNotExistException
from drf_yasg.utils import swagger_auto_schema
from django.db import transaction
from authentication.permissions import isLecturer, isLecturerInKnowCourse

class KnowQuizListView(APIView):
    permission_classes = [IsAuthenticated,]

    @swagger_auto_schema(operation_summary="Add a quiz question", request_body=AddKnowQuizQuestionSerializer)
    def post(self, request):
        try:
            serializer = AddKnowQuizQuestionSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"message": "Quiz added successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @swagger_auto_schema(operation_summary="Get all quiz questions")
    def get(self, request):
        try:
            know_quiz = KnowQuizQuestion.objects.all()
            serializer = KnowQuizQuestionSerializer(know_quiz, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class KnowQuizzesByTopicView(APIView):
    permission_classes = [IsAuthenticated,]

    @swagger_auto_schema(operation_summary="Get all quiz question and options by topic id")
    def get(self, request, topic_id):
        try:
            quiz = KnowQuizQuestion.objects.filter(know__topic_id=topic_id)
            serializer = KnowQuizQuestionSerializer(quiz, many=True)
            print(serializer.data)
            return Response({"questions": serializer.data}, status=status.HTTP_200_OK)
        except KnowQuizQuestion.DoesNotExist:
            raise KnowQuizNotFoundException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(operation_summary="Delete a quiz question by topic id")
    def delete(self, request, topic_id):
        try:
            know = Know.objects.get(topic=topic_id)
            know.delete()
            return Response({"message": "Quiz deleted successfully"}, status=status.HTTP_200_OK)
        except Know.DoesNotExist:
            raise KnowDoesNotExistException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    
        

class KnowQuizDetailView(APIView):
    permission_classes = [IsAuthenticated,]

    @swagger_auto_schema(operation_summary="Get a quiz question")
    def get(self, request, quiz_id):
        try:
            quiz = KnowQuizQuestion.objects.get(id=quiz_id)
            serializer = KnowQuizQuestionSerializer(quiz)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except KnowQuizQuestion.DoesNotExist:
            raise KnowQuizNotFoundException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @swagger_auto_schema(operation_summary="Update a quiz question", request_body=EditKnowQuizQuestionSerializer)
    def put(self, request, quiz_id):
        try:
            quiz = KnowQuizQuestion.objects.get(id=quiz_id)
            serializer = EditKnowQuizQuestionSerializer(quiz, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"message": "Quiz updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
        except KnowQuizQuestion.DoesNotExist:
            raise KnowQuizNotFoundException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class KnowEssayListView(APIView):
    permission_classes = [IsAuthenticated, isLecturer]

    @swagger_auto_schema(operation_summary="Add a reflection question", request_body=AddKnowEssaySerializer)
    def post(self, request):
        try:
            serializer = AddKnowEssaySerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"message": "Reflection question added successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @swagger_auto_schema(operation_summary="Get all reflection questions")
    def get(self, request):
        try:
            know_essay = KnowReflection.objects.all()
            serializer = KnowReflectionSerializer(know_essay, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class KnowEssayDetailView(APIView):
    permission_classes = [IsAuthenticated, isLecturerInKnowCourse]

    @swagger_auto_schema(operation_summary="Get a reflection question by topic id")
    def get(self, request, topic_id):
        
        try:
            print(request.user.username)
            essay = KnowReflection.objects.get(know__topic_id=topic_id)
            serializer = KnowReflectionSerializer(essay)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except KnowReflection.DoesNotExist:
            raise KnowReflectionNotFoundException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @swagger_auto_schema(operation_summary="Update a reflection question by topic id", request_body=EditKnowEssaySerializer)
    def put(self, request, topic_id):
        try:
            essay = KnowReflection.objects.get(know__topic_id=topic_id)
            self.check_object_permissions(request, essay)
            serializer = EditKnowEssaySerializer(essay, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"message": "Reflection question updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
        except KnowReflection.DoesNotExist:
            raise KnowReflectionNotFoundException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @swagger_auto_schema(operation_summary="Delete a reflection question by topic id")
    def delete(self, request, topic_id):
        try:
            know = Know.objects.get(topic=topic_id)
            know.delete()
            return Response({"message": "Reflection question deleted successfully"}, status=status.HTTP_200_OK)
        except Know.DoesNotExist:
            raise KnowDoesNotExistException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class KnowEssayAnswerView(APIView):
    permission_classes = [IsAuthenticated,]

    @swagger_auto_schema(operation_summary="Save a reflection answer")
    def post(self, request):
        try:
            userid = request.user
            serializer = KnowReflectionAnswerSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            topic = serializer.validated_data['topic']
            reflection = serializer.validated_data['reflection']
            student = Student.objects.get(user_id=userid)
         
            know_reflection = KnowReflection.objects.get(know__topic_id=topic)
            answer, answer_created = KnowReflectionStudentAnswer.objects.get_or_create(know_ref=know_reflection, student=student)
            answer.reflection = reflection
            answer.save()
            student_point, reward_created = RewardStudentPoint.objects.get_or_create(student=student, course=know_reflection.know.topic.course)
            kwl_point, kwl_created = KwlPoint.objects.get_or_create(student=student, topic=know_reflection.know.topic)
            kwl_point.kwl_status = 'know'
            know_reflection.know.total_participants += 1
            know_reflection.know.save()
            if answer_created:
                kwl_point.know_score = know_reflection.score
                kwl_point.save()
                total_score = know_reflection.score + student_point.total_point
                student_point.total_point = total_score
                student_point.save()
            return Response({"message": "Reflection answer saved successfully"}, status=status.HTTP_201_CREATED)
        except KnowReflection.DoesNotExist:
            raise KnowReflectionNotFoundException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class KnowQuizAnswerView(APIView):
    permission_classes = [IsAuthenticated,]

    @swagger_auto_schema(operation_summary="Save a quiz answer")
    def post(self, request):
        try:
            with transaction.atomic():
                userid = request.user
                serializer = KnowQuizAnswerSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                topic = serializer.validated_data['topic']

                student = Student.objects.get(user_id=userid)
                know = Know.objects.get(topic_id=topic)
                know.total_participants += 1
                know.save()
                answers = serializer.validated_data['answers']
                quiz_answers, answer_created = KnowQuizStudentAnswer.objects.get_or_create(student=student)
                student_point, reward_created = RewardStudentPoint.objects.get_or_create(student=student, course=know.topic.course)
                kwl_point, kwl_created = KwlPoint.objects.get_or_create(student=student, topic=know.topic)
                kwl_point.kwl_status = 'know'
               
                for answer_pk in answers:
                    quiz_option = KnowQuizOption.objects.get(id=answer_pk)
                    quiz_answers.answers.add(quiz_option)
                    quiz_answers.save()

                    if answer_created:
                        if quiz_option.isCorrect:
                            kwl_point.know_score += quiz_option.know_quiz.score
                            student_point.total_point += quiz_option.know_quiz.score
                            
                kwl_point.save()
                student_point.save()

                return Response({"message": "Quiz answer saved successfully"}, status=status.HTTP_201_CREATED)
        except KnowQuizQuestion.DoesNotExist:
            raise KnowQuizNotFoundException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
