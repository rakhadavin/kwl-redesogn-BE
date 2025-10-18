from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Quiz, GuestQuizAttempt
from .serializers import (
    QuizListSerializer, QuizCreateSerializer, QuizDetailSerializer, 
    QuizUpdateSerializer, GuestQuizAttemptSerializer, GuestJoinQuizSerializer,
    UpdateGuestNameSerializer
)
from rest_framework import status

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def quiz_list_create(request):
    if request.method == 'GET':
      quizzes = Quiz.objects.filter(lecturer_team__in=[request.user.lecturer_profile]).order_by('-created_at')
      serializer = QuizListSerializer(quizzes, many=True)
      
      return Response({
          'message': 'Quizzes retrieved successfully',
          'data': serializer.data
      }, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        serializer = QuizCreateSerializer(data=request.data)
        if serializer.is_valid():
          quiz = serializer.save()

          if hasattr(request.user, 'lecturer_profile'):
              quiz.lecturer_team.add(request.user.lecturer_profile)
          else:
              quiz.delete()
              return Response({
                  'message': 'Failed to create quiz',
                  'error': 'Only lecturers can create quizzes'
              }, status=status.HTTP_403_FORBIDDEN)
          
          detail_serializer = QuizDetailSerializer(quiz)
          return Response({
                'message': 'Quiz created successfully',
                'data': detail_serializer.data
            }, status=status.HTTP_201_CREATED)
       
        return Response({
            'message': 'Failed to create quiz',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if request.method in ['PUT', 'DELETE']:
        if not hasattr(request.user, 'lecturer_profile'):
            return Response({
                'message': 'Permission denied',
                'error': 'Only lecturers can modify quizzes'
            }, status=status.HTTP_403_FORBIDDEN)
        
        lecturer = request.user.lecturer_profile
        if not quiz.lecturer_team.filter(id=lecturer.id).exists():
            return Response({
                'message': 'Permission denied',
                'error': 'You are not authorized to modify this quiz'
            }, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        serializer = QuizDetailSerializer(quiz)
        return Response({
            'message': 'Quiz retrieved successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        serializer = QuizCreateSerializer(quiz, data=request.data, partial=True)
        
        if serializer.is_valid():
            quiz = serializer.save()
            detail_serializer = QuizDetailSerializer(quiz)
            
            return Response({
                'message': 'Quiz updated successfully',
                'data': detail_serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response({
            'message': 'Failed to update quiz',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        quiz.delete()
        return Response({
            'message': 'Quiz deleted successfully'
        }, status=status.HTTP_200_OK)
    
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_quiz_questions(request, quiz_id):
    """
    Update quiz questions
    """
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Check if user has permission (is in lecturer_team)
    if not hasattr(request.user, 'lecturer_profile'):
        return Response({
            'message': 'Permission denied',
            'error': 'Only lecturers can modify quiz questions'
        }, status=status.HTTP_403_FORBIDDEN)
    
    lecturer = request.user.lecturer_profile
    if not quiz.lecturer_team.filter(id=lecturer.id).exists():
        return Response({
            'message': 'Permission denied',
            'error': 'You are not authorized to modify this quiz'
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = QuizUpdateSerializer(quiz, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        
        # Return updated quiz data
        quiz_serializer = QuizDetailSerializer(quiz)
        return Response({
            'message': 'Quiz questions updated successfully',
            'data': quiz_serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response({
        'message': 'Failed to update quiz questions',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def join_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Check if quiz exists and is accessible
    if not quiz.is_lobby:
        return Response({
            'message': 'Quiz is not available for joining',
            'error': 'Quiz lobby is not open'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if quiz.is_started:
        return Response({
            'message': 'Quiz has already started',
            'error': 'Cannot join quiz after it has started'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if quiz.if_finished:
        return Response({
            'message': 'Quiz has finished',
            'error': 'Cannot join finished quiz'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate input data
    serializer = GuestJoinQuizSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({
            'message': 'Invalid data',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    guest_name = serializer.validated_data['guest_name']
    
    # Check if name is already taken in this quiz
    existing_guest = GuestQuizAttempt.objects.filter(
        quiz=quiz,
        guest_name=guest_name
    ).first()
    
    if existing_guest:
        return Response({
            'message': 'Name already taken',
            'error': f'The name "{guest_name}" is already used by another participant'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Create guest quiz attempt with provided name
    guest_attempt = GuestQuizAttempt.objects.create(
        quiz=quiz,
        guest_name=guest_name
    )
    
    response_serializer = GuestQuizAttemptSerializer(guest_attempt)
    
    return Response({
        'message': 'Successfully joined quiz',
        'data': response_serializer.data,
        'quiz_info': {
            'title': quiz.title,
            'description': quiz.description,
            'quiz_pin': quiz.quiz_pin
        }
    }, status=status.HTTP_201_CREATED)

@api_view(['PUT'])
@permission_classes([AllowAny])
def update_guest_name(request, attempt_id):
    guest_attempt = get_object_or_404(GuestQuizAttempt, id=attempt_id)
    if guest_attempt.quiz.is_started:
        return Response({
            'message': 'Cannot update name',
            'error': 'Quiz has already started'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if guest_attempt.quiz.if_finished:
        return Response({
            'message': 'Cannot update name',
            'error': 'Quiz has finished'
        }, status=status.HTTP_400_BAD_REQUEST)
    serializer = UpdateGuestNameSerializer(data=request.data)
    if serializer.is_valid():
        guest_name = serializer.validated_data['guest_name']
        existing_guest = GuestQuizAttempt.objects.filter(
            quiz=guest_attempt.quiz,
            guest_name=guest_name
        ).exclude(id=guest_attempt.id).first()
        
        if existing_guest:
            return Response({
                'message': 'Name already taken',
                'error': f'The name "{guest_name}" is already used by another participant'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        guest_attempt.guest_name = guest_name
        guest_attempt.save()
        response_serializer = GuestQuizAttemptSerializer(guest_attempt)
        return Response({
            'message': 'Guest name updated successfully',
            'data': response_serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response({
        'message': 'Failed to update guest name',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_quiz_by_pin(request, quiz_pin):
    try:
        quiz = Quiz.objects.get(quiz_pin=quiz_pin, is_lobby=True)
    except Quiz.DoesNotExist:
        return Response({
            'message': 'Quiz not found',
            'error': f'No quiz found with PIN: {quiz_pin}'
        }, status=status.HTTP_404_NOT_FOUND)
    
    return Response({
        'message': 'Quiz found',
        'data': {
            'id': quiz.id,
            'title': quiz.title,
            'description': quiz.description,
            'quiz_pin': quiz.quiz_pin,
            'is_lobby': quiz.is_lobby,
            'is_started': quiz.is_started,
            'if_finished': quiz.if_finished,
            'join_url': f'/quiz/{quiz.id}/join'
        }
    }, status=status.HTTP_200_OK)