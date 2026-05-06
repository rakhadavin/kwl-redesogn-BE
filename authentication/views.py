from rest_framework import status, serializers

from django.contrib.auth import authenticate, logout
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from smtplib import SMTPException     
from kwl import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .serializers import LoginSerializer, StudentSerializer, LecturerSerializer, EditLecturerSerializer, EditStudentSerializer, ResetPasswordRequestSerializer, ChangePasswordSerializer, CreateStudentSerializer, CreateLecturerSerializer, ProviderAuthSerializer, ConsentSerializer, UserConsentSubmitSerializer
from .models import KwlUser, Student, Lecturer, ResetPasswordToken, Consent, UserConsent
from .api_exceptions import ExistingEmailException, ExistingUsernameException
from rest_framework_simplejwt.tokens import RefreshToken
from authentication.utils import get_tokens_for_user
from rest_framework.response import Response
from django.core.mail import send_mail
from drf_yasg.utils import swagger_auto_schema
import requests
from django.core.cache import cache
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError

def send_welcome_email(user, role):
    """Send welcome email to newly registered user"""
    try:
        subject = f"🎉 Selamat Datang di KWL Platform - {role.title()}"
        
        # Context for template
        context = {
            'user': user,
            'role': role,
            'frontend_url': settings.FRONTEND_URL or 'https://kwl-dev.cs.ui.ac.id',
        }
        
        # Render HTML email
        html_message = render_to_string('emails/welcome_email.html', context)
        
        # Render plain text email
        plain_message = render_to_string('emails/welcome_email.txt', context)

        # Send email with both HTML and plain text versions
        send_mail(
            subject=subject,
            message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
        
    except SMTPException as e:
        print(f"SMTP Error sending welcome email: {e}")
        return False
    except Exception as e:
        print(f"Error sending welcome email: {e}")
        return False
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
            student = serializer.save()
            
            # Send welcome email
            email_sent = send_welcome_email(student.user, 'student')
            
            response_message = "Student registered successfully"
            if email_sent:
                response_message += " and welcome email sent"
            else:
                response_message += " but welcome email could not be sent"
            
            return Response({"message": response_message}, status=status.HTTP_201_CREATED)
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


class ConsentListView(APIView):
    """Public endpoint — returns all available consent items."""
    permission_classes = [AllowAny,]

    @swagger_auto_schema(responses={200: ConsentSerializer(many=True)}, operation_summary="Get all consents", tags=["Consent"])
    def get(self, request):
        consents = Consent.objects.all()
        serializer = ConsentSerializer(consents, many=True)
        return Response(serializer.data)


class UserConsentStatusView(APIView):
    """Check and submit consent for the logged-in user."""
    permission_classes = [IsAuthenticated,]

    @swagger_auto_schema(
        responses={200: "{'has_consented': bool, 'consented_at': datetime|null}"},
        operation_summary="Check if current user has submitted consent",
        tags=["Consent"]
    )
    def get(self, request):
        user_consent = UserConsent.objects.filter(user=request.user).first()
        if user_consent:
            return Response({
                "has_consented": True,
                "consented_at": user_consent.agreed_at,
                "consent": ConsentSerializer(user_consent.consent).data,
            })
        return Response({"has_consented": False, "consented_at": None, "consent": None})

    @swagger_auto_schema(
        request_body=UserConsentSubmitSerializer,
        responses={201: "Consent submitted", 400: "Bad Request"},
        operation_summary="Submit consent for current user",
        tags=["Consent"]
    )
    def post(self, request):
        serializer = UserConsentSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        consent_id = serializer.validated_data['consent_id']
        consent = Consent.objects.get(id=consent_id)
        user_consent, created = UserConsent.objects.get_or_create(user=request.user, consent=consent)
        if created:
            return Response({"message": "Consent submitted successfully", "consented_at": user_consent.agreed_at}, status=status.HTTP_201_CREATED)
        return Response({"message": "Consent already submitted", "consented_at": user_consent.agreed_at})
    
    
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
            student = serializer.save(user=user)

            # Send welcome email for role assignment
            email_sent = send_welcome_email(user, 'student')
            
            response_message = "Student assigned successfully"
            if email_sent:
                response_message += " and welcome email sent"

            return Response({"message": response_message, "data": get_tokens_for_user(request.user)}, status=status.HTTP_200_OK)
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


class LecturerByPkView(APIView):
    """Get any lecturer by their Lecturer model PK."""
    permission_classes = [IsAuthenticated,]

    def get(self, request, pk, format=None):
        try:
            lecturer = Lecturer.objects.get(pk=pk)
            serializer = LecturerSerializer(lecturer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Lecturer.DoesNotExist:
            return Response({"message": "Lecturer not found"}, status=status.HTTP_404_NOT_FOUND)


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
            lecturer = serializer.save(user=user)

            # Send welcome email for role assignment
            email_sent = send_welcome_email(user, 'lecturer')
            
            response_message = "Lecturer assigned successfully"
            if email_sent:
                response_message += " and welcome email sent"

            return Response({"message": response_message, "data": get_tokens_for_user(request.user)}, status=status.HTTP_200_OK)
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
            lecturer = serializer.save()
            
            # Send welcome email
            email_sent = send_welcome_email(lecturer.user, 'lecturer')
            
            response_message = "Lecturer registered successfully"
            if email_sent:
                response_message += " and welcome email sent"
            else:
                response_message += " but welcome email could not be sent"
            
            return Response({"message": response_message}, status=status.HTTP_201_CREATED)
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
                
            user = None

            if data['provider'] == 'google':
                user = KwlUser.objects.filter(google_id=user_info.get('id')).first()
                if not user:
                    user = KwlUser.objects.filter(email=user_info['email']).first()
                    if user:
                        user.google_id = user_info.get('id')
                        user.save(update_fields=['google_id'])
                if not user:
                    username = user_info['email'].replace('@gmail.com', '')
                    user = KwlUser.objects.create_user(
                        username=username,
                        email=user_info['email'],
                        first_name=user_info.get('given_name', ''),
                        last_name=user_info.get('family_name', ''),
                        google_id=user_info.get('id'),
                    )

            elif data['provider'] == 'keycloak':
                keycloak_sub = user_info.get('sub')
                keycloak_username = user_info.get('preferred_username', user_info.get('email', ''))
                user = KwlUser.objects.filter(keycloak_id=keycloak_sub).first()
                if not user:
                    user = KwlUser.objects.filter(username=keycloak_username).first() or \
                           KwlUser.objects.filter(email=user_info.get('email', '')).first()
                    if user:
                        user.keycloak_id = keycloak_sub
                        user.save(update_fields=['keycloak_id'])
                if not user:
                    user = KwlUser.objects.create_user(
                        username=keycloak_username,
                        email=user_info.get('email', ''),
                        first_name=user_info.get('given_name', ''),
                        last_name=user_info.get('family_name', ''),
                        keycloak_id=keycloak_sub,
                    )

            else:
                user = KwlUser.objects.filter(email=user_info['email']).first()
            
            if user is None:
                return Response({'error': 'User not found and could not be created'}, status=status.HTTP_401_UNAUTHORIZED)

            tokens = get_tokens_for_user(user)
            return Response(data={"message": "Login Success", "data": tokens}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(data = {"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)