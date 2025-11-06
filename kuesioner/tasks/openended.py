from django.db.models import Count, Q
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from ..models import Question, Choice, GuestQuizAnswer, KuesionerSession, Kuesioner
import json

channel_layer = get_channel_layer()

def send_openended_responses_to_teacher(kuesioner_id, question_id):
    """
    Send real-time Open Ended responses to teacher for a specific question
    """
    try:
        question = Question.objects.get(id=question_id)
        kuesioner = Kuesioner.objects.get(id=kuesioner_id)
        
        if kuesioner.question_type != 'Open Ended':
            print(f"⚠️ Question {question.number} is not an Open Ended question, skipping responses")
            return
        
        active_session = KuesionerSession.objects.filter(
            kuesioner=kuesioner,
            is_active=True
        ).order_by('-started_at').first()
        
        if not active_session:
            print(f"⚠️ No active session found for kuesioner {kuesioner_id}")
            return
        
        # Get all text answers for this question
        answers = GuestQuizAnswer.objects.filter(
            question=question,
            guest__session=active_session,
            text_answer__isnull=False
        ).exclude(text_answer='').select_related('guest')
        
        responses = []
        for answer in answers:
            responses.append({
                'id': str(answer.id),
                'participant_name': answer.guest.guest_name,
                'participant_id': str(answer.guest.id),
                'answer': answer.text_answer,
                'submitted_at': answer.created_at.isoformat()
            })
        
        openended_responses = {
            'type': 'openended_responses',
            'question': {
                'id': str(question.id),
                'question_text': question.question_text,
                'number': question.number
            },
            'responses': responses,
            'total_responses': len(responses),
            'session_id': str(active_session.id),
            'session_participants': active_session.total_participants
        }
        
        teacher_group_name = f'kuesioner_{kuesioner_id}_teacher'
        
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                teacher_group_name,
                {
                    'type': 'openended_responses_update',
                    'message': openended_responses
                }
            )
            print(f"✅ Sent {len(responses)} Open Ended responses to teacher for question {question.number}")
        else:
            print(f"❌ Channel layer not available")
            
    except Question.DoesNotExist:
        print(f"❌ Question {question_id} does not exist")
    except Kuesioner.DoesNotExist:
        print(f"❌ Kuesioner {kuesioner_id} does not exist")
    except Exception as e:
        print(f"❌ Error in send_openended_responses_to_teacher: {e}")

def get_openended_responses(kuesioner_id, question_id):
    """
    Get Open Ended responses for a specific question (synchronous version)
    """
    try:
        question = Question.objects.get(id=question_id)
        kuesioner = Kuesioner.objects.get(id=kuesioner_id)
        
        if kuesioner.question_type != 'Open Ended':
            return None
        
        active_session = KuesionerSession.objects.filter(
            kuesioner=kuesioner,
            is_active=True
        ).order_by('-started_at').first()
        
        if not active_session:
            return None
        
        # Get all text answers for this question
        answers = GuestQuizAnswer.objects.filter(
            question=question,
            guest__session=active_session,
            text_answer__isnull=False
        ).exclude(text_answer='').select_related('guest').order_by('-created_at')
        
        responses = []
        for answer in answers:
            responses.append({
                'id': str(answer.id),
                'participant_name': answer.guest.guest_name,
                'participant_id': str(answer.guest.id),
                'answer': answer.text_answer,
                'submitted_at': answer.created_at.isoformat()
            })
        
        return {
            'question': {
                'id': str(question.id),
                'question_text': question.question_text,
                'number': question.number
            },
            'responses': responses,
            'total_responses': len(responses),
            'session_id': str(active_session.id),
            'session_participants': active_session.total_participants
        }
        
    except (Question.DoesNotExist, Kuesioner.DoesNotExist) as e:
        print(f"❌ Error in get_openended_responses: {e}")
        return None
    except Exception as e:
        print(f"❌ Error in get_openended_responses: {e}")
        return None

def get_all_openended_responses(kuesioner_id):
    """
    Get Open Ended responses for ALL questions in a kuesioner (for quiz finish)
    """
    try:
        kuesioner = Kuesioner.objects.get(id=kuesioner_id)
        
        if kuesioner.question_type != 'Open Ended':
            return None
        
        active_session = KuesionerSession.objects.filter(
            kuesioner=kuesioner,
            is_active=True
        ).order_by('-started_at').first()
        
        # If no active session, get the latest session (for when quiz is finished)
        if not active_session:
            active_session = KuesionerSession.objects.filter(
                kuesioner=kuesioner
            ).order_by('-started_at').first()
        
        if not active_session:
            print(f"⚠️ No session found for kuesioner {kuesioner_id}")
            return None
        
        # Get all questions for this kuesioner
        questions = Question.objects.filter(kuesioner=kuesioner).order_by('number')
        all_results = []
        
        for question in questions:
            answers = GuestQuizAnswer.objects.filter(
                question=question,
                guest__session=active_session,
                text_answer__isnull=False
            ).exclude(text_answer='').select_related('guest').order_by('-created_at')
            
            responses = []
            for answer in answers:
                responses.append({
                    'id': str(answer.id),
                    'participant_name': answer.guest.guest_name,
                    'participant_id': str(answer.guest.id),
                    'answer': answer.text_answer,
                    'submitted_at': answer.created_at.isoformat()
                })
            
            question_result = {
                'question': {
                    'id': str(question.id),
                    'question_text': question.question_text,
                    'number': question.number
                },
                'responses': responses,
                'total_responses': len(responses)
            }
            
            all_results.append(question_result)
        
        return {
            'type': 'all_openended_responses',
            'kuesioner_id': str(kuesioner_id),
            'session_id': str(active_session.id),
            'session_participants': active_session.total_participants,
            'total_questions': len(all_results),
            'questions': all_results
        }
        
    except (Question.DoesNotExist, Kuesioner.DoesNotExist) as e:
        print(f"❌ Error in get_all_openended_responses: {e}")
        return None
    except Exception as e:
        print(f"❌ Error in get_all_openended_responses: {e}")
        return None