from django.http import Http404
from django.shortcuts import render

from authentication.models import Student
from .serializers import AddLearnedEssaySerializer, EditLearnedEssaySerializer, LearnedReflectionSerializer, AddLearnedQuizQuestionSerializer, EditLearnedQuizQuestionSerializer, LearnedQuizQuestionSerializer 
from .models import Learned, LearnedReflection, LearnedReflectionStudentAnswer, LearnedQuizQuestion, LearnedQuizStudentAnswer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from course.models import RewardStudentPoint

#additional functions
def get_learned_essay_or_404_by_ref_id(learned_ref_id):
        try:
            return LearnedReflection.objects.get(id=learned_ref_id)
        except LearnedReflection.DoesNotExist:
            raise Http404
def get_learned_essay_or_404_by_learned_id(learned_id):
        try:
            return LearnedReflection.objects.get(learned=learned_id)
        except LearnedReflection.DoesNotExist:
            raise Http404

def get_learned_quiz_or_404_by_ref_id(learned_ref_id):
        try:
            return LearnedQuizQuestion.objects.get(id=learned_ref_id)
        except LearnedQuizQuestion.DoesNotExist:
            raise Http404
        
def get_learned_quiz_or_404_by_learned_id(learned_id):
        try:
            return LearnedQuizQuestion.objects.get(learned=learned_id)
        except LearnedQuizQuestion.DoesNotExist:
            raise Http404

@api_view(['GET'])      
def get_learned_by_topic_id(request, topic_id):
        try:
            return Learned.objects.get(topic=topic_id)
        except Learned.DoesNotExist:
            raise Http404
        
@api_view(['GET'])
def is_learned_exist_by_topic_id(request, topic_id):
    learned = Learned.objects.filter(topic_id=topic_id).first()
    if learned:
        return Response({"data": True}, status=status.HTTP_200_OK)
    return Response({"data": False}, status=status.HTTP_200_OK)

@api_view(['DELETE'])
def delete_learned_by_topic_id(request, topic_id):
    try:
        learned = Learned.objects.get(topic_id=topic_id)
        learned.delete()
        return Response({"message": "Learned deleted successfully"}, status=status.HTTP_200_OK)
    except Learned.DoesNotExist:
        return Response({"error": "Learned not found"}, status=status.HTTP_404_NOT_FOUND)

class LearnedQuizView():
    
        @api_view(['POST'])
        def add_learned_quiz(request):
            serializer = AddLearnedQuizQuestionSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Quiz added successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        @api_view(['GET'])
        def get_learned_quiz(request, learned_id):
            try:
                quiz = get_learned_quiz_or_404_by_learned_id(learned_id)
                serializer = LearnedQuizQuestionSerializer(quiz)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Http404:
                return Response({"error": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)
            
        def get_all_learned_quiz(request, know_id):
            try:
                quiz = get_learned_quiz_or_404_by_ref_id(know_id)
                serializer = LearnedQuizQuestionSerializer(quiz)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Http404:
                return Response({"error": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)
        
        @api_view(['PUT'])
        def edit_learned_quiz(request, learned_id):
            try:
                quiz = get_learned_quiz_or_404_by_learned_id(learned_id)
                serializer = EditLearnedQuizQuestionSerializer(quiz, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response({"message": "Quiz updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
                return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            except Http404:
                return Response({"error": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)
                
        @api_view(['POST'])
        @permission_classes([IsAuthenticated]) 
        def save_quiz_answer(request, learned_quiz_id):
            try:
                user = request.user
                answer = request.data['answer']
                learned_quiz = get_learned_quiz_or_404_by_ref_id(learned_quiz_id)
                student = Student.objects.get(user_id=user.id)
                history, created = LearnedQuizStudentAnswer.objects.get_or_create(student_id=student, learned_ref_id=learned_quiz)
                history.score = learned_quiz.score
                history.answer = answer
                
                correct_option = learned_quiz.get_answers().get(isCorrect=True)
                if answer == correct_option.option_answer:
                    history.score = history.score + learned_quiz.score
                else:
                    history.score = 0

                history.save()
    
                return Response({"message": "Quiz answer saved successfully"}, status=status.HTTP_201_CREATED)
            except Http404:
                return Response({"error": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)

        def save_all_answers_by_know_id(request, know_id):
            try:
                user = request.user
                student = Student.objects.get(user_id=user.id)
                quiz = get_learned_quiz_or_404_by_ref_id(know_id)
                answers = request.data['answers']
                for answer in answers:
                    history, created = LearnedQuizStudentAnswer.objects.get_or_create(student_id=student, learned_ref_id=quiz)
                    history.score = quiz.score
                    history.answer = answer
                    correct_option = quiz.get_answers().get(isCorrect=True)
                    if answer == correct_option.option_answer:
                        history.score = history.score + quiz.score
                    else:
                        history.score = 0
                    history.save()
                return Response({"message": "Quiz answers saved successfully"}, status=status.HTTP_201_CREATED)
            except Http404:
                return Response({"error": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)


class LearnedEssayView():

    @api_view(['POST'])
    def add_learned_essay(request):
        serializer = AddLearnedEssaySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Reflection question added successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
   
    @api_view(['GET'])
    def get_learned_essay(request, learned_id):
        try:
            essay = get_learned_essay_or_404_by_learned_id(learned_id)
            serializer = LearnedReflectionSerializer(essay)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Http404:
            return Response({"error": "Reflection question not found"}, status=status.HTTP_404_NOT_FOUND)
    
    @api_view(['PUT'])
    def edit_learned_essay(request, learned_id):
        try:
            essay = get_learned_essay_or_404_by_learned_id(learned_id)
            serializer = EditLearnedEssaySerializer(essay, data=request.data)
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
            course_id = request.data['course_id']
            know_essay = get_learned_essay_or_404_by_ref_id(know_ref_id)
            student = Student.objects.get(user_id=user.id)
            history, created = LearnedReflectionStudentAnswer.objects.get_or_create(student_id=student, know_ref_id=know_essay)
            reward_point, created = RewardStudentPoint.objects.get_or_create(student_id=student, course_id=course_id)
            history.reflection = reflection
    
            history.save()

            return Response({"message": "Reflection answer saved successfully"}, status=status.HTTP_201_CREATED)
        except Http404:
            return Response({"error": "Reflection question not found"}, status=status.HTTP_404_NOT_FOUND)