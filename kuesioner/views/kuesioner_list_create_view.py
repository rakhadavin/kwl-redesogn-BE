from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render
from ..serializers.kuesioner_serializers import (
    KuesionerListSerializer, 
    KuesionerCreateSerializer, 
    KuesionerDetailSerializer
)
from rest_framework.response import Response
from rest_framework import status
from ..models import Kuesioner


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def kuesioner_list_create(request):
    if request.method == 'GET':
        kuesioner = Kuesioner.objects.filter(
            lecturer_team__in=[request.user.lecturer_profile]
        ).order_by('-created_at')
        serializer = KuesionerListSerializer(kuesioner, many=True)

        return Response({
            'message': 'Kuesioner retrieved successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        # KuesionerCreateSerializer sekarang sudah handle questions!
        serializer = KuesionerCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            kuesioner = serializer.save()

            # Add lecturer to team
            if hasattr(request.user, 'lecturer_profile'):
                kuesioner.lecturer_team.add(request.user.lecturer_profile)
            else:
                kuesioner.delete()
                return Response({
                    'message': 'Failed to create kuesioner',
                    'error': 'Only lecturers can create kuesioner'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Return detail response
            detail_serializer = KuesionerDetailSerializer(kuesioner)
            return Response({
                'message': 'Kuesioner created successfully',
                'data': detail_serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'message': 'Failed to create kuesioner',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)