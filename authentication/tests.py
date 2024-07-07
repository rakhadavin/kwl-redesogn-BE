from unittest import mock
from django.test import TestCase
from authentication.models import KwlUser, Student
from rest_framework.test import APIClient
from authentication.utils import get_tokens_for_user
# Create your tests here.


def generate_student_payload():
    return {
        "user": {
            "username": "anisa.faradisa",
            "password": "anisa123",
            "email": "anisa.faradisa@gmail.com",
            "role": "student",
            "domisili": "Jakarta",
        },
        "student_id": "1234567890",
        "major": "Computer Science",
        "term": "3",
        "faculty": "Computer Science",
        "nama_lengkap": "Anisa Faradisa"
    }

def generate_lecturer_payload():
    return {
        "user": {
            "username": "anisa.faradisa",
            "password": "anisa123",
            "email": "anisa.faradisa@gmail.com",
            "role": "lecturer",
            "domisili": "Jakarta",
        },
        "lecturer_id": "1234567890",
        "department": "Computer Science",
        "nama_lengkap": "Anisa Faradisa"
    }

class RegisterStudentTest(TestCase):
    def setUp(self):
        self.valid_payload = generate_student_payload()
        self.invalid_payload = {
            "username": "anisa.faradiso",
            "password": "anisafaradisa123",
            "email": "",
        }


    def test_register_student(self):
        response = self.client.post(
            '/api/auth/register/student',
            data=self.valid_payload,
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {"message": "Student registered successfully"})


    def test_register_student_invalid_payload(self):
        response = self.client.post(
            '/api/auth/register/student',
            data=self.invalid_payload,
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)

        
class RegisterLecturerTest(TestCase):
    def setUp(self):
        self.valid_payload = generate_lecturer_payload()
        self.invalid_payload = {
            "username": "anisa.faradiso",
            "password": "anisaf",
            "email": "",
        }

    def test_register_lecturer(self):
        response = self.client.post(
            '/api/auth/register/lecturer',
            data=self.valid_payload,
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {"message": "Lecturer registered successfully"})

    def test_register_lecturer_invalid_payload(self):
        response = self.client.post(
            '/api/auth/register/lecturer',
            data=self.invalid_payload,
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)

class LoginTest(TestCase):
    def setUp(self):
        user = KwlUser.objects.create(username="anisa.faradisa",email="anisa.faradisa@gmail.com", role="student", domisili="Jakarta")
        user.set_password("anisa1234")
        user.save()

        student = Student.objects.create(user=user, student_id="1234567890", major="Computer Science", term="3", faculty="Computer Science")
        student.save()


        self.valid_payload = {
            "username": "anisa.faradisa",
            "password": "anisa1234"
        }
        self.invalid_payload = {
            "username": "anisa.faradisa",
            "password": "anisa123"
        }

    def test_login(self):
        response = self.client.post(
            '/api/auth/login',
            data=self.valid_payload,
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue('access' in response.data['data'])
        self.assertTrue('refresh' in response.data['data'])

        


    def test_login_invalid_credentials(self):
        response = self.client.post(
            '/api/auth/login',
            data=self.invalid_payload,
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 401)

def student_api_client():
    client = APIClient()
    user = KwlUser.objects.create(username="anisa.faradisa",email="anisa.faradisa@gmail.com", role="student", domisili="Jakarta")
    user.set_password("anisa1234")
    user.save()

    student = Student.objects.create(user=user, student_id="1234567890", major="Computer Science", term="3", faculty="Computer Science")
    student.save()

    access = get_tokens_for_user(user)['access']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')


    return client

class StudentDetailViewTest(TestCase):

    def test_student_detail(self):
        self.client = student_api_client()
        response = self.client.get(
            '/api/auth/student'
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue('student_id' in response.data)
        self.assertTrue('major' in response.data)

    def test_student_detail_unauthenticated(self):
        response = self.client.get(
            '/api/auth/student'
        )
        self.assertEqual(response.status_code, 401)
        
class StudentListViewTest(TestCase):
        
        def setUp(self):
            self.client = APIClient()
  
        def test_student_list(self):
            self.client = student_api_client()
            response = self.client.get(
                '/api/auth/student/all'
            )
    
            self.assertEqual(response.status_code, 200)
            self.assertTrue(len(response.data) > 0)
    
        def test_student_list_unauthenticated(self):
            response = self.client.get(
                '/api/auth/student/all'
            )
            self.assertEqual(response.status_code, 401)


class ResetPasswordTest(TestCase):
    
    def test_reset_password(self):
        user = KwlUser.objects.create(username="anisa.faradisa",email="anisa.faradisa@gmail.com", role="student", domisili="Jakarta")
        user.set_password("anisa1234")
        user.save()
    
        response = self.client.post(
            '/api/auth/reset',
            data={"email": "anisa.faradisa@gmail.com"},
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)

  