from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Course, Topic, StudentActivity
from django.utils import timezone
import json

class CourseNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]

        if user.is_anonymous:
            await self.close()
            return

        self.course_id = self.scope['url_route']['kwargs']['course_id']
        self.topic_id = self.scope['url_route']['kwargs']['topic_id']
        self.user = user
        self.groups_joined = []

        # Check user type safely with database_sync_to_async
        user_type = await self.check_user_type(user)
        self.user_type = user_type

        course_access = await self.check_course_topic_access(user, self.course_id)
        if not course_access:
            await self.close()
            return
        
        await self.accept()
        await self.join_user_groups()

        if self.user_type['is_lecturer']:
            active_students = await self.get_active_students()
            await self.send(text_data=json.dumps({
                'type': 'active_students_list',
                'active_students': active_students
            }))

    @database_sync_to_async
    def check_user_type(self, user):
        """Check if user is student or lecturer safely"""
        try:
            has_student = hasattr(user, 'student') and user.student is not None
            has_lecturer = hasattr(user, 'lecturer_profile') and user.lecturer_profile is not None
            
            student_id = None
            if has_student:
                student_id = user.student.id
                
            return {
                'is_student': has_student,
                'is_lecturer': has_lecturer,
                'student_id': student_id
            }
        except Exception as e:
            print(f"Error checking user type: {e}")
            return {'is_student': False, 'is_lecturer': False, 'student_id': None}

    async def join_user_groups(self):
        if self.user_type['is_lecturer']:
            course_group = f'course_{self.course_id}_topic_{self.topic_id}_lecturers'
            await self.channel_layer.group_add(
                course_group,
                self.channel_name
            )
            self.groups_joined.append(course_group)

        if self.user_type['is_student']:
            course_group = f'course_{self.course_id}_topic_{self.topic_id}_students'
            await self.channel_layer.group_add(
                course_group,
                self.channel_name
            )
            self.groups_joined.append(course_group)

    async def disconnect(self, close_code):
        for group in self.groups_joined:
            await self.channel_layer.group_discard(
                group,
                self.channel_name
            )

        if self.user_type['is_student'] and self.user_type['student_id']:
            await self.delete_student_activity(
                self.user_type['student_id'],
                self.course_id
            )
            
            active_students = await self.get_active_students()
            await self.channel_layer.group_send(
                f'course_{self.course_id}_topic_{self.topic_id}_lecturers',
                {
                    'type': 'active_students_list_broadcast',
                    'active_students': active_students
                }
            )

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'topic_view' and self.user_type['is_student']:
            topic_id = self.topic_id
            # topic_name = await self.get_topic_name(topic_id)
            
            # Save activity to DB
            success = await self.save_student_activity(
                self.user_type['student_id'],
                self.course_id,
                topic_id,
                'viewing_topic'
            )

            if success:
                active_students = await self.get_active_students()
                await self.channel_layer.group_send(
                    f'course_{self.course_id}_topic_{self.topic_id}_lecturers',
                    {
                        'type': 'active_students_list_broadcast',
                        'active_students': active_students
                    }
                )
                await self.send(text_data=json.dumps({
                    'type': 'active_students_list',
                    'active_students': active_students
                }))
            # active_students = await self.get_active_students()
            # await self.channel_layer.group_send(
            #     f'course_{self.course_id}_topic_{self.topic_id}_lecturers',
            #     {
            #         'type': 'active_students_list_broadcast',
            #         'active_students': active_students
            #     }
            # )
            # await self.send(text_data=json.dumps({
            #     'type': 'active_students_list',
            #     'active_students': active_students
            # }))

    async def active_students_list_broadcast(self, event):
        # Handler untuk broadcast ke lecturer group
        await self.send(text_data=json.dumps({
            'type': 'active_students_list',
            'active_students': event['active_students']
        }))

    @database_sync_to_async
    def check_course_topic_access(self, user, course_id):
        try:
            course = Course.objects.get(id=course_id)
            if hasattr(user, 'lecturer_profile'):
                return course.lecturer_team.filter(user=user).exists()
            if hasattr(user, 'student'):
                return course.students.filter(user=user).exists()
            return False
        except (Course.DoesNotExist, Topic.DoesNotExist):
            return False

    @database_sync_to_async
    def get_topic_name(self, topic_id):
        try:
            topic = Topic.objects.get(id=topic_id)
            return topic.name
        except Topic.DoesNotExist:
            return None

    @database_sync_to_async
    def save_student_activity(self, student_id, course_id, topic_id, activity_type):
        from authentication.models import Student
        try:
            student = Student.objects.get(id=student_id)
            course = Course.objects.get(id=course_id)
            topic = Topic.objects.get(id=topic_id) if topic_id else None
            activity, created = StudentActivity.objects.get_or_create(
                student=student,
                course=course,
                topic=topic,
                defaults={
                    'activity_type': activity_type,
                    'is_active': (activity_type == 'viewing_topic'),
                    'timestamp': timezone.now()
                }
            )
            if not created:
                activity.activity_type = activity_type
                activity.is_active = (activity_type == 'viewing_topic')
                activity.timestamp = timezone.now()
                activity.save()
            return True
        except Exception as e:
            print(f"Error saving student activity: {e}")
            return False

    @database_sync_to_async
    def delete_student_activity(self, student_id, course_id):
        try:
            StudentActivity.objects.filter(
                student_id=student_id,
                course_id=course_id
            ).delete()
        except Exception as e:
            print(f"Error deleting student activity: {e}")

    @database_sync_to_async
    def get_active_students(self):
        # Debug: print course_id, topic_id, and query
        try:
            # course_id = int(self.course_id)
            # topic_id = int(self.topic_id)
            print(f"get_active_students: course_id={self.course_id} (type={type(self.course_id)}), topic_id={self.topic_id} (type={type(self.topic_id)})")
            activities = StudentActivity.objects.filter(
                course_id=self.course_id,
                topic_id=self.topic_id,
                is_active=True
            )
            print(f"StudentActivity Query: course_id={self.course_id}, topic_id={self.topic_id}, is_active=True")
            print(f"Queryset count: {activities.count()}")
            result = []
            for activity in activities:
                print(f"Activity: student_id={activity.student.id}, course_id={activity.course.id}, topic_id={activity.topic.id if activity.topic else None}, is_active={activity.is_active}")
                result.append({
                    'student_id': activity.student.id,
                    'student_name': activity.student.user.get_full_name() or activity.student.user.username,
                    'topic_id': activity.topic.id if activity.topic else None,
                    'topic_name': activity.topic.name if activity.topic else None,
                    'last_activity': activity.timestamp.isoformat() if hasattr(activity, 'timestamp') and activity.timestamp else None
                })
            print(f"Active students result: {result}")
            return result
        except Exception as e:
            print(f"Error getting active students: {e}")
            return []