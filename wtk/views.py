
import os
from django.conf import settings

from authentication.models import Student
from .models import Prereading, WtkPollQuestion, WantToKnow, WtkStudentAnswer, WtkChoices, WtkReflection, WtkReflectionStudentAnswer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .serializers import AddPollingQuestionSerializer, EditWtkEssaySerializer, WtkPollingQuestionSerializer, WtkPollingAnswerSerializer, AddWtkEssaySerializer, WtkReflectionSerializer, AddPrereadingSerializer, EditPrereadingSerializer, PrereadingSerializer, EditPollingQuestionSerializer
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.http import Http404
# Create your views here.

@api_view(['POST'])
def add_prereading(request):
    serializer = AddPrereadingSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Prereading added successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
    return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def edit_prereading(request):
    try:
        prereading = Prereading.objects.get(id=request.data['id'])
        serializer = EditPrereadingSerializer(prereading, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Prereading updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    except Prereading.DoesNotExist:
        return Response({"error": "Prereading not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_prereading_by_wtk_id(request):
    try:
        wtk_id = request.data['wtk_id']
        prereading = Prereading.objects.get(wtk_id=wtk_id)
        serializer = PrereadingSerializer(prereading)
    except Prereading.DoesNotExist:
        return Response({"error": "Prereading not found"}, status=status.HTTP_404_NOT_FOUND)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def is_wtk_exist_by_topic_id(request, topic_id):
    wtk = WantToKnow.objects.filter(topic_id=topic_id).first()
    if wtk:
        return Response({"data": True}, status=status.HTTP_200_OK)
    return Response({"data": False}, status=status.HTTP_200_OK)

def get_wtk_question_or_404(question_id):
    try:
        return WtkPollQuestion.objects.get(id=question_id)
    except WtkPollQuestion.DoesNotExist:
        raise Http404

class PollingView():
    
    @api_view(['POST'])
    def add_polling_question(request):
        serializer = AddPollingQuestionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Polling question added successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    @api_view(['PUT'])
    def edit_polling_question(request):
        try:
            question = get_wtk_question_or_404(request.data['id'])
            serializer = EditPollingQuestionSerializer(question, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Polling question updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Http404:
            return Response({"error": "Polling question not found"}, status=status.HTTP_404_NOT_FOUND)

    @api_view(['GET'])
    def get_polling_question(request, question_id):
        try:
            question = get_wtk_question_or_404(question_id)
            question_serializer = WtkPollingQuestionSerializer(question)
            answer_serializer = WtkPollingAnswerSerializer( question.choices.all(), many=True)
            poll = {"question": question_serializer.data, "options": answer_serializer.data}
            return Response(poll, status=status.HTTP_200_OK)
        except Http404:
            return Response({"error": "Polling question not found"}, status=status.HTTP_404_NOT_FOUND)

        
    @api_view(['POST'])
    @permission_classes([IsAuthenticated])
    def vote_multiple_choice(request):
        try:
            user_id = request.user
            student = Student.objects.get(user_id=user_id)
            question_id = request.data['question_id']
            choices = request.data['choices_ids']
            if not choices and not question_id:
                return Response({"error": "Question id and choices ids are required"}, status=status.HTTP_400_BAD_REQUEST)
            question = get_wtk_question_or_404(question_id)
            student_answer, created = WtkStudentAnswer.objects.get_or_create(wtk_poll_question_id=question, student_id=student, score=question.score)
            for choice_id in choices:
                try:
                    choice = WtkChoices.objects.get(id=choice_id)
                    student_answer.choices.add(choice)
                except WtkChoices.DoesNotExist:
                    return Response({"error": f"Choice with id {choice_id} does not exist"}, status=status.HTTP_400_BAD_REQUEST)
            student_answer.save()
            return Response({"message": "Voted successfully"}, status=status.HTTP_201_CREATED)
        except Http404:
            return Response({"error": "Polling question not found"}, status=status.HTTP_404_NOT_FOUND)
        
    @api_view(['GET'])
    def count_votes(request, question_id):
        try:
            question = get_wtk_question_or_404(question_id)
            choices = question.choices.all()
            student_answers = WtkStudentAnswer.objects.filter(wtk_poll_question_id=question)
            votes = {}
            for student_answer in student_answers:
                for choice in choices:
                    if choice in student_answer.choices.all():
                        if choice.option_answer in votes:
                            votes[choice.option_answer] += 1
                        else:
                            votes[choice.option_answer] = 1
                    else:
                        if choice.option_answer not in votes:
                            votes[choice.option_answer] = 0
            return Response({"votes": votes}, status=status.HTTP_200_OK)
        except Http404:
            return Response({"error": "Polling question not found"}, status=status.HTTP_404_NOT_FOUND)


def get_wtk_essay_or_404(know_ref_id):
    try:
        return WtkReflection.objects.get(id=know_ref_id)
    except WtkReflection.DoesNotExist:
        raise Http404
    
class WtkEssayView():

    @api_view(['POST'])
    def add_wtk_essay(request):
        serializer = AddWtkEssaySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Reflection question added successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    @api_view(['PUT'])
    def edit_wtk_essay(request, ref_id):
        try:
            essay = get_wtk_essay_or_404(ref_id)
            serializer = EditWtkEssaySerializer(essay, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Reflection question updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Http404:
            return Response({"error": "Reflection question not found"}, status=status.HTTP_404_NOT_FOUND)
   
    @api_view(['GET'])
    def get_wtk_essay(request, know_id ):
        try:
            essay = get_wtk_essay_or_404(know_id)
            serializer = WtkReflectionSerializer(essay)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Http404:
            return Response({"error": "Reflection question not found"}, status=status.HTTP_404_NOT_FOUND)
            
    @api_view(['POST'])
    @permission_classes([IsAuthenticated]) 
    def save_essay_answer(request, know_ref_id):
        try:
            user = request.user

            reflection = request.data['reflection']

            know_essay = get_wtk_essay_or_404(know_ref_id)
            student = Student.objects.get(user_id=user.id)
            history, created = WtkReflectionStudentAnswer.objects.get_or_create(student_id=student, know_ref_id=know_essay)
            history.score = know_essay.score
            history.reflection = reflection
    
            history.save()

            return Response({"message": "Reflection answer saved successfully"}, status=status.HTTP_201_CREATED)
        except Http404:
            return Response({"error": "Reflection question not found"}, status=status.HTTP_404_NOT_FOUND)