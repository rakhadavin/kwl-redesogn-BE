from django.http import Http404
from django.shortcuts import render

from authentication.models import Student
from .serializers import AddLearnedEssaySerializer, LearnedReflectionSerializer
from .models import LearnedReflection, LearnedReflectionStudentAnswer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
# Create your views here.
# TEST WORD_CLOUD
class LearnedEssayView():

    def get_learned_essay_or_404(self, know_ref_id):
        try:
            return LearnedReflection.objects.get(id=know_ref_id)
        except LearnedReflection.DoesNotExist:
            raise Http404
        
    @api_view(['POST'])
    def add_learned_essay(self,request):
        serializer = AddLearnedEssaySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Reflection question added successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
   
    @api_view(['GET'])
    def get_learned_essay(self,request, know_id ):
        
        serializer = LearnedReflectionSerializer(LearnedReflection.objects.filter(know_id=know_id), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
            
    @api_view(['POST'])
    @permission_classes([IsAuthenticated]) 
    def save_essay_answer(self,request, know_ref_id):
        try:
            user = request.user

            reflection = request.data['reflection']

            know_essay = self.get_know_essay_or_404(know_ref_id)
            student = Student.objects.get(user_id=user.id)
            history, created = LearnedReflectionStudentAnswer.objects.get_or_create(student_id=student, know_ref_id=know_essay)
            history.score = know_essay.score
            history.reflection = reflection
    
            history.save()

            return Response({"message": "Reflection answer saved successfully"}, status=status.HTTP_201_CREATED)
        except Http404:
            return Response({"error": "Reflection question not found"}, status=status.HTTP_404_NOT_FOUND)