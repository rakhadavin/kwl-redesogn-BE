import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .models import Quiz, GuestQuizAttempt, Question, StudentQuizAnswer, Choice
import random

class QuizTeacherConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for quiz Teacher"""
    async def connect(self):
      try:
        self.quiz_id = self.scope['url_route']['kwargs']['quiz_id']
        self.quiz_group_name = f'quiz_{self.quiz_id}_teacher'
        self.user = self.scope["user"]
    
        if self.user.is_anonymous:
            await self.close()
            return

        is_lecturer = await self.check_if_lecturer_owner()
        if not is_lecturer:
            await self.close()
            return
        
        await self.channel_layer.group_add(
            self.quiz_group_name,
            self.channel_name
        )
        await self.accept()

        quiz_pin = await self.activate_lobby()
        quiz_status = await self.get_quiz_status()

        await self.send(text_data=json.dumps({
            'type': 'lobby_activated',
            'quiz_pin': quiz_pin,
            'quiz_status': quiz_status,
        }))

      except KeyError as e:
          print(f"KeyError in QuizTeacherConsumer.connect: {e}")
          await self.close()
      except Exception as e:
          print(f"Error in QuizTeacherConsumer.connect: {e}")
          await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'quiz_id') and self.quiz_id:
            pin = await self.deactivate_lobby()
        if hasattr(self, 'quiz_lobby_group_name'):
            await self.channel_layer.group_discard(
                self.quiz_lobby_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        """Handle messages dari frontend teacher"""
        try:
            data = json.loads(text_data)
            action = data.get('action')

            if action == 'start_quiz':
                await self.start_quiz()
        
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))

    async def participant(self, event):
        await self.send(text_data=json.dumps({
            'type': 'participant',
            'participants': event['participants'],
            'quiz_status': event.get('quiz_status', {})
        }))
    
    @database_sync_to_async
    def check_if_lecturer_owner(self):
        """Check if user is lecturer who owns this quiz"""
        try:
            if not hasattr(self.user, 'lecturer_profile'):
                print(f"User {self.user.username} has no lecturer_profile")
                return False
            
            quiz = Quiz.objects.get(id=self.quiz_id)
            is_owner = quiz.lecturer_team.filter(id=self.user.id).exists()
            return is_owner
        except Quiz.DoesNotExist:
            print(f"Quiz {self.quiz_id} does not exist")
            return False
        except Exception as e:
            print(f"Error in check_if_lecturer_owner: {e}")
            return False
        
    @database_sync_to_async
    def activate_lobby(self):
        """Activate lobby and generate quiz PIN"""
        try:
            quiz = Quiz.objects.get(id=self.quiz_id)
            quiz.is_lobby = True
            quiz.quiz_pin = random.randint(100000, 999999)
            quiz.save()
            return quiz.quiz_pin
        except Quiz.DoesNotExist:
            return None
        
    @database_sync_to_async
    def get_quiz_status(self):
        try:
            quiz = Quiz.objects.get(id=self.quiz_id)
            return {
                'is_started': quiz.is_started,
                'if_finished': quiz.if_finished,
                'is_lobby': quiz.is_lobby,
            }
        except Quiz.DoesNotExist:
            return None
        
    @database_sync_to_async
    def deactivate_lobby(self):
        """Deactivate lobby and reset quiz PIN"""
        try:
            quiz = Quiz.objects.get(id=self.quiz_id)
            if not quiz.if_finished:
                quiz.is_started = False
                quiz.is_lobby = False
                quiz.quiz_pin = 0
                quiz.save()

                guest = GuestQuizAttempt.objects.filter(quiz=quiz, completed_at__isnull=True)
                guest.delete()
                
            return quiz.quiz_pin
        except Quiz.DoesNotExist:
            return None
        
    @database_sync_to_async
    def start_quiz(self):
        """Start quiz - akan trigger signal yang jalankan Celery task"""
        try:
            quiz = Quiz.objects.get(id=self.quiz_id)
            quiz.is_started = True
            quiz.is_lobby = False  # Tutup lobby
            quiz.save()  # Ini akan trigger signal!
            return True
        except Exception as e:
            print(f"Error starting quiz: {e}")
            return False
        

class QuizGuestConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.guest_id = self.scope['url_route']['kwargs']['guest_id']
            is_guest = await self.check_if_valid_guest()
            if not is_guest:
                await self.close()
                return

            self.quiz_id = await self.get_quiz_id_for_guest()
            self.quiz_room_group_name = f'quiz_{self.quiz_id}'
            await self.channel_layer.group_add(
                  self.quiz_room_group_name,
                  self.channel_name
              )
            await self.accept()

            quiz_status = await self.get_quiz_status()
            await self.send(text_data=json.dumps({
                'type': 'quiz_status',
                'quiz_status': quiz_status
            }))
          
        except KeyError as e:
            print(f"KeyError in QuizGuestConsumer.connect: {e}")
            await self.close()
        except Exception as e:
            print(f"Error in QuizGuestConsumer.connect: {e}")
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'quiz_id') and self.quiz_id:
            self.is_game_active = await self.check_if_game_finished()
            if not self.is_game_active:
                await self.remove_guest_from_active_list()

        if hasattr(self, 'quiz_room_group_name'):
            await self.channel_layer.group_discard(
                self.quiz_room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        """Handle messages dari frontend guest"""
        try:
            data = json.loads(text_data)
            action = data.get('action')

            if action == 'submit_answer':
                question_id = data.get('question_id')
                selected_choice_ids = data.get('selected_choice_ids', [])

                await self.save_answer(question_id, selected_choice_ids)

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
        except Exception as e:
            print(f"Error in receive: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    async def participant(self, event):
        await self.send(text_data=json.dumps({
            'type': 'participant',
            'participants': event['participants'],
            'quiz_status': event.get('quiz_status', {})
        }))

    @database_sync_to_async
    def check_if_valid_guest(self):
        """Check if guest_id corresponds to a valid GuestQuizAttempt"""
        try:
            guest_attempt = GuestQuizAttempt.objects.get(id=self.guest_id)
            return True
        except GuestQuizAttempt.DoesNotExist:
            return False
        
    @database_sync_to_async
    def get_quiz_id_for_guest(self):
        """Get the quiz ID associated with this guest attempt"""
        try:
            guest_attempt = GuestQuizAttempt.objects.get(id=self.guest_id)
            self.quiz_id = str(guest_attempt.quiz.id)
            return self.quiz_id
        except GuestQuizAttempt.DoesNotExist:
            return None
        

    @database_sync_to_async
    def get_quiz_status(self):
        """Get current quiz status"""
        try:
            quiz = Quiz.objects.get(id=self.quiz_id)
            return {
                'is_started': quiz.is_started,
                'if_finished': quiz.if_finished,
                'is_lobby': quiz.is_lobby,
            }
        except Quiz.DoesNotExist:
            return None

    @database_sync_to_async
    def check_if_game_finished(self):
        """Check if the quiz has finished"""
        try:
            quiz = Quiz.objects.get(id=self.quiz_id)
            return quiz.if_finished
        except Quiz.DoesNotExist:
            return False
        
    @database_sync_to_async
    def remove_guest_from_active_list(self):
        """Remove guest from active participants list when they disconnect"""
        try:
            if hasattr(self, 'guest_id') and self.guest_id:
                guest_attempt = GuestQuizAttempt.objects.get(id=self.guest_id)
                quiz = guest_attempt.quiz
                
                if quiz.is_lobby and not quiz.is_started:
                    orphaned_answers = StudentQuizAnswer.objects.filter(
                        question__quiz=quiz,
                        student__isnull=True
                    )
                    if orphaned_answers.exists():
                        orphaned_answers.delete()
                guest_attempt.delete()
                return True
            return False
        except GuestQuizAttempt.DoesNotExist:
            print(f"Guest attempt {self.guest_id} not found")
            return False
        except Exception as e:
            print(f"Error removing guest from active list: {e}")
            return False
        
    @database_sync_to_async
    def save_answer(self, question_id, selected_choice_ids):
        """Simpan jawaban guest"""
        try:
            guest_attempt = GuestQuizAttempt.objects.get(id=self.guest_id)
            question = Question.objects.get(id=question_id)
            
            # Buat atau update answer
            # Karena model Anda belum support guest_attempt, kita simpan dengan student=None
            answer, created = StudentQuizAnswer.objects.get_or_create(
                question=question,
                student=None,  # Guest answer
                defaults={'created_at': question.quiz.created_at}
            )
            
            # Clear dan set choices
            answer.selected_choices.clear()
            
            for choice_id in selected_choice_ids:
                try:
                    choice = Choice.objects.get(id=choice_id, question=question)
                    answer.selected_choices.add(choice)
                except Choice.DoesNotExist:
                    print(f"Choice {choice_id} not found")
            
            print(f"Answer saved for guest {self.guest_id}, question {question_id}")
            return True
            
        except Exception as e:
            print(f"Error saving answer: {e}")
            return False