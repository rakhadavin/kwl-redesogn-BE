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
from know.models import Know, KnowReflectionStudentAnswer, KnowQuizStudentAnswer, KnowQuizQuestion
from learned.models import Learned, LearnedReflectionStudentAnswer, LearnedQuizStudentAnswer, LearnedQuizQuestion
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
        print(reflections)
        all_reflections = ' '.join(reflection[1] for reflection in reflections)
       

        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_reflections)

        image_path = os.path.join(settings.MEDIA_ROOT, 'word_cloud.png')

        wordcloud.to_file(image_path)

        image_url = os.path.join(settings.MEDIA_URL, 'word_cloud.png')

        return Response({'image_url': image_url, 'reflections': reflections})


class KwlParticipantCountView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(operation_description="Get the number of participants for each KWL stage", responses={200: "OK", 400: "Bad Request"})
    def get(self, request,topic):

        try:
            topic_id = topic

            topic = Topic.objects.get(id=topic_id)
            course = topic.course
            total_enrolled_students = course.students.all().count()
            if total_enrolled_students == 0:
                return Response({'error': 'No students enrolled in this course.'}, status=status.HTTP_400_BAD_REQUEST)
            
            know = Know.objects.get(topic=topic)
            learned = Learned.objects.get(topic=topic)
            wtk = WantToKnow.objects.get(topic=topic)

            know_count = know.total_participants
            know_percentage = (know_count / total_enrolled_students) * 100
            learned_count = learned.total_participants
            learned_percentage = (learned_count / total_enrolled_students) * 100
            wtk_count = wtk.total_participants
            wtk_percentage = (wtk_count / total_enrolled_students) * 100

        

            return Response({'know': {'count': know_count, 'percentage': know_percentage}, 'learned': {'count': learned_count, 'percentage': learned_percentage}, 'wtk': {'count': wtk_count, 'percentage': wtk_percentage}})   
        except Topic.DoesNotExist:
            
            raise TopicNotFoundException()
        except Exception as e:
            print(str(e))
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class KwlPointLadderView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(operation_description="Get 4 highest and 4 lowest kwl scores", responses={200: "OK", 400: "Bad Request"})
    def get(self, request, topic):
        kwl_points = KwlPoint.objects.annotate(total_point=F('know_score') + F('wtk_score') + F('learned_score'))
        four_highest_student_points = kwl_points.filter(topic=topic).order_by('-total_point')[:4]
        four_lowest_student_points = kwl_points.filter(topic=topic).order_by('total_point')[:4]

        four_highest_student_points_data = []
        four_lowest_student_points_data = []

        for student_point in four_highest_student_points:
            student_data = {
                'student': student_point.student.user.username,
                'total_point': student_point.get_total_point()
            }
            four_highest_student_points_data.append(student_data)

        for student_point in four_lowest_student_points:
            student_data = {
                'student': student_point.student.user.username,
                'total_point': student_point.get_total_point()
            }
            four_lowest_student_points_data.append(student_data)
        
        return Response({'highest': four_highest_student_points_data, 'lowest': four_lowest_student_points_data})


# class KwlPointLadderView(APIView):
#     permission_classes = [IsAuthenticated]
#     @swagger_auto_schema(operation_description="Get 4 highest and 4 lowest total kwl scores of each student", responses={200: "OK", 400: "Bad Request"})
#     def get(self, request, topic):
#         try:
#             topic = Topic.objects.get(id=topic)
#             know = Know.objects.filter(topic=topic)
#             learned = Learned.objects.filter(topic=topic)
#             wtk = WantToKnow.objects.filter(topic=topic)
           
#             students_score = {
#                 [
#                     {'student': 'John Doe', 'know_score': 100, 'learned_score': 50, 'wtk_score': 75, 'total_score': 225}, 
#                 ],
#             }
         
#             if know.exists():
#                 know_type = know.first().type
#                 if know_type == 'reflection':
                    
#                     for student in topic.course.students.all():
#                         try:
#                             student_know_reflection = KnowReflectionStudentAnswer.objects.get(know_ref__know=know, student=student)
#                             student_know_score = student_know_reflection.know_ref.score
#                         except KnowReflectionStudentAnswer.DoesNotExist:
#                             student_know_score = 0

