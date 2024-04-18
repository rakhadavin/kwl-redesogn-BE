
from django.http import Http404
from django.shortcuts import render

from authentication.models import Student
from know.models import KnowQuizQuestion, KnowQuizStudentAnswer, KnowReflectionStudentAnswer
from .serializers import AddKnowQuizQuestionSerializer, KnowQuizOptionsSerializer, KnowQuizQuestionSerializer, AddKnowEssaySerializer, KnowReflectionSerializer, EditKnowQuizQuestionSerializer, EditKnowEssaySerializer, KnowSerializer
from rest_framework import status

from .models import Know, KnowQuizQuestion, KnowReflection
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response



def get_know_quiz_question_or_404_by_quiz_id(question_id):
        try:
            return KnowQuizQuestion.objects.get(id=question_id)
        except KnowQuizQuestion.DoesNotExist:
            raise Http404
        
def get_know_essay_or_404_by_ref_id(know_ref_id):
        try:
            return KnowReflection.objects.get(id=know_ref_id)
        except KnowReflection.DoesNotExist:
            raise Http404
        
def get_know_essay_or_404_by_know_id(know_id):
        try:
            return KnowReflection.objects.get(know__id=know_id)
        except KnowReflection.DoesNotExist:
            raise Http404
        
@api_view(['GET'])
def get_know_by_topic_id(request, topic_id):
    know = Know.objects.filter(topic_id=topic_id).first()
    serializer = KnowSerializer(know)
    return Response({"data": serializer.data}, status=status.HTTP_200_OK)


class KnowQuizView():
        
    @api_view(['POST'])
    def add_know_quiz(request):
        serializer = AddKnowQuizQuestionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Quiz added successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        else:
             return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
    @api_view(['PUT'])
    def edit_know_quiz(request, quiz_id):
        try:
            quiz = get_know_quiz_question_or_404_by_quiz_id(quiz_id)
            serializer = EditKnowQuizQuestionSerializer(quiz, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Quiz updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Http404:
            return Response({"error": "Quiz question not found"}, status=status.HTTP_404_NOT_FOUND)
   
    @api_view(['GET'])
    def get_question_by_quiz_id(request, quiz_id):
        try:
            know_quiz = get_know_quiz_question_or_404_by_quiz_id(quiz_id)
        
            question_serializer = KnowQuizQuestionSerializer(know_quiz)
            options = know_quiz.get_answers()
            option_serializer = KnowQuizOptionsSerializer(options, many=True)
    
            return Response({"question":question_serializer.data,"options":option_serializer.data}, status=status.HTTP_200_OK)
        except Http404:
            return Response({"error": "Quiz question not found"}, status=status.HTTP_404_NOT_FOUND)
        
    @api_view(['GET'])
    def get_all_questions_by_know_id(request, know_id):
        questions = KnowQuizQuestion.objects.filter(know_id=know_id)
        questions_data = []
        for question in questions:
            question_data = {
                "question": KnowQuizQuestionSerializer(question).data,
                "options": KnowQuizOptionsSerializer(question.get_answers(), many=True).data,
                "correct_answer": question.get_answers().get(isCorrect=True).option_answer
            }
            questions_data.append(question_data)
        return Response({"questions": questions_data}, status=status.HTTP_200_OK)
    
    @api_view(['POST'])
    @permission_classes([IsAuthenticated])
    def save_student_all_answers_by_know_id(request, know_id):
        user_id = request.user
        student = Student.objects.get(user_id=user_id)
        answers = request.data['answers']
        questions = KnowQuizQuestion.objects.filter(know_id=know_id)
        student_answers = []
        for answer in answers:
            id = answer['know_quiz_id']
            question = questions.get(id=id)
            correct_option = question.get_answers().get(isCorrect=True)
            history, created = KnowQuizStudentAnswer.objects.get_or_create(know_quiz_question_id=question, student_id=student)
            if correct_option.option_answer == answer['answer']:
                score = question.score
                history.score = score
            else:
                history.score = 0
            history.answer = answer['answer']
            history.save()

            question = KnowQuizQuestionSerializer(question).data
            student_answers.append({"question": question, "answer": answer['answer'], "score": history.score})
 

        return Response({"message": "Answers saved successfully", "data": student_answers}, status=status.HTTP_201_CREATED)
        
    
    @api_view(['POST'])
    @permission_classes([IsAuthenticated])
    def save_student_answer(request,know_quiz_id):
        try:
            user_id = request.user
            student = Student.objects.get(user_id=user_id)
            answer = request.data['answer']
            know_quiz = get_know_quiz_question_or_404_by_quiz_id(know_quiz_id)
            correct_option = know_quiz.get_answers().get(isCorrect=True)

            history, created = KnowQuizStudentAnswer.objects.get_or_create(know_quiz_question_id=know_quiz, student_id=student)
            history.answer = answer
            if correct_option.option_answer == answer:
                score = know_quiz.score 
                history.score = score
                history.save()
            else: 
                history.score = 0
                history.save()
            return Response({"message": "Answer saved successfully"}, status=status.HTTP_201_CREATED)
        except Http404:
            return Response({"error": "Quiz question not found"}, status=status.HTTP_404_NOT_FOUND)
        
    @api_view(['GET'])
    def get_student_answers_by_student_id(request, student_id):
        student_answers = KnowQuizStudentAnswer.objects.filter(student_id=student_id)
        return Response({"data": student_answers}, status=status.HTTP_200_OK)
    
class KnowEssayView():


    @api_view(['POST'])
    def add_know_essay(request):
        serializer = AddKnowEssaySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Reflection question added successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
   
    @api_view(['GET'])
    def get_know_essay_by_know_id(request, know_id ):
        try:
            essay = get_know_essay_or_404_by_know_id(know_id)
            serializer = KnowReflectionSerializer(essay)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Http404:
            return Response({"error": "Reflection question not found"}, status=status.HTTP_404_NOT_FOUND)
    
    @api_view(['PUT'])
    def edit_know_essay_by_ref_id(request, ref_id):
        try:
            know_ref = get_know_essay_or_404_by_ref_id(ref_id)
            serializer = EditKnowEssaySerializer(know_ref, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Reflection question updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Http404:
            return Response({"error": "Reflection question not found"}, status=status.HTTP_404_NOT_FOUND)


            
    @api_view(['POST'])
    @permission_classes([IsAuthenticated]) 
    def save_essay_answer(request, know_ref_id):
        try:
            user = request.user

            reflection = request.data['reflection']

            know_essay = get_know_essay_or_404_by_ref_id(know_ref_id)
            student = Student.objects.get(user_id=user.id)
            history, created = KnowReflectionStudentAnswer.objects.get_or_create(student_id=student, know_ref_id=know_essay)
            history.score = know_essay.score
            history.reflection = reflection
    
            history.save()

            return Response({"message": "Reflection answer saved successfully"}, status=status.HTTP_201_CREATED)
        except Http404:
            return Response({"error": "Reflection question not found"}, status=status.HTTP_404_NOT_FOUND)