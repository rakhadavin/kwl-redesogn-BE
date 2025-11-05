from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from ..models import Kuesioner, GuestQuizAttempt, Question, Choice, KuesionerSession, GuestQuizAnswer
import random
import json

class TeacherConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.kuesioner_id = self.scope['url_route']['kwargs']['kuesioner_id']
            self.kuesioner_group_name = f'kuesioner_{self.kuesioner_id}_teacher'
            self.user = self.scope["user"]

            if self.user.is_anonymous:
                await self.close()
                return
            
            is_lecturer = await self.check_if_lecturer_owner()
            if not is_lecturer:
                await self.close()
                return
            
            await self.channel_layer.group_add(
                self.kuesioner_group_name,
                self.channel_name
            )
            await self.accept()

            try:
                pin = await self.activate_lobby()
                kuesioner_status = await self.check_status_kuesioner()
                await self.send(text_data=json.dumps({
                    'type': 'kuesioner_status',
                    'pin': pin,
                    'kuesioner_status': kuesioner_status.get('kuesioner_status'),
                    'question_type': kuesioner_status.get('question_type'),
                }))

                participants = await self.get_participant()
                await self.send(text_data=json.dumps({
                    'type': 'participant',
                    'participants': participants,
                }))

            except Exception as send_error:
                print(f"⚠️ Failed to send initial data to teacher: {send_error}")

        except KeyError as e:
            print(f"❌ KeyError in QuizTeacherConsumer.connect: {e}")
            await self.safe_close()
        except Exception as e:
            print(f"❌ Error in QuizTeacherConsumer.connect: {e}")
            await self.safe_close()

    async def disconnect(self, close_code):
        """Handle WebSocket disconnect with cleanup"""
        try:
            # Cleanup session and check if cleanup happened
            cleanup_happened = await self.cleanup_session()
            
            # If cleanup happened, notify all guests about session end
            if cleanup_happened:
                await self.notify_guests_session_ended()
            
            await self.channel_layer.group_discard(
                self.kuesioner_group_name,
                self.channel_name
            )
        except Exception as e:
            print(f"⚠️ Error during teacher disconnect: {e}")

    async def receive(self, text_data):
        """Receive message from WebSocket"""
        try:
            data = json.loads(text_data)
            action = data.get('action')

            if action == 'start_kuesioner':
                # Update kuesioner status
                result = await self.start_kuesioner()
                if result:
                    kuesioner_status = result['kuesioner_status']
                    question_type = result['question_type']
                    
                    # Send status update to teacher and guests
                    status_message = {
                        'type': 'kuesioner_status',
                        'kuesioner_status': kuesioner_status,
                        'question_type': question_type,
                    }
                    
                    # Send to teacher
                    await self.send(text_data=json.dumps(status_message))
                    
                    # Send to guests
                    guests_group_name = f'kuesioner_{self.kuesioner_id}_guests'
                    await self.channel_layer.group_send(
                        guests_group_name,
                        {
                            'type': 'kuesioner_status_update',
                            'message': status_message
                        }
                    )
                    
                    if question_type == "Polling":
                        question_data = await self.get_question_by_number(1)
                        if question_data:
                            question_message = {
                                'type': 'question',
                                'question': question_data['question'],
                                'choices': question_data['choices'],
                                'question_number': question_data['question_number'],
                                'total_questions': question_data['total_questions']
                            }
                            
                            # Send to teacher
                            await self.send(text_data=json.dumps(question_message))
                            
                            # Send to guests
                            await self.channel_layer.group_send(
                                guests_group_name,
                                {
                                    'type': 'question_update',
                                    'message': question_message
                                }
                            )

            elif action == 'get_question':
                question_number = data.get('question_number', 1)
                question_data = await self.get_question_by_number(question_number)
                
                if question_data:
                    question_message = {
                        'type': 'question',
                        'question': question_data['question'],
                        'choices': question_data['choices'],
                        'question_number': question_data['question_number'],
                        'total_questions': question_data['total_questions']
                    }
                    
                    # Send to teacher
                    await self.send(text_data=json.dumps(question_message))
                    
                    # Send to guests
                    guests_group_name = f'kuesioner_{self.kuesioner_id}_guests'
                    await self.channel_layer.group_send(
                        guests_group_name,
                        {
                            'type': 'question_update',
                            'message': question_message
                        }
                    )
                else:
                    await self.send(text_data=json.dumps({
                        'type': 'error',
                        'message': f'Question {question_number} not found'
                    }))

            elif action == 'get_polling_results':
                question_id = data.get('question_id')
                if question_id:
                    polling_results = await self.get_polling_results(question_id)
                    if polling_results:
                        await self.send(text_data=json.dumps(polling_results))
                    else:
                        await self.send(text_data=json.dumps({
                            'type': 'error',
                            'message': 'No polling results found'
                        }))
                else:
                    await self.send(text_data=json.dumps({
                        'type': 'error',
                        'message': 'Question ID is required'
                    }))

        except Exception as e:
            print(f"❌ Error in TeacherConsumer.receive: {e}")

    async def notify_guests_session_ended(self):
        """Notify all guests that session has ended due to teacher disconnect"""
        try:
            guests_group_name = f'kuesioner_{self.kuesioner_id}_guests'
            
            await self.channel_layer.group_send(
                guests_group_name,
                {
                    'type': 'session_ended_notification',
                    'message': {
                        'type': 'kuesioner_status',
                        'kuesioner_status': {
                            'is_started': False,
                            'is_lobby': False,
                            'if_finished': False
                        },
                        'session_ended': True,
                        'reason': 'teacher_disconnect',
                        'message': 'Session ended because teacher disconnected'
                    }
                }
            )
            print(f"✅ Notified guests in group {guests_group_name} about session end")
            
        except Exception as e:
            print(f"❌ Error notifying guests: {e}")

    async def participant(self, event):
        """Handle participant updates"""
        try:
            participants = await self.get_participant()
            await self.send(text_data=json.dumps({
                'type': 'participant',
                'participants': participants,
            }))
        except Exception as e:
            print(f"❌ Error in participant handler: {e}")

    async def polling_results_update(self, event):
        """Handle polling results updates"""
        try:
            message = event['message']
            await self.send(text_data=json.dumps(message))
            print(f"✅ Sent polling results to teacher for question {message.get('question', {}).get('number', 'unknown')}")
        except Exception as e:
            print(f"❌ Error in polling_results_update handler: {e}")

    @database_sync_to_async
    def cleanup_session(self):
        """Cleanup session data when teacher disconnects"""
        try:
            kuesioner = Kuesioner.objects.get(id=self.kuesioner_id)
            if not kuesioner.if_finished:
                active_session = KuesionerSession.objects.filter(
                    kuesioner=kuesioner,
                    is_active=True
                ).order_by('-started_at').first()
                
                if active_session:
                    guest_attempts = GuestQuizAttempt.objects.filter(session=active_session)
                    if kuesioner.is_started:
                        GuestQuizAnswer.objects.filter(
                            guest__in=guest_attempts
                        ).delete()
                        print(f"✅ Deleted GuestQuizAnswer for session {active_session.id}")
                    
                    attempts_count = guest_attempts.count()
                    guest_attempts.delete()
                    
                    session_id = active_session.id
                    active_session.delete()
                    
                kuesioner.is_started = False
                kuesioner.is_lobby = False
                kuesioner.save()
                return True
            else:
                print(f"ℹ️ Kuesioner {kuesioner.id} is finished, skipping cleanup")
                return False
            
        except Kuesioner.DoesNotExist:
            print(f"❌ Kuesioner {self.kuesioner_id} does not exist during cleanup")
            return False
        except Exception as e:
            print(f"❌ Error in cleanup_session: {e}")
            return False

    @database_sync_to_async
    def start_kuesioner(self):
        """Start kuesioner and update status"""
        try:
            kuesioner = Kuesioner.objects.get(id=self.kuesioner_id)
            kuesioner.is_started = True
            kuesioner.is_lobby = False
            kuesioner.save()
            
            kuesioner_status = {
                'is_started': kuesioner.is_started,
                'if_finished': kuesioner.if_finished,
                'is_lobby': kuesioner.is_lobby,
            }
            return {
                'kuesioner_status': kuesioner_status,
                'question_type': kuesioner.question_type
            }
        except Kuesioner.DoesNotExist:
            print(f"❌ Kuesioner {self.kuesioner_id} does not exist")
            return None
        except Exception as e:
            print(f"❌ Error in start_kuesioner: {e}")
            return None

    @database_sync_to_async
    def get_question_by_number(self, question_number):
        """Get question and choices by question number"""
        try:
            kuesioner = Kuesioner.objects.get(id=self.kuesioner_id)
            question = Question.objects.filter(
                kuesioner=kuesioner,
                number=question_number
            ).first()
            
            if not question:
                print(f"❌ Question {question_number} not found for kuesioner {self.kuesioner_id}")
                return None
            
            choices = Choice.objects.filter(question=question).values(
                'id', 'choice_text', 'is_correct'
            )
            
            total_questions = Question.objects.filter(kuesioner=kuesioner).count()
            
            question_data = {
                'question': {
                    'id': str(question.id),
                    'question_text': question.question_text,
                    'time_limit': question.time_limit,
                    'score': question.score,
                    'number': question.number
                },
                'choices': [
                    {
                        'id': str(choice['id']),
                        'choice_text': choice['choice_text'],
                        'is_correct': choice['is_correct']
                    }
                    for choice in choices
                ],
                'question_number': question_number,
                'total_questions': total_questions
            }
            
            return question_data
            
        except Kuesioner.DoesNotExist:
            print(f"❌ Kuesioner {self.kuesioner_id} does not exist")
            return None
        except Exception as e:
            print(f"❌ Error in get_question_by_number: {e}")
            return None

    @database_sync_to_async
    def get_polling_results(self, question_id):
        """Get polling results for a specific question"""
        try:
            from ..tasks.polling import get_polling_results
            results = get_polling_results(self.kuesioner_id, question_id)
            if results:
                results['type'] = 'polling_results'
            return results
        except Exception as e:
            print(f"❌ Error in get_polling_results: {e}")
            return None
        # """Check if user is lecturer who owns this kuesioner"""
        # try:
        #     if not hasattr(self.user, 'lecturer_profile'):
        #         print(f"User {self.user.username} has no lecturer_profile")
        #         return False

        #     kuesioner = Kuesioner.objects.get(id=self.kuesioner_id)
        #     lecturer_profile = self.user.lecturer_profile
        #     is_owner = kuesioner.lecturer_team.filter(id=lecturer_profile.id).exists()
        #     return is_owner
        # except Kuesioner.DoesNotExist:
        #     print(f"Kuesioner {self.kuesioner_id} does not exist")
        #     return False
        # except Exception as e:
        #     print(f"Error in check_if_lecturer_owner: {e}")
        #     return False
        
    @database_sync_to_async
    def activate_lobby(self):
        """Activate lobby and generate kuesioner PIN"""
        try:
            kuesioner = Kuesioner.objects.get(id=self.kuesioner_id)
            
            kuesioner.is_lobby = True
            kuesioner.pin = random.randint(100000, 999999)
            kuesioner.save()

            last_session = KuesionerSession.objects.filter(
                kuesioner=kuesioner
            ).order_by('-session_number').first()
            
            next_session_number = 1 if not last_session else last_session.session_number + 1
            new_session = KuesionerSession.objects.create(
                kuesioner=kuesioner,
                session_number=next_session_number,
                started_by=self.user.lecturer_profile if hasattr(self.user, 'lecturer_profile') else None,
                is_active=True,
                total_participants=0  # Start with 0 participants
            )
            
            print(f"✅ Created new KuesionerSession: {new_session.id} (Session #{next_session_number})")
            return kuesioner.pin
        except Kuesioner.DoesNotExist:
            print(f"❌ Kuesioner {self.kuesioner_id} does not exist")
            return None
        except Exception as e:
            print(f"❌ Error in activate_lobby: {e}")
            return None
        
    @database_sync_to_async
    def check_status_kuesioner(self):
        try:
            kuesioner = Kuesioner.objects.get(id=self.kuesioner_id)
            kuesioner_status = {
                'is_started': kuesioner.is_started,
                'if_finished': kuesioner.if_finished,
                'is_lobby': kuesioner.is_lobby,
            }
            question_type = kuesioner.question_type

            return {
                'kuesioner_status': kuesioner_status,
                'question_type': question_type
            }
        except Kuesioner.DoesNotExist:
            print(f"Kuesioner {self.kuesioner_id} does not exist")
            return None
        
    @database_sync_to_async
    def get_participant(self):
        try:
            kuesioner = Kuesioner.objects.get(id=self.kuesioner_id)
            
            # Get current active session
            active_session = KuesionerSession.objects.filter(
                kuesioner=kuesioner,
                is_active=True
            ).order_by('-started_at').first()
            
            if active_session:
                # Get participants from current session only
                participants = GuestQuizAttempt.objects.filter(session=active_session)
            else:
                # If no active session, return empty list
                participants = GuestQuizAttempt.objects.none()
            
            participants_data = [
                {
                    'id': str(participant.id),
                    'guest_name': participant.guest_name,
                    'joined_at': participant.created_at.isoformat(),
                    'session_id': str(participant.session.id) if participant.session else None,
                }
                for participant in participants
            ]
            return participants_data
        except Kuesioner.DoesNotExist:
            print(f"Kuesioner {self.kuesioner_id} does not exist")
            return []

    @database_sync_to_async
    def check_if_lecturer_owner(self):
        """Check if user is lecturer who owns this kuesioner"""
        try:
            if not hasattr(self.user, 'lecturer_profile'):
                print(f"User {self.user.username} has no lecturer_profile")
                return False

            kuesioner = Kuesioner.objects.get(id=self.kuesioner_id)
            lecturer_profile = self.user.lecturer_profile
            is_owner = kuesioner.lecturer_team.filter(id=lecturer_profile.id).exists()
            return is_owner
        except Kuesioner.DoesNotExist:
            print(f"Kuesioner {self.kuesioner_id} does not exist")
            return False
        except Exception as e:
            print(f"Error in check_if_lecturer_owner: {e}")
            return False

    async def safe_close(self, code=4000):
        """Safely close the WebSocket connection with error handling"""
        try:
            await self.close(code=code)
        except Exception as e:
            print(f"⚠️ Error during teacher safe_close: {e}")

    