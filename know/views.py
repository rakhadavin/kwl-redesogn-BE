
from django.http import Http404
from django.shortcuts import render

from authentication.models import Student
from know.models import KnowQuizQuestion, KnowQuizStudentAnswer, KnowReflectionStudentAnswer
from .serializers import AddKnowQuizQuestionSerializer, KnowQuizOptionsSerializer, KnowQuizQuestionSerializer, AddKnowEssaySerializer, KnowReflectionSerializer, EditKnowQuizQuestionSerializer, EditKnowEssaySerializer, KnowSerializer, KnowReflectionAnswerSerializer, KnowQuizAnswerSerializer, KnowQuizAnswersSerializer
from rest_framework import status
from course.models import RewardStudentPoint
from .models import Know, KnowQuizQuestion, KnowReflection
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .api_exceptions import ExistingKnowException, KnowQuizNotFoundException, KnowReflectionNotFoundException, KnowDoesNotExistException
from drf_yasg.utils import swagger_auto_schema

class KnowQuizListView(APIView):
    permission_classes = [IsAuthenticated,]

    @swagger_auto_schema(operation_description="Add a quiz question", request_body=AddKnowQuizQuestionSerializer)
    def post(self, request):
        try:
            serializer = AddKnowQuizQuestionSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"message": "Quiz added successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @swagger_auto_schema(operation_description="Get all quiz questions")
    def get(self, request):
        try:
            know_quiz = KnowQuizQuestion.objects.all()
            serializer = KnowQuizQuestionSerializer(know_quiz, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class KnowQuizzesByTopicView(APIView):
    permission_classes = [IsAuthenticated,]

    @swagger_auto_schema(operation_description="Get all quiz question and options by topic id")
    def get(self, request, topic_id):
        try:
            quiz = KnowQuizQuestion.objects.filter(know__topic_id=topic_id)
            serializer = KnowQuizQuestionSerializer(quiz, many=True)
            return Response({"questions": serializer.data}, status=status.HTTP_200_OK)
        except KnowQuizQuestion.DoesNotExist:
            raise KnowQuizNotFoundException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(operation_description="Delete a quiz question by topic id")
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

    @swagger_auto_schema(operation_description="Get a quiz question")
    def get(self, request, quiz_id):
        try:
            quiz = KnowQuizQuestion.objects.get(id=quiz_id)
            serializer = KnowQuizQuestionSerializer(quiz)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except KnowQuizQuestion.DoesNotExist:
            raise KnowQuizNotFoundException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @swagger_auto_schema(operation_description="Update a quiz question", request_body=EditKnowQuizQuestionSerializer)
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


# class KnowQuizAnswerView(APIView):
#     permission_classes = [IsAuthenticated,]

#     @swagger_auto_schema(operation_description="Save a bulk of quiz answer")
#     def post(self, request):
#         try:
#             userid = request.user
#             serializer = KnowQuizAnswersSerializer(data=request.data)
#             serializer.is_valid(raise_exception=True)
#             answers = serializer.validated_data['answers']
#             student = Student.objects.get(user_id=userid)
#             student_answers = []
#             for answer in answers:
#                 quiz = KnowQuizQuestion.objects.get(id=answer['know_quiz_id'])
#                 correct_option = quiz.get_answers().get(isCorrect=True)
#                 history, created = KnowQuizStudentAnswer.objects.get_or_create(know_quiz=quiz, student=student)
#                 history.answer = answer['answer']
#                 if correct_option.option_answer == answer['answer']:
#                     score = quiz.score
#                     history.score = score
#                 else:
#                     history.score = 0
#                 history.save()
#                 student_answers.append({"question": quiz.question, "answer": answer['answer'], "score": history.score})
#             return Response({"message": "Answers saved successfully", "data": student_answers}, status=status.HTTP_201_CREATED)
#         except KnowQuizQuestion.DoesNotExist:
#             raise KnowQuizNotFoundException()
#         except Exception as e:
#             return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        



# class KnowQuizView():
        
#     @api_view(['POST'])
#     def add_know_quiz(request):
#         serializer = AddKnowQuizQuestionSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({"message": "Quiz added successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
#         else:
#              return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
#     @api_view(['PUT'])
#     def edit_know_quiz(request, quiz_id):
#         try:
#             quiz = get_know_quiz_question_or_404_by_quiz_id(quiz_id)
#             serializer = EditKnowQuizQuestionSerializer(quiz, data=request.data)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response({"message": "Quiz updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
#             return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
#         except Http404:
#             return Response({"error": "Quiz question not found"}, status=status.HTTP_404_NOT_FOUND)
   
#     @api_view(['GET'])
#     def get_question_by_quiz_id(request, quiz_id):
#         try:
#             know_quiz = get_know_quiz_question_or_404_by_quiz_id(quiz_id)
        
#             question_serializer = KnowQuizQuestionSerializer(know_quiz)
#             options = know_quiz.get_answers()
#             option_serializer = KnowQuizOptionsSerializer(options, many=True)
    
#             return Response({"question":question_serializer.data,"options":option_serializer.data}, status=status.HTTP_200_OK)
#         except Http404:
#             return Response({"error": "Quiz question not found"}, status=status.HTTP_404_NOT_FOUND)
        
#     @api_view(['DELETE'])
#     def delete_know_quiz(request, quiz_id):
#         try:
#             quiz = get_know_quiz_question_or_404_by_quiz_id(quiz_id)
#             quiz.delete()
#             return Response({"message": "Quiz deleted successfully"}, status=status.HTTP_200_OK)
#         except Http404:
#             return Response({"error": "Quiz question not found"}, status=status.HTTP_404_NOT_FOUND)
    
#     @api_view(['GET'])
#     def get_all_questions_by_know_id(request, know_id):
#         questions = KnowQuizQuestion.objects.filter(know_id=know_id)
#         questions_data = []
#         for question in questions:
#             question_data = {
#                 "question": KnowQuizQuestionSerializer(question).data,
#                 "options": KnowQuizOptionsSerializer(question.get_answers(), many=True).data,
#                 "correct_answer": question.get_answers().get(isCorrect=True).option_answer
#             }
#             questions_data.append(question_data)
#         return Response({"questions": questions_data}, status=status.HTTP_200_OK)
    
#     @api_view(['POST'])
#     @permission_classes([IsAuthenticated])
#     def save_student_all_answers_by_know_id(request, know_id):
#         user_id = request.user
#         student = Student.objects.get(user_id=user_id)
#         answers = request.data['answers']
#         questions = KnowQuizQuestion.objects.filter(know_id=know_id)
#         student_answers = []
#         for answer in answers:
#             id = answer['know_quiz_id']
#             question = questions.get(id=id)
#             correct_option = question.get_answers().get(isCorrect=True)
#             history, created = KnowQuizStudentAnswer.objects.get_or_create(know_quiz_question_id=question, student_id=student)
#             if correct_option.option_answer == answer['answer']:
#                 score = question.score
#                 history.score = score
#             else:
#                 history.score = 0
#             history.answer = answer['answer']
#             history.save()

#             question = KnowQuizQuestionSerializer(question).data
#             student_answers.append({"question": question, "answer": answer['answer'], "score": history.score})
 

#         return Response({"message": "Answers saved successfully", "data": student_answers}, status=status.HTTP_201_CREATED)
        
    
#     @api_view(['POST'])
#     @permission_classes([IsAuthenticated])
#     def save_student_answer(request,know_quiz_id):
#         try:
#             user_id = request.user
#             student = Student.objects.get(user_id=user_id)
#             answer = request.data['answer']
#             know_quiz = get_know_quiz_question_or_404_by_quiz_id(know_quiz_id)
#             correct_option = know_quiz.get_answers().get(isCorrect=True)

#             history, created = KnowQuizStudentAnswer.objects.get_or_create(know_quiz_question_id=know_quiz, student_id=student)
#             history.answer = answer
#             if correct_option.option_answer == answer:
#                 score = know_quiz.score 
#                 history.score = score
#                 history.save()
#             else: 
#                 history.score = 0
#                 history.save()
#             return Response({"message": "Answer saved successfully"}, status=status.HTTP_201_CREATED)
#         except Http404:
#             return Response({"error": "Quiz question not found"}, status=status.HTTP_404_NOT_FOUND)
        
#     @api_view(['GET'])
#     def get_student_answers_by_student_id(request, student_id):
#         student_answers = KnowQuizStudentAnswer.objects.filter(student_id=student_id)
#         return Response({"data": student_answers}, status=status.HTTP_200_OK)
    
class KnowEssayListView(APIView):
    permission_classes = [IsAuthenticated,]

    @swagger_auto_schema(operation_description="Add a reflection question", request_body=AddKnowEssaySerializer)
    def post(self, request):
        try:
            serializer = AddKnowEssaySerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"message": "Reflection question added successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @swagger_auto_schema(operation_description="Get all reflection questions")
    def get(self, request):
        try:
            know_essay = KnowReflection.objects.all()
            serializer = KnowReflectionSerializer(know_essay, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class KnowEssayDetailView(APIView):
    permission_classes = [IsAuthenticated,]

    @swagger_auto_schema(operation_description="Get a reflection question by topic id")
    def get(self, request, topic_id):
        try:
            essay = KnowReflection.objects.get(know__topic_id=topic_id)
            serializer = KnowReflectionSerializer(essay)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except KnowReflection.DoesNotExist:
            raise KnowReflectionNotFoundException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @swagger_auto_schema(operation_description="Update a reflection question by topic id", request_body=EditKnowEssaySerializer)
    def put(self, request, topic_id):
        try:
            essay = KnowReflection.objects.get(know__topic_id=topic_id)
            serializer = EditKnowEssaySerializer(essay, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"message": "Reflection question updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
        except KnowReflection.DoesNotExist:
            raise KnowReflectionNotFoundException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @swagger_auto_schema(operation_description="Delete a reflection question by topic id")
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

    @swagger_auto_schema(operation_description="Save a reflection answer")
    def post(self, request):
        try:
            userid = request.user
            serializer = KnowReflectionAnswerSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            topic = serializer.validated_data['topic']
            reflection = serializer.validated_data['reflection']
            student = Student.objects.get(user_id=userid)
         
            know_reflection = KnowReflection.objects.get(know__topic_id=topic)
            answer = KnowReflectionStudentAnswer.objects.create(know_ref=know_reflection, reflection=reflection, student=student)
            student_point, created = RewardStudentPoint.objects.get_or_create(student=student, course=know_reflection.know.topic.course)
            total_score = know_reflection.score + student_point.total_point
            print(know_reflection.score)
            student_point.total_point = total_score
            student_point.save()
            return Response({"message": "Reflection answer saved successfully"}, status=status.HTTP_201_CREATED)
        except KnowReflection.DoesNotExist:
            raise KnowReflectionNotFoundException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
