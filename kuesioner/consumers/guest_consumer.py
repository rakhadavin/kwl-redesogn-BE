from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from ..models import Kuesioner, GuestQuizAttempt, Question, Choice, KuesionerSession
import json

class GuestConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.guest_id = self.scope['url_route']['kwargs']['guest_id']
            guest_info = await self.get_guest_info()
            if not guest_info:
                await self.close(code=4404)
                return
            
            self.kuesioner_id = guest_info['kuesioner_id']
            self.guest_name = guest_info['guest_name']
            self.kuesioner_group_name = f'kuesioner_{self.kuesioner_id}_guests'

            kuesioner_info = await self.get_kuesioner_info()
            if not kuesioner_info:
                await self.close(code=4404)
                return

            if not kuesioner_info['is_lobby']:
                await self.close(code=4403)
                return

            await self.channel_layer.group_add(
                self.kuesioner_group_name,
                self.channel_name
            )
            await self.accept()

            kuesioner_status = await self.check_status_kuesioner()
            await self.send(text_data=json.dumps({
                    'type': 'kuesioner_status',
                    'kuesioner_status': kuesioner_status.get('kuesioner_status'),
                    'question_type': kuesioner_status.get('question_type'),
                }))

        except Exception as e:
            print(f"❌ Error in GuestConsumer.connect: {e}")
            await self.safe_close()

    @database_sync_to_async
    def get_guest_info(self):
        """Get guest information from guest_id"""
        try:
            guest_attempt = GuestQuizAttempt.objects.select_related(
                'kuesioner', 'session'
            ).get(id=self.guest_id)
            
            return {
                'guest_name': guest_attempt.guest_name,
                'kuesioner_id': str(guest_attempt.kuesioner.id),
                'session_id': str(guest_attempt.session.id) if guest_attempt.session else None,
                'session_number': guest_attempt.session.session_number if guest_attempt.session else None
            }
        except GuestQuizAttempt.DoesNotExist:
            print(f"❌ GuestQuizAttempt {self.guest_id} does not exist")
            return None
        except Exception as e:
            print(f"❌ Error in get_guest_info: {e}")
            return None

    @database_sync_to_async
    def get_kuesioner_info(self):
        """Get kuesioner information"""
        try:
            kuesioner = Kuesioner.objects.get(id=self.kuesioner_id)
            return {
                'id': str(kuesioner.id),
                'title': kuesioner.title,
                'pin': kuesioner.pin,
                'is_lobby': kuesioner.is_lobby,
                'is_started': kuesioner.is_started,
                'if_finished': kuesioner.if_finished,
                'question_type': kuesioner.question_type
            }
        except Kuesioner.DoesNotExist:
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

    async def disconnect(self, close_code):
        """Handle WebSocket disconnect"""
        try:
            # Check if we need to clean up guest data (if kuesioner is not finished)
            if hasattr(self, 'guest_id') and hasattr(self, 'kuesioner_id'):
                await self.cleanup_guest_on_disconnect()
            
            # Remove from group
            if hasattr(self, 'kuesioner_group_name'):
                await self.channel_layer.group_discard(
                    self.kuesioner_group_name,
                    self.channel_name
                )
        except Exception as e:
            print(f"⚠️ Error during guest disconnect: {e}")

    @database_sync_to_async
    def cleanup_guest_on_disconnect(self):
        """Clean up guest data when disconnecting if kuesioner is not finished"""
        try:
            from ..models import GuestQuizAnswer
            
            # Get kuesioner status
            kuesioner = Kuesioner.objects.get(id=self.kuesioner_id)
            
            # Only clean up if kuesioner is not finished
            if not kuesioner.if_finished:
                # Get guest attempt
                guest_attempt = GuestQuizAttempt.objects.get(id=self.guest_id)
                
                # Delete all answers related to this guest
                GuestQuizAnswer.objects.filter(guest=guest_attempt).delete()
                
                # Update session participant count if there's a session
                if guest_attempt.session:
                    session = guest_attempt.session
                    session.total_participants = max(0, session.total_participants - 1)
                    session.save()
                    print(f"🔄 Updated session {session.session_number} participant count to {session.total_participants}")
                
                # Delete the guest attempt
                guest_attempt.delete()
                
                print(f"🧹 Cleaned up data for guest {getattr(self, 'guest_name', 'unknown')} (ID: {self.guest_id})")
            else:
                print(f"ℹ️ Kuesioner finished - keeping guest data for {getattr(self, 'guest_name', 'unknown')}")
                
        except Kuesioner.DoesNotExist:
            print(f"❌ Kuesioner {self.kuesioner_id} not found during cleanup")
        except GuestQuizAttempt.DoesNotExist:
            print(f"❌ GuestQuizAttempt {self.guest_id} not found during cleanup")
        except Exception as e:
            print(f"❌ Error in cleanup_guest_on_disconnect: {e}")

    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')

            if message_type == 'submit_answer':
                # Handle answer submission
                result = await self.submit_answer(text_data_json)
                await self.send(text_data=json.dumps({
                    'type': 'answer_submitted',
                    'success': result is not None,
                    'data': result
                }))
                
            elif message_type == 'get_session_info':
                session_info = await self.get_current_session_info()
                await self.send(text_data=json.dumps({
                    'type': 'session_info',
                    'session': session_info
                }))

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
        except Exception as e:
            print(f"❌ Error in guest receive: {e}")

    @database_sync_to_async
    def submit_answer(self, data):
        """Submit answer for current guest"""
        try:
            from ..models import GuestQuizAnswer
            
            guest_attempt = GuestQuizAttempt.objects.get(id=self.guest_id)
            question_id = data.get('question_id')
            
            if not question_id:
                return None
                
            question = Question.objects.get(id=question_id)
            
            # Create or update answer
            answer, created = GuestQuizAnswer.objects.get_or_create(
                guest=guest_attempt,
                question=question,
                defaults={
                    'text_answer': data.get('text_answer', '')
                }
            )
            
            if not created:
                answer.text_answer = data.get('text_answer', '')
                answer.save()
            
            # Handle selected choices for multiple choice
            selected_choice_ids = data.get('selected_choices', [])
            if selected_choice_ids:
                choices = Choice.objects.filter(id__in=selected_choice_ids)
                answer.selected_choices.set(choices)
            
            return {
                'answer_id': str(answer.id),
                'question_id': str(question.id),
                'submitted_at': answer.created_at.isoformat()
            }
            
        except (GuestQuizAttempt.DoesNotExist, Question.DoesNotExist) as e:
            print(f"❌ Error in submit_answer: {e}")
            return None
        except Exception as e:
            print(f"❌ Error in submit_answer: {e}")
            return None

    @database_sync_to_async
    def get_current_session_info(self):
        """Get current session information"""
        try:
            guest_attempt = GuestQuizAttempt.objects.select_related(
                'session', 'kuesioner'
            ).get(id=self.guest_id)
            
            if guest_attempt.session:
                return {
                    'session_id': str(guest_attempt.session.id),
                    'session_number': guest_attempt.session.session_number,
                    'total_participants': guest_attempt.session.total_participants,
                    'started_at': guest_attempt.session.started_at.isoformat(),
                    'kuesioner_status': {
                        'is_lobby': guest_attempt.kuesioner.is_lobby,
                        'is_started': guest_attempt.kuesioner.is_started,
                        'if_finished': guest_attempt.kuesioner.if_finished
                    }
                }
            return None
            
        except GuestQuizAttempt.DoesNotExist:
            print(f"❌ GuestQuizAttempt {self.guest_id} does not exist")
            return None
        except Exception as e:
            print(f"❌ Error in get_current_session_info: {e}")
            return None

    async def session_ended_notification(self, event):
        """Handle session ended notification from teacher"""
        try:
            message = event['message']
            await self.send(text_data=json.dumps(message))
            print(f"✅ Sent session ended notification to guest {getattr(self, 'guest_name', 'unknown')}")
            
            # Optionally close the connection after a short delay
            # await asyncio.sleep(2)
            # await self.close(code=4000)
            
        except Exception as e:
            print(f"❌ Error sending session ended notification: {e}")

    async def safe_close(self, code=4000):
        """Safely close the WebSocket connection"""
        try:
            await self.close(code=code)
        except Exception as e:
            print(f"⚠️ Error during guest safe_close: {e}")
