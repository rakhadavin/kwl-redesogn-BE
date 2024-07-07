from rest_framework import status

from django.contrib.auth import authenticate, logout
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from smtplib import SMTPException     
from kwl import settings
from .serializers import LoginSerializer, StudentSerializer, LecturerSerializer, EditLecturerSerializer, EditStudentSerializer, ResetPasswordRequestSerializer, ChangePasswordSerializer
from .models import KwlUser, Student, Lecturer, ResetPasswordToken
from rest_framework_simplejwt.tokens import RefreshToken
from authentication.utils import get_tokens_for_user
from rest_framework.response import Response
from django.core.mail import send_mail
from drf_yasg.utils import swagger_auto_schema

class LoginView(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(request_body=LoginSerializer, responses={200: "Login Success", 401: "Unauthorized"}, operation_summary="Login using username and password")
    def post(self, request):
        try:
            
            serializer = LoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
                
            user = authenticate(request, username=username, password=password)
            if user is not None:
                return Response(data = {"message":'Login Success',"data":get_tokens_for_user(user)}, status=status.HTTP_200_OK)
            else:
                return Response(data = {'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response(data = {'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class RegisterStudentView(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(request_body=StudentSerializer, responses={201: "Student registered successfully"}, operation_summary="Register student")
    def post(self, request): 
        try:
            serializer = StudentSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"message":"Student registered successfully"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"message":str(e)}, status=status.HTTP_400_BAD_REQUEST)

        
class StudentListView(APIView): 
    permission_classes = [IsAuthenticated,]

    @swagger_auto_schema(responses={200: StudentSerializer(many=True), 401: "Unauthorized"}, operation_summary="Get all students", operation_description="Get all students", tags=["Student"])
    def get(self, request):
        students = Student.objects.all()
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)

class LecturerListView(APIView):
    permission_classes = [IsAuthenticated,]

    @swagger_auto_schema(responses={200: LecturerSerializer(many=True), 401: "Unauthorized"}, operation_summary="Get all lecturers", operation_description="Get all lecturers", tags=["Lecturer"])
    def get(self, request):
        lecturers = Lecturer.objects.all()
        serializer = LecturerSerializer(lecturers, many=True)
        return Response(serializer.data)
    
    
class StudentDetailView(APIView):
    permission_classes = [IsAuthenticated,]


    def get_student_by_kwluser_id(self, kwluser_id):
        try:
            student = Student.objects.get(user_id=kwluser_id)
            return student
        except Student.DoesNotExist:
            return None
        
    @swagger_auto_schema(responses={200: StudentSerializer, 401: "Unauthorized"}, operation_summary="Get student detail", operation_description="Get student detail", tags=["Student"])
    def get(self, request, format=None):
        id = request.user.id
        student = self.get_student_by_kwluser_id(id)
        serializer = StudentSerializer(student)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=EditStudentSerializer, responses={200: StudentSerializer, 400: "Bad Request"}, operation_summary="Edit student", operation_description="Edit student", tags=["Student"])
    def put(self, request, format=None):
        id = request.user.id
        student = self.get_student_by_kwluser_id(id)
        serializer = EditStudentSerializer(student, data=request.data, context={'user': request.user})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
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
    
    @swagger_auto_schema(request_body=EditLecturerSerializer)
    def put(self, request, format=None):
        id = request.user.id
        lecturer = self.get_lecturer_by_kwluser_id(id)
        if lecturer is None:
            return Response({"message": "Lecturer not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = EditLecturerSerializer(lecturer, data=request.data, context={'user': request.user})
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
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"message": "Lecturer registered successfully"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
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
    
        email_serializer = ResetPasswordRequestSerializer(data=request.data)
        email_serializer.is_valid(raise_exception=True)
        email = email_serializer.data["email"] 
        user = KwlUser.objects.get(email=email)
        reset_password_token = ResetPasswordToken()
        reset_password_token.save()
        user.reset_password_token = reset_password_token
        user.save()
        reset_url = settings.FRONTEND_URL + "/auth/confirm-reset/"+ reset_password_token.token
        try:
            send_mail(
                subject='Reset Password',
                message = f'Click the link below to reset your password\n\n{reset_url}',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
                auth_password=settings.EMAIL_HOST_PASSWORD,
                auth_user=settings.EMAIL_HOST_USER
            )
        except SMTPException as e:
            return Response({"message": f"Email could not be sent. Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({"message": "Reset password email sent successfully"}, status=status.HTTP_200_OK)



class ResetPasswordConfirmByTokenView(APIView):
    permission_classes = (AllowAny,)
    @swagger_auto_schema(request_body=ChangePasswordSerializer)
    def post(self, request, token):
        try:     
            new_password_serializer = ChangePasswordSerializer(data=request.data)
            new_password_serializer.is_valid(raise_exception=True)
              
            user = KwlUser.objects.get(reset_password_token__token=token)
            old_password = new_password_serializer.data['old_password']
            new_password = new_password_serializer.data['new_password']
            if user.check_password(old_password) == False:
                return Response({"message": "Old password is incorrect"}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(new_password)
            user.reset_password_token = None
            user.save()

            return Response({"message": "Password reset successfully"}, status=status.HTTP_200_OK)
        except KwlUser.DoesNotExist:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    def get(self, request, token):
        try:
            user = KwlUser.objects.get(reset_password_token__token=token)
            if user.reset_password_token.is_expired():
                user.reset_password_token.delete()
                return Response({"message": "Token is expired"}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"message": "Token is valid"}, status=status.HTTP_200_OK)
        except KwlUser.DoesNotExist:
            return Response({"message": "Token is invalid"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


