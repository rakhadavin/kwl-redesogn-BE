from django.shortcuts import render
from django.db.models import F

import os
from django.conf import settings
from wordcloud import WordCloud
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.http import Http404
from analysis import models
from course.api_exceptions import TopicNotFoundException
from course.models import KwlPoint, Topic
from know.models import Know, KnowReflectionStudentAnswer, KnowQuizStudentAnswer, KnowQuizQuestion, KnowQuizOption
from learned.models import Learned, LearnedReflectionStudentAnswer, LearnedQuizStudentAnswer, LearnedQuizQuestion, LearnedQuizOption
from wtk.models import WantToKnow, WtkPollStudentAnswer, WtkReflectionStudentAnswer, WtkPollQuestion
from drf_yasg.utils import swagger_auto_schema

from .api_exceptions import InvalidTypeException, EmptyReflectionException

# Create your views here.
def get_topic(topic_id):
    try:
        return Topic.objects.get(pk=topic_id)
    except Topic.DoesNotExist:
        raise TopicNotFoundException()
    
class WordCloudAPIView(APIView):
    @swagger_auto_schema(operation_description="Get the word cloud image of the reflections", responses={200: "OK", 400: "Bad Request"})
    def get(self, request, type, topic):

        reflections = []

        topic = get_topic(topic)
        

        if type == 'learned':
            reflections = LearnedReflectionStudentAnswer.objects.filter(learned_ref__learned__topic=topic).values_list('student__user__username', 'reflection')
        elif type == 'wtk':
            reflections = WtkReflectionStudentAnswer.objects.filter(wtk_ref__wtk__topic=topic).values_list('student__user__username', 'reflection')
        elif type == 'know':
            reflections = KnowReflectionStudentAnswer.objects.filter(know_ref__know__topic=topic).values_list('student__user__username', 'reflection')
        else:
            raise InvalidTypeException()
        if len(reflections) == 0:
            raise EmptyReflectionException()
        all_reflections = ' '.join(reflection[1] for reflection in reflections)
       

        wordcloud = WordCloud(width=1600, height=800, background_color='white', max_font_size=200).generate(all_reflections)

        image_path = os.path.join(settings.MEDIA_ROOT, 'word_cloud.png')

        wordcloud.to_file(image_path)

        image_url = os.path.join(settings.MEDIA_URL, 'word_cloud.png')

        return Response({'image_url': image_url, 'reflections': reflections})

