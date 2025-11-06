from django.db.models import Count, Q
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from ..models import Question, Choice, GuestQuizAnswer, KuesionerSession, Kuesioner
import json

channel_layer = get_channel_layer()

def send_polling_results_to_teacher(kuesioner_id, question_id):
    """
    Send real-time polling results to teacher for a specific question
    """
    try:
        question = Question.objects.get(id=question_id)
        kuesioner = Kuesioner.objects.get(id=kuesioner_id)
        
        if kuesioner.question_type != 'Polling':
            print(f"⚠️ Question {question.number} is not a polling question, skipping results")
            return
        
        active_session = KuesionerSession.objects.filter(
            kuesioner=kuesioner,
            is_active=True
        ).order_by('-started_at').first()
        
        if not active_session:
            print(f"⚠️ No active session found for kuesioner {kuesioner_id}")
            return
        
        choices = Choice.objects.filter(question=question).order_by('id')
        choice_results = []
        total_votes = 0
        
        for choice in choices:
            vote_count = GuestQuizAnswer.objects.filter(
                question=question,
                selected_choices=choice,
                guest__session=active_session
            ).count()
            
            choice_results.append({
                'id': str(choice.id),
                'choice_text': choice.choice_text,
                'vote_count': vote_count,
                'is_correct': choice.is_correct
            })
            total_votes += vote_count
        
        for choice_result in choice_results:
            choice_result['percentage'] = (
                round((choice_result['vote_count'] / total_votes) * 100, 1) 
                if total_votes > 0 else 0
            )
        
        polling_results = {
            'type': 'polling_results',
            'question': {
                'id': str(question.id),
                'question_text': question.question_text,
                'number': question.number
            },
            'results': choice_results,
            'total_votes': total_votes,
            'session_id': str(active_session.id),
            'session_participants': active_session.total_participants
        }
        
        teacher_group_name = f'kuesioner_{kuesioner_id}_teacher'
        
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                teacher_group_name,
                {
                    'type': 'polling_results_update',
                    'message': polling_results
                }
            )
        else:
            print(f"❌ Channel layer not available")
            
    except Question.DoesNotExist:
        print(f"❌ Question {question_id} does not exist")
    except Kuesioner.DoesNotExist:
        print(f"❌ Kuesioner {kuesioner_id} does not exist")
    except Exception as e:
        print(f"❌ Error in send_polling_results_to_teacher: {e}")

def get_polling_results(kuesioner_id, question_id):
    """
    Get polling results for a specific question (synchronous version)
    """
    try:
        question = Question.objects.get(id=question_id)
        kuesioner = Kuesioner.objects.get(id=kuesioner_id)
        
        if kuesioner.question_type != 'Polling':
            return None
        
        active_session = KuesionerSession.objects.filter(
            kuesioner=kuesioner,
            is_active=True
        ).order_by('-started_at').first()
        
        if not active_session:
            return None
        
        choices = Choice.objects.filter(question=question).annotate(
            vote_count=Count(
                'guestquizanswer',
                filter=Q(
                    guestquizanswer__guest__session=active_session,
                    guestquizanswer__question=question
                )
            )
        ).order_by('id')
        
        choice_results = []
        total_votes = 0
        
        for choice in choices:
            choice_results.append({
                'id': str(choice.id),
                'choice_text': choice.choice_text,
                'vote_count': choice.vote_count,
                'is_correct': choice.is_correct
            })
            total_votes += choice.vote_count
        
        for choice_result in choice_results:
            choice_result['percentage'] = (
                round((choice_result['vote_count'] / total_votes) * 100, 1) 
                if total_votes > 0 else 0
            )
        
        return {
            'question': {
                'id': str(question.id),
                'question_text': question.question_text,
                'number': question.number
            },
            'results': choice_results,
            'total_votes': total_votes,
            'session_id': str(active_session.id),
            'session_participants': active_session.total_participants
        }
        
    except (Question.DoesNotExist, Kuesioner.DoesNotExist) as e:
        print(f"❌ Error in get_polling_results: {e}")
        return None
    except Exception as e:
        print(f"❌ Error in get_polling_results: {e}")
        return None

def get_all_polling_results(kuesioner_id):
    """
    Get polling results for ALL questions in a kuesioner (for quiz finish)
    """
    try:
        kuesioner = Kuesioner.objects.get(id=kuesioner_id)
        
        if kuesioner.question_type != 'Polling':
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
            choices = Choice.objects.filter(question=question).annotate(
                vote_count=Count(
                    'guestquizanswer',
                    filter=Q(
                        guestquizanswer__guest__session=active_session,
                        guestquizanswer__question=question
                    )
                )
            ).order_by('id')
            
            choice_results = []
            total_votes = 0
            
            for choice in choices:
                choice_results.append({
                    'id': str(choice.id),
                    'choice_text': choice.choice_text,
                    'vote_count': choice.vote_count,
                    'is_correct': choice.is_correct
                })
                total_votes += choice.vote_count
            
            # Calculate percentages
            for choice_result in choice_results:
                choice_result['percentage'] = (
                    round((choice_result['vote_count'] / total_votes) * 100, 1) 
                    if total_votes > 0 else 0
                )
            
            question_result = {
                'question': {
                    'id': str(question.id),
                    'question_text': question.question_text,
                    'number': question.number
                },
                'results': choice_results,
                'total_votes': total_votes
            }
            
            all_results.append(question_result)
        
        return {
            'type': 'all_polling_results',
            'kuesioner_id': str(kuesioner_id),
            'session_id': str(active_session.id),
            'session_participants': active_session.total_participants,
            'total_questions': len(all_results),
            'questions': all_results
        }
        
    except (Question.DoesNotExist, Kuesioner.DoesNotExist) as e:
        print(f"❌ Error in get_all_polling_results: {e}")
        return None
    except Exception as e:
        print(f"❌ Error in get_all_polling_results: {e}")
        return None