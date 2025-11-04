from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status

from ..models import Kuesioner
from ..serializers.kuesioner_serializers import (
    KuesionerDetailSerializer, 
    KuesionerCreateSerializer,
    KuesionerUpdateSerializer
)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def kuesioner_detail(request, kuesioner_id):
    kuesioner = get_object_or_404(Kuesioner, id=kuesioner_id)

    if request.method in ['PUT', 'DELETE']:
        if not hasattr(request.user, 'lecturer_profile'):
            return Response({
                'message': 'Permission denied',
                'error': 'Only lecturers can modify kuesioner'
            }, status=status.HTTP_403_FORBIDDEN)
        
        lecturer = request.user.lecturer_profile
        if not kuesioner.lecturer_team.filter(id=lecturer.id).exists():
            return Response({
                'message': 'Permission denied',
                'error': 'You are not authorized to modify this kuesioner'
            }, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        serializer = KuesionerDetailSerializer(kuesioner)
        return Response({
            'message': 'Kuesioner retrieved successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        serializer = KuesionerUpdateSerializer(kuesioner, data=request.data, partial=True)
        
        if serializer.is_valid():
            kuesioner = serializer.save()
            detail_serializer = KuesionerDetailSerializer(kuesioner)
            
            return Response({
                'message': 'Kuesioner updated successfully',
                'data': detail_serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response({
            'message': 'Failed to update kuesioner',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        kuesioner.delete()
        return Response({
            'message': 'Kuesioner deleted successfully'
        }, status=status.HTTP_200_OK)