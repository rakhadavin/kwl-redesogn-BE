from authentication.models import Student
from know.models import KnowQuizQuestion, KnowQuizStudentAnswer, KnowReflectionStudentAnswer
from .serializers import KnowQuizQuestionSerializer, AddKnowEssaySerializer, KnowReflectionSerializer, EditKnowQuizQuestionSerializer, EditKnowEssaySerializer, KnowSerializer, KnowReflectionAnswerSerializer, KnowQuizAnswerSerializer, BulkAddQuizSerializer, BulkEditQuizSerializer, get_topic
from rest_framework import status
from course.models import RewardStudentPoint, KwlPoint
from .models import Know, KnowQuizOption, KnowQuizQuestion, KnowReflection
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .api_exceptions import KnowQuizNotFoundException, KnowReflectionNotFoundException, KnowDoesNotExistException
from drf_yasg.utils import swagger_auto_schema
from django.db import transaction
from authentication.permissions import isLecturer, isLecturerInCourse
from rest_framework import exceptions

class KnowQuizListView(APIView):
    permission_classes = [IsAuthenticated,isLecturerInCourse]

    @swagger_auto_schema(operation_summary="Add many quizzes", request_body=BulkAddQuizSerializer)
    def post(self, request):
        try:
            topic = get_topic(request.data['topic'])
            course = topic.course
            self.check_object_permissions(request, course)
            serializer = BulkAddQuizSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"message": "Quizzes added successfully"}, status=status.HTTP_201_CREATED)
        except exceptions.PermissionDenied:
            raise exceptions.PermissionDenied()
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
        
    @swagger_auto_schema(operation_summary="Bulk edit questions")
    def put(self, request):
        try:
            serializer = BulkEditQuizSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            with transaction.atomic():

                first_question_validated = serializer.validated_data['questions'][0]
                know_quiz = KnowQuizQuestion.objects.get(pk=first_question_validated['id'])
                total_questions_before_update = KnowQuizQuestion.objects.filter(know=know_quiz.know).count()
                total_questions_after_update = len(serializer.validated_data['questions'])

                if total_questions_before_update != total_questions_after_update:
                    for total_question in range(total_questions_before_update):
                        question = serializer.validated_data['questions'][total_question]
                        know_quiz = KnowQuizQuestion.objects.get(pk=question['id'])
                        know_quiz.question = question['question']
                        know_quiz.score = question['score']
                        know_quiz.save()
                        options = know_quiz.get_answers()
                        options_tuple = [('option_a', 'Opsi A'), ('option_b', 'Opsi B'), ('option_c', 'Opsi C'), ('option_d', 'Opsi D')]
                        for option in options_tuple:
                            if option[0] in question:
                                answer = options.get(alias=option[0])
                                answer.option_answer = question[option[0]]
                                if 'correct_option' in question:
                                    answer.isCorrect = question['correct_option'] == option[1]
                                answer.save()

                    for question in range(total_questions_before_update, total_questions_after_update):
                        question = serializer.validated_data['questions'][question]
                        question['know'] = know_quiz.know
                        options_data = [
                            {'option_answer': question.pop('option_a'), 'isCorrect': question['correct_option'] == 'Opsi A', 'alias': 'option_a'},
                            {'option_answer': question.pop('option_b'), 'isCorrect': question['correct_option'] == 'Opsi B', 'alias': 'option_b'},
                            {'option_answer': question.pop('option_c'), 'isCorrect': question['correct_option'] == 'Opsi C', 'alias': 'option_c'},
                            {'option_answer': question.pop('option_d'), 'isCorrect': question['correct_option'] == 'Opsi D', 'alias': 'option_d'}
                        ]
                        question.pop('correct_option')      
                        question.pop('id')
                        know_quiz = KnowQuizQuestion.objects.create(**question)
                        options = [KnowQuizOption(know_quiz=know_quiz, **option_data) for option_data in options_data]
                        KnowQuizOption.objects.bulk_create(options)


                else:
                    for question in serializer.validated_data['questions']:
                        know_quiz = KnowQuizQuestion.objects.get(pk=question['id'])
            
                        know_quiz.question = question['question']
                        
                        options = know_quiz.get_answers()
                        options_tuple = [('option_a', 'Opsi A'), ('option_b', 'Opsi B'), ('option_c', 'Opsi C'), ('option_d', 'Opsi D')]

                        for option in options_tuple:
                            if option[0] in question:
                                answer = options.get(alias=option[0])
                                answer.option_answer = question[option[0]]
                                answer.isCorrect = question['correct_option'] == option[1]
                                answer.save()

                        know_quiz.score = question['score']
                        know_quiz.save()
                        
                
            return Response({"message": "Quizzes updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class KnowQuizzesByTopicView(APIView):
    permission_classes = [IsAuthenticated,]

    @swagger_auto_schema(operation_summary="Get all quiz question and options by topic id")
    def get(self, request, topic_id):
        try:
            quiz = KnowQuizQuestion.objects.filter(know__topic_id=topic_id)
            serializer = KnowQuizQuestionSerializer(quiz, many=True)
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
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_summary="Get a reflection question by topic id")
    def get(self, request, topic_id):
        
        try:
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
            kwl_point.know_score += know_reflection.score

            if answer_created:
                know_reflection.know.total_participants += 1
                know_reflection.know.save()
                total_score = know_reflection.score + student_point.total_point
                student_point.total_point = total_score

            student_point.save()
            kwl_point.save()

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
             
                answers = serializer.validated_data['answers']
                quiz_answers, answer_created = KnowQuizStudentAnswer.objects.get_or_create(student=student)
                student_point, reward_created = RewardStudentPoint.objects.get_or_create(student=student, course=know.topic.course)
                kwl_point, kwl_created = KwlPoint.objects.get_or_create(student=student, topic=know.topic)
                
               
                know.total_participants += 1
                know.save()

                kwl_point.kwl_status = 'know'
                quiz_answers.answers.clear()

                kwl_point.know_score = 0
 
                for answer_pk in answers:
                    quiz_option = KnowQuizOption.objects.get(id=answer_pk)
                    quiz_answers.answers.add(quiz_option)
                    
                    if answer_created:
                        if quiz_option.isCorrect:
                            student_point.total_point += quiz_option.know_quiz.score
                    
                    if quiz_option.isCorrect:
                        kwl_point.know_score += quiz_option.know_quiz.score

                quiz_answers.save()     
                kwl_point.save()
                student_point.save()

                return Response({"message": "Quiz answer saved successfully"}, status=status.HTTP_201_CREATED)
        except KnowQuizQuestion.DoesNotExist:
            raise KnowQuizNotFoundException()
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
