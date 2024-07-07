from django.test import TestCase
from rest_framework.test import APIClient
from authentication.models import KwlUser, Lecturer
from authentication.utils import get_tokens_for_user
from course.models import Course, Topic

# Create your tests here.
def lecturer_api_client_first():
    client = APIClient()
    user = KwlUser.objects.create(username="monica.rajasa",email="monica.rajasa@gmail.com", role="lecturer", domisili="Jakarta")
    user.set_password("monica1234")
    user.save()

    lecturer = Lecturer.objects.create(user=user, lecturer_id="1234567890", department="Computer Science")

    access = get_tokens_for_user(user)['access']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')


    return client, lecturer

def lecturer_api_client_second():
    client = APIClient()
    user = KwlUser.objects.create(username="daniel.rajasa",email="daniel.rajasa@gmail.com", role="lecturer", domisili="Jakarta")
    user.set_password("daniel1234")
    user.save()

    lecturer = Lecturer.objects.create(user=user, lecturer_id="1234567890", department="Computer Science")

    access = get_tokens_for_user(user)['access']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')

    return client, lecturer

class testBulkCreateAndEditQuiz(TestCase):
    def setUp(self):
        # Setup test data
        topic = Topic.objects.create(name="Test Topic")
        self.client, lecturer = lecturer_api_client_first()
        course = Course.objects.create(short_name="Test Course", full_name="Test Course", color_theme="blue")
        topic.course = course
        topic.save()
        course.lecturer_team.add(lecturer)
        course.save()
        self.quiz_data = {
            "topic": topic.id,
            "type": "quiz",  
            "questions": [
                {
                    "question": "Sample Question 1",
                    "option_a": "Option 1",
                    "option_b": "Option 2",
                    "option_c": "Option 3",
                    "option_d": "Option 4",
                    "score": 10,
                    "correct_option": "Opsi A"
                },
                {
                    "question": "Sample Question 2",
                    "option_a": "Option 1",
                    "option_b": "Option 2",
                    "option_c": "Option 3",
                    "option_d": "Option 4",
                    "score": 10,
                    "correct_option": "Opsi B"
                },
                {
                    "question": "Sample Question 3",
                    "option_a": "Option 1",
                    "option_b": "Option 2",
                    "option_c": "Option 3",
                    "option_d": "Option 4",
                    "score": 10,
                    "correct_option": "Opsi C"
                },
                {
                    "question": "Sample Question 4",
                    "option_a": "Option 1",
                    "option_b": "Option 2",
                    "option_c": "Option 3",
                    "option_d": "Option 4",
                    "score": 10,
                    "correct_option": "Opsi D"
                }
            ]
        }

    def test_bulk_create_quiz(self):
        # Test bulk create quiz
        response = self.client.post('/api/know/quiz', self.quiz_data, format='json')
        self.assertEqual(response.status_code, 201)

    def test_edit_quiz(self):
        # Test edit quiz
        response = self.client.post('/api/know/quiz', self.quiz_data, format='json')
        self.assertEqual(response.status_code, 201)
       
        edit_data = {
             "questions": [
                {
                    "id": 1,
                    "question": "Sample Question 1",
                    "option_a": "Option 1",
                    "option_b": "Option 2",
                    "option_c": "Option 3",
                    "option_d": "Option 4",
                    "score": 30,
                    "correct_option": "Opsi C"
                },
                {
                    "id": 2,
                    "question": "Sample Question 2",
                    "option_a": "Option 1",
                    "option_b": "Option 2",
                    "option_c": "Option 3",
                    "option_d": "Option 4",
                    "score": 30,
                    "correct_option": "Opsi A"
                },
                {
                    "id": 3,
                    "question": "Sample Question 3",
                    "option_a": "Option 1",
                    "option_b": "Option 2",
                    "option_c": "Option 3",
                    "option_d": "Option 4",
                    "score": 30,
                    "correct_option": "Opsi B"
                },
                {
                    "id": 4,
                    "question": "Sample Question 4",
                    "option_a": "Option 1",
                    "option_b": "Option 2",
                    "option_c": "Option 3",
                    "option_d": "Option 4",
                    "score": 30,
                    "correct_option": "Opsi D"
                }
             ]

        }
        response = self.client.put(f'/api/know/quiz', edit_data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_bulk_edit_and_add_more_quiz(self):

        response = self.client.post('/api/know/quiz', self.quiz_data, format='json')
        self.assertEqual(response.status_code, 201)
       
        edit_data = {
             "questions": [
                {
                    "id": 1,
                    "question": "Sample Question 1",
                    "option_a": "Option 1",
                    "option_b": "Option 2",
                    "option_c": "Option 3",
                    "option_d": "Option 4",
                    "score": 30,
                    "correct_option": "Opsi C"
                },
                {
                    "id": 2,
                    "question": "Sample Question 2",
                    "option_a": "Option 1",
                    "option_b": "Option 2",
                    "option_c": "Option 3",
                    "option_d": "Option 4",
                    "score": 30,
                    "correct_option": "Opsi A"
                },
                {
                    "id": 3,
                    "question": "Sample Question 3",
                    "option_a": "Option 1",
                    "option_b": "Option 2",
                    "option_c": "Option 3",
                    "option_d": "Option 4",
                    "score": 30,
                    "correct_option": "Opsi B"
                },
                {
                    "id": 4,
                    "question": "Sample Question 4",
                    "option_a": "Option 1",
                    "option_b": "Option 2",
                    "option_c": "Option 3",
                    "option_d": "Option 4",
                    "score": 30,
                    "correct_option": "Opsi D"
                },
                {
                    "id": 0,
                    "question": "Sample Question 5",
                    "option_a": "Option 1",
                    "option_b": "Option 2",
                    "option_c": "Option 3",
                    "option_d": "Option 4",
                    "score": 40,
                    "correct_option": "Opsi D"
                }
             ]

        }
        response = self.client.put(f'/api/know/quiz', edit_data, format='json')
        self.assertEqual(response.status_code, 200)



    def test_bulk_create_quiz_by_non_assigned_lecturer(self):
        # Test bulk create quiz by non assigned lecturer
        client, lecturer = lecturer_api_client_second()
        response = client.post('/api/know/quiz', self.quiz_data, format='json')
        self.assertEqual(response.status_code, 403)
