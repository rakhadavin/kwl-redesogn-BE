from django.db import DatabaseError
from django.http import Http404
from rest_framework import status

from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from .serializers import LoginSerializer, StudentSerializer
from .models import KwlUser, Student

from authentication.utils import sso_login, get_tokens_for_user
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt


class LoginView(APIView):
    permission_classes = (AllowAny,)
    @csrf_exempt
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            # Check if user exists in the database
            user = KwlUser.objects.filter(username=username).first()

            if user is None:
                # If user doesn't exist in the database, try SSO login
                sso_response = sso_login(username, password)
                print(sso_response)
                if sso_response.status_code == 200 and sso_response.json()['state'] != 0:
                    # User authenticated via SSO, create user in database
                    nama_lengkap = sso_response.json().get("nama")
                    nama_lengkap = nama_lengkap[0].upper() + nama_lengkap[1:]
                    # Split nama_lengkap into first_name and last_name
                    first_name = nama_lengkap.split()[0]
                    print(nama_lengkap)
                    last_name = ' '.join(nama_lengkap.split()[1:]) if len(nama_lengkap) > 1 else ''
                    user = KwlUser.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name)
            
                    return Response(data = {"message":'success',"data":get_tokens_for_user(user)}, status=status.HTTP_200_OK)
                else:
                    # SSO login failed, return error response //ini bisa di-comment saja apabila non-ui
                    return Response({'message': 'SSO Login failed'}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                # If user exists in the database, perform regular authentication
                user = authenticate(request, username=username, password=password)
                print(user)
                if user is not None:
                    return Response(data = {"message":'success',"data":get_tokens_for_user(user)}, status=status.HTTP_200_OK)
                else:
                    return Response(data = {'message': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(data = {'message':"unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        

class RegisterStudentView(APIView):
    permission_classes = (AllowAny,)

    # Register Student
    @csrf_exempt
    def post(self, request):  
        try:
            serializer = StudentSerializer(data=request.data)
            if serializer.is_valid():
                    serializer.save()
        
                    return Response({"message": "Student registered successfully"}, status=status.HTTP_201_CREATED)

            else:
                return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:

            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def put(self, request, format=None):
        print(request.user.id)
        # student = self.get_object(pk)
        # serializer = StudentSerializer(student, data=request.data)
        # if serializer.is_valid():
        #     serializer.save()
        #     return Response(serializer.data, status=status.HTTP_200_OK)
        # return Response({"error": str(serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error"}, status=status.HTTP_400_BAD_REQUEST)
    

class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Student.objects.get(pk=pk)
        except Student.DoesNotExist:
            raise Http404
        
    def get(self, request, format=None):
        id = request.user.id
        print("Id "+str(id))
        # student = self.get_object(id)
        # serializer = StudentSerializer(student)
        # return Response(serializer.data)
        return Response(data={"message": "success"}, status=status.HTTP_200_OK)
    def put(self, request, format=None):
        id = request.user.id
        student = self.get_object(id)
        serializer = StudentSerializer(student, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error": str(serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)
        
    
    def delete(self, request, pk, format=None):
        id = request.user.id
        student = self.get_object(id)
        student.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

        

class RegisterTeacherView(APIView):
    permission_classes = (AllowAny,)
    @csrf_exempt
    def post(self, request):
        try:
            print(request.data)
            serializer = StudentSerializer(data=request.data)
            if serializer.is_valid():
                    serializer.save()
        
                    return Response({"message": "Student registered successfully"}, status=status.HTTP_201_CREATED)

            else:
                return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:

            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)