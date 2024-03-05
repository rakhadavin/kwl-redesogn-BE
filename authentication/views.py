from django.db import DatabaseError
from rest_framework import status

from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from .serializers import LoginSerializer, StudentSerializer
from .models import KwlUser, Student

from authentication.utils import sso_login, get_tokens_for_user
from rest_framework.response import Response
# from dj_rest_auth.registration.views import RegisterView
from rest_framework.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt

# queryset = Profile.objects.all().order_by('-user__date_joined')

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
                if sso_response.status_code == 200:
                    # User authenticated via SSO, create user in database
                    nama_lengkap = sso_response.json().get("nama")
                    # Split nama_lengkap into first_name and last_name
                    first_name = nama_lengkap.split()[0]
                    last_name = ' '.join(nama_lengkap[1:]) if len(nama_lengkap) > 1 else ''
                    user = KwlUser.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name)
            
                    return Response(data = {'message': 'SSO Login successful'}, status=status.HTTP_200_OK)
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
    @csrf_exempt
    def post(self, request):
        try:
            serializer = StudentSerializer(data=request.data)
            if serializer.is_valid():
                    serializer.save()
                # # Extract data from serializer
                # username = serializer.validated_data['username']
                # password = serializer.validated_data['password']
                # domisili = serializer.validated_data['domisili']
                # # term = serializer.validated_data['term']
                # # student_id = serializer.validated_data['student_id']
                # # fakultas = serializer.validated_data['fakultas']
                # nama_lengkap = serializer.validated_data['nama_lengkap']
                # # jurusan = serializer.validated_data['jurusan']
                # email = serializer.validated_data['email']

                # # Split nama_lengkap into first_name and last_name
                # first_name = nama_lengkap.split()[0]
                # last_name = ' '.join(nama_lengkap.split()[1:]) if len(nama_lengkap.split()) > 1 else ''

                # # Check if user exists in the database
                # user = KwlUser.objects.filter(username=username).first()

                # if user is None:
                #     # Create KwlUser instance
                #     kwlUser = KwlUser.objects.create(username=username,
                #                                       password=password,
                #                                       domisili=domisili,
                #                                       first_name=first_name,
                #                                       last_name=last_name,
                #                                       email=email
                #                                       )

                #     # Save the Student instance
                #     student = serializer.save(user=kwlUser)

                    return Response({"message": "Student registered successfully"}, status=status.HTTP_201_CREATED)
                # else:
                #     return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Handle exceptions
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)