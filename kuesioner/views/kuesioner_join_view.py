from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status

from ..models import Kuesioner, GuestQuizAttempt, KuesionerSession
from ..serializers.kuesioner_serializers import (
    GuestJoinKuesionerSerializer,
    GuestKuesionerAttemptSerializer,
    UpdateGuestNameSerializer
)

@api_view(['POST'])
@permission_classes([AllowAny])
def kuesioner_join(request, kuesioner_id):
    """
    API untuk guest join kuesioner
    """
    kuesioner = get_object_or_404(Kuesioner, id=kuesioner_id)
    
    # Check if kuesioner exists and is accessible
    if not kuesioner.is_lobby:
        return Response({
            'message': 'Kuesioner is not available for joining',
            'error': 'Kuesioner lobby is not open'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if kuesioner.is_started:
        return Response({
            'message': 'Kuesioner has already started',
            'error': 'Cannot join kuesioner after it has started'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if kuesioner.if_finished:
        return Response({
            'message': 'Kuesioner has finished',
            'error': 'Cannot join finished kuesioner'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate input data
    serializer = GuestJoinKuesionerSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({
            'message': 'Invalid data',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    guest_name = serializer.validated_data['guest_name']
    
    # Get current active session
    active_session = KuesionerSession.objects.filter(
        kuesioner=kuesioner,
        is_active=True
    ).order_by('-started_at').first()
    
    if not active_session:
        return Response({
            'message': 'No active session',
            'error': 'No active session found for this kuesioner'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if name is already taken in current session
    existing_guest = GuestQuizAttempt.objects.filter(
        session=active_session,
        guest_name=guest_name
    ).first()
    
    if existing_guest:
        return Response({
            'message': 'Name already taken',
            'error': f'The name "{guest_name}" is already used by another participant in this session'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Create guest kuesioner attempt with provided name and link to session
    guest_attempt = GuestQuizAttempt.objects.create(
        kuesioner=kuesioner,
        session=active_session,
        guest_name=guest_name
    )
    
    # Update session participant count
    active_session.total_participants = GuestQuizAttempt.objects.filter(
        session=active_session
    ).count()
    active_session.save()
    
    response_serializer = GuestKuesionerAttemptSerializer(guest_attempt)
    
    return Response({
        'message': 'Successfully joined kuesioner',
        'data': response_serializer.data,
        'kuesioner_info': {
            'title': kuesioner.title,
            'description': kuesioner.description,
            'pin': kuesioner.pin,
            'question_type': kuesioner.question_type
        },
        'session_info': {
            'session_id': str(active_session.id),
            'session_number': active_session.session_number,
            'total_participants': active_session.total_participants
        }
    }, status=status.HTTP_201_CREATED)

@api_view(['PUT'])
@permission_classes([AllowAny])
def update_guest_name(request, attempt_id):
    """
    API untuk update guest name
    """
    guest_attempt = get_object_or_404(GuestQuizAttempt, id=attempt_id)
    
    if guest_attempt.kuesioner.is_started:
        return Response({
            'message': 'Cannot update name',
            'error': 'Kuesioner has already started'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if guest_attempt.kuesioner.if_finished:
        return Response({
            'message': 'Cannot update name',
            'error': 'Kuesioner has finished'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = UpdateGuestNameSerializer(data=request.data)
    if serializer.is_valid():
        guest_name = serializer.validated_data['guest_name']
        
        # Check if name is already taken by another participant in the same session
        existing_guest = GuestQuizAttempt.objects.filter(
            session=guest_attempt.session,
            guest_name=guest_name
        ).exclude(id=guest_attempt.id).first()
        
        if existing_guest:
            return Response({
                'message': 'Name already taken',
                'error': f'The name "{guest_name}" is already used by another participant'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        guest_attempt.guest_name = guest_name
        guest_attempt.save()
        
        response_serializer = GuestKuesionerAttemptSerializer(guest_attempt)
        return Response({
            'message': 'Guest name updated successfully',
            'data': response_serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response({
        'message': 'Failed to update guest name',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def get_kuesioner_by_pin(request, pin):
    """
    GET: API untuk mendapatkan kuesioner berdasarkan PIN
    POST: API untuk join kuesioner berdasarkan PIN dengan guest_name
    """
    try:
        kuesioner = Kuesioner.objects.get(pin=pin, is_lobby=True)
    except Kuesioner.DoesNotExist:
        return Response({
            'message': 'Kuesioner not found',
            'error': f'No kuesioner found with PIN: {pin}'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        return Response({
            'message': 'Kuesioner found',
            'data': {
                'id': kuesioner.id,
                'title': kuesioner.title,
                'description': kuesioner.description,
                'pin': kuesioner.pin,
                'question_type': kuesioner.question_type,
                'is_lobby': kuesioner.is_lobby,
                'is_started': kuesioner.is_started,
                'if_finished': kuesioner.if_finished,
                'join_url': f'/kuesioner/{kuesioner.id}/join'
            }
        }, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        # Check kuesioner status
        if kuesioner.is_started:
            return Response({
                'message': 'Kuesioner has already started',
                'error': 'Cannot join kuesioner after it has started'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if kuesioner.if_finished:
            return Response({
                'message': 'Kuesioner has finished',
                'error': 'Cannot join finished kuesioner'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate input data
        serializer = GuestJoinKuesionerSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'message': 'Invalid data',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
    guest_name = serializer.validated_data['guest_name']
    
    # Get current active session
    active_session = KuesionerSession.objects.filter(
        kuesioner=kuesioner,
        is_active=True
    ).order_by('-started_at').first()
    
    if not active_session:
        return Response({
            'message': 'No active session',
            'error': 'No active session found for this kuesioner'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if name is already taken in current session
    existing_guest = GuestQuizAttempt.objects.filter(
        session=active_session,
        guest_name=guest_name
    ).first()
    
    if existing_guest:
        return Response({
            'message': 'Name already taken',
            'error': f'The name "{guest_name}" is already used by another participant in this session'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Create guest kuesioner attempt with provided name and link to session
    guest_attempt = GuestQuizAttempt.objects.create(
        kuesioner=kuesioner,
        session=active_session,
        guest_name=guest_name
    )
    
    # Update session participant count
    active_session.total_participants = GuestQuizAttempt.objects.filter(
        session=active_session
    ).count()
    active_session.save()
    
    return Response({
            'message': 'Successfully joined kuesioner',
            'data': {
                'id': str(guest_attempt.id),
                'guest_name': guest_attempt.guest_name,
                'kuesioner_id': str(kuesioner.id),
                'kuesioner_title': kuesioner.title,
                'kuesioner_description': kuesioner.description,
                'question_type': kuesioner.question_type,
                'pin': kuesioner.pin,
                'session_id': str(active_session.id),
                'session_number': active_session.session_number
            }
        }, status=status.HTTP_201_CREATED)