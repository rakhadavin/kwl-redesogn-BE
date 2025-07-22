from rest_framework import status, serializers

from django.contrib.auth import authenticate, logout
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from smtplib import SMTPException     
from kwl import settings
from .serializers import LoginSerializer, StudentSerializer, LecturerSerializer, EditLecturerSerializer, EditStudentSerializer, ResetPasswordRequestSerializer, ChangePasswordSerializer, CreateStudentSerializer, CreateLecturerSerializer, ProviderAuthSerializer
from .models import KwlUser, Student, Lecturer, ResetPasswordToken
from .api_exceptions import ExistingEmailException, ExistingUsernameException
from rest_framework_simplejwt.tokens import RefreshToken
from authentication.utils import get_tokens_for_user
from rest_framework.response import Response
from django.core.mail import send_mail
from drf_yasg.utils import swagger_auto_schema
import requests
from django.core.cache import cache
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
import jwt

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

    @swagger_auto_schema(request_body=CreateStudentSerializer, responses={200: "Student assigned successfully", 400: "Bad Request"}, operation_summary="Assign student role to existing user", operation_description="Assign student role to existing user if user exists and doesn't have student role", tags=["Student"])
    def post(self, request, format=None):
        try:
            user = request.user
            user.role = 'student'
            user_data = request.data.get('user', {})
            domisili = user_data.get('domisili')
            user.domisili = domisili

            nama_lengkap = request.data.get('nama_lengkap', '')
            if nama_lengkap:
                nama_parts = nama_lengkap.strip().split(' ', 1)
                user.first_name = nama_parts[0] if nama_parts else ''
                user.last_name = nama_parts[1] if len(nama_parts) > 1 else ''
            user.save()

            if Student.objects.filter(user=user).exists():
                return Response({"message": "User already has student role"}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = CreateStudentSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user)

            return Response({"message": "Student assigned successfully", "data": get_tokens_for_user(request.user)}, status=status.HTTP_200_OK)
        except serializers.ValidationError as e:
            return Response({"message": "Validation failed", "errors": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": f"Failed to assign student role: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

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

    @swagger_auto_schema(request_body=CreateLecturerSerializer, responses={200: "Lecturer assigned successfully", 400: "Bad Request"}, operation_summary="Assign lecturer role to existing user", operation_description="Assign lecturer role to existing user if user exists and doesn't have lecturer role", tags=["Lecturer"])
    def post(self, request, format=None):
        try:
            user = request.user
            user.role = 'lecturer'
            user_data = request.data.get('user', {})
            domisili = user_data.get('domisili')
            user.domisili = domisili

            nama_lengkap = request.data.get('nama_lengkap', '')
            if nama_lengkap:
                nama_parts = nama_lengkap.strip().split(' ', 1)
                user.first_name = nama_parts[0] if nama_parts else ''
                user.last_name = nama_parts[1] if len(nama_parts) > 1 else ''
            user.save()

            if Lecturer.objects.filter(user=user).exists():
                return Response({"message": "User already has lecturer role"}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = CreateLecturerSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user)

            return Response({"message": "Student assigned successfully", "data": get_tokens_for_user(request.user)}, status=status.HTTP_200_OK)
        except serializers.ValidationError as e:
            return Response({"message": "Validation failed", "errors": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": f"Failed to assign student role: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
    
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



# class ResetPasswordConfirmByTokenView(APIView):
#     permission_classes = (AllowAny,)
#     @swagger_auto_schema(request_body=ChangePasswordSerializer)
#     def post(self, request, token):
#         try:     
#             new_password_serializer = ChangePasswordSerializer(data=request.data)
#             new_password_serializer.is_valid(raise_exception=True)
              
#             user = KwlUser.objects.get(reset_password_token__token=token)
#             old_password = new_password_serializer.data['old_password']
#             new_password = new_password_serializer.data['new_password']
#             if user.check_password(old_password) == False:
#                 return Response({"message": "Old password is incorrect"}, status=status.HTTP_400_BAD_REQUEST)
#             user.set_password(new_password)
#             user.reset_password_token = None
#             user.save()

#             return Response({"message": "Password reset successfully"}, status=status.HTTP_200_OK)
#         except KwlUser.DoesNotExist:
#             return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ResetPasswordConfirmByTokenView(APIView):
    permission_classes = (AllowAny,)
    @swagger_auto_schema(request_body=ChangePasswordSerializer)
    def post(self, request, token):
        try:     
            new_password_serializer = ChangePasswordSerializer(data=request.data)
            new_password_serializer.is_valid(raise_exception=True)
              
            user = KwlUser.objects.get(reset_password_token__token=token)
            new_password = new_password_serializer.data['new_password']
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
     

def verify_google_access_token(access_token):
    """Verify Google access token and get user info"""
    try:
        if not access_token:
            print("ERROR: No access token provided")
            return None
            
        response = requests.get(
            'https://www.googleapis.com/oauth2/v2/userinfo',
            params={'access_token': access_token}
        )
        
        if response.status_code == 200:
            user_info = response.json()
            return user_info
        else:
            print(f"Failed to get user info: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error verifying Google access token: {e}")
        return None

def get_keycloak_public_keys():
    """Get Keycloak public keys from JWKS endpoint with caching"""
    cache_key = 'keycloak_public_keys'
    keys = cache.get(cache_key)
    
    if not keys:
        try:
            response = requests.get(settings.KEYCLOAK_CERTS_URL, timeout=10)
            response.raise_for_status()
            jwks = response.json()
            keys = jwks.get('keys', [])
            
            # Cache the keys for the configured timeout
            cache.set(cache_key, keys, settings.KEYCLOAK_KEYS_CACHE_TIMEOUT)
            print(f"Cached {len(keys)} Keycloak public keys")
            
        except Exception as e:
            print(f"Error fetching Keycloak public keys: {e}")
            return []
    
    return keys

def verify_keycloak_access_token(access_token):
    """Verify Keycloak access token and get user info"""
    try:
        if not access_token:
            print("ERROR: No access token provided")
            return None
        
        public_keys = get_keycloak_public_keys()
        if not public_keys:
            print("ERROR: Could not retrieve Keycloak public keys")
            return None
        
        try:
            unverified_header = jwt.get_unverified_header(access_token)
            kid = unverified_header.get('kid')
        except Exception as e:
            print(f"Error decoding token header: {e}")
            return None
        
        public_key = None
        for key in public_keys:
            if key.get('kid') == kid:
                try:
                    public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
                    break
                except Exception as e:
                    print(f"Error converting JWK to PEM: {e}")
                    continue
        
        if not public_key:
            print(f"ERROR: Public key with kid '{kid}' not found")
            return None
        
        try:
            decoded_token = jwt.decode(
                access_token,
                public_key,
                algorithms=['RS256'],
                audience="account",
                issuer=settings.KEYCLOAK_ISSUER_URL,
                options={
                    'verify_signature': True,
                    'verify_exp': True,
                    'verify_iat': True,
                    'verify_aud': True,
                    'verify_iss': True
                },
                leeway=1000
            )
            
            user_info = {
                'email': decoded_token.get('email'),
                'given_name': decoded_token.get('given_name'),
                'family_name': decoded_token.get('family_name'),
                'name': decoded_token.get('name'),
                'preferred_username': decoded_token.get('preferred_username'),
                'sub': decoded_token.get('sub'), 
            }
            
            return user_info
            
        except ExpiredSignatureError:
            print("ERROR: Token has expired")
            return None
        except InvalidTokenError as e:
            print(f"ERROR: Invalid token: {e}")
            return None
            
    except Exception as e:
        print(f"Error verifying Keycloak access token: {e}")
        return None

class ProviderLoginView(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(request_body=ProviderAuthSerializer, responses={200: "Login Success", 401: "Unauthorized"}, operation_summary="Login using Provider OAuth")
    def post(self, request):
        try:
            serializer = ProviderAuthSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            data = serializer.validated_data

            if data['provider'] == 'google':
                user_info = verify_google_access_token(data['access_token'])
                if not user_info:
                    return Response({'error': 'Invalid Google token'}, status=status.HTTP_401_UNAUTHORIZED)
            if data['provider'] == 'keycloak':
                user_info = verify_keycloak_access_token(data['access_token'])
                if not user_info:
                    return Response({'error': 'Invalid Keycloak token'}, status=status.HTTP_401_UNAUTHORIZED)
                
            try:
                user = KwlUser.objects.get(email=user_info['email'])
            except KwlUser.DoesNotExist:
                first_name = user_info.get('given_name', '')
                last_name = user_info.get('family_name', '')
                
                extra_fields = {}
                if data['provider'] == 'google':
                    extra_fields['google_id'] = user_info.get('id')
                    username = user_info['email'].replace('@gmail.com', '')
                elif data['provider'] == 'keycloak':
                    extra_fields['keycloak_id'] = user_info.get('sub')
                    username = user_info.get('preferred_username', user_info['email'])

                user = KwlUser.objects.create_user(
                    username=username,
                    email=user_info['email'],
                    first_name=first_name,
                    last_name=last_name,
                    **extra_fields
                )
            
            if user is not None:
                tokens = get_tokens_for_user(user)
                return Response(data={"message": "Login Success", "data": tokens}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(data = {"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)