#                         students_score.append({'student': student.user.username, 'know_score': student_know_score, 'total_score': student_know_score})

#                 elif know_type == 'quiz':
#                     for student in topic.course.students.all():
#                         try:
#                             student_know_quiz = KnowQuizStudentAnswer.objects.get(answers__know_quiz__know=know, student=student)
#                             student_know_score = 0
#                             for answer in student_know_quiz.answers.all():
#                                 student_know_score += answer.know_quiz.score
#                             students_score.append({'student': student.user.username, 'know_score': student_know_score, 'total_score': student_know_score})
#                         except KnowQuizStudentAnswer.DoesNotExist:
#                             students_score.append({'student': student.user.username, 'know_score': 0, 'total_score': 0})
                        
#             if learned.exists():
#                 learned_type = learned.first().type
#                 if learned_type == 'reflection':
#                     for student in topic.course.students.all():
#                         try:
#                             student_learned_reflection = LearnedReflectionStudentAnswer.objects.get(learned_ref__learned=learned, student=student)
#                             student_learned_score = student_learned_reflection.learned_ref.score
#                         except LearnedReflectionStudentAnswer.DoesNotExist:
#                             student_learned_score = 0
#                         students_score.append({'student': student.user.username, 'learned_score': student_learned_score})
#                 elif learned_type == 'quiz':
#                     for student in topic.course.students.all():
#                         try:
#                             student_learned_quiz = LearnedQuizStudentAnswer.objects.get(answers__learned_quiz__learned=learned, student=student)
#                             student_learned_score = 0
#                             for answer in student_learned_quiz.answers.all():
#                                 student_learned_score += answer.learned_quiz.score
#                             students_score.append({'student': student.user.username, 'learned_score': student_learned_score})
#                         except LearnedQuizStudentAnswer.DoesNotExist:
#                             students_score.append({'student': student.user.username, 'learned_score': 0})

#             if wtk.exists():
#                 wtk_type = wtk.first().type
#                 if wtk_type == 'reflection':   
#                     for student in topic.course.students.all():
#                         try:
#                             student_wtk_reflection = WtkReflectionStudentAnswer.objects.get(wtk_ref__wtk=wtk, student=student)
#                             student_wtk_score = student_wtk_reflection.wtk_ref.score
#                         except WtkReflectionStudentAnswer.DoesNotExist:
#                             student_wtk_score = 0
#                         students_score.append({'student': student.user.username, 'wtk_score': student_wtk_score})
#                 elif wtk_type == 'poll':
#                     for student in topic.course.students.all():
#                         try:
#                             student_wtk_poll = WtkPollStudentAnswer.objects.get(answers__wtk_poll__wtk=wtk, student=student)
#                             student_wtk_score = 0
#                             for answer in student_wtk_poll.answers.all():
#                                 student_wtk_score += answer.wtk_poll.score
#                             students_score.append({'student': student.user.username, 'wtk_score': student_wtk_score})
#                         except WtkPollStudentAnswer.DoesNotExist:
#                             students_score.append({'student': student.user.username, 'wtk_score': 0})

                
#             students_score.sort(key=lambda x: x['total_score'])

#             lowest_scores = students_score[:4]

#             highest_scores = students_score[-4:]


#             return Response({'lowest_scores': lowest_scores, 'highest_scores': highest_scores}, status=status.HTTP_200_OK)
#         except Topic.DoesNotExist:
#             raise TopicNotFoundException()
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
            

        
class TopicPollingAnalysisView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_description="Get the polling data for the topic", responses={200: "OK", 400: "Bad Request"})
    def get(self, request, topic):
        poll_data = []
        topic = Topic.objects.get(id=topic)
        question = WtkPollQuestion.objects.get(wtk__topic=topic)
        choices = question.choices.all()
        for choice in choices:
            choice_data = {
                'choice': choice.option_answer,
                'total_votes': choice.total_votes
            }
            poll_data.append(choice_data)

        course_short_name = topic.course.short_name
        course_full_name = topic.course.full_name
        topic_name = topic.name
        poll_data.append({'course_full_name':course_full_name,'course_short_name': course_short_name, 'topic_name': topic_name})


        return Response(poll_data, status=status.HTTP_200_OK)
    
class QuizAccuracyAnalysisView(APIView):

    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(operation_description="Get the number of correct answers for each quiz question", responses={200: "OK", 400: "Bad Request"})
    def get(self, request, type, topic):
        topic = Topic.objects.get(id=topic)
        quiz_data = []
        if type == 'know':
            quiz_question = KnowQuizQuestion.objects.filter(know__topic=topic)
            for question in quiz_question:
                correct_answers = KnowQuizStudentAnswer.objects.filter(answers__know_quiz=question, answers__isCorrect=True).count()
                accuracy = (correct_answers / question.know.total_participants) * 100
                question_data = {
                    'question': question.question,
                    'accuracy': accuracy
                }
                quiz_data.append(question_data)
        elif type == 'learned':
            quiz_question = LearnedQuizQuestion.objects.filter(learned__topic=topic)
            for question in quiz_question:
                correct_answers = LearnedQuizStudentAnswer.objects.filter(answers__learned_quiz=question, answers__isCorrect=True).count()
                accuracy = (correct_answers / question.learned.total_participants) * 100
                question_data = {
                    'question': question.question,
                    'accuracy': accuracy
                }
                quiz_data.append(question_data)
        else:
            raise InvalidTypeException()
            

        return Response({'questions': quiz_data}, status=status.HTTP_200_OK)
       

class QuizBarchartImageView(APIView):

    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(operation_description="Get the image of the barchart for the quiz questions", responses={200: "OK", 400: "Bad Request"})
    def get(self, request, type, topic):
        topic = Topic.objects.get(id=topic)
        quiz_data = []
        if type == 'know':
            quiz_question = KnowQuizQuestion.objects.filter(know__topic=topic)
            for index, question in enumerate(quiz_question):
                correct_answers = KnowQuizStudentAnswer.objects.filter(answers__know_quiz=question, answers__isCorrect=True).count()
                incorrect_answers = question.know.total_participants - correct_answers
                question_data = {
                    'question': index+1,
                    'correct_answers': correct_answers,
                    'incorrect_answers': incorrect_answers
                }
                quiz_data.append(question_data)
        elif type == 'learned':
            quiz_question = LearnedQuizQuestion.objects.filter(learned__topic=topic)
            for question in quiz_question:
                correct_answers = LearnedQuizStudentAnswer.objects.filter(answers__learned_quiz=question, answers__isCorrect=True).count()
                incorrect_answers = question.learned.total_participants - correct_answers
                question_data = {
                    'question': index+1,
                    'correct_answers': correct_answers,
                    'incorrect_answers': incorrect_answers
                }
                quiz_data.append(question_data)
        else:
            raise InvalidTypeException()

        # Generate bar chart
        fig, ax = plt.subplots()
        questions = [data['question'] for data in quiz_data]
        correct_answers = [data['correct_answers'] for data in quiz_data]
        incorrect_answers = [data['incorrect_answers'] for data in quiz_data]
        ax.bar(range(len(questions)), correct_answers, label='Correct Answers')
        ax.bar(range(len(questions)), incorrect_answers, bottom=correct_answers, label='Incorrect Answers')

        # Set x-ticks and x-ticklabels
        ax.set_xticks(range(len(questions)))
        ax.set_xticklabels(questions)

        yticks = range(0, max(correct_answers + incorrect_answers) + 1)
        ax.set_yticks(yticks)
        ax.set_yticklabels([str(ytick) for ytick in yticks])


        ax.set_ylabel('Number of Answers')
        ax.set_title('Quiz Answers Bar Chart')
        ax.legend()

        # Save the plot to a file in the media root directory
        image_path = os.path.join(settings.MEDIA_ROOT, 'barchart.png')
        plt.savefig(image_path)

        # Create the URL to access the image
        image_url = os.path.join(settings.MEDIA_URL, 'barchart.png')

        return Response({'questions': quiz_data, 'barchart': image_url}, status=status.HTTP_200_OK)