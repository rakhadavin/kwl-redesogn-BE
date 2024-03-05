from django.shortcuts import render
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
# Create your views here.
class CourseView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
            content = {
                'status': 'request was permitted'
            }
            return Response(content)