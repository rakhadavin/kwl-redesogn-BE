from django.http import Http404
from django.shortcuts import render

from authentication.models import Student
from learned.api_exceptions import LearnedDoesNotExistException, LearnedReflectionNotFoundException
from .serializers import AddLearnedEssaySerializer, EditLearnedEssaySerializer, LearnedQuizAnswerSerializer, LearnedReflectionAnswerSerializer, LearnedReflectionSerializer, AddLearnedQuizQuestionSerializer, EditLearnedQuizQuestionSerializer, LearnedQuizQuestionSerializer, BulkEditQuizSerializer, BulkAddLearnedQuizSerializer 
from .models import Learned, LearnedQuizOption, LearnedReflection, LearnedReflectionStudentAnswer, LearnedQuizQuestion, LearnedQuizStudentAnswer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from course.models import RewardStudentPoint, KwlPoint
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from django.db import transaction

class LearnedQuizListView(APIView):
    permission_classes = [IsAuthenticated,]

    @swagger_auto_schema(operation_description="Add bulk of learned quiz", request_body=BulkAddLearnedQuizSerializer)
    def post(self, request):
        try:
            serializer = BulkAddLearnedQuizSerializer(data=request.data)
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
        
    @swagger_auto_schema(operation_description="Edit bulk of learned quiz", request_body=BulkEditQuizSerializer)
    def put(self, request):
        try:
            serializer = BulkEditQuizSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            with transaction.atomic():
                validated_data = serializer.validated_data
                questions = validated_data.pop('questions')
                for question in questions:
                    question_instance = LearnedQuizQuestion.objects.get(pk=question['id'])
                    question_instance.question = question['question']
                    question_instance.score = question['score']
                    question_instance.save()
                    options = question_instance.get_answers()
                    options_tuple = [('option_a', 'Opsi A'), ('option_b', 'Opsi B'), ('option_c', 'Opsi C'), ('option_d', 'Opsi D')]
                    for option in options_tuple:
                        if option[0] in question:
                            answer = options.get(alias=option[0])
                            answer.option_answer = question[option[0]]
                            if 'correct_option' in question:
                                answer.isCorrect = question['correct_option'] == option[1]
                            answer.save()
      
            return Response({"message": "Quiz updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            print(str(e))
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class LearnedQuizzesByTopicView(APIView):   
    permission_classes = [IsAuthenticated,]

    @swagger_auto_schema(operation_description="Get all learned quiz by topic id")
    def get(self, request, topic_id):
        try:
            quiz = LearnedQuizQuestion.objects.filter(learned__topic_id=topic_id)
            serializer = LearnedQuizQuestionSerializer(quiz, many=True)
            return Response({"questions":serializer.data}, status=status.HTTP_200_OK)
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
        

class LearnedEssayAnswerView(APIView):
    permission_classes = [IsAuthenticated,]

    @swagger_auto_schema(operation_description="Save a reflection answer")
    def post(self, request):
        try:
            with transaction.atomic():
                userid = request.user
                serializer = LearnedReflectionAnswerSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                topic = serializer.validated_data['topic']
                reflection = serializer.validated_data['reflection']
                student = Student.objects.get(user_id=userid)
            
                learned_reflection = LearnedReflection.objects.get(learned__topic_id=topic)
                answer, answer_created = LearnedReflectionStudentAnswer.objects.get_or_create(learned_ref=learned_reflection, student=student)
                answer.reflection = reflection
                answer.save()
                student_point, reward_created = RewardStudentPoint.objects.get_or_create(student=student, course=learned_reflection.learned.topic.course)
                kwl_point, kwl_created = KwlPoint.objects.get_or_create(student=student, topic=learned_reflection.learned.topic)
                kwl_point.kwl_status = 'learned'
                kwl_point.learned_score = learned_reflection.score
                learned_reflection.learned.total_participants += 1
                learned_reflection.learned.save()
                kwl_point.save()
                
                if answer_created:
                    total_score = learned_reflection.score + student_point.total_point
                    student_point.total_point = total_score
                    student_point.save()
            return Response({"message": "Reflection answer saved successfully"}, status=status.HTTP_201_CREATED)
        except LearnedReflection.DoesNotExist:
            raise LearnedReflectionNotFoundException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LearnedQuizAnswerView(APIView):
    permission_classes = [IsAuthenticated,]
    
    def post(self, request):
        try:
            with transaction.atomic():
                userid = request.user
                serializer = LearnedQuizAnswerSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                topic = serializer.validated_data['topic']
                answers = serializer.validated_data['answers']
                student = Student.objects.get(user_id=userid)
                quiz_answers, answer_created = LearnedQuizStudentAnswer.objects.get_or_create(student=student)
                learned = Learned.objects.get(topic_id=topic)
                learned.total_participants += 1
                learned.save()
                student_point, reward_created = RewardStudentPoint.objects.get_or_create(student=student, course=learned.topic.course)
                kwl_point, kwl_created = KwlPoint.objects.get_or_create(student=student, topic=learned.topic)
                kwl_point.kwl_status = 'learned'
                kwl_point.learned_score = 0
                
                for answer_pk in answers:
                    quiz_option = LearnedQuizOption.objects.get(id=answer_pk)
                    quiz_answers.answers.add(quiz_option)
                    quiz_answers.save()

                    if answer_created:
                        if quiz_option.isCorrect:
                            total_score = quiz_option.learned_quiz.score + student_point.total_point
                            student_point.total_point = total_score
                    else:
                        if quiz_option.isCorrect:
                            kwl_point.learned_score += quiz_option.learned_quiz.score

                           
                kwl_point.save()
                student_point.save()
                return Response({"message": "Quiz answer saved successfully"}, status=status.HTTP_201_CREATED)
        except LearnedQuizQuestion.DoesNotExist:
            raise LearnedReflectionNotFoundException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                