class KwlParticipantCountView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(operation_description="Get the number of participants for each KWL stage", responses={200: "OK", 400: "Bad Request"})

    def get(self, request, topic):
        try:
            wtk = WantToKnow.objects.get(topic=topic)
            know = Know.objects.get(topic=topic)
            learned = Learned.objects.get(topic=topic)
            topic = Topic.objects.get(id=topic)
            total_students_enrolled = topic.course.students.all().count()
            wtk_total_participants = 0

            if wtk.type == 'checkbox':
                wtk_total_participants = WtkPollStudentAnswer.objects.filter(wtk_poll__wtk=wtk).count()
            elif wtk.type == 'reflection':
                wtk_total_participants = WtkReflectionStudentAnswer.objects.filter(wtk_ref__wtk=wtk).count()

            know_total_participants = 0

            if know.type == 'quiz':
                know_total_participants = KnowQuizStudentAnswer.objects.filter(answers__know_quiz__know=know).distinct().count()
            elif know.type == 'reflection':
                know_total_participants = KnowReflectionStudentAnswer.objects.filter(know_ref__know=know).count()

            learned_total_participants = 0

            if learned.type == 'quiz':
                learned_total_participants = LearnedQuizStudentAnswer.objects.filter(answers__learned_quiz__learned=learned).distinct().count()
            elif learned.type == 'reflection':
                learned_total_participants = LearnedReflectionStudentAnswer.objects.filter(learned_ref__learned=learned).count()
            

            res_data = {
            }
            res_data['wtk'] = {
                'total_participants': wtk_total_participants,
                'percentage': "{:,.2f}".format((wtk_total_participants / total_students_enrolled) * 100)
            }

            res_data['know'] = {
                'total_participants': know_total_participants,
                'percentage': "{:,.2f}".format((know_total_participants / total_students_enrolled) * 100)
            }

            res_data['learned'] = {
                'total_participants': learned_total_participants,
                'percentage': "{:,.2f}".format((learned_total_participants / total_students_enrolled) * 100)
            }

            res_data['total_students_enrolled'] = total_students_enrolled
            
            return Response(res_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class KwlPointLadderView(APIView):
        permission_classes = [IsAuthenticated]
        @swagger_auto_schema(operation_description="Get 5 highest and 5 lowest kwl scores", responses={200: "OK", 400: "Bad Request"})
        def get(self, request, topic, filter_number=5):
            kwl_points = KwlPoint.objects.annotate(total_point=F('know_score') + F('wtk_score') + F('learned_score'))
            four_highest_student_points = kwl_points.filter(topic=topic).order_by('-total_point')[:filter_number]
            four_lowest_student_points = kwl_points.filter(topic=topic).order_by('total_point')[:filter_number]

            four_highest_student_points_data = []
            four_lowest_student_points_data = []

            for student_point in four_highest_student_points:
                student_data = {
                    'student': student_point.student.user.first_name + ' ' + student_point.student.user.last_name,
                    'total_point': student_point.get_total_point()
                }
                four_highest_student_points_data.append(student_data)

            for student_point in four_lowest_student_points:
                student_data = {
                    'student': student_point.student.user.first_name + ' ' + student_point.student.user.last_name,
                    'total_point': student_point.get_total_point()
                }
                four_lowest_student_points_data.append(student_data)
            
            return Response({'highest': four_highest_student_points_data, 'lowest': four_lowest_student_points_data})

class StudentKWLRecapView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(operation_description="Get the student's KWL recap", responses={200: "OK", 400: "Bad Request"})
    def get(self, request, topic, student_id):
        try:
            topic = get_topic(topic)
            student = topic.course.students.get(pk=student_id)
            know = Know.objects.get(topic=topic)
            learned = Learned.objects.get(topic=topic)
            wtk = WantToKnow.objects.get(topic=topic)
            
            know_type = know.type
            learned_type = learned.type
            wtk_type = wtk.type

            know_answered = False
            learned_answered = False
            wtk_answered = False

            if know_type == 'reflection':
                know_answered = KnowReflectionStudentAnswer.objects.filter(know_ref__know=know, student=student).exists()
            elif know_type == 'quiz':
                know_answered = KnowQuizStudentAnswer.objects.filter(answers__know_quiz__know=know, student=student).exists()
            
            if learned_type == 'reflection':
                learned_answered = LearnedReflectionStudentAnswer.objects.filter(learned_ref__learned=learned, student=student).exists()
            elif learned_type == 'quiz':
                learned_answered = LearnedQuizStudentAnswer.objects.filter(answers__learned_quiz__learned=learned, student=student).exists()
            
            if wtk_type == 'reflection':
                wtk_answered = WtkReflectionStudentAnswer.objects.filter(wtk_ref__wtk=wtk, student=student).exists()
            elif wtk_type == 'checkbox':
                wtk_answered = WtkPollStudentAnswer.objects.filter(wtk_poll__wtk=wtk, student=student).exists()

            participation_counter = 0
            if know_answered:
                participation_counter += 1
            if learned_answered:
                participation_counter += 1
            if wtk_answered:
                participation_counter += 1

            participation_percentage = "{:,.2f}".format((participation_counter / 3) * 100)


            res_data = {
                'know': {
                    'answered': know_answered,
                    'type': know_type
                },
                'learned': {
                    'answered': learned_answered,
                    'type': learned_type
                },
                'wtk': {
                    'answered': wtk_answered,
                    'type': wtk_type
                },
                'participation_percentage': participation_percentage

            }

            return Response(res_data, status=status.HTTP_200_OK)
        

        except Topic.DoesNotExist:
            raise TopicNotFoundException()
        
class StudentAnswerDetailAnalysis(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(operation_description="Get the student's answer details for each KWL stage", responses={200: "OK", 400: "Bad Request"})
    def get(self, request, type, topic, student_id):
   

        try:
            topic = get_topic(topic)
            student = topic.course.students.get(pk=student_id)
            student_data = {}
            if type == 'know':
                know = Know.objects.get(topic=topic)
                if know.type == 'reflection':
                    student_answer = KnowReflectionStudentAnswer.objects.get(know_ref__know=know, student=student)
                    student_data = {
                        'student': student.user.username,
                        'answer': student_answer.reflection,
                        'question': student_answer.know_ref.question
                    }

                elif know.type == 'quiz':
                    answers = []
                    quiz_questions = KnowQuizQuestion.objects.filter(know__topic=topic)
                    for question in quiz_questions:
                        quiz_data = []
                        all_quiz_options = KnowQuizOption.objects.filter(know_quiz=question)
                        for option in all_quiz_options:
                            student_answer = KnowQuizStudentAnswer.objects.filter(answers__know_quiz=question, student=student).first()
                            if student_answer is None:
                                return Response({'message': 'Mahasiswa belum mengisi tahap know'}, status=status.HTTP_400_BAD_REQUEST)
                            student_answer_isSelected = student_answer.answers.filter(id=option.id).exists()
                            correct_answer = option.isCorrect
                            option_answer = option.option_answer
                            quiz_data.append({'isSelected': student_answer_isSelected, 'isCorrect': correct_answer, 'option': option_answer})
                        answers.append({'question': question.question, 'choices': quiz_data})
                    student_data = {
                        'student': student.user.username,
                        'answers': answers
                    }

                    
            elif type == 'learned':
                learned = Learned.objects.get(topic=topic)
                if learned.type == 'reflection':
                    student_answer = LearnedReflectionStudentAnswer.objects.get(learned_ref__learned=learned, student=student)
                    student_data = {
                        'student': student.user.username,
                        'answer': student_answer.reflection
                    }
                elif learned.type == 'quiz':
                    answers = []
                    quiz_questions = LearnedQuizQuestion.objects.filter(learned__topic=topic)
                    for question in quiz_questions:
                        quiz_data = []
                        all_quiz_options = LearnedQuizOption.objects.filter(learned_quiz=question)
                        for option in all_quiz_options:
        
                            student_answer = LearnedQuizStudentAnswer.objects.filter(answers__learned_quiz=question, student=student).first()
                            if student_answer is None:
                                return Response({'error': 'Mahasiswa belum mengisi tahap learned'}, status=status.HTTP_400_BAD_REQUEST)
                            student_answer_isSelected = student_answer.answers.filter(id=option.id).exists()
                            correct_answer = option.isCorrect
                            option_answer = option.option_answer
                            
                            quiz_data.append({'isSelected': student_answer_isSelected, 'isCorrect': correct_answer, 'option': option_answer})
                        answers.append({'question': question.question, 'choices': quiz_data})
                    student_data = {
                        'student': student.user.username,
                        'answers': answers
                    }

            elif type == 'wtk':
                wtk = WantToKnow.objects.get(topic=topic)
                if wtk.type == 'reflection':
                    student_answer = WtkReflectionStudentAnswer.objects.get(wtk_ref__wtk=wtk, student=student)
                    student_data = {
                        'student': student.user.username,
                        'answer': student_answer.reflection
                    }
                elif wtk.type == 'checkbox':
                    student_answer = WtkPollStudentAnswer.objects.filter(wtk_poll__wtk=wtk, student=student)
                    wtk_poll = student_answer.first().wtk_poll
                    
                    checkbox_choices = []
                    for choice in wtk_poll.choices.all():
                        checkbox_student = student_answer.filter(choices__in=[choice]).exists()
                        checkbox_choices.append({'choice': choice.option_answer, 'selected': checkbox_student})
                    student_data = {
                        'student': student.user.username,
                        'choices': checkbox_choices,
                        'question' : wtk_poll.question  
                    }
                  
            else:
                raise InvalidTypeException()
        except Topic.DoesNotExist:
            raise TopicNotFoundException()
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        student_data['topic'] = topic.name
        student_data['course'] = topic.course.short_name    
        return Response(student_data, status=status.HTTP_200_OK)


# class KwlParticipantCountView(APIView):
#     permission_classes = [IsAuthenticated]
#     @swagger_auto_schema(operation_description="Get the number of participants for each KWL stage", responses={200: "OK", 400: "Bad Request"})
#     def get(self, request,topic):

#         try:
#             topic_id = topic

#             topic = Topic.objects.get(id=topic_id)
#             course = topic.course
#             total_enrolled_students = course.students.all().count()
#             if total_enrolled_students == 0:
#                 return Response({'error': 'No students enrolled in this course.'}, status=status.HTTP_400_BAD_REQUEST)
            
#             know = Know.objects.get(topic=topic)
#             learned = Learned.objects.get(topic=topic)
#             wtk = WantToKnow.objects.get(topic=topic)

#             know_count = know.total_participants
#             know_percentage = (know_count / total_enrolled_students) * 100
#             learned_count = learned.total_participants
#             learned_percentage = (learned_count / total_enrolled_students) * 100
#             wtk_count = wtk.total_participants
#             wtk_percentage = (wtk_count / total_enrolled_students) * 100
            
        

#             return Response({'know': {'count': know_count, 'percentage': know_percentage}, 'learned': {'count': learned_count, 'percentage': learned_percentage}, 'wtk': {'count': wtk_count, 'percentage': wtk_percentage}})   
#         except Topic.DoesNotExist:
            
#             raise TopicNotFoundException()
#         except Exception as e:
#             print(str(e))
#             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


        
class TopicPollingAnalysisView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_description="Get the polling data for the topic", responses={200: "OK", 400: "Bad Request"})
    def get(self, request, topic):
        try:
            poll_data = {}
            topic = Topic.objects.get(id=topic)
            question = WtkPollQuestion.objects.get(wtk__topic=topic)
            choices = question.choices.all()
            choices_data = []
            wtk = WantToKnow.objects.get(topic=topic)
            wtk_total_participants = WtkPollStudentAnswer.objects.filter(wtk_poll__wtk=wtk).count()
            for choice in choices:
                choice_data = {
                    'choice': choice.option_answer,
                    'total_votes': "{:.2f}".format((choice.total_votes/wtk_total_participants) * 100)+'%'
                }
                choices_data.append(choice_data)
            poll_data['question'] = question.question
            poll_data['choices'] = choices_data

            course_short_name = topic.course.short_name
            course_full_name = topic.course.full_name
            topic_name = topic.name
            poll_data['course'] = {
                'short_name': course_short_name,
                'full_name': course_full_name
            }
            poll_data['topic'] = topic_name

        course_short_name = topic.course.short_name
        course_full_name = topic.course.full_name
        topic_name = topic.name
        poll_data.append({'course_full_name':course_full_name,'course_short_name': course_short_name, 'topic_name': topic_name})


            return Response(poll_data, status=status.HTTP_200_OK)
        except Topic.DoesNotExist:
            raise TopicNotFoundException()
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

class QuizAccuracyAnalysisView(APIView):

    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(operation_description="Get the number of correct answers for each quiz question", responses={200: "OK", 400: "Bad Request"})
    def get(self, request, type, topic):
        topic = Topic.objects.get(id=topic)
        accuracy_data = {}
        accuracy_data['topic'] = topic.name
        accuracy_data['course_short_name'] = topic.course.short_name
        quiz_data = []
        if type == 'know':
            quiz_question = KnowQuizQuestion.objects.filter(know__topic=topic)
            for question in quiz_question:
                correct_answers = KnowQuizStudentAnswer.objects.filter(answers__know_quiz=question, answers__isCorrect=True).count()
                accuracy = "{:.2f}".format((correct_answers / question.know.total_participants) * 100)
                question_data = {
                    'question': question.question,
                    'accuracy': accuracy
                }
                quiz_data.append(question_data)
            accuracy_data['quiz_data'] = quiz_data

        elif type == 'learned':
            quiz_question = LearnedQuizQuestion.objects.filter(learned__topic=topic)
            for question in quiz_question:
                correct_answers = LearnedQuizStudentAnswer.objects.filter(answers__learned_quiz=question, answers__isCorrect=True).count()
                accuracy = "{:.2f}".format((correct_answers / question.learned.total_participants) * 100)
                question_data = {
                    'question': question.question,
                    'accuracy': accuracy
                }
                quiz_data.append(question_data)
            accuracy_data['quiz_data'] = quiz_data
        else:
            raise InvalidTypeException()
            

        return Response(accuracy_data, status=status.HTTP_200_OK)
       

class QuizBarchartView(APIView):

    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(operation_description="Get the image of the barchart for the quiz questions", responses={200: "OK", 400: "Bad Request"})
    def get(self, request, type, topic):
        try:
            topic = Topic.objects.get(id=topic)
            quiz_data = []
            if type == 'know':
                quiz_question = KnowQuizQuestion.objects.filter(know__topic=topic)
                for index, question in enumerate(quiz_question):
                    correct_answers = KnowQuizStudentAnswer.objects.filter(answers__know_quiz=question, answers__isCorrect=True).count()
                    incorrect_answers = question.know.total_participants - correct_answers
                    question_data = {
                        'index': index+1,
                        'correct_answers': correct_answers,
                        'incorrect_answers': incorrect_answers
                    }
                    quiz_data.append(question_data)
            elif type == 'learned':
                quiz_question = LearnedQuizQuestion.objects.filter(learned__topic=topic).all()
                for index, question in enumerate(quiz_question):
                    
                    correct_answers = LearnedQuizStudentAnswer.objects.filter(answers__learned_quiz=question, answers__isCorrect=True).count()
                    incorrect_answers = question.learned.total_participants - correct_answers
                    question_data = {
                        'index': index+1,
                        'correct_answers': correct_answers,
                        'incorrect_answers': incorrect_answers
                    }
                    quiz_data.append(question_data)
            else:
                raise InvalidTypeException()


            return Response({'quiz_data': quiz_data}, status=status.HTTP_200_OK)
        except Topic.DoesNotExist:
            raise TopicNotFoundException()
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)