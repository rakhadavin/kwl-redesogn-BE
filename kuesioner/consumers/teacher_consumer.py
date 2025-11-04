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
                    print(f"✅ Deleted {attempts_count} GuestQuizAttempt for session {active_session.id}")
                    
                    session_id = active_session.id
                    active_session.delete()
                    print(f"✅ Deleted KuesionerSession {session_id}")
                
                # Reset kuesioner status only if not finished
                kuesioner.is_started = False
                kuesioner.is_lobby = False
                kuesioner.save()
                print(f"✅ Reset kuesioner {kuesioner.id} status (keeping if_finished={kuesioner.if_finished})")
                
                # Return True to indicate cleanup happened (for notification)
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
                is_active=True
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

    async def safe_close(self, code=4000):
        """Safely close the WebSocket connection with error handling"""
        try:
            await self.close(code=code)
        except Exception as e:
            print(f"⚠️ Error during teacher safe_close: {e}")