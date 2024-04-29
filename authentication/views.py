from rest_framework import status

from django.contrib.auth import authenticate, logout
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from smtplib import SMTPException     
from kwl import settings
from .serializers import LoginSerializer, StudentSerializer, LecturerSerializer, EditLecturerSerializer, EditStudentSerializer, ResetPasswordRequestSerializer, ChangePasswordSerializer
from .models import KwlUser, Student, Lecturer
from rest_framework_simplejwt.tokens import RefreshToken
from authentication.utils import sso_login, get_tokens_for_user
from rest_framework.response import Response
from django.core.mail import send_mail
import random
import string
from drf_yasg.utils import swagger_auto_schema

class LoginView(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            user = KwlUser.objects.filter(username=username).first()

            if user is None:
                sso_response = sso_login(username, password)
                if sso_response.status_code == 200 and sso_response.json()['state'] != 0:
                    nama_lengkap = sso_response.json().get("nama")
                    nama_lengkap = nama_lengkap[0].upper() + nama_lengkap[1:]
                    first_name = nama_lengkap.split()[0]
                    last_name = ' '.join(nama_lengkap.split()[1:]) if len(nama_lengkap) > 1 else ''
                    user = KwlUser.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name)
                    Student.objects.create(user=user)
            
                    return Response(data = {"message":'Login Success',"data":get_tokens_for_user(user)}, status=status.HTTP_200_OK)
                else:
                    return Response({'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                user = authenticate(request, username=username, password=password)
                print(user)
                if user is not None:
                    return Response(data = {"message":'Login Success',"data":get_tokens_for_user(user)}, status=status.HTTP_200_OK)
                else:
                    return Response(data = {'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(data = {'message':"Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        

class RegisterStudentView(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(request_body=StudentSerializer)
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
        

class StudentDetailView(APIView):
    permission_classes = [IsAuthenticated,]

    def get_student_by_kwluser_id(self, kwluser_id):
        try:
            student = Student.objects.get(user_id=kwluser_id)
            return student
        except Student.DoesNotExist:
            return None
        
    def get(self, request, format=None):
        id = request.user.id
        student = self.get_student_by_kwluser_id(id)
        serializer = StudentSerializer(student)
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, format=None):
        id = request.user.id
        student = self.get_student_by_kwluser_id(id)
        serializer = EditStudentSerializer(student, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        print(serializer.errors)
        return Response(str(serializer.errors), status=status.HTTP_400_BAD_REQUEST)


class LecturerDetailView(APIView):
    permission_classes = [IsAuthenticated,]

    def get_lecturer_by_kwluser_id(self, kwluser_id):
        try:
            lecturer = Lecturer.objects.get(user_id=kwluser_id)
            return lecturer
        except Lecturer.DoesNotExist:
            return None
        
    def get(self, request, format=None):
        id = request.user.id
        lecturer = self.get_lecturer_by_kwluser_id(id)
        serializer = LecturerSerializer(lecturer)
        return Response(serializer.data)

    def put(self, request, format=None):
        id = request.user.id
        lecturer = self.get_lecturer_by_kwluser_id(id)
        serializer = EditLecturerSerializer(lecturer, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error": str(serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)


class RegisterTeacherView(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(request_body=LecturerSerializer)
    def post(self, request):
        try:
            serializer = LecturerSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Lecturer registered successfully"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            logout(request)
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(data=str(e),status=status.HTTP_400_BAD_REQUEST)


class RequestPasswordResetEmailView(APIView):
    permission_classes = (AllowAny,)
   
    @swagger_auto_schema(request_body=ResetPasswordRequestSerializer, responses={200: "Reset password email sent successfully", 404: "User not found", 500: "Email could not be sent"})
    def post(self, request):
        try:
            email_serializer = ResetPasswordRequestSerializer(data=request.data)
            if not email_serializer.is_valid():
                return Response(email_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            email = email_serializer.data["email"] 
            user = KwlUser.objects.get(email=email)
            token = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=20))
            user.reset_password_token = token
            user.save()
            try:
                send_mail(
                    subject='Reset Password',
                    message='Click the link below to reset your password\n\nhttps://localhost:3000/reset-password?token=' + token,
                    from_email="kowl.apps@gmail.com",
                    recipient_list=[user.email],
                    fail_silently=False,
                    auth_password=settings.EMAIL_HOST_PASSWORD,
                    auth_user=settings.EMAIL_HOST_USER
                )
            except SMTPException as e:
                return Response({"message": f"Email could not be sent. Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response({"message": "Reset password email sent successfully"}, status=status.HTTP_200_OK)
        except KwlUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ResetPasswordConfirmByTokenView(APIView):
    permission_classes = (AllowAny,)
    @swagger_auto_schema(request_body=ChangePasswordSerializer)
    def post(self, request, token):
        try:
            new_password_serializer = ChangePasswordSerializer(data=request.data)
            if not new_password_serializer.is_valid():
                return Response(new_password_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            user = KwlUser.objects.get(reset_password_token=token)
            new_password = new_password_serializer.data['password']
            user.set_password(new_password)
            user.reset_password_token = None
            user.save()
            return Response({"message": "Password reset successfully"}, status=status.HTTP_200_OK)
        except KwlUